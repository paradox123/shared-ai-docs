# Free Entry v2 Child Specs

Diese Child Specs schneiden die v2-Master-Spec in lieferbare Slices. Sie liegen bewusst unter `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`, nicht unter `v2/docs`.

Fuehrend bleiben:

1. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
2. `v2/docs/APPLICATION-FLOW.md`
3. `v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md`
4. `v2/docs/adr/*.md`

## Specs

| Slice | Spec | Status |
|---|---|---|
| S0 | [2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md](2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md) | 🔵 Implemented |
| S1 | [2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md](2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md) | 🟢 Accepted |
| S2 | [2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md](2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md) | 🟢 Accepted |
| S3 | [2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md](2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md) | 🟡 Spec |
| S4 | [2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md](2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md) | 🟡 Spec |
| S5 | [2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md](2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md) | 🟡 Spec |
| S6 | [2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md](2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md) | 🟡 Spec |
| S7 | [2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md](2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md) | 🟡 Spec |

## Slice-Regeln

- Keine Child Spec darf Anforderungen aus der Master-Spec still streichen.
- Jede Child Spec muss ihre Master-Spec-Abdeckung nennen.
- ADR-Entscheidungen werden nicht in Child Specs neu verhandelt.
- Alte Specs und `_legacy/v1-node-prototype` duerfen nur als historische Detailquellen genutzt werden.
- Wenn eine Child Spec einen Exit-Code verwendet, muss sie auf die fuehrende Exit-Code-Liste in der Master-Spec verweisen.
