import { createExecutionContext } from "cloudflare:test";
import { expect, it } from "vitest";

import worker, { type DeliveryEnvelope } from "../src/index";
import { ImmediateQueue, testEnv } from "./fakes";

const GITHUB_SECRET = "github-edge-test-secret";
const BODY = JSON.stringify({
  action: "labeled",
  repository: { full_name: "daniel/probare-crm" },
  issue: { number: 41 },
  label: { name: "ready-for-agent" },
});

class RecordingQueue extends ImmediateQueue {
  private readonly sendStarted: Promise<void>;
  private markSendStarted: (() => void) | undefined;
  private releaseSend: (() => void) | undefined;

  constructor() {
    super();
    this.sendStarted = new Promise<void>((resolve) => {
      this.markSendStarted = resolve;
    });
  }

  override async send(message: unknown): Promise<QueueSendResponse> {
    this.messages.push(message);
    this.markSendStarted?.();
    await new Promise<void>((resolve) => {
      this.releaseSend = resolve;
    });
    return { metadata: { metrics: { backlogCount: this.messages.length, backlogBytes: 0 } } };
  }

  release(): void {
    this.releaseSend?.();
  }

  async waitForSend(): Promise<void> {
    await this.sendStarted;
  }
}

class FailingQueue extends ImmediateQueue {
  override async send(message: unknown): Promise<QueueSendResponse> {
    this.messages.push(message);
    throw new Error("queue unavailable");
  }
}

async function githubSignature(body: string | Uint8Array): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(GITHUB_SECRET),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const bytes = typeof body === "string" ? new TextEncoder().encode(body) : body;
  const digest = await crypto.subtle.sign("HMAC", key, bytes);
  return `sha256=${Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("")}`;
}

it("accepts a valid GitHub delivery only after one durable Queue publication", async () => {
  const queue = new RecordingQueue();
  const signature = await githubSignature(BODY);
  const request = new Request("https://relay.example.com/webhooks/github", {
    method: "POST",
    headers: {
      "content-type": "application/json; charset=utf-8",
      "x-github-delivery": "delivery-001",
      "x-github-event": "issues",
      "x-hub-signature-256": signature,
    },
    body: BODY,
  });

  const responsePromise = worker.fetch(request, testEnv(queue), createExecutionContext());
  await queue.waitForSend();

  expect(queue.messages).toHaveLength(1);
  expect(queue.messages[0]).toEqual({
    schema_version: 1,
    delivery_id: "delivery-001",
    event: "issues",
    action: "labeled",
    repository: "daniel/probare-crm",
    content_type: "application/json; charset=utf-8",
    raw_body: new TextEncoder().encode(BODY).buffer,
  });

  let responseSettled = false;
  void responsePromise.then(() => {
    responseSettled = true;
  });
  await Promise.resolve();
  expect(responseSettled).toBe(false);

  queue.release();
  const response = await responsePromise;

  expect(response.status).toBe(202);
  await expect(response.json()).resolves.toEqual({
    delivery_id: "delivery-001",
    status: "accepted",
  });
});

it("preserves the exact authenticated JSON bytes in the Queue envelope", async () => {
  const queue = new ImmediateQueue();
  const json = BODY.replace('"ready-for-agent"', '"bereit-✓"');
  const encoded = new TextEncoder().encode(json);
  const body = new Uint8Array(encoded.byteLength + 3);
  body.set([0xef, 0xbb, 0xbf]);
  body.set(encoded, 3);
  const signature = await githubSignature(body);
  const request = new Request("https://relay.example.com/webhooks/github", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-github-delivery": "delivery-binary-001",
      "x-github-event": "issues",
      "x-hub-signature-256": signature,
    },
    body,
  });

  const response = await worker.fetch(request, testEnv(queue), createExecutionContext());

  expect(response.status).toBe(202);
  const envelope = queue.messages[0] as DeliveryEnvelope;
  expect(new Uint8Array(envelope.raw_body)).toEqual(body);
});

it.each([
  {
    name: "wrong method",
    method: "GET",
    path: "/webhooks/github",
    body: BODY,
    headers: {},
    expectedStatus: 404,
  },
  {
    name: "wrong path",
    method: "POST",
    path: "/webhooks/other",
    body: BODY,
    headers: {},
    expectedStatus: 404,
  },
  {
    name: "body too large",
    method: "POST",
    path: "/webhooks/github",
    body: BODY,
    headers: {},
    maximum: "16",
    expectedStatus: 413,
  },
  {
    name: "invalid signature before invalid JSON",
    method: "POST",
    path: "/webhooks/github",
    body: "not-json",
    headers: { "x-hub-signature-256": "sha256=invalid" },
    expectedStatus: 401,
  },
  {
    name: "malformed signed JSON",
    method: "POST",
    path: "/webhooks/github",
    body: "not-json",
    headers: {},
    expectedStatus: 400,
  },
  {
    name: "missing delivery ID",
    method: "POST",
    path: "/webhooks/github",
    body: BODY,
    headers: { "x-github-delivery": "" },
    expectedStatus: 400,
  },
  {
    name: "unsupported content type",
    method: "POST",
    path: "/webhooks/github",
    body: BODY,
    headers: { "content-type": "text/plain" },
    expectedStatus: 415,
  },
  {
    name: "disallowed repository",
    method: "POST",
    path: "/webhooks/github",
    body: BODY,
    headers: {},
    repositories: "daniel/other",
    expectedStatus: 403,
  },
  {
    name: "disallowed event",
    method: "POST",
    path: "/webhooks/github",
    body: BODY,
    headers: { "x-github-event": "pull_request" },
    expectedStatus: 403,
  },
  {
    name: "disallowed action",
    method: "POST",
    path: "/webhooks/github",
    body: BODY.replace('"labeled"', '"edited"'),
    headers: {},
    expectedStatus: 403,
  },
])("rejects $name without a Queue effect", async (example) => {
  const queue = new ImmediateQueue();
  const signature = await githubSignature(example.body);
  const headers = new Headers({
    "content-type": "application/json",
    "x-github-delivery": "delivery-001",
    "x-github-event": "issues",
    "x-hub-signature-256": signature,
    ...example.headers,
  });
  const env = testEnv(queue);
  if (example.maximum !== undefined) {
    Object.assign(env, { MAX_BODY_BYTES: example.maximum });
  }
  if (example.repositories !== undefined) {
    Object.assign(env, { ALLOWED_REPOSITORIES: example.repositories });
  }
  const request = new Request(`https://relay.example.com${example.path}`, {
    method: example.method,
    headers,
    body: example.method === "GET" ? undefined : example.body,
  });

  const response = await worker.fetch(request, env, createExecutionContext());

  expect(response.status).toBe(example.expectedStatus);
  expect(queue.messages).toEqual([]);
});

it("returns a retryable error when durable Queue publication fails", async () => {
  const queue = new FailingQueue();
  const signature = await githubSignature(BODY);
  const request = new Request("https://relay.example.com/webhooks/github", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-github-delivery": "delivery-001",
      "x-github-event": "issues",
      "x-hub-signature-256": signature,
    },
    body: BODY,
  });

  const response = await worker.fetch(request, testEnv(queue), createExecutionContext());

  expect(response.status).toBe(503);
  await expect(response.json()).resolves.toEqual({ error: "queue unavailable" });
  expect(queue.messages).toHaveLength(1);
});

it.each(["", "0", "-1", "not-a-number", "120001", "16px"])(
  "rejects invalid MAX_BODY_BYTES configuration %j without reading or queuing the body",
  async (maximum) => {
    const body = new ReadableStream<Uint8Array>({
      pull(controller) {
        controller.enqueue(new TextEncoder().encode(BODY));
        controller.close();
      },
    });
    const queue = new ImmediateQueue();
    const env = testEnv(queue);
    Object.assign(env, { MAX_BODY_BYTES: maximum });
    const request = new Request("https://relay.example.com/webhooks/github", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body,
    });

    const response = await worker.fetch(request, env, createExecutionContext());

    expect(response.status).toBe(500);
    expect(queue.messages).toEqual([]);
  },
);

it("stops reading an untrusted streaming body as soon as its configured limit is exceeded", async () => {
  let pulls = 0;
  let cancelled = false;
  const body = new ReadableStream<Uint8Array>({
    pull(controller) {
      pulls += 1;
      if (pulls <= 10) {
        controller.enqueue(new Uint8Array(10));
      } else {
        controller.close();
      }
    },
    cancel() {
      cancelled = true;
    },
  });
  const queue = new ImmediateQueue();
  const env = testEnv(queue);
  Object.assign(env, { MAX_BODY_BYTES: "16" });
  const request = new Request("https://relay.example.com/webhooks/github", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });

  const response = await worker.fetch(request, env, createExecutionContext());

  expect(response.status).toBe(413);
  expect(pulls).toBeLessThanOrEqual(3);
  expect(cancelled).toBe(true);
  expect(queue.messages).toEqual([]);
});
