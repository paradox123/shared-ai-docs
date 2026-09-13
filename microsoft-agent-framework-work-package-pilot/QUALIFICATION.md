# Head qualification and bounded repair

Issue 13 extends the [publication workflow](PUBLICATION.md) with an optional
`headQualification` section in the immutable publication plan. Include it before
admission/first delivery. Plans without it still stop at `draft-published` and
have no qualified head.

```json
{
  "headQualification": {
    "requirements": "The original issue requirements and acceptance criteria.",
    "verification": {
      "argv": ["/absolute/path/to/python", "-B", "-m", "unittest", "-q"],
      "expected": "the exact trusted stdout assertion"
    },
    "guidance": ["AGENTS.md", "CONTEXT.md", "docs/adr/0001-example.md"],
    "skills": {
      "code-review": {"path": "/absolute/path/to/code-review/SKILL.md", "sha256": "<content SHA-256>"},
      "codebase-design": {"path": "/absolute/path/to/codebase-design/SKILL.md", "sha256": "<content SHA-256>"},
      "domain-modeling": {"path": "/absolute/path/to/domain-modeling/SKILL.md", "sha256": "<content SHA-256>"}
    }
  }
}
```

The example paths and expected stdout are placeholders. Use existing guidance
paths in the admitted repository, an executable check with decisive stdout, and
real content hashes. Guidance is read from the reviewed commit. The configured
skills are read and checksum-validated before agent work and again before review.
The existing `--publication-plan`, `--codex-python`, provider credentials and
`WPCP_REAL_ADAPTER_ORIGIN`/`WPCP_REAL_ADAPTER_TOKEN` settings remain the entry point.

The worker verifies local HEAD, branch, clean worktree and authoritative draft
head around deterministic checks and each review. A failed command cannot hide
a mutation. A normal check failure still receives all three reviews. Requirements,
code-quality and architecture use distinct fresh Codex sessions with Terra/xhigh,
read-only access and the prescribed skill routing. They receive the same
requirements, guidance, full changed source files, diff and current evidence, without writer conversation or
peer verdicts. The pinned runtime adapter disables reviewer tools and receives
all required inputs explicitly.

`GET /api/v1/runs/<run-id>` exposes `publication.headQualification`:

- `headSha` is the head currently undergoing qualification.
- `qualifiedHeadSha` is non-null only after exact-head evidence, checks and all
  applicable reviews pass. Requirements cannot be `not_applicable`.
- `rounds` retains initial round 0 and subsequent repaired heads, evidence,
  verification, separate reviewer results, invocation/session IDs and policies.
- `repairs` retains monotonic rounds 1–3, the original writer session/worktree,
  actionable findings, assignment, result, new head and updated draft receipt.
  Later assignments include the earlier repairs' result summaries.
- `humanRequest` gives the concrete blocker/open findings and links to the draft
  and run evidence. These are handoff requests for inspecting and resolving the
  retained conflict; this slice does not introduce an in-app answer command.

Initial `publication.intent` and `publication.report` stay immutable historical
publication evidence. For a repaired head, use the latest qualification round's
`evidence` and repair's `publicationReport`. The run history and portable dossier
also contain these redacted observations.

Ordinary repairs use Terra/xhigh and only the original worktree. Round three uses
Sol/xhigh with `final_repair_round`. The writer changes files; the control plane
commits, captures evidence and updates the same draft. It never starts a fourth
repair, even after worker/API replacement or another delivery. Product decisions,
invalid output, unchanged repair heads and evidence drift create explicit human
handoff/blocking. A new head never inherits a prior verdict.

A completed adapter operation is adopted by its persisted operation ID after a
worker crash. An interrupted deterministic check/capture is blocked, because its
side effects cannot safely be assumed absent. `qualification-uncertain` retains
repository ownership while an existing draft update needs reconciliation; repeat
the same worker command to read and adopt the effect. An ambiguous adapter writer
operation also retains ownership until its outcome is established. Do not change
the plan or delete receipts to restart an exhausted run.

`qualified` means **ready for human review**. The PR remains a draft. This slice
creates no GitHub approval, merge, deployment, release or automatic provider label
change. Qualification is tied to the recorded SHA; redelivery rechecks provider
and local state and clears stale qualification. It does not install a background
head monitor.

## Verification

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_head_qualification -v
WPCP_CODEX_ENDPOINT_PROBE=1 \
  uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_head_qualification_native.NativeHeadQualificationTests -v
```

The first suite uses real PostgreSQL and local/bare Git with controlled adapter
and GitHub boundaries. The second uses the pinned real Codex runtime and native
writer session with a controlled GitHub provider. Neither command uses an
unrelated production repository.

Protocol parameters were checked against the schema generated by pinned
`codex-cli 0.153.4` and the [official App Server documentation](https://learn.chatgpt.com/docs/app-server).
