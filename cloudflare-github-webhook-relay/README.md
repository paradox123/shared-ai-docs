# Cloudflare GitHub Webhook Relay

This package receives GitHub webhooks at Cloudflare, verifies GitHub's raw-body signature and allowlists, buffers accepted deliveries in Cloudflare Queues, and forwards them through a named outbound Cloudflare Tunnel to the local issue pilot. Queue transport is at-least-once; `X-GitHub-Delivery` remains the identity that makes repeated delivery converge on one durable local workflow.

## Trust and delivery boundaries

1. GitHub sends `POST /webhooks/github` with `X-Hub-Signature-256`.
2. The Worker verifies the unchanged bounded body before parsing, checks repository/event/action, and awaits one Queue `send()` before returning `202`.
3. The Queue consumer signs the UTF-8 delivery/event prefix followed by the exact authenticated raw-body bytes with `PILOT_INTERNAL_WEBHOOK_SECRET` and posts those unchanged bytes to the exact Tunnel URL.
4. The local receiver verifies that independent signature and atomically accepts or deduplicates the delivery before replying.
5. The consumer acknowledges only matching `202 accepted` or `200 already_accepted`; every other outcome is retried with bounded backoff.

Queue envelopes and logs exclude both signatures, both secrets, and response/request bodies. `GITHUB_WEBHOOK_SECRET` and `PILOT_INTERNAL_WEBHOOK_SECRET` must be distinct.

`MAX_BODY_BYTES` must be a positive integer no greater than `120000`. The hard ceiling leaves room below Cloudflare Queues' 128-KB message limit for envelope metadata. The Queue envelope stores the raw body as an `ArrayBuffer`, avoiding a lossy text round-trip. Oversized bodies are rejected while streaming rather than buffered in full.

## Accepted operating boundary

Cloudflare Queues on Workers Free provides 10,000 included operations per day and a non-configurable message retention period of 24 hours. This relay therefore guarantees buffering only within that 24-hour window; it does not claim recovery after a longer Mac outage. Issue 10 owns startup reconciliation for that case.

Primary references:

- [Cloudflare Queues pricing and free-plan retention](https://developers.cloudflare.com/queues/platform/pricing/)
- [Cloudflare Queues limits](https://developers.cloudflare.com/queues/platform/limits/)
- [Queue retries and delays](https://developers.cloudflare.com/queues/configuration/batching-retries/)
- [GitHub webhook signature validation](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)

## Local verification

```bash
npm install
npm run types
npm run check
npm run deploy:dry
```

The tests execute the production Worker `fetch` and `queue` handlers in Cloudflare's Workers Vitest runtime. Queue publication and outbound HTTP are the only controlled system boundaries.

## Provision the Worker and Queues

These commands change Cloudflare account state and are intentionally not executed by repository tests:

```bash
npx wrangler queues create danielsvault-github-deliveries
npx wrangler queues create danielsvault-github-deliveries-dlq
npx wrangler secret put GITHUB_WEBHOOK_SECRET
npx wrangler secret put PILOT_INTERNAL_WEBHOOK_SECRET
npm run deploy
```

Do not pipe secrets through shell history or add them to `wrangler.jsonc`, `.env`, evidence, or logs. Replace the example `LOCAL_RECEIVER_URL` hostname in `wrangler.jsonc` before deployment while keeping HTTPS and the exact `/webhooks/github` path.

## Configure the named outbound Tunnel

Install `cloudflared`, authenticate, create a named tunnel, and route the chosen hostname:

```bash
cloudflared tunnel login
cloudflared tunnel create danielsvault-github-pilot
cloudflared tunnel route dns danielsvault-github-pilot github-pilot.example.com
```

Copy [config.example.yml](cloudflared/config.example.yml) to a private configuration location, replace the tunnel UUID, credentials path, and hostname, then validate and run it:

```bash
cloudflared tunnel --config /private/path/config.yml ingress validate
cloudflared tunnel --config /private/path/config.yml ingress rule https://github-pilot.example.com/webhooks/github
cloudflared tunnel --config /private/path/config.yml run danielsvault-github-pilot
```

`cloudflared` establishes outbound-only connections to Cloudflare; no router ingress port is opened. The final `http_status:404` rule and exact path expression prevent the tunnel from publishing any other local route. Do not create a Cloudflare Access application in front of this machine webhook hostname/path: the internal HMAC is the machine authentication contract and Access would intercept it before the receiver.

References:

- [Cloudflare Tunnel outbound-only model](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)
- [Locally managed Tunnel ingress rules](https://developers.cloudflare.com/tunnel/advanced/local-management/configuration-file/)

## Start the local receiver in relay mode

Configure exactly one webhook authentication mode. For Cloudflare relay operation, set only the internal hop secret:

```bash
unset GITHUB_WEBHOOK_SECRET
export PILOT_INTERNAL_WEBHOOK_SECRET="..."
cd ../langgraph-github-issue-pilot
export PILOT_DATABASE_PATH="$PWD/pilot.db"
export PILOT_ALLOWED_REPOSITORIES="daniel/probare-crm"
export GITHUB_TOKEN="..."
uv run github-issue-pilot
```

The receiver stays on `127.0.0.1:8788`; the tunnel terminates at that loopback service.

## Observe retries and dead letters

`wrangler.jsonc` sets three retries and names `danielsvault-github-deliveries-dlq`. Cloudflare moves a still-failing message to that queue after the retry limit. Use `npx wrangler tail` for structured outcome logs and the Cloudflare Queues dashboard to inspect primary/DLQ backlog and individual DLQ messages. The DLQ intentionally has no Worker consumer, so failed messages remain visible until an operator investigates, acknowledges, retries, or retention expires.

Safe retry procedure:

1. Locate logs by `delivery_id`; do not copy payloads or signatures into evidence.
2. Correct the receiver, tunnel, URL, or secret configuration.
3. Redeliver the DLQ message with the same `delivery_id`.
4. Confirm `200 already_accepted` or `202 accepted` and public local workflow state before acknowledging the DLQ copy.

Rollback restores the previous GitHub webhook target and stops the Worker consumer/tunnel. Queue and local database data are not deleted automatically.
