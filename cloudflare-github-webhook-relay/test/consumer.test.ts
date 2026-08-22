import { createExecutionContext } from "cloudflare:test";
import { HttpResponse, http } from "msw";
import { expect, it, vi } from "vitest";

import worker, { type DeliveryEnvelope } from "../src/index";
import { ImmediateQueue, testEnv } from "./fakes";
import { network } from "./setup";

const BODY =
  '{"action":"labeled","repository":{"full_name":"daniel/probare-crm"},"issue":{"number":41},"label":{"name":"ready-for-agent"}}';
const FIXED_RELAY_SIGNATURE = "sha256=ba8bc97e411592a16dc39e0677ca0ebb8e4348d8d33096f22e2c0c1210396dff";
const ENVELOPE: DeliveryEnvelope = {
  schema_version: 1,
  delivery_id: "delivery-001",
  event: "issues",
  action: "labeled",
  repository: "daniel/probare-crm",
  content_type: "application/json",
  raw_body: new TextEncoder().encode(BODY).buffer as ArrayBuffer,
};

class TestMessage implements Message<DeliveryEnvelope> {
  readonly id = "queue-message-001";
  readonly timestamp = new Date("2026-08-21T10:30:00Z");
  readonly body: DeliveryEnvelope;
  readonly attempts: number;
  acked = false;
  readonly retryDelays: Array<number | undefined> = [];

  constructor(attempts = 1, body = ENVELOPE) {
    this.attempts = attempts;
    this.body = body;
  }

  ack(): void {
    this.acked = true;
  }

  retry(options?: QueueRetryOptions): void {
    this.retryDelays.push(options?.delaySeconds);
  }
}

function batchFor(message: TestMessage): MessageBatch<DeliveryEnvelope> {
  return {
    queue: "danielsvault-github-deliveries",
    messages: [message],
    metadata: { metrics: { backlogCount: 1, backlogBytes: BODY.length } },
    ackAll(): void {
      throw new Error("consumer must acknowledge individual messages");
    },
    retryAll(): void {
      throw new Error("consumer must retry individual messages");
    },
  };
}

function consumerEnv(): Env {
  return testEnv(new ImmediateQueue());
}

it.each([
  { status: 202, outcome: "accepted" },
  { status: 200, outcome: "already_accepted" },
])("acknowledges a matching durable local $outcome response", async ({ status, outcome }) => {
  let observedRequest: { headers: Headers; body: Uint8Array } | undefined;
  network.use(
    http.post("https://github-pilot.example.com/webhooks/github", async ({ request }) => {
      observedRequest = {
        headers: new Headers(request.headers),
        body: new Uint8Array(await request.arrayBuffer()),
      };
      return HttpResponse.json({ delivery_id: "delivery-001", status: outcome }, { status });
    }),
  );
  const message = new TestMessage();

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  expect(message.acked).toBe(true);
  expect(message.retryDelays).toEqual([]);
  expect(observedRequest).toBeDefined();
  expect(observedRequest?.headers.get("x-github-delivery")).toBe("delivery-001");
  expect(observedRequest?.headers.get("x-github-event")).toBe("issues");
  expect(observedRequest?.headers.get("x-pilot-signature-256")).toBe(FIXED_RELAY_SIGNATURE);
  expect(observedRequest?.body).toEqual(new TextEncoder().encode(BODY));
});

it("signs and forwards exact BOM and non-ASCII body bytes", async () => {
  const encoded = new TextEncoder().encode(BODY.replace('"ready-for-agent"', '"bereit-✓"'));
  const rawBody = new Uint8Array(encoded.byteLength + 3);
  rawBody.set([0xef, 0xbb, 0xbf]);
  rawBody.set(encoded, 3);
  const envelope: DeliveryEnvelope = {
    ...ENVELOPE,
    delivery_id: "delivery-binary-001",
    raw_body: rawBody.buffer as ArrayBuffer,
  };
  let observedBody: Uint8Array | undefined;
  let observedSignature: string | null = null;
  network.use(
    http.post("https://github-pilot.example.com/webhooks/github", async ({ request }) => {
      observedBody = new Uint8Array(await request.arrayBuffer());
      observedSignature = request.headers.get("x-pilot-signature-256");
      return HttpResponse.json({ delivery_id: "delivery-binary-001", status: "accepted" }, { status: 202 });
    }),
  );
  const message = new TestMessage(1, envelope);

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  expect(message.acked).toBe(true);
  expect(observedBody).toEqual(rawBody);
  expect(observedSignature).toBe("sha256=09e86f7383c85ebb2f11a2f95dc522b5c6beded123e27d0a1fd759a4b1953326");
});

it.each([
  {
    name: "mismatched delivery",
    response: HttpResponse.json({ delivery_id: "other", status: "accepted" }, { status: 202 }),
  },
  {
    name: "unrecognized success",
    response: HttpResponse.json({ delivery_id: "delivery-001", status: "accepted" }, { status: 200 }),
  },
  { name: "malformed response", response: new HttpResponse("not-json", { status: 202 }) },
  { name: "local rejection", response: HttpResponse.json({ detail: "invalid signature" }, { status: 401 }) },
])("retries a $name without acknowledging it", async ({ response }) => {
  network.use(http.post("https://github-pilot.example.com/webhooks/github", () => response));
  const message = new TestMessage();

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  expect(message.acked).toBe(false);
  expect(message.retryDelays).toEqual([5]);
});

it.each([
  { attempts: 1, expectedDelay: 5 },
  { attempts: 2, expectedDelay: 10 },
  { attempts: 3, expectedDelay: 20 },
  { attempts: 7, expectedDelay: 300 },
  { attempts: 100, expectedDelay: 300 },
])("retries attempt $attempts with bounded backoff $expectedDelay seconds", async ({ attempts, expectedDelay }) => {
  network.use(http.post("https://github-pilot.example.com/webhooks/github", () => HttpResponse.error()));
  const message = new TestMessage(attempts);

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  expect(message.acked).toBe(false);
  expect(message.retryDelays).toEqual([expectedDelay]);
});

it("retries with backoff when the local response stream fails", async () => {
  const failingBody = new ReadableStream({
    pull(controller) {
      controller.error(new Error("response stream failed"));
    },
  });
  network.use(
    http.post(
      "https://github-pilot.example.com/webhooks/github",
      () => new HttpResponse(failingBody, { status: 202 }),
    ),
  );
  const message = new TestMessage(2);

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  expect(message.acked).toBe(false);
  expect(message.retryDelays).toEqual([10]);
});

it.each([
  "http://github-pilot.example.com/webhooks/github",
  "https://github-pilot.example.com/webhooks/other",
  "https://github-pilot.example.com/webhooks/github?bypass=true",
  "https://user:password@github-pilot.example.com/webhooks/github",
])("does not send to unsafe receiver URL %s", async (receiverUrl) => {
  let requests = 0;
  network.use(
    http.post("*", () => {
      requests += 1;
      return HttpResponse.json({ delivery_id: "delivery-001", status: "accepted" }, { status: 202 });
    }),
  );
  const env = consumerEnv();
  Object.assign(env, { LOCAL_RECEIVER_URL: receiverUrl });
  const message = new TestMessage();

  await worker.queue(batchFor(message), env, createExecutionContext());

  expect(requests).toBe(0);
  expect(message.acked).toBe(false);
  expect(message.retryDelays).toEqual([5]);
});

it("does not deliver when the GitHub and internal hop secrets are equal", async () => {
  let requests = 0;
  network.use(
    http.post("*", () => {
      requests += 1;
      return HttpResponse.json({ delivery_id: "delivery-001", status: "accepted" }, { status: 202 });
    }),
  );
  const env = consumerEnv();
  Object.assign(env, { PILOT_INTERNAL_WEBHOOK_SECRET: env.GITHUB_WEBHOOK_SECRET });
  const message = new TestMessage();

  await worker.queue(batchFor(message), env, createExecutionContext());

  expect(requests).toBe(0);
  expect(message.acked).toBe(false);
  expect(message.retryDelays).toEqual([5]);
});

it("keeps payloads, signatures, and secrets out of retry logs", async () => {
  network.use(http.post("https://github-pilot.example.com/webhooks/github", () => HttpResponse.error()));
  const log = vi.spyOn(console, "log").mockImplementation(() => undefined);
  const message = new TestMessage();

  await worker.queue(batchFor(message), consumerEnv(), createExecutionContext());

  const output = log.mock.calls.flat().join("\n");
  expect(output).toContain('"delivery_id":"delivery-001"');
  expect(output).not.toContain(BODY);
  expect(output).not.toContain(FIXED_RELAY_SIGNATURE);
  expect(output).not.toContain("internal-relay-test-secret");
  expect(output).not.toContain("github-edge-test-secret");
  log.mockRestore();
});
