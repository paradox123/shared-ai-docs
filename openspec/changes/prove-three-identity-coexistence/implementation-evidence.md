# Issue 14 live rehearsal — work in progress

The user chose ProBara CRM issue 3 and one person playing A/B/C on a branch ending in `-issue14-test`. This explicitly changes the rehearsal scope; it does not create three distinct people or satisfy the original external-governance gates.

## Ownership and live surfaces

- Control-plane root and authorized branch: `shared-ai-docs`, `main`, baseline `f6f5d15677dc4cb0a11cdc12f0738b51492f2f18`.
- CRM source base: `c32e056f3d242008d15f6e0c7b5333c7572ed186`; isolated target: `codex/probare-issue-3-issue14-test`.
- Real GitHub repository ID: `1332818325`; issue: [probare-crm#3](https://github.com/paradox123/probare-crm/issues/3).
- Actual ImplementationRun: `0f9245e0-3d4f-4c04-9fba-342ccf4b95d1`; implementation attempt: `1a0f0f4b-d090-42f8-8844-e341eedb0c27`.
- Actual pinned Codex session: `01a09bc0-1d97-7673-9b46-f1c5ccc803dc`. All native continuation turns so far use this same session through the authenticated gateway.
- GitHub credentials came from the existing `gh` credential store. Automated client calls use that one real human account's credential. They are **not evidence of an interactive human action** merely because GitHub reports `type: User`.

## Observed pilot limits

1. Large native execution receipts are artifact-backed in public history. The native write client does not rehydrate the oversized receipt before reading its response, so the agent received `Execution denied or unavailable` despite successful command observations. Small bounded reads continued. The retained history contains both sides; no file-read permission change was made.
2. Native sandboxed `dotnet test` reached VSTest's IPC socket setup and failed with `SocketException (13): Permission denied`. No business assertion ran in that attempt. The trusted outer verification process then ran the test and observed the real newsletter assertion failure, followed by success after the same writer's correction. No sandbox restriction was removed.
3. The pinned hook emits `permissionDecision: allow`, which this runtime reports as unsupported in hook events. Execution still passed through the gateway's authenticated control boundary. This diagnostic requires follow-up rather than being silently counted as a clean preflight.

## Behavior observations so far

| Requirement | Observed result | Evidence |
| --- | --- | --- |
| Preserve existing CRM behavior | 14 original backend tests passed before implementation | Baseline operator command; isolated clone only |
| Exclude a general newsletter | New HTTP test first failed with one unwanted case; after native writer change it passed | [Initial behavioral red](evidence/initial-red.json), native history |
| Detect repeated postings without merging roles | Integrated public test compiled and failed: expected two actionable cases, observed three | Trusted operator `IngestionDecisionTests` run; implementation in progress |
| Preserve original main/operations | Baseline captured eight protected boundaries; CRM main matched source base | [Before-state](evidence/before.json) |

## Candidate decision

Pending final evidence. The original three-person approval and externally approved agent-definition revision gates are currently unproven. Therefore no replacement Go can be inferred from this rehearsal or from a passing CRM branch. LangGraph remains in place.
