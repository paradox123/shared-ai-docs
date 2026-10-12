## 1. Authoritative cursor

- [x] 1.1 Prove the completion-time gap with a failing public resolver CLI test and preserve existing dirty snapshot changes.
- [x] 1.2 Implement sole valid processed-window cutoff, explicit absent-cursor legacy fallback and fail-closed malformed cursor.
- [x] 1.3 Update canonical cutoff guidance and verify the resolver CLI suite.

## 2. Complete protected review receipts

- [x] 2.1 Implement and test protected persisted selection capture/restart with immutable index and resolver files.
- [x] 2.2 Implement and test complete same-manifest page proof including omissions, gaps and manual records.
- [x] 2.3 Implement and test topic receipt reuse/staleness against source pins and wiki-input content.
- [x] 2.4 Document .NET entrypoint, invocation, dependencies and local-only effects.

## 3. Integration and evidence

- [x] 3.1 Update canonical guidance and existing NCG automation with the tested command contracts.
- [x] 3.2 Verify end-to-end isolated capture/extraction/topic/resume flow and failure cases, including unchanged page replay after restart.
- [x] 3.3 Confirm actual automation readback, unchanged memory/metadata, preserved existing work, strict OpenSpec validation and scoped diff checks.
- [x] 3.4 Save requirements/results/content identity and report implementation readiness awaiting acceptance; no live wiki run, push or archive.
