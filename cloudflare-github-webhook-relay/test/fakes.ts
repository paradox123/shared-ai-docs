export class ImmediateQueue implements Queue {
  readonly messages: unknown[] = [];

  async metrics(): Promise<QueueMetrics> {
    return { backlogCount: this.messages.length, backlogBytes: 0 };
  }

  async send(message: unknown): Promise<QueueSendResponse> {
    this.messages.push(message);
    return { metadata: { metrics: { backlogCount: this.messages.length, backlogBytes: 0 } } };
  }

  async sendBatch(messages: Iterable<MessageSendRequest>): Promise<QueueSendBatchResponse> {
    this.messages.push(...Array.from(messages, (message) => message.body));
    return { metadata: { metrics: { backlogCount: this.messages.length, backlogBytes: 0 } } };
  }
}

export function testEnv(queue: Queue): Env {
  return {
    DELIVERY_QUEUE: queue,
    ALLOWED_REPOSITORIES: "daniel/probare-crm",
    ALLOWED_EVENT_ACTIONS: "issues:labeled",
    MAX_BODY_BYTES: "100000",
    LOCAL_RECEIVER_URL: "https://github-pilot.example.com/webhooks/github",
    GITHUB_WEBHOOK_SECRET: "github-edge-test-secret",
    PILOT_INTERNAL_WEBHOOK_SECRET: "internal-relay-test-secret",
  };
}
