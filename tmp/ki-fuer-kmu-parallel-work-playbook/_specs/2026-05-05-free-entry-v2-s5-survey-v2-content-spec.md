**Date:** 2026-05-05  
**Status:** 🟡 Spec  
**Scope:** Survey-v2-Inhalte in drei Varianten, gemeinsamer Pflichtkern, bedingter Regulatorikblock und agentische Zusatzfragen im Survey-Stil.

---

## 1. Ziel

S5 migriert den vorhandenen Survey-Katalog in die neue v2-Reihenfolge und macht ihn server-renderbar sowie lokal fallbackfaehig.

## 2. In Scope

- Drei Survey-Varianten: `A` Einsteiger, `B` Anwender, `C` Technisch versiert.
- Gemeinsamer fachlicher Pflichtkern.
- Profil- und Betriebstyp-Erfassung vor Routing.
- Regulatorik-/KRITIS-Fragen nur im relevanten Pfad.
- Dokumentationslage, Dokumentpfade und Freigaben.
- ROI-Mindestdaten oder begruendete Annahmen.
- Begrenzte ROI-Agent-Zusatzfragen im Survey-Schema.

## 3. Out of Scope

- Agent, der den kompletten Survey frei als Chat fuehrt.
- RAG-/Dokumentenverarbeitung waehrend des Surveys.
- Provider-Aktivierung vor Survey-Ende, ausser Bestandspruefung eines vorhandenen kunden-eigenen LLM-Zugangs.

## 4. Master-Spec-Abdeckung

- V2-FR-001 Einsteigerverstaendlicher Start.
- V2-FR-002 Profil- und Betriebstyp-Routing.
- V2-FR-010 Survey-Definition.
- V2-FR-011 Survey-Inhalte.
- V2-FR-012 Agent-Zusatzfragen.
- V2-FR-040 Dokumentationslage.

## 5. Akzeptanz

- `03-product/survey-v1-final.md` ist nur Inhaltsquelle, nicht fuehrende Reihenfolge.
- A/B/C erfassen denselben Pflichtkern.
- Nicht regulierte Standardbetriebe erhalten keine direkte KRITIS-Frage im Standardpfad.
- Zusatzfragen sind begrenzt, stilgebunden und strukturiert gespeichert.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S5 Child Spec aus Survey-Abschnitten der Master-Spec abgeleitet. |

SessionId: codex-free-entry-v2-s5-survey-content-2026-05-05
