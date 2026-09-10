# WPCP black-box fixture boundary

`fixtures/postgres-test-fixture.json` defines a disposable PostgreSQL 17 test
resource with a Docker-assigned host port. It is isolated from the
managed-durability probe and the test always removes its uniquely named
container after the run.

`fixtures/synthetic-provider-redaction-fixture.json` is the only synthetic
repository-provider and controlled-redaction input for the first public-surface
slice. Its canary strings are test data: later implementation must redact them
before any durable write or operator-visible serialization.

The public API exposes `GET /healthz`, `POST /api/v1/issues/{repositoryId}/
{issueNumber}/runs`, `GET /api/v1/runs/{runId}`, and
`GET /api/v1/runs/{runId}/events?after={position}`. The last three routes
require the test harness's ephemeral `X-Wpcp-Fixture-Access` capability; the
read routes also require the fixture-defined actor header. The separate
`Wpcp.OperatorCli` is the intended public client and supplies the capability
from `WPCP_FIXTURE_ACCESS_TOKEN` without persisting or printing it.
