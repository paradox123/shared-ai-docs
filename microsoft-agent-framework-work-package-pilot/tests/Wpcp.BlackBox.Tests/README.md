# WPCP black-box fixture boundary

`fixtures/postgres-test-fixture.json` defines a disposable PostgreSQL 17 resource
with a Docker-assigned loopback port. Tests remove their uniquely named container
and all API processes afterward. No managed scheduler, live provider or existing
pilot database is used.

`fixtures/synthetic-provider-redaction-fixture.json` defines synthetic issues,
pinned GitHub repository bindings and controlled canaries. It contains no member
or permission list. The harness adds synthetic issues in a temporary fixture file.

`tests/github_provider_fixture.py` implements only the external GitHub HTTP test
boundary, with separate ephemeral credentials for humans and a bot. Tests can
change provider rights, simulate errors or replace credentials while the real
application remains running. These test accounts are not persisted application
members. `WPCP_GITHUB_TEST_ORIGIN` is restricted to an explicit loopback origin.

All Operator routes require both the ephemeral `X-Wpcp-Fixture-Access` harness
capability and a GitHub bearer credential. The CLI reads them from
`WPCP_FIXTURE_ACCESS_TOKEN` and `WPCP_PROVIDER_TOKEN`. Caller-supplied actor labels
are ignored. Only `/healthz` is unauthenticated.

The tests observe API/CLI results and ordered history/audit; they do not query
application tables or use database edits to establish behavior. Concurrent claim
tests run two API processes against one database, and reconnect tests use a new
CLI credential for the same provider subject after API replacement.

Commands and public contracts are documented in the [pilot README](../../README.md).

## Ticket 04 external fake attempt

`tests/test_fake_codex_attempt.py` shares the process harness with Ticket 02/03.
It launches `tests/fake_codex_provider.py` as a separate HTTP process with its own
SQLite receipts, invokes real worker processes, and observes the product only
through authenticated API/CLI calls. Provider session counts are read through
its public fixture diagnostics endpoint; tests never query product tables.

Coverage includes canonical message/tool/artifact/result order and canary
redaction; SIGKILL before/after session mapping and after result capture;
concurrent redelivery; unchanged original blocked result plus separate rejection;
process/timeout/transport/contract/schema/infrastructure diagnostics; conflicting
sequence/identity and null-event rejection; immutable adapter assignment; and
independent attempt selection after API restart with truthful unavailable Codex
opening capability.

Ticket 06 extends the same public proof with durable `humanRequest` read-back,
exactly-once Resume/Fork/Fresh Retry lineage, selected-session open versus
explicit handoff, lease/fence-protected write-back, and API-replacement recovery
after a provider-side continuation or interaction success gap. It also rejects
misbound adapter receipts, preserves the original fake attempt on redelivery
after a fork, proves redacted-message command replay, rejects substituted
write messages and incompatible completion contracts, and proves that an
adapter capability canary is redacted in API/CLI read-back across API
replacement. It reads only HTTP/CLI state plus the fake provider's public
diagnostics; it never inspects product tables. All database containers,
provider processes and receipt files are disposable. This is explicit local
delivery, not automatic DTS orchestration or real Codex app integration.
