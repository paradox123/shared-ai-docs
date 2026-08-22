## Context

The existing Python package owns the productive local `POST /webhooks/github` seam and atomically deduplicates deliveries in SQLite by `X-GitHub-Delivery`. It currently expects GitHub's signature directly and therefore cannot distinguish a separately authenticated Cloudflare-to-Mac hop. The new edge module runs in a different trust boundary and must buffer short Mac outages without adding inbound router access, polling, or paid infrastructure.

Cloudflare Queues on Workers Free has a non-configurable 24-hour retention period and at-least-once consumer delivery. Queue `send()` resolves only after the message is written, while an explicitly acknowledged consumer message is removed; retries can be delayed and exhausted messages can be routed to a configured dead-letter queue. The design treats these platform semantics as an operating boundary rather than promising end-to-end exactly-once transport.

## Goals / Non-Goals

**Goals:**

- Authenticate the unchanged raw GitHub body before JSON parsing and reject all requests outside explicit size, repository, event, and action bounds without queue effects.
- Publish one serializable envelope for each accepted HTTP request and await durable Queue acceptance before returning success.
- Preserve GitHub's delivery GUID end to end so at-least-once queue delivery converges on the existing local inbox and one claim.
- Authenticate the second hop with a different secret over delivery ID, event, and raw body, then acknowledge only a recognized durable local acceptance response.
- Retry failed local deliveries with bounded exponential backoff and use a named dead-letter queue after the configured attempt limit.
- Provide deployable, secret-free Worker/Tunnel configuration and direct behavioral verification at Worker and local HTTP seams.

**Non-Goals:**

- Guaranteeing availability beyond the free plan's 24-hour Queue retention window.
- Deduplicating producer writes across repeated GitHub HTTP deliveries; Queue transport is at-least-once and the durable local inbox remains the idempotency authority.
- Cloudflare Access in front of the machine webhook path, inbound router ports, periodic GitHub polling, or issue-10 startup reconciliation.
- Provisioning a real Cloudflare account, DNS zone, queue, tunnel, or production secret from this repository.
- Changing claim eligibility, LangGraph scheduling, worktree execution, review, merge, or deployment behavior.

## Decisions

### Use one TypeScript Worker module for the edge `fetch` and Queue `queue` handlers

`cloudflare-github-webhook-relay/` contains a module Worker with a Queue producer binding and a push consumer for the same named primary queue. The fetch handler has one public path, buffers only a configured sub-128-KB body, verifies `X-Hub-Signature-256` with Web Crypto over the unchanged bytes, validates the parsed envelope, awaits exactly one `QUEUE.send(...)`, and then returns `202`.

Alternative considered: a Python or generic HTTP relay outside Workers. It would not execute against Cloudflare's runtime or binding types and would weaken the deployable contract this issue requires.

### Rely on end-to-end idempotency rather than an edge deduplication store

The Queue envelope contains a schema version, `delivery_id`, `event`, `action`, `repository`, content type, and the unchanged body bytes as a structured-cloneable `ArrayBuffer`. It never contains either signature or secret. Repeated GitHub requests may produce repeated Queue messages because Cloudflare Queues is at-least-once and offers no transactional uniqueness constraint with `send()`. Every copy keeps the same delivery ID, and the existing local SQLite inbox returns `already_accepted` without a second run or GitHub claim.

Alternative considered: D1 or Durable Object edge deduplication. Neither can atomically commit its state and a Queue send, creating crash windows that falsely suppress or duplicate delivery while adding a second idempotency authority. The local inbox already provides the required durable convergence point.

### Sign a canonical second-hop representation with a separate secret

The consumer computes HMAC-SHA256 over the UTF-8 bytes of `delivery_id + "\\n" + event + "\\n"` followed by the unchanged body bytes and sends it as `X-Pilot-Signature-256`. The local receiver can run in either direct-GitHub mode or relay mode, but exactly one authentication mode is configured per application instance. Relay mode verifies this signature before JSON parsing and then reuses the existing repository/event/action checks and atomic inbox code. The GitHub signature is not forwarded.

Alternative considered: signing only the body. That would leave the delivery identity and event header outside the integrity boundary. Forwarding and rechecking the GitHub signature would also fail the explicit requirement for independent hop authentication.

### Treat only the local receiver's durable acceptance contract as success

The consumer sends the original body to the configured HTTPS Tunnel URL, whose pathname must be exactly `/webhooks/github`. It acknowledges a Queue message only when the receiver returns `202 {status: "accepted"}` or `200 {status: "already_accepted"}` with the same delivery ID. Network errors, malformed responses, unexpected 2xx results, and all non-2xx statuses call `message.retry({delaySeconds})`.

Backoff is deterministic and bounded: `min(300, 5 * 2^(attempts-1))` seconds. The Wrangler consumer configuration sets `max_retries` and `dead_letter_queue`; after that limit Cloudflare moves the still-failing message to the named DLQ. Structured logs include only outcome, delivery ID, attempt, status, and delay—never bodies, signatures, or secrets.

Alternative considered: acknowledge every 2xx response. A generic or malformed 2xx does not prove that the durable local inbox accepted the intended delivery.

### Publish only the exact local webhook path through a named outbound Tunnel

A checked-in example `cloudflared` configuration uses a named tunnel, one hostname-plus-path ingress rule targeting `http://127.0.0.1:8788`, and a final `http_status:404` catch-all. Setup guidance validates the ingress rules and documents that `cloudflared` creates outbound-only connections, no router port is opened, and no Access application is placed before this machine endpoint. The Worker validates its receiver URL as HTTPS with the exact pathname before delivery.

Alternative considered: expose the receiver directly or protect it with interactive Access. Direct exposure violates the network boundary, while Access would intercept the machine-to-machine request before the receiver's HMAC contract.

### Test through public handlers and a shared hop contract

Worker tests run in the Workers Vitest runtime and invoke the exported `fetch` and `queue` handlers. Only Queue and outbound HTTP are controlled boundaries. Python tests drive the productive local HTTP route with relay-signed bodies and real SQLite/LangGraph persistence. Shared fixed examples ensure both runtimes compute the same canonical HMAC. Configuration checks and Wrangler dry-run/types validation prove the Queue/DLQ binding contract; a duplicate relay delivery test proves convergence to one local run and claim.

## Risks / Trade-offs

- [The Mac can remain offline beyond 24 hours and messages then expire] → Document the free-tier limit explicitly and leave compensation to issue 10's startup reconciliation.
- [A repeated GitHub delivery can enqueue more than one message] → Preserve `X-GitHub-Delivery` unchanged and require local atomic deduplication before any claim side effect.
- [A crash can occur after local acceptance but before Queue acknowledgement] → The message is retried and the local receiver returns `already_accepted`, after which it is safely acknowledged.
- [Tunnel hostname or DNS is operator-specific] → Commit placeholders and deterministic validators, keep credentials out of the repository, and require operator provisioning before live activation.
- [Logging delivery IDs reveals correlation metadata] → Log only the minimum identifier needed to find a failed delivery; never log raw payloads, headers, signatures, or response bodies.
- [Platform limits or configuration fields change] → Pin tested toolchain versions in the lockfile, use generated Wrangler binding types, validate against Wrangler's bundled schema, and record the accepted 24-hour constraint in docs/specs.

## Migration Plan

1. Deploy the Worker and create the primary Queue plus named DLQ on Workers Free.
2. Store `GITHUB_WEBHOOK_SECRET` and `PILOT_INTERNAL_WEBHOOK_SECRET` with Wrangler secret commands; configure only non-secret allowlists and receiver URL in `vars`.
3. Create the named Tunnel and DNS route, install its credentials outside the repository, validate the exact ingress rule, and start `cloudflared` outbound from the Mac.
4. Start the local receiver in relay-authentication mode with the matching internal secret, still bound to loopback.
5. Send a signed test delivery, observe Queue consumption and the local workflow read model, then point the GitHub webhook at the Worker route.
6. Roll back by restoring the prior GitHub webhook target and stopping the Worker consumer/Tunnel; retained Queue messages can be inspected or drained without changing the local database.

## Open Questions

None for this slice. Real account identifiers, hostname, and tunnel credentials are deployment inputs reserved for issue 12 live activation.
