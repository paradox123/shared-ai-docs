**Date:** 2026-04-21  
**Status:** 🟢 Accepted  
**Scope:** Phase-1-Agentintegration fuer research-for-review und spec-closeout auf Basis des lokalen RAG

---

# 05 DanielsVault RAG Agent Integration Research-for-Review und Spec-Closeout

## Zweck

Diese Child-Spec definiert, wie Agent-Workflows den Retrieval-Kern nutzen muessen, damit Reviews und Closeouts nachvollziehbar und effizient werden.

## Reihenfolge und Abhaengigkeiten

- Reihenfolge: `05`
- setzt `03` und `04` voraus

## Ziel-Workflows

1. `research-for-review`
2. `spec-closeout`

## Verbindliche Integrationsanforderungen

### A) research-for-review

Pro Treffer mindestens:

- `path`
- `section_or_chunk`
- `excerpt`
- `why_relevant`

### B) spec-closeout

Pro vorgeschlagenem Doku-Update mindestens:

- `path`
- `update_reason`
- `source_evidence`

## Routing- und Scope-Regeln

- Default-Retrieval in `ncg/ncg-docs`
- `private` nur bei explizitem Scope-Override (`--scope private` oder `--scope all`)
- Full-Vault nur expliziter Opt-in, nicht stillschweigender Fallback

## Akzeptanzkriterien

1. Beide Workflows liefern die Pflichtfelder vollstaendig.
2. Quellenbezug ist fuer alle vorgeschlagenen Aussagen vorhanden.
3. Agenten muessen ohne Vollsuche gezielt auf relevante Dokumente routen koennen.

## Verifikation (Nachweisform)

```bash
mkdir -p .rag/runs
command -v rag >/dev/null
rag --version > .rag/runs/00-rag-version.txt
test -s .rag/runs/00-rag-version.txt
rag workflow research-for-review --scope ncg/ncg-docs --query "Welche Dokumente sind fuer den Docker BaseUrl Fix relevant?" --top-k 5 --format json > .rag/runs/05-review-1.json
rag workflow research-for-review --scope ncg/ncg-docs --query "Welche Quellen brauche ich fuer eine Spec-Review zu Service-Abhaengigkeiten?" --top-k 5 --format json > .rag/runs/05-review-2.json
rag workflow spec-closeout --scope ncg/ncg-docs --change "Docker BaseUrl Fix" --top-k 5 --format json > .rag/runs/05-closeout-1.json
rag workflow spec-closeout --scope ncg/ncg-docs --change "Migration to Hetzner-Dev" --top-k 5 --format json > .rag/runs/05-closeout-2.json
python3 - <<'PY'
import json
from pathlib import Path
for name in [".rag/runs/05-review-1.json", ".rag/runs/05-review-2.json"]:
    data = json.loads(Path(name).read_text())
    hits = data.get("hits", [])
    assert hits, f"keine hits: {name}"
    for hit in hits:
        assert hit.get("path"), f"path fehlt: {name}"
        assert hit.get("section_or_chunk"), f"section_or_chunk fehlt: {name}"
        assert hit.get("excerpt"), f"excerpt fehlt: {name}"
        assert hit.get("why_relevant"), f"why_relevant fehlt: {name}"
for name in [".rag/runs/05-closeout-1.json", ".rag/runs/05-closeout-2.json"]:
    data = json.loads(Path(name).read_text())
    recs = data.get("recommendations", [])
    assert recs, f"keine recommendations: {name}"
    for rec in recs:
        assert rec.get("path"), f"path fehlt: {name}"
        assert rec.get("update_reason"), f"update_reason fehlt: {name}"
        assert rec.get("source_evidence"), f"source_evidence fehlt: {name}"
PY
```

Gate-Regel:

- Jeder Schritt in der Verifikationsstrecke muss real mit Exit-Code `0` laufen.
- `blocked` oder `failed` ist ein Abnahmefehler (kein gueltiger Teilerfolg).

## Nicht in dieser Spec

- Multi-Rechner-Synchronisierung
- globale Vollindex-Strategie ueber alle kuenftigen Projekte

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-21 | Codex | Agentische Integrationsanforderungen als letzte Child-Spec der Implementierungsreihenfolge ausgegliedert. |
| 2026-04-21 | Codex | Routing-Regel fuer `private` auf expliziten Scope-Override konkretisiert. |
| 2026-04-22 | Codex | Konkrete Workflow-Verifikationskommandos fuer research-for-review/spec-closeout inklusive Feldvalidierung ergaenzt. |
| 2026-04-22 | Codex | Workflow-Verifikation gehaertet: non-empty Assertions fuer `hits` und `recommendations` ergaenzt. |
| 2026-04-23 | User + Codex | Verifikation um harten `rag`-Install-Preflight (`command -v`, `--version`, non-empty Nachweisdatei) und eindeutige `blocked/failed`-Gate-Regel erweitert. |
| 2026-04-23 | User + Codex | Status auf `🔵 Implemented` gesetzt: Workflow-Outputs fuer `research-for-review` und `spec-closeout` sind runtime-seitig umgesetzt und mit gruener Verifikationsstrecke nachgewiesen. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: Closeout-Run bestaetigt vollstaendige, gruene Workflow-Verifikation und archivierten OpenSpec-Change. |

SessionId: codex-desktop-current-thread
