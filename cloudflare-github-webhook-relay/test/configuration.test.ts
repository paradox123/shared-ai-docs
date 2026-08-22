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
    queues?: { consumers?: QueueConsumerConfiguration[] };
    observability?: { enabled?: unknown; traces?: { enabled?: unknown; head_sampling_rate?: unknown } };
  };
  const consumer = configuration.queues?.consumers?.[0];

  expect(configuration.compatibility_date).toBe("2026-08-22");
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
