**Date:** 2026-04-21  
**Status:** 🟢 Accepted  
**Scope:** Phase-1-Evaluation gegen Eval-Set mit messbaren Qualitaetsgates

---

# 04 DanielsVault RAG Evaluation und Qualitaetsgates

## Zweck

Diese Child-Spec macht Evaluation verpflichtend und messbar, statt nur narrativ.

## Reihenfolge und Abhaengigkeiten

- Reihenfolge: `04`
- setzt `03` voraus
- Voraussetzung fuer Acceptance in `05`

## Eval-Grundlage

Verbindliches Eval-Set:

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl`

Phase-1-Minimum:

- Lauf ueber das bestehende Eval-Set
- Top-5 Kandidaten pro Frage speichern
- dokumentierte Metriken fuer Domain-/Dateitreffer und Leakage

### Bucket-Gating-Regel (verbindlich)

Blocking fuer Phase-1-Abnahme:

- `historical-user`
- `historical-agent`

Nur Monitoring (nicht blocking in Phase 1):

- `counterfactual-helpful`
- `future`

Normative Regel:

- Die Mindestqualitaetsziele muessen fuer die zusammengefasste Blocking-Menge erreicht werden.
- Monitoring-Buckets werden immer mitgerunnt und separat reportet, blockieren aber Phase 1 nicht.

## Mindestqualitaetsziele (Phase 1)

- `domain_hit_rate >= 0.90`
- `file_hit_rate >= 0.70`
- `cross_domain_leakage <= 0.10`

## Metrikdefinitionen (verbindlich)

- `domain_hit_rate`: Anteil Fragen, bei denen unter Top-5 mindestens ein Treffer in erwarteter Domain liegt.
- `file_hit_rate`: Anteil Fragen, bei denen unter Top-5 mindestens eine erwartete Datei getroffen wird.
- `cross_domain_leakage`: Anteil Fragen, bei denen mindestens 3 der Top-5 Treffer aus einer nicht erwarteten Domain stammen.

### Optionale Monitoring-Metriken (nicht blocking in Phase 1)

- Zusaetzliche Metriken wie `source_precision` duerfen reportet werden, sind aber kein Phase-1-Blocking-Gate solange diese Spec sie nicht explizit als blocking definiert.

## Akzeptanzkriterien

1. Eval-Lauf ist reproduzierbar und versionierbar.
2. Metrikbericht ist maschinell auswertbar und menschenlesbar.
3. Mindestqualitaetsziele werden fuer die Blocking-Buckets erreicht oder als klarer Gap reportet.
4. Monitoring-Buckets werden separat ausgewiesen.

## Verifikation (Nachweisform)

```bash
mkdir -p .rag/eval
command -v rag >/dev/null
rag --version > .rag/eval/00-rag-version.txt
test -s .rag/eval/00-rag-version.txt
rag eval run \
  --set /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl \
  --scope-default ncg/ncg-docs \
  --scope-allow ncg/ncg-docs,private \
  --top-k 5 \
  --blocking-buckets historical-user,historical-agent \
  --monitoring-buckets counterfactual-helpful,future \
  --output .rag/eval/04-phase1-eval.json
rag eval report \
  --input .rag/eval/04-phase1-eval.json \
  --metrics domain_hit_rate,file_hit_rate,cross_domain_leakage \
  --split-by-gating \
  --output .rag/eval/04-phase1-report.md
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path(".rag/eval/04-phase1-eval.json").read_text())
b = data["kpi"]["blocking"]
assert b["domain_hit_rate"] >= 0.90, b
assert b["file_hit_rate"] >= 0.70, b
assert b["cross_domain_leakage"] <= 0.10, b
assert "monitoring" in data["kpi"], "monitoring-kpi fehlt"
PY
```

Gate-Regel:

- Jeder Schritt in der Verifikationsstrecke muss real mit Exit-Code `0` laufen.
- `blocked` oder `failed` ist ein Abnahmefehler (kein gueltiger Teilerfolg).

## Nicht in dieser Spec

- Ausgestaltung spaeterer Re-Ranking-Strategien
- Produktivbetrieb/Monitoring ausserhalb lokaler Entwicklungslaeufe

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-21 | Codex | Eval- und Qualitaetsgates als eigener, pruefbarer Delivery-Slice separiert. |
| 2026-04-21 | Codex | `cross_domain_leakage` messbar praezisiert (mindestens 3 von Top-5 Treffern aus nicht erwarteter Domain). |
| 2026-04-21 | Codex | Bucket-Gating verbindlich gemacht: `historical-*` blocking, `counterfactual/future` nur Monitoring. |
| 2026-04-22 | Codex | Platzhalter durch konkrete Eval- und Report-Kommandos inkl. KPI-Threshold-Check ersetzt. |
| 2026-04-23 | User + Codex | Optionale Monitoring-Metriken (`source_precision`) explizit als non-blocking fuer Phase 1 praezisiert, um Parent/Child-Metrikvertrag eindeutig zu halten. |
| 2026-04-23 | User + Codex | Verifikation um harten `rag`-Install-Preflight (`command -v`, `--version`, non-empty Nachweisdatei) und eindeutige `blocked/failed`-Gate-Regel erweitert. |
| 2026-04-23 | User + Codex | Status auf `🔵 Implemented` gesetzt: Eval-Run/Report laufen in der Runtime, Blocking-KPIs werden erfuellt und mit Evidence dokumentiert. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: Closeout-Verifikation ist erneut gruen; `source_precision` bleibt non-blocking gemaess Child-Gate. |

SessionId: codex-desktop-current-thread
