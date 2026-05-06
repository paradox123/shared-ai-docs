**Date:** 2026-05-05  
**Status:** 🟡 Spec  
**Scope:** Provider-Empfehlungsmatrix, gepflegte Aktivierungsguides, lokale Guide-Visualisierung und Readiness-Test.

---

## 1. Ziel

S4 fuehrt Nutzer nach Survey-Ende zu einem passenden kunden-eigenen KI-Zugang oder Assisted/Paid-Pilot-Pfad, ohne Zahlungsdaten im Script abzufragen.

## 2. In Scope

- Versionierte Provider-/Modell-Empfehlungsmatrix.
- Aktivierungsguides fuer OpenAI API, Anthropic API, Assisted Setup und Managed Gateway Paid Pilot.
- Drei Sprach-/Detailvarianten fuer Profile `A`, `B`, `C`.
- Visuelle Guide-Schritte mit offiziellen Links, `last_verified_at`, Review-Intervall und optionalen Screenshots.
- Lokaler Readiness-Test mit nicht-kundenspezifischem Prompt.
- Secret-Redaction und lokale Credential-Ablage.

## 3. Out of Scope

- Dynamische LLM-Erklaerung vor aktivem LLM-Zugang.
- Kreditkarten- oder Zahlungsdatenerfassung im lokalen Script.
- Automatische Provider-Account-Erstellung.
- Weitergabe von Daniels Provider-Subscription.

## 4. Master-Spec-Abdeckung

- V2-FR-020 Aktivierungsstatus.
- V2-FR-021 Readiness.
- V2-FR-022 Provider-Guardrails.
- V2-FR-023 Provider-/Modell-Empfehlungsmatrix.
- V2-FR-024 Provider-Aktivierungsguides.
- V2-FR-024a Visualisierung der Aktivierungsguides.
- V2-FR-053 Report-Hinweise.

## 5. Akzeptanz

- Empfehlung erfolgt deterministisch nach Survey-Ende.
- Nutzer gibt Zahlungsdaten nur auf offiziellen Provider-Seiten oder im separaten Vertragsprozess ein.
- `provider_ready=true` wird erst nach erfolgreichem Readiness-Test gesetzt.
- Kein Secret erscheint in Logs, Reports oder Registrierungsdaten.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S4 Child Spec aus Provider-Abschnitten der Master-Spec abgeleitet. |

SessionId: codex-free-entry-v2-s4-provider-guides-2026-05-05
