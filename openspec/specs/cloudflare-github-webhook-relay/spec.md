# cloudflare-github-webhook-relay Specification

## Purpose

Define authenticated Cloudflare edge ingestion, 24-hour Queue buffering, independently signed Tunnel delivery, retry and dead-letter handling, and stable verification boundaries for the local GitHub issue pilot.

## Requirements

### Requirement: Authenticate and authorize the edge request before enqueueing
The edge ingress MUST accept only `POST /webhooks/github` requests whose bounded unchanged body has a valid GitHub `X-Hub-Signature-256`, non-empty `X-GitHub-Delivery`, configured repository, and explicitly allowed event/action combination. It MUST verify the signature before parsing JSON and MUST NOT enqueue a rejected request.

#### Scenario: Allowed signed GitHub delivery
- **WHEN** an allowed repository sends a correctly signed bounded `issues/labeled` request with a delivery ID
- **THEN** the edge ingress validates the unchanged body and proceeds to Queue publication

#### Scenario: Invalid or unauthorized edge request
- **WHEN** the method or path is wrong, the body exceeds the configured limit, the signature or delivery ID is invalid, or repository/event/action is not allowed
- **THEN** the ingress returns a reasoned non-success response without publishing a Queue message

### Requirement: Persist the accepted delivery before acknowledging ingress
The edge ingress MUST await one successful Cloudflare Queue `send` for each accepted HTTP request before returning `202`. The serializable Queue envelope MUST preserve the delivery ID, event, action, repository, content type, and unchanged raw body and MUST exclude signatures and secrets.

#### Scenario: Queue publication succeeds
- **WHEN** a valid request is received and the Queue binding durably accepts its envelope
- **THEN** the ingress returns `202` with the same delivery ID and accepted status after exactly one send attempt

#### Scenario: Queue publication fails
- **WHEN** the Queue binding rejects the publication
- **THEN** the ingress returns a retryable server error and does not claim that the delivery was accepted

### Requirement: Operate within the free 24-hour Queue boundary
The relay MUST use Cloudflare Queues on Workers Free with its non-configurable 24-hour message retention and MUST document that availability beyond that window is not guaranteed. Every Queue copy MUST retain `X-GitHub-Delivery` as its end-to-end idempotency key.

#### Scenario: Duplicate at-least-once delivery
- **WHEN** GitHub or Cloudflare delivers the same logical event more than once
- **THEN** every copy carries the same delivery ID so the durable local inbox can converge on one workflow transition

#### Scenario: Offline period exceeds retention
- **WHEN** the local receiver is unavailable beyond the free plan's 24-hour retention window
- **THEN** the relay makes no guarantee that the expired message can still be delivered and operating guidance points to later startup reconciliation

### Requirement: Authenticate the Tunnel hop independently
The Queue consumer MUST send only to a configured HTTPS receiver URL whose pathname is exactly `/webhooks/github` and MUST sign a canonical representation of delivery ID, event, and unchanged body with an internal secret distinct from the GitHub webhook secret. The deployment configuration MUST use a named outbound Cloudflare Tunnel, expose only that receiver path, open no router ingress port, and place no Cloudflare Access application before the machine endpoint.

#### Scenario: Consumer constructs the local request
- **WHEN** a Queue message is delivered to the consumer
- **THEN** it posts the unchanged body and preserved GitHub delivery/event headers with a valid internal signature to the exact configured receiver URL

#### Scenario: Unsafe receiver URL is configured
- **WHEN** the configured receiver URL is not HTTPS or does not use exactly `/webhooks/github`
- **THEN** the consumer does not send the request and marks the message for retry without exposing secret material

### Requirement: Acknowledge only durable local acceptance
The Queue consumer MUST acknowledge an individual message only when the local receiver returns `202 accepted` or `200 already_accepted` for the same delivery ID. It MUST retry network errors, malformed or mismatched responses, unexpected success responses, and non-success statuses with bounded backoff.

#### Scenario: Newly accepted local delivery
- **WHEN** the local receiver durably persists the delivery and returns matching `202 accepted`
- **THEN** the consumer acknowledges that Queue message

#### Scenario: Repeated local delivery
- **WHEN** the local receiver recognizes the delivery ID and returns matching `200 already_accepted`
- **THEN** the consumer acknowledges the Queue message without creating a second local workflow transition

#### Scenario: Local delivery is not durably accepted
- **WHEN** delivery fails, times out, or returns any response outside the recognized durable acceptance contract
- **THEN** the consumer leaves it unacknowledged and requests a bounded delayed retry

### Requirement: Exhausted failures become visible without secret leakage
The primary Queue consumer configuration MUST set a finite retry limit and a named dead-letter queue. When processing reaches the platform retry limit without durable local acceptance, Cloudflare MUST route the message to that DLQ. Relay logs and test evidence MUST exclude request bodies, response bodies, signatures, and secrets.

#### Scenario: Retry limit is exhausted
- **WHEN** a message continues to fail local durable acceptance through the configured retry limit
- **THEN** the platform configuration routes it to the named dead-letter queue and structured logs identify only the delivery, attempt, outcome, status, and retry delay

### Requirement: Verify relay behavior at stable system boundaries
Verification MUST invoke the production Worker `fetch` and `queue` handlers and the production local HTTP receiver, control only Queue and outbound HTTP/GitHub boundaries, and use real local SQLite and LangGraph persistence. It MUST cover acceptance, rejection, retry, dead-letter configuration, hop-signature compatibility, and duplicate convergence to one local claim.

#### Scenario: Contract tests observe edge behavior
- **WHEN** valid, invalid, and failing deliveries are exercised
- **THEN** assertions observe HTTP responses, Queue envelopes, message acknowledgements or retries, and secret-free logs rather than private helper calls

#### Scenario: System test observes duplicate convergence
- **WHEN** the same relay-signed delivery reaches the productive local webhook path more than once
- **THEN** public workflow lookup and controlled GitHub effects show one inbox identity, one LangGraph run, one checkpoint lineage, and one claim
