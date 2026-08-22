## Implementation Evidence

Verified on 2026-08-22 in the isolated worktree on branch `codex/issue-09-cloudflare-github-webhooks`.

| Issue 09 criterion | Direct evidence | Result |
| --- | --- | --- |
| OpenSpec before runtime work | `openspec validate github-webhooks-cloudflare-delivery --strict` passed before the Worker behavior was implemented and passed again after implementation. | Verified |
| Authenticate, allowlist, and durably enqueue before `202` | Workers Vitest drives the production `fetch` handler with a fixed raw-body HMAC. It observes the byte-preserved envelope (including BOM and non-ASCII bytes), exactly one awaited Queue `send`, and no settled response until the controlled send completes. | Verified |
| Reject invalid requests without Queue effects | Parameterized production-handler tests observe reasoned HTTP rejection for method, path, streamed/body limit, signature, JSON, delivery ID, content type, repository, event, and action failures while the Queue remains empty. Queue publication failure returns `503`, not acceptance. | Verified |
| Free-plan 24-hour boundary and delivery identity | The OpenSpec and operating guide explicitly accept the non-configurable Workers Free 24-hour retention boundary. Handler/consumer/local HTTP tests preserve `delivery_id` end to end. | Verified |
| Named outbound Tunnel and exact local path | The consumer tests reject non-HTTPS, wrong-path, credential-bearing, or query-bearing URLs. The parsed Tunnel example contains one exact `^/webhooks/github$` loopback route plus a `404` catch-all; operating guidance requires a named outbound tunnel, no router ingress port, and no Access application on this machine endpoint. | Verified at code/configuration boundary; live Tunnel activation is reserved for issue 12. |
| Independent second-hop authentication and secret-free evidence | Worker and Python tests share a fixed canonical HMAC example that binds delivery ID, event, and unchanged body. Ambiguous local auth modes and equal Worker secrets fail safely. Retry logs are asserted not to contain bodies, signatures, or either secret. | Verified |
| Acknowledge, retry, and dead-letter handling | Production `queue` handler tests acknowledge only matching durable `accepted`/`already_accepted` responses and retry network, stream, malformed, mismatched, unsafe-URL, and non-success outcomes with bounded backoff. Configuration tests and Wrangler schema/dry-run validate `max_retries: 3` and named DLQ `danielsvault-github-deliveries-dlq`; docs make it operator-visible and give a safe replay procedure. | Verified at handler and deployable platform-contract boundaries. |
| Contract/system coverage through public seams | 40 Worker tests pass through exported Worker handlers. 21 Python tests pass, including a focused productive HTTP + real SQLite/LangGraph duplicate test proving one delivery, run, checkpoint lineage, and controlled GitHub claim. | Verified |

## Commands and outcomes

```text
cloudflare-github-webhook-relay: npm run check
  Wrangler generated types current; TypeScript checks pass; type-aware oxlint passes;
  3 test files, 40 tests passed.

cloudflare-github-webhook-relay: npm run deploy:dry
  Wrangler 4.125.0 built the Worker and resolved the primary Queue and variable bindings.

cloudflare-github-webhook-relay: npm audit --audit-level=high
  0 vulnerabilities.

langgraph-github-issue-pilot: uv lock --check && uvx ruff check . && uv run pytest -q
  Lock current; lint passes; 21 tests passed.

langgraph-github-issue-pilot: uv run pytest -vv \
  tests/test_relay_authentication.py::test_duplicate_relay_delivery_converges_on_one_local_run_checkpoint_and_claim
  Passed through the production HTTP/read-model seam.

langgraph-github-issue-pilot: uvx pip-audit --path .venv/lib/python3.14/site-packages \
  --skip-editable --progress-spinner off
  No known vulnerabilities found (the local editable package is intentionally skipped).

repository: git diff HEAD --check
  Passed.

repository: openspec validate github-webhooks-cloudflare-delivery --strict
  Change is valid.
```

The Tunnel example was also parsed and structurally checked for its exact route and catch-all. `cloudflared` is not installed in this environment, and no Cloudflare account resources, DNS zone, production secrets, or Tunnel credentials were supplied. Therefore no claim is made that a live message was observed traversing Cloudflare or entering a real DLQ. The closest safe verification is the production-handler behavior, Wrangler's current generated types/schema/dry-run, the named-DLQ configuration contract, and the exact-path Tunnel configuration. Live provisioning and observation remain the explicit activation step in issue 12.

The Python suite's only warning is an upstream Starlette deprecation notice for its current `TestClient` import path; it does not affect the results.
