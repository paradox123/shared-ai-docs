**Date:** 2026-05-05  
**Status:** 🟡 Spec  
**Scope:** Szenariobasierte Docker-/Safe-Harness fuer fuehrende Kontrollfluss-Pfade, Artefakte, Exit-Codes und Secret-Leak-Assertions.

---

## 1. Ziel

S7 beweist, dass die fuehrenden v2-Kontrollfluss-Pfade reproduzierbar getestet werden koennen, ohne Host-Secrets oder produktive Kundensysteme zu beruehren.

## 2. In Scope

- Szenario-Dateien, zum Beispiel `tests/harness/cases/*.yaml`.
- Survey-Modi: `server_rendered`, `local_fallback`, `preloaded_answers`.
- Provider-Modi: `none`, `stub_success`, `stub_failure`, optional `real_provider_explicit`.
- Bundle-Manifest- und Handoff-Fehlerfaelle.
- Erwartete Exit-Codes, Manifestfelder, Dateien, Reports und Secret-Leak-Assertions.
- KRITIS-/Regulatorik-Stop, RAG an/aus, Provider an/aus, Survey-Handoff erfolgreich/fehlerhaft.

## 3. Out of Scope

- Produktive Provider-Aufrufe ohne explizite Freigabe.
- Normale Host-Env-Secrets in Testcontainern.
- UI-Vollausbau jenseits der fuer Kontrollfluss noetigen Harness-Oberflaechen.

## 4. Master-Spec-Abdeckung

- Docker- und Test-Harness.
- V2-FR-060 Artefaktstruktur.
- V2-FR-061 Run-Manifest.
- V2-FR-063 Exit-Codes.
- V2-NFR-001 Sicherheit.
- Alle fuehrenden Kontrollfluss-Pfade aus Abschnitt 2 der Master-Spec.

## 5. Akzeptanz

- Jeder fuehrende Pfad hat mindestens einen Case.
- Negativfaelle blockieren deterministisch und ohne falsche Erfolgsmeldung.
- Secret-Leak-Assertions pruefen Logs, Reports und Manifeste.
- Exit-Codes, sobald verwendet, sind in Master-Spec oder Child Spec dokumentiert.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S7 Child Spec aus Harness-Abschnitten der Master-Spec abgeleitet. |

SessionId: codex-free-entry-v2-s7-harness-2026-05-05
