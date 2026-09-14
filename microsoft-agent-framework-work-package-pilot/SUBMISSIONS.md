# GitHub submissions in the Operator GUI (GUI Ticket 01)

The GUI labels the work inputs **Anforderungen**.
The API serves the GUI at `/operator/` and persists actual GitHub issue title/body
snapshots in PostgreSQL. Admission produces `state: admitted` and `runId: null`.
It does not start a worker, create a run, claim a lease or write to GitHub.
Background processing is GUI Ticket 02.

## Start the service

Build from this directory:

```bash
dotnet restore --locked-mode Wpcp.WorkPackageControlPlane.sln
dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore
```

Set `WPCP_CONNECTION_STRING` for a dedicated PostgreSQL database. Start the API
with deployment configuration (repository bindings and a versioned redaction
policy), using the example as a starting point:

```bash
dotnet src/Wpcp.Api/bin/Debug/net10.0/Wpcp.Api.dll \
  --submission-config submission-config.example.json \
  --urls http://127.0.0.1:5080
```

The configuration contains no issue catalogue, execution plans or member list.
Use each repository's existing logical `repositoryId`, exact owner/name and
immutable GitHub numeric ID. Repository IDs must be unique. Do not invent a new
binding for an existing repository after data has been admitted. The example
uses the established Probare pilot binding; change it only for another actual
repository. Configure the real deployment's controlled redaction inventory in a
private configuration file. As with the existing pilot, this literal policy is
not automatic secret/PII discovery.

Open `/operator/`, connect with the human's GitHub user credential and enter an
issue URL. The credential requires repository metadata access, effective read
and write permissions, and Issues read permission. It is held in the opened
page's memory and sent in Authorization headers; it is not put in URLs,
browser storage or the application database. Reloading the browser requires
reconnecting. Read-only humans can inspect admitted submissions. Bot credentials
cannot authorize human admission or observation.

Admission checks the live repository identity and current contributor rights,
then fetches the actual issue. It must be open and labelled `ready-for-agent`.
A GitHub pull request is not an eligible issue. The server makes no authorization
label changes or inference of new mandates in this slice. A repeat submission
revalidates the provider checks and returns the first admitted version.

## Separate human clients

The GUI uses the service's same-origin HTTP API. No shared filesystem, database
credential or fixture capability is needed by a browser client. Host the service
at a reachable HTTPS address (configure Kestrel's HTTPS certificate through its
standard environment configuration), or forward a loopback listener through an
authenticated SSH tunnel / TLS reverse proxy. Non-loopback HTTP listeners are
rejected. A proxy must preserve the Authorization header and disable body/header
logging and caching for these endpoints. Keep the service and GUI on the same
origin; there is no wildcard CORS or cookie authentication.

The legacy `--fixture` mode and CLI/run/worker APIs remain available with their
existing fixture capability and loopback restriction. Choose exactly one of
`--fixture` and `--submission-config`. In submission mode the legacy synthetic
start/control routes fail closed; setting `WPCP_FIXTURE_ACCESS_TOKEN` alone does
not enable them. No live pilot database was migrated for this ticket.

The schema addition is `wpcp_submissions`. Its unique GitHub issue identity
serializes concurrent deliveries: one creates the record, all others read that
original snapshot. A source edit does not update the stored title/body, revision,
author, admission time or content checksum. The checksum identifies the redacted
stored title/body JSON, not unredacted provider content.

## Public contract

All endpoints require `Authorization: Bearer <human GitHub credential>` and
recheck provider access. Responses are not cached.

| Request | Result |
| --- | --- |
| `POST /api/v1/submissions` with `{"sourceUrl":"https://github.com/owner/repo/issues/123"}` | 201 for first admission, 200 for an existing logical issue; same immutable submission document. |
| `GET /api/v1/submissions` | `submissions` array filtered by current repository read permission. |
| `GET /api/v1/submissions/{submissionId}` | Persisted snapshot after current authorization against its stored repository binding. |

A snapshot includes `submissionId`, `state`, nullable `runId`, `title`, `body`,
`source` (provider, issue ID/number, URL, update time), `repository`,
`submittedBy` (provider-asserted human ID), `admittedAt`, `contentSha256` and
`redaction` metadata. The browser renders provider content as text, never HTML.

Errors carry a stable `code`: invalid URL (400), expired/missing credential
(401), repository access/contribution/identity or unconfigured repository (403),
missing source/submission (404), conflicting source identity (409),
closed/unready/pull-request/redacted-correlation source (422), and GitHub/storage
unavailability (503). GUI messages explain these failures in German. An empty
list means no currently visible submissions, including on repositories to which
access has since been revoked.

## Verification

```bash
python3 -m unittest tests.test_submissions tests.test_submission_browser -v
```

Tests use fresh disposable PostgreSQL, a controlled external GitHub boundary,
separate service processes and real Chrome. They assert the public snapshot,
parallel duplicate delivery, immutable source edits, authorization/revocation,
redaction, inert source markup, desktop/mobile rendering and a fresh browser after
API restart. The existing black-box suite covers compatible fixture/CLI behavior. Run the
complete pilot suite with its pinned Python dependencies:

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest discover -s tests -v
```
The browser proof uses local Chrome and the bundled Playwright runtime, or
`WPCP_TEST_PLAYWRIGHT` pointing to an installed module. It never prints tokens.

For a real existing eligible issue, use `gh`'s authenticated human account:

```bash
WPCP_LIVE_GITHUB_SUBMISSION_URL=https://github.com/paradox123/probare-crm/issues/4 \
WPCP_SUBMISSION_PROOF_DIR=/tmp/wpcp-submission-proof \
  python3 -m unittest tests.test_submission_live_github.LiveGitHubSubmissionTests -v
```

The opt-in proof starts with an empty dedicated database, admits through the GUI,
reads the public snapshot, closes Chrome and restarts the API, then reads the same
snapshot from a new Chrome process. It performs no GitHub writes and removes its
database/container. Retained proof contains sanitized snapshot JSON and screenshots.
Running this on one host does **not** establish the required separate-machine
acceptance; that requires a reachable test server and another human workstation.

Provider contract: [GitHub issue API](https://docs.github.com/en/rest/issues/issues#get-an-issue).
Static delivery: [ASP.NET Core static files](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-10.0).
