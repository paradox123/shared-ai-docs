export class ImmediateQueue implements Queue {
  readonly messages: unknown[] = [];
  readonly sendOptions: Array<QueueSendOptions | undefined> = [];

  async metrics(): Promise<QueueMetrics> {
    return { backlogCount: this.messages.length, backlogBytes: 0 };
  }

  async send(message: unknown, options?: QueueSendOptions): Promise<QueueSendResponse> {
    this.messages.push(message);
    this.sendOptions.push(options);
    return { metadata: { metrics: { backlogCount: this.messages.length, backlogBytes: 0 } } };
  }

  async sendBatch(messages: Iterable<MessageSendRequest>): Promise<QueueSendBatchResponse> {
    this.messages.push(...Array.from(messages, (message) => message.body));
    return { metadata: { metrics: { backlogCount: this.messages.length, backlogBytes: 0 } } };
  }
}

export function testEnv(queue: Queue): Env {
  const environment = {
    DELIVERY_QUEUE: queue,
    LOCAL_NETWORK: { fetch: (input: RequestInfo | URL, init?: RequestInit) => fetch(input, init) },
    ALLOWED_REPOSITORIES: "daniel/probare-crm",
    ALLOWED_EVENT_ACTIONS: "issues:labeled,pull_request_review:submitted,pull_request_review_comment:created,pull_request:closed",
    MAX_BODY_BYTES: "100000",
    LOCAL_RECEIVER_URL: "http://127.0.0.1:8788/webhooks/github",
    GITHUB_WEBHOOK_SECRET: "github-edge-test-secret",
    PILOT_INTERNAL_WEBHOOK_SECRET: "internal-relay-test-secret",
  };
  // Wrangler narrows configured production vars to string literals. Tests
  // deliberately substitute other valid values to exercise policy boundaries.
  return environment as unknown as Env;
}
