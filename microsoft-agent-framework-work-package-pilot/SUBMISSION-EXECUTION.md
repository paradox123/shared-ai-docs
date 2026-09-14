# First background activity from the Operator GUI (GUI Ticket 02)

The Operator can **Starten** a new GitHub URL or choose **Analyse starten** on
saved requirements. One atomic database transaction links the immutable admission
to an ImplementationRun and a durable dispatch record. A separate worker performs
a real requirements analysis. The GUI distinguishes waiting, running, completed
analysis and failure, with the actual result and run/activity/attempt/session IDs.
Analysis completion is `analysis-completed` on the run, not implementation,
publication, qualification or human approval. The full workflow is GUI Ticket 09.

## Configure and operate the three services

Use the existing [submission configuration](SUBMISSIONS.md), repository bindings
and private redaction inventory. Add this optional deployment configuration:

```json
"backgroundExecution": {
  "adapterOrigin": "http://127.0.0.1:8791/",
  "timeoutSeconds": 180
}
```

The adapter origin must be loopback HTTP, without credentials, path, query or
fragment. Redirects are disabled. Timeout is bounded to 10–600 seconds. No browser
request supplies adapter configuration, a checkout path or an execution plan.
The selected configuration is stored with the disposition; a changed binding or
execution configuration produces a visible failure instead of rerouting old work.

Configure these values privately in the service manager's environment:

| Variable | Services | Purpose |
| --- | --- | --- |
| `WPCP_CONNECTION_STRING` | API, worker | The same persistent PostgreSQL database. |
| `WPCP_ARTIFACT_ROOT` | API, worker | The same dedicated absolute, persistent artifact directory; both services need read/write access. |
| `WPCP_REAL_ADAPTER_TOKEN` | API, worker, adapter | One random private service credential; never the browser's GitHub credential. |
| `CODEX_HOME` | adapter | The existing supported Codex authentication source, if different from the default. Only its auth file is copied into the adapter's private runtime home. |

Build the solution as in SUBMISSIONS.md. Resolve an absolute Python interpreter
from the pinned `codex-requirements.txt` environment. Service commands, with paths
resolved by deployment, are:

```bash
# API
 dotnet src/Wpcp.Api/bin/Debug/net10.0/Wpcp.Api.dll \
   --submission-config state/submission.json --urls http://127.0.0.1:5080

# Independent dispatcher: no run ID or per-issue worker command
 dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
   --submission-config state/submission.json --dispatch-submissions true

# Existing real Codex adapter, with a new dedicated private state root
 python codex_adapter.py --config codex-runtime-pin.json \
   --state-root state/submission-agent --api-url http://127.0.0.1:5080 \
   --port 8791 --native-port 8792
```

These are service entry points. Run each under the host's service manager
(`launchd` on the verified Mac, `systemd` on a prepared Linux host), with its own
restart policy and private environment file. Interactive foreground shells are
useful for debugging but are not the unattended deployment. For example, a Linux
worker unit can use:

```ini
[Unit]
Description=WPCP submission dispatcher
After=network.target

[Service]
Type=simple
User=wpcp
WorkingDirectory=/opt/wpcp/pilot
EnvironmentFile=/etc/wpcp/operator.env
ExecStart=/usr/bin/dotnet /opt/wpcp/pilot/src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll --submission-config /etc/wpcp/submission.json --dispatch-submissions true
Restart=on-failure
RestartSec=3
UMask=0077

[Install]
WantedBy=multi-user.target
```

Keep the environment file and adapter state private; retain database, artifacts
and adapter receipts across process replacement. The committed runtime pin is
for the established Mac executable. A Linux deployment needs its own supported,
verified executable/protocol/dependency pin and authentication. The existing
[Azure deployment](deploy/azure-vm/README.md) remains the accepted Ticket 01 intake
service; this implementation does not claim that the new worker/runtime has been
deployed there. Separate-machine acceptance remains GUI Ticket 16.

## Start and read contracts

All human APIs use current GitHub user credentials in Authorization headers.
The API rechecks repository identity and contributor rights; a fresh start also
requires an open ready-for-agent issue and an available authenticated runtime and
artifact store. The retained content remains the mandate if GitHub changed after
admission. Analysis has only a scoped read-admitted-issue tool and cannot modify
the implementation repository or turn source text into extra authority.

| Request | Behavior |
| --- | --- |
| `POST /api/v1/submissions` with `sourceUrl` and `start: true` | Resolve/admit and queue in one user action. Returns the submission with `state: started`, `runId`, HTTP 202 for a new run or 200 for replay. |
| `POST /api/v1/submissions/{id}/start` with `{}` | Start the saved version. Replay returns its existing run, including if the runtime has since gone offline. |
| `GET /api/v1/submissions/{id}/execution` | Persistent dispatch status: `submissionId`, `runId`, `state` (`queued`, `running`, `completed`, `failed`) and a concrete error `code` when applicable. |
| `GET /api/v1/runs/{runId}` and existing history/artifact/dossier reads | Shared authorized public contracts, also available in submission mode without the synthetic fixture capability. |

Intake without `start: true` still creates no run. A pre-existing run from another
admission path is rejected with `issue-already-has-run`, never silently adopted
for a new analysis. Missing configuration, credentials, runtime capability or
artifact storage prevents a new run. Source/authorization errors retain the
existing intake codes. Long result bodies are retrieved through the existing
artifact API; unavailable artifact content is explicit in the GUI.

The browser keeps credentials only in memory. Reloading requires authentication;
the URL hash selects the same submission. No control lease is acquired by start.
Existing fixture CLI/mutation contracts remain intact; new GUI human-control
features are subsequent tickets.

## Execution and recovery

PostgreSQL `wpcp_submission_dispatch` stores the submission/run relationship,
pinned configuration and durable disposition. Per-repository connection locks
serialize dispatchers. A dead worker releases its lock; a replacement redelivers
the same operation ID to the adapter. The existing Agent Framework session graph
records activity/attempt, original responses, session mapping, source events,
redaction and terminal result in central Run History. Large values and artifact
bytes use the existing content-addressed store and dossier export.

The real adapter uses the existing pinned app-server connection, private runtime
home, sandbox preflight and tool authorization. The first step's additive
`submission-analysis/v1` result contains `outcome`, `summary` and `findings`;
`worker-result-v3` remains the implementation result contract. Native runtime
messages and tool calls/results are retained as ordered source observations;
private reasoning is excluded. The actual analysis result is also a downloadable
JSON artifact. Analysis sessions disclose unsupported interactive opening until
the corresponding later Operator/Handover work is delivered.

Each analysis operation has a private durable receipt with input digest, actual
session identity and observable events. Successful replay returns the identical
receipt. A mapped interrupted operation returns a concrete interruption with its
retained observations, rather than creating another session or model turn. A gap
before a session mapping is confirmed reports `session-start-uncertain`; the
service does not invent a session ID. This first-step recovery does not claim the
full workflow's automatic repair/continuation behavior.

A queued run remains queued while no dispatcher is available. A running worker
continues without a browser or API connection. Runtime/transport/process failures
become durable failures. These diagnostics acknowledge delivery and preserved
history, not successful issue implementation.

## Verification

```bash
python3 -m unittest tests.test_submission_execution tests.test_submission_execution_browser -v

WPCP_CODEX_ENDPOINT_PROBE=1 \
WPCP_LIVE_GITHUB_SUBMISSION_URL=https://github.com/paradox123/probare-crm/issues/4 \
WPCP_SUBMISSION_PROOF_DIR=/tmp/wpcp-submission-execution-proof \
  uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_submission_execution_live -v
```

The opt-in proof reads an existing eligible GitHub issue, starts it in real Chrome,
closes Chrome and the API, and dispatches the real worker from a short-lived
launcher. The launcher exits and the worker is adopted by PID 1. A new browser
reads the completed analysis and its artifacts from the same run. A separate
fresh database proves a controlled outage after preflight and later GUI failure
readback. There are no GitHub writes. Fixtures cover concurrency, worker
replacement, authorization/mandate checks, process errors and large result reads.

Protocol reference: [official Codex app-server documentation](https://learn.chatgpt.com/docs/app-server).
The executable-generated schema and the repository's pinned protocol are the
runtime compatibility authority for this integration.
