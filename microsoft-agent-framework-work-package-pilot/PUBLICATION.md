# Executable evidence, recovery and draft publication (Tickets 11–12)

The worker accepts a trusted `wpcp-publication-plan/v1` JSON file outside the agent
checkout. It binds its bytes and Python interpreter to the admitted run, checks
readiness before starting Codex, executes evidence on a committed head and
publishes one draft through the GitHub REST API. The worker never merges or marks
ready. Review qualification belongs to Ticket 13.

Run from this directory using the Python environment from `codex-requirements.txt`:

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt python -c 'import sys; print(sys.executable)'
```

Pass the printed interpreter to the worker and configure the existing isolated
PostgreSQL connection, fixture, real adapter origin and adapter service token.
`WPCP_PUBLICATION_TOKEN` supplies GitHub API credentials to `api.github.com` only.
Git uses a separately configured noninteractive credential mechanism from the
local repository config or SSH setup; global/system Git config is disabled.
Fetch and push URLs must each match the provider-reported `clone_url` or `ssh_url`;
a fork containing the same base does not authorize a different remote. Tokens
must not appear in the plan, command arguments or outgoing source.

```bash
dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
  --fixture <issue-fixture.json> --run-id <admitted-run-uuid> \
  --worker-id publication --codex-python <absolute-python-interpreter> \
  --publication-plan <absolute-trusted-plan.json>
```

The plan contains these fields. Use real absolute paths and an actual Git SHA;
the placeholders below are deliberately not executable configuration.

```json
{
  "schemaVersion": "wpcp-publication-plan/v1",
  "repository": {"repositoryId": "repo-1", "fullName": "owner/repository", "providerRepositoryId": 123},
  "issueNumber": 11,
  "localPath": "<absolute-isolated-checkout>",
  "remoteName": "origin",
  "baseBranch": "main",
  "branch": "codex/issue-11",
  "expectedBaseSha": "<40-character-provider-base>",
  "providerOrigin": "https://api.github.com",
  "agentOrigin": "http://127.0.0.1:5091",
  "title": "Implement the requested behavior",
  "prerequisites": {
    "contract": {"argv": ["<interpreter>", "<trusted-contract-probe>"], "expected": "contract compatible"},
    "tools": {"argv": ["<interpreter>", "<trusted-tools-probe>"], "expected": "tools available"},
    "dependencies": {"argv": ["<interpreter>", "<trusted-dependency-probe>"], "expected": "dependencies available"},
    "access": {"argv": ["<interpreter>", "<trusted-access-probe>"], "expected": "access available"},
    "sandbox": {"argv": ["<interpreter>", "<trusted-sandbox-probe>"], "expected": "sandbox permits required surfaces"}
  },
  "criteria": [{
    "id": "AC1", "description": "The greeting contains the supplied name",
    "kind": "command", "surface": "public greet function",
    "expectedReadBack": "Hello, Ada!",
    "phases": [{
      "name": "read-back",
      "probe": {"argv": ["<interpreter>", "<trusted-surface-probe>"], "expected": "surface available"},
      "execute": {"argv": ["<interpreter>", "-B", "-c", "from greeting import greet; print(greet('Ada'))"], "expected": "Hello, Ada!"}
    }]
  }]
}
```

`expected` is a nonempty exact UTF-8 stdout assertion (outer whitespace trimmed).
A successful exit alone is insufficient. Every executable runs in the planned
checkout, with bounded time/output and without inherited service tokens. Each
phase receives `WPCP_EVIDENCE_HEAD`. Keep probes observational, use synthetic data,
and place screenshot/document output outside the source checkout; changes during
evidence invalidate it. Trusted commands must exercise the declared business
surface. A deliberately dishonest assertion script is not independently proven
correct by this runner; its command, expected output and observation remain in
the PR for review.

| Evidence kind | Required ordered phases |
| --- | --- |
| `command` | `read-back` |
| `rest` | `request`, `response`, `read-back` |
| `idempotency` | `request`, `response`, `repeat`, `read-back` |
| `ui` | `interaction`, `screenshot`, `read-back` |
| `document` | `generate`, `render`, `inspect`, `read-back` |
| `negative-gate` | `rejection`, `read-back` |
| `recovery` | `restart`, `read-back` |
| `background` | `request`, `read-back` |

Each phase has its own `probe` and `execute`. A screenshot phase additionally
requires `imagePath`, `imageUrl`, `probeImageUrl` and `probeImageSha256`. The
readiness probe image must be readable at the same origin as the final image and
match its configured checksum before agent start. Images must use non-interlaced
8-bit grayscale, RGB, grayscale-alpha or RGBA PNG encoding. Decoded rows and
pixels are checked within a 32 MiB limit. Final PNG bytes at the local and public
surfaces must match; the PR embeds the URL and checksum. Publish images from a
durable, already sanitized artifact surface; do not place private data in screenshots.
The source check covers all outgoing Git blobs and commit messages, including
content removed from the tip; uninspectable binary source is rejected. The runner redacts
configured canaries and recognizable textual credentials; it does not implement
OCR or general image PII discovery. Artifact lifetime remains the responsibility
of that configured surface.

The real adapter's authenticated `GET /publication-readiness` verifies the pinned
runtime, dependencies, protocol, tools and sandbox without starting a model turn.
It reports the actual checkout, which must match the plan. Prepare that checkout
under the adapter's isolated state root (`repository/`) with the desired base,
run branch, remote and ISSUE.md before publication admission. This extends the
Ticket 10 disposable workflow; it does not move or import a product checkout.
The existing native adapter initially returns a blocked preparation result. Open
and claim the same session using the Ticket 10 Operator/TUI flow, perform the
prepared assignment, then repeat the publication worker command. Only an accepted
terminal completed result in that session's canonical history can resume
publication. Large results and interactive observations are resolved from their
checksum-verified dossier artifacts; unavailable bytes do not qualify.
Quarantined observations do not qualify. Adapters returning a valid
completed initial result proceed directly.

`run`, `events`, and portable dossier export retain `publication`, including the
assignment hash, readiness observations, immutable evidence/head/body intent,
dispatch state and authoritative PR receipt. `draft-published` is publication
success; worker exit zero alone means the disposition was persisted, including
blockers. Existing initial session observations remain immutable.

Repeat the same command to reconcile. A lost response or worker death after
provider success adopts the matching PR. Different body/base/head, multiple
receipts, a closed or non-draft PR, or an absent already-dispatched create blocks
further writes. Restore matching external state and repeat; never delete runtime
rows or change the plan to manufacture a fresh create. An unresolved dispatched
effect retains repository ownership; preflight and evidence rejection before
dispatch release it. Other publication runs expose `repository-publication-busy`.
Standalone session dispatch cannot bypass a registered publication plan.

## Bounded evidence recovery

After the original completed result passes schema validation, the worker commits
safe implementation changes once and records `publication.captureHeadSha`.
`publication.qualification` separately reports `schemaValid`, `complete` and the
exact missing `{criterion, phase}` pairs from the trusted plan. Worker
`read_back` maps to plan `read-back`; failed verdicts, a different evidence kind
and log phases cannot fill a required phase. The `command` plan kind accepts the
worker schema's `background` kind. Document phases absent from schema v3 are
captured through the plan rather than silently counted as present.

Every direct capture is a numbered `evidence-capture` or `evidence-correction`
activity in `run.activities`, with an attempt and a durable start/result event.
Missing original phases make the first activity a correction. There are at most
two capture rounds total, including failed or interrupted rounds. Each round
executes the trusted scenarios in their declared order, preserving request and
interaction context for read-backs and screenshots. Plans must therefore use
repeatable synthetic business scenarios. Agent claims alone never qualify a PR.

Correction reuses the recorded head and branch and does not call Codex or commit
source. Clean worktree, branch and head are checked before capture and after every
phase, including a failed command. Drift blocks immediately. A replacement
worker counts an interrupted dispatch and can execute only the remaining round.
Capture command groups monitor adapter/worker liveness and have a time bound so
a killed delivery cannot leave its tool running indefinitely.

`EvidenceQualificationObserved`, `EvidenceCaptureStarted` and
`EvidenceCaptureObserved` retain the source attempt/session/result event and
capture head. The original result remains in its original session/artifact;
correction never overwrites it. The authenticated Operator projection and history
contain redacted observations, and the provider's draft body exposes the same
successful head-bound phases and screenshot references.

Exhaustion or drift ends as `publication-blocked`, with `publication.blocker`,
the capture report and `publication.report.requiredAction`. These pre-dispatch
terminal runs release repository serialization and have no running capture
activity. A superseded native preparation Human Request is resolved in the same
terminal transaction; its original request remains in history. Repeating an exhausted/drifted run is read-only and cannot reset the
limit; inspect the reported cause and submit a new authorized run when corrected.
An already dispatched uncertain PR remains subject to the existing ownership
policy above. A replacement worker command is required after process death;
this slice does not introduce a background recovery scheduler.

A new plan/interpreter requires a new authorized run after settling the old one.
Stop older API/worker binaries before upgrading the additive PostgreSQL schema;
mixed versions cannot enforce the new publication/control guards. Restored
historical dossiers remain read-only.

## Verification

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_evidence_recovery tests.test_publication_adapter tests.test_publication_worker -v
WPCP_CODEX_ENDPOINT_PROBE=1 \
  uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_publication_native -v
```

The first suite uses independent worker/API processes, disposable PostgreSQL,
real local Git and a controlled GitHub HTTP boundary. The surface test executes
real REST calls, Chrome interaction/screenshot and HTML document rendering.
Set `WPCP_TEST_NODE` and `WPCP_TEST_PLAYWRIGHT` for another Node/Playwright
installation; defaults use the bundled desktop runtime and Chrome channel.
The second suite runs the actual pinned Codex and native TUI, still against the
controlled publication provider. It makes authenticated model calls but creates
no live GitHub PR. Set `WPCP_PUBLICATION_PROOF_DIR` to retain public proof and PNGs.
