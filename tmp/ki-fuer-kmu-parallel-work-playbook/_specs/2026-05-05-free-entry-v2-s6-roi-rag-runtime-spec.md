**Date:** 2026-05-05  
**Status:** 🟡 Spec  
**Scope:** Dokumentationslage, RAG-Status, Quellenstatus, ROI-Agent und Report unter LLM-/Freigabe-Guardrails.

---

## 1. Ziel

S6 erzeugt belastbare ROI-/RAG-Ergebnisse nur, wenn Survey-Antworten, LLM-Readiness, Arbeitsumgebung und Freigaben vorliegen.

## 2. In Scope

- Dokumentationslage nach Survey-Ende auswerten.
- Dokumente nur mit aktivem LLM und Freigabe lesen/extrahieren/normalisieren.
- RAG-Statuswerte: `disabled_no_docs`, `disabled_no_approval`, `prepared`, `preprocessing_required`, `unsupported_sources_present`.
- ROI-Agent fuer 1 bis 3 Prozesse.
- Annahmen, Erfahrungswerte, Datenqualitaet und Bandbreiten sichtbar machen.
- Report mit Chancen, Risiken, ROI, Aktivierungsstatus, RAG-/Quellenstatus und naechstem Schritt.

## 3. Out of Scope

- ROI-Behauptung ohne `provider_ready=true`.
- Produktive Kundensystemaenderungen.
- OCR-/Scan-Aufbereitung als harter Pflichtblocker, solange `preprocessing_required` sichtbar ist.

## 4. Master-Spec-Abdeckung

- V2-FR-041 RAG-Status.
- V2-FR-050 ROI-Agent.
- V2-FR-051 ROI-Modell.
- V2-FR-052 Report.
- V2-FR-053 Report-Hinweise.
- V2-FR-062 Agent-Konfiguration.

## 5. Akzeptanz

- Ohne LLM entsteht Vorbereitungs-/Blockerreport, keine belastbare ROI-Berechnung.
- Quellenstatus und Annahmen sind im Report sichtbar.
- Top-Empfehlung darf keinen negativen Payback verstecken.
- Secrets erscheinen nicht in Agent-Konfiguration, Logs oder Reports.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S6 Child Spec aus ROI/RAG-Abschnitten der Master-Spec abgeleitet. |

SessionId: codex-free-entry-v2-s6-roi-rag-runtime-2026-05-05
