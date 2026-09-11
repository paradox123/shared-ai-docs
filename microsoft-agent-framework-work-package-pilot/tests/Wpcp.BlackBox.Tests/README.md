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
