## Why

The local issue-claim receiver is unavailable while the Mac sleeps or is offline, so GitHub cannot reliably start authorized work through direct webhooks. This slice adds the bounded Cloudflare relay promised by pilot issue 09 while accepting the free plan's guaranteed 24-hour retention window.

## What Changes

- Add a separately deployable Cloudflare Worker that authenticates the unchanged GitHub request body, enforces repository/event/action allowlists, and publishes an accepted delivery to Cloudflare Queues before acknowledging it.
- Preserve `X-GitHub-Delivery` as the delivery identity across the queue and local inbox while treating queue delivery as at-least-once.
- Add a Queue consumer that signs the second hop with a distinct internal secret and delivers only to the receiver's named Tunnel hostname and exact webhook path.
- Retry non-durable local outcomes with bounded backoff and route exhausted deliveries to a named dead-letter queue with secret-free structured logs.
- Extend the local receiver to authenticate the independently signed relay request without exposing either hop's secret.
- Add contract and system behavior tests for acceptance, rejection, retry, dead-letter configuration, and deduplicated delivery through the local claim seam.

## Capabilities

### New Capabilities

- `cloudflare-github-webhook-relay`: Authenticated Cloudflare edge ingress, 24-hour Queue buffering, separately signed Tunnel delivery, retry, and dead-letter behavior.

### Modified Capabilities

- `local-github-issue-claim`: The productive webhook path can authenticate a separately signed Cloudflare relay hop while preserving the existing durable inbox and delivery-id contract.

## Impact

- **Write-set:** a new TypeScript Worker package under `cloudflare-github-webhook-relay/`, local receiver authentication/configuration and tests under `langgraph-github-issue-pilot/`, the active OpenSpec artifacts, pilot operating documentation, and issue 09 evidence/checklist updates.
- **Interfaces:** Cloudflare `POST /webhooks/github`, a Queue producer/consumer binding, and the existing local `POST /webhooks/github` route reached through one named Tunnel hostname and path.
- **Infrastructure:** Workers Free, Cloudflare Queues with non-configurable 24-hour free-plan retention, a named Cloudflare Tunnel, and a named dead-letter queue; no router ingress port or Cloudflare Access policy in front of the machine webhook path.
- **Secrets:** the GitHub webhook secret exists only at the edge; a different internal relay secret exists in the consumer and local receiver; both are provisioned outside version control.
- **Direct verification:** drive signed and rejected raw requests through the Worker handler, drive Queue batches through the consumer against the productive local HTTP route, and observe HTTP outcomes, queue acknowledgements/retries, dead-letter configuration, local read models, and controlled GitHub effects.
