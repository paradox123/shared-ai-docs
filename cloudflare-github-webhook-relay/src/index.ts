export interface DeliveryEnvelope {
  schema_version: 1;
  delivery_id: string;
  event: string;
  action: string;
  repository: string;
  content_type: string;
  raw_body: ArrayBuffer;
}

interface GitHubPayload {
  action: string;
  repository: { full_name: string };
}

const encoder = new TextEncoder();
const MAXIMUM_CONFIGURED_BODY_BYTES = 120_000;

function jsonResponse(body: object, status: number): Response {
  return Response.json(body, { status });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseGitHubPayload(rawBody: string): GitHubPayload | undefined {
  let value: unknown;
  try {
    value = JSON.parse(rawBody);
  } catch {
    return undefined;
  }
  if (!isRecord(value) || typeof value.action !== "string" || !isRecord(value.repository)) {
    return undefined;
  }
  const fullName = value.repository.full_name;
  if (typeof fullName !== "string") {
    return undefined;
  }
  return { action: value.action, repository: { full_name: fullName } };
}

function hexBytes(value: string): Uint8Array | undefined {
  if (!/^[0-9a-f]{64}$/i.test(value)) {
    return undefined;
  }
  const bytes = new Uint8Array(32);
  for (let index = 0; index < value.length; index += 2) {
    bytes[index / 2] = Number.parseInt(value.slice(index, index + 2), 16);
  }
  return bytes;
}

async function validGitHubSignature(body: Uint8Array, supplied: string | null, secret: string): Promise<boolean> {
  if (supplied === null || !supplied.startsWith("sha256=")) {
    return false;
  }
  const signature = hexBytes(supplied.slice("sha256=".length));
  if (signature === undefined) {
    return false;
  }
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  );
  return crypto.subtle.verify("HMAC", key, signature, body);
}

function allowed(value: string, configured: string): boolean {
  return configured.split(",").some((candidate) => candidate.trim() === value);
}

async function internalSignature(envelope: DeliveryEnvelope, secret: string): Promise<string> {
  const prefix = encoder.encode(`${envelope.delivery_id}\n${envelope.event}\n`);
  const canonical = new Uint8Array(prefix.byteLength + envelope.raw_body.byteLength);
  canonical.set(prefix);
  canonical.set(new Uint8Array(envelope.raw_body), prefix.byteLength);
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const digest = await crypto.subtle.sign("HMAC", key, canonical);
  const hexadecimal = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  return `sha256=${hexadecimal}`;
}

async function smallJson(response: Response, maximumBytes = 4096): Promise<unknown> {
  const declaredLength = response.headers.get("content-length");
  if (declaredLength !== null && Number.parseInt(declaredLength, 10) > maximumBytes) {
    await response.body?.cancel();
    return undefined;
  }
  if (response.body === null) {
    return undefined;
  }

  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  while (true) {
    const result = await reader.read();
    if (result.done) {
      break;
    }
    size += result.value.byteLength;
    if (size > maximumBytes) {
      await reader.cancel();
      return undefined;
    }
    chunks.push(result.value);
  }

  const body = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  try {
    return JSON.parse(new TextDecoder().decode(body)) as unknown;
  } catch {
    return undefined;
  }
}

function configuredBodyLimit(value: string): number | undefined {
  if (!/^\d+$/.test(value)) {
    return undefined;
  }
  const limit = Number(value);
  if (!Number.isSafeInteger(limit) || limit <= 0 || limit > MAXIMUM_CONFIGURED_BODY_BYTES) {
    return undefined;
  }
  return limit;
}

async function readBoundedBody(request: Request, maximumBytes: number): Promise<Uint8Array | undefined> {
  if (request.body === null) {
    return new Uint8Array();
  }

  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  while (true) {
    const result = await reader.read();
    if (result.done) {
      break;
    }
    size += result.value.byteLength;
    if (size > maximumBytes) {
      try {
        await reader.cancel();
      } catch {
        // The body is already rejected; cancellation is best-effort cleanup.
      }
      return undefined;
    }
    chunks.push(result.value);
  }

  const body = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return body;
}

function isDurableAcceptance(response: Response, value: unknown, deliveryId: string): boolean {
  if (!isRecord(value) || value.delivery_id !== deliveryId || typeof value.status !== "string") {
    return false;
  }
  return (
    (response.status === 202 && value.status === "accepted") ||
    (response.status === 200 && value.status === "already_accepted")
  );
}

function retryDelay(attempts: number): number {
  return Math.min(300, 5 * 2 ** Math.max(0, attempts - 1));
}

function logDelivery(fields: Record<string, string | number>): void {
  console.log(JSON.stringify(fields));
}

function safeReceiverUrl(configured: string): URL | undefined {
  let url: URL;
  try {
    url = new URL(configured);
  } catch {
    return undefined;
  }
  if (
    url.protocol !== "https:" ||
    url.username !== "" ||
    url.password !== "" ||
    url.pathname !== "/webhooks/github" ||
    url.search !== "" ||
    url.hash !== ""
  ) {
    return undefined;
  }
  return url;
}

async function secretsAreDistinct(first: string, second: string): Promise<boolean> {
  const [firstHash, secondHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(first)),
    crypto.subtle.digest("SHA-256", encoder.encode(second)),
  ]);
  return !crypto.subtle.timingSafeEqual(firstHash, secondHash);
}

async function deliverMessage(message: Message<DeliveryEnvelope>, env: Env): Promise<void> {
  const delaySeconds = retryDelay(message.attempts);
  const receiverUrl = safeReceiverUrl(env.LOCAL_RECEIVER_URL);
  if (
    receiverUrl === undefined ||
    !(await secretsAreDistinct(env.GITHUB_WEBHOOK_SECRET, env.PILOT_INTERNAL_WEBHOOK_SECRET))
  ) {
    message.retry({ delaySeconds });
    logDelivery({
      outcome: "configuration_retry",
      delivery_id: message.body.delivery_id,
      attempt: message.attempts,
      delay_seconds: delaySeconds,
    });
    return;
  }
  let response: Response;
  let result: unknown;
  try {
    const signature = await internalSignature(message.body, env.PILOT_INTERNAL_WEBHOOK_SECRET);
    response = await fetch(receiverUrl, {
      method: "POST",
      headers: {
        "content-type": message.body.content_type,
        "x-github-delivery": message.body.delivery_id,
        "x-github-event": message.body.event,
        "x-pilot-signature-256": signature,
      },
      body: message.body.raw_body,
      signal: AbortSignal.timeout(10_000),
    });
    result = await smallJson(response);
  } catch {
    message.retry({ delaySeconds });
    logDelivery({
      outcome: "delivery_retry",
      delivery_id: message.body.delivery_id,
      attempt: message.attempts,
      delay_seconds: delaySeconds,
    });
    return;
  }

  if (isDurableAcceptance(response, result, message.body.delivery_id)) {
    message.ack();
    logDelivery({
      outcome: "delivery_acknowledged",
      delivery_id: message.body.delivery_id,
      attempt: message.attempts,
      status: response.status,
    });
    return;
  }

  message.retry({ delaySeconds });
  logDelivery({
    outcome: "delivery_retry",
    delivery_id: message.body.delivery_id,
    attempt: message.attempts,
    status: response.status,
    delay_seconds: delaySeconds,
  });
}

async function handleIngress(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (request.method !== "POST" || url.pathname !== "/webhooks/github") {
    return jsonResponse({ error: "not found" }, 404);
  }
  const originalContentType = request.headers.get("content-type")?.trim();
  const mediaType = originalContentType?.split(";", 1)[0]?.trim().toLowerCase();
  if (originalContentType === undefined || mediaType !== "application/json") {
    return jsonResponse({ error: "unsupported content type" }, 415);
  }

  const maximum = configuredBodyLimit(env.MAX_BODY_BYTES);
  if (maximum === undefined) {
    console.error(JSON.stringify({ outcome: "invalid_body_limit_configuration" }));
    return jsonResponse({ error: "invalid server configuration" }, 500);
  }
  const declaredLength = request.headers.get("content-length");
  if (declaredLength !== null) {
    if (!/^\d+$/.test(declaredLength)) {
      return jsonResponse({ error: "invalid content length" }, 400);
    }
    if (Number(declaredLength) > maximum) {
      try {
        await request.body?.cancel();
      } catch {
        // The body is already rejected; cancellation is best-effort cleanup.
      }
      return jsonResponse({ error: "request body too large" }, 413);
    }
  }

  let body: Uint8Array | undefined;
  try {
    body = await readBoundedBody(request, maximum);
  } catch {
    return jsonResponse({ error: "invalid request body" }, 400);
  }
  if (body === undefined) {
    return jsonResponse({ error: "request body too large" }, 413);
  }
  if (!(await validGitHubSignature(body, request.headers.get("x-hub-signature-256"), env.GITHUB_WEBHOOK_SECRET))) {
    return jsonResponse({ error: "invalid signature" }, 401);
  }

  let decodedBody: string;
  try {
    decodedBody = new TextDecoder("utf-8", { fatal: true, ignoreBOM: false }).decode(body);
  } catch {
    return jsonResponse({ error: "invalid utf-8 body" }, 400);
  }
  const payload = parseGitHubPayload(decodedBody);
  const deliveryId = request.headers.get("x-github-delivery")?.trim() ?? "";
  const event = request.headers.get("x-github-event")?.trim() ?? "";
  if (payload === undefined || deliveryId.length === 0 || event.length === 0) {
    return jsonResponse({ error: "invalid delivery" }, 400);
  }
  if (
    !allowed(payload.repository.full_name, env.ALLOWED_REPOSITORIES) ||
    !allowed(`${event}:${payload.action}`, env.ALLOWED_EVENT_ACTIONS)
  ) {
    return jsonResponse({ error: "delivery not allowed" }, 403);
  }

  const envelope: DeliveryEnvelope = {
    schema_version: 1,
    delivery_id: deliveryId,
    event,
    action: payload.action,
    repository: payload.repository.full_name,
    content_type: originalContentType,
    raw_body: body.slice().buffer,
  };
  try {
    await env.DELIVERY_QUEUE.send(envelope);
  } catch {
    console.error(JSON.stringify({ outcome: "queue_publish_failed", delivery_id: deliveryId }));
    return jsonResponse({ error: "queue unavailable" }, 503);
  }
  return jsonResponse({ delivery_id: deliveryId, status: "accepted" }, 202);
}

const worker = {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    return handleIngress(request, env);
  },

  async queue(batch: MessageBatch<DeliveryEnvelope>, env: Env, _ctx: ExecutionContext): Promise<void> {
    for (const message of batch.messages) {
      await deliverMessage(message, env);
    }
  },
} satisfies ExportedHandler<Env, DeliveryEnvelope>;

export default worker;
