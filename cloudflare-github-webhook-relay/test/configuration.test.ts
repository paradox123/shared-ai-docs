import { expect, it } from "vitest";

import configurationText from "../wrangler.jsonc?raw";

interface QueueConsumerConfiguration {
  queue?: unknown;
  max_batch_size?: unknown;
  max_batch_timeout?: unknown;
  max_retries?: unknown;
  dead_letter_queue?: unknown;
}

it("configures finite retries and a named dead-letter queue for the primary Queue", () => {
  const configuration = JSON.parse(configurationText) as {
    compatibility_date?: unknown;
    compatibility_flags?: unknown;
    vpc_services?: unknown;
    queues?: { consumers?: QueueConsumerConfiguration[] };
    observability?: { enabled?: unknown; traces?: { enabled?: unknown; head_sampling_rate?: unknown } };
  };
  const consumer = configuration.queues?.consumers?.[0];

  expect(configuration.compatibility_date).toBe("2026-08-22");
  expect(configuration.compatibility_flags).toEqual(["nodejs_compat"]);
  expect(configuration.vpc_services).toEqual([
    {
      binding: "LOCAL_NETWORK",
      service_id: "01a02e8e-5e1d-70f1-90ef-83c0030fb326",
      remote: true,
    },
  ]);
  expect(consumer).toEqual({
    queue: "danielsvault-github-deliveries",
    max_batch_size: 10,
    max_batch_timeout: 5,
    max_retries: 3,
    dead_letter_queue: "danielsvault-github-deliveries-dlq",
  });
  expect(configuration.observability?.enabled).toBe(true);
  expect(configuration.observability?.traces).toEqual({ enabled: true, head_sampling_rate: 0.01 });
});

it("binds the live relay to the probare-crm adapter profile and exact VPC service", () => {
  const configuration = JSON.parse(configurationText) as {
    vars?: Record<string, string>;
  };

  expect(configuration.vars).toEqual({
    ALLOWED_REPOSITORIES: "paradox123/probare-crm",
    ALLOWED_EVENT_ACTIONS:
      "issue_comment:created,issue_comment:edited,issues:closed,issues:edited,issues:labeled,issues:opened,issues:reopened,issues:unlabeled,pull_request:closed,pull_request:opened,pull_request:synchronize,pull_request_review:dismissed,pull_request_review:submitted,pull_request_review_comment:created,pull_request_review_comment:edited",
    MAX_BODY_BYTES: "100000",
    LOCAL_RECEIVER_URL: "http://127.0.0.1:8788/webhooks/github",
  });
});
