# Implementation evidence

## Direct public-surface proof

From `microsoft-agent-framework-work-package-pilot`:

```bash
python3 -m unittest tests/test_control_plane_black_box.py -v
```

Result: one public black-box test passed. It creates a disposable PostgreSQL
container, starts the compiled loopback API, admits the initial command through
one `Wpcp.OperatorCli` process, retries through another, and reads through a
separate observer CLI process. It proves identical-command convergence,
conflicting reuse rejection, missing-capability and unauthorized-actor denial,
and controlled-canary rejection in a correlation field.

The same test records actual start, heartbeat, and stop observations from two
separate worker processes; terminates the API process group; verifies its old
port no longer responds; starts a new API process on another port; and reads the
same run/history afterward. It asserts distinct worker/process clocks,
unchanged canonical event positions, admission provenance, supplemental Agent
Framework/Durable Task identifiers, and no raw controlled canary in public
responses or worker output. A second clean admission with a canary only in
worker evidence proves lifecycle redaction is surfaced in both the evidence and
the root projection metadata. Class cleanup removes the uniquely named test
container even if setup fails after Docker starts it.

## Complementary checks

```bash
dotnet restore Wpcp.WorkPackageControlPlane.sln --locked-mode
dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore
dotnet restore --locked-mode ManagedDurabilityProbe/ManagedDurabilityProbe.csproj
dotnet build --no-restore ManagedDurabilityProbe/ManagedDurabilityProbe.csproj
python3 -m unittest tests/test_managed_gate_cli.py -v
openspec validate accept-authorized-issue-as-observable-run --strict
git diff --check
```

All checks passed. The managed-gate suite passed all 25 tests, confirming this
slice did not regress the pre-existing managed-DTS gate. No `wpcp-blackbox-*`
container remained after the public-surface test.
