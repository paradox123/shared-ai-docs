# Issue 12 live proof

Captured on 2026-08-23 for the production `paradox123/probare-crm` pilot. Raw workflow state and the mode-`600` manifest remain outside the repository under the pilot's Application Support directory.

## Productive path

- GitHub delivery `4720a490-9eef-11f1-99f6-58907957a3bf` was accepted from a real `issues.labeled` event for issue 1.
- Cloudflare Worker ingress acknowledged the delivery only after Queue publication; the Queue used explicit V8 serialization for the raw `ArrayBuffer` body.
- The Queue consumer reached the loopback receiver through VPC Service `01a02e8e-5e1d-70f1-90ef-83c0030fb326`, named Tunnel `230958c3-1143-485c-961a-8f26c84e1546`, and the authenticated `/webhooks/github` hop.
- Durable run `e588463d-bde9-44d9-bcfc-021a24d99fe1` used its isolated `codex/run-e588463d-bde9-44d9-bcfc-021a24d99fe1` worktree and published commit `65f20067dd3c37100cc09ee48e3662c89c1482bf`.
- Draft PR [paradox123/probare-crm#14](https://github.com/paradox123/probare-crm/pull/14) remains open and unmerged for Daniel's review.

## Exact-head gates

- Configured deterministic check: `git diff --check origin/main...HEAD`, observed successful on the published head.
- Requirements review: `pass`, `gpt-5.6-terra`, `xhigh`, read-only.
- Code review: `pass`, `gpt-5.6-terra`, `xhigh`, read-only.
- Architecture review: `pass`, `gpt-5.6-terra`, `xhigh`, read-only.
- The PR body contains one direct rendered-document read-back for each of the six acceptance criteria.
- Current issue labels are `ready-for-agent`, `verified`, and `awaiting-review`; `agent-running` is absent.
- No merge, deployment, or release was performed.

## Private correlation manifest

- Manifest schema: `1`
- Manifest status: `verified`
- Manifest SHA-256: `b9db47c700a6f75ef1b306df33a0b97fd6ebbed56e8a458a9331be6c80a5cfd6`
- Criterion count: 6
- Current PR number: 14
- Current head: `65f20067dd3c37100cc09ee48e3662c89c1482bf`
- File permissions: `600`

The committed summary excludes webhook bodies, issue bodies, tokens, signatures, email addresses, arbitrary reviewer diagnostics, and raw external responses.
