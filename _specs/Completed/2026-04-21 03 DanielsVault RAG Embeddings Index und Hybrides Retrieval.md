**Date:** 2026-04-21  
**Status:** 🟢 Accepted  
**Scope:** Phase-1-Definition fuer lokalen Embedding-Index, semantisches und hybrides Retrieval via CLI

---

# 03 DanielsVault RAG Embeddings Index und Hybrides Retrieval

## Zweck

Diese Child-Spec definiert den Retrieval-Kern fuer Phase 1:

1. lokaler Embedding-basierter Dokumentindex
2. semantisches Retrieval mit Quellenbezug
3. hybrider Retrieval-Pfad (semantisch + strukturiert)

## Reihenfolge und Abhaengigkeiten

- Reihenfolge: `03`
- setzt `01` und `02` voraus
- Voraussetzung fuer `04` und `05`

## Architekturleitplanken (Phase 1)

- lokale Embeddings (keine API-Embeddings als Pflichtpfad)
- CLI-first als verbindlicher Agentenzugang
- lokale Wissensbasis ohne externe Inhaltsquellen

## Query-Modi

Verbindlich:

- `semantic`: freie Fragen ueber Dokument-Embeddings
- `structured`: exakte Faktenfragen ueber projizierte Records
- `hybrid`: kombinierte Ergebnisbildung mit nachvollziehbarer Quellenlage

## Ergebnisanforderungen

Rueckgaben muessen maschinell lesbar sein und mindestens enthalten:

- `query`
- `mode`
- `domain`
- `generated_at`
- `hits[]` mit `path`, `section_or_chunk`, `excerpt`, `score`, `why_relevant`
- optional `facts[]` mit `name`, `value`, `source_path`, `source_anchor`

## Akzeptanzkriterien

1. lokaler Index kann fuer Default-Scope aufgebaut und aktualisiert werden.
2. semantische Queries liefern reproduzierbar Top-K-Treffer mit Quellenbezug.
3. hybride Queries koennen strukturierte Fakten und Dokumentkontext zusammenfuehren.
4. Default-Scope bleibt ohne expliziten Override auf `ncg/ncg-docs` begrenzt.

## Verifikation (Nachweisform)

```bash
mkdir -p .rag/runs
command -v rag >/dev/null
rag --version > .rag/runs/00-rag-version.txt
test -s .rag/runs/00-rag-version.txt
rag index build --scope ncg/ncg-docs --embedding-model local-default --output .rag/runs/03-index-build.json
rag retrieve semantic --scope ncg/ncg-docs --query "Wo ist die Migration zu Hetzner-Dev dokumentiert?" --top-k 5 --format json > .rag/runs/03-semantic.json
rag retrieve hybrid --scope ncg/ncg-docs --record-type ci_setting_fact --query "Welche CI-Variable steuert das Deployment-Target?" --top-k 5 --format json > .rag/runs/03-hybrid.json
rag retrieve semantic --scope ncg/ncg-docs --query "Wo ist die Migration zu Hetzner-Dev dokumentiert?" --top-k 5 --format json > .rag/runs/03-default-scope.json
rag retrieve semantic --scope private --query "ELR Foerderung Finanzierungsnachweis" --top-k 5 --format json > .rag/runs/03-private-override.json
python3 - <<'PY'
import json
from pathlib import Path
semantic = json.loads(Path(".rag/runs/03-semantic.json").read_text())
for field in ["query", "mode", "domain", "generated_at"]:
    assert semantic.get(field), f"semantic ohne pflichtfeld {field}"
assert semantic.get("mode") == "semantic", f"unerwarteter mode: {semantic.get('mode')}"
for hit in semantic.get("hits", []):
    for field in ["path", "section_or_chunk", "excerpt", "score", "why_relevant"]:
        assert hit.get(field) is not None and hit.get(field) != "", f"semantic-hit ohne {field}"
default_hits = json.loads(Path(".rag/runs/03-default-scope.json").read_text()).get("hits", [])
assert default_hits, "default-scope lieferte keine Treffer"
assert all("/private/" not in h.get("path","") for h in default_hits), "default-scope leakage nach private"
private_hits = json.loads(Path(".rag/runs/03-private-override.json").read_text()).get("hits", [])
assert private_hits, "private-override lieferte keine Treffer"
assert all("/private/" in h.get("path","") for h in private_hits), "private-override enthaelt non-private Treffer"
hybrid = json.loads(Path(".rag/runs/03-hybrid.json").read_text())
for field in ["query", "mode", "domain", "generated_at"]:
    assert hybrid.get(field), f"hybrid ohne pflichtfeld {field}"
assert hybrid.get("mode") == "hybrid", f"unerwarteter mode: {hybrid.get('mode')}"
assert hybrid.get("hits"), "hybrid ohne dokumenttreffer"
assert hybrid.get("facts"), "hybrid ohne strukturierte facts"
for hit in hybrid.get("hits", []):
    for field in ["path", "section_or_chunk", "excerpt", "score", "why_relevant"]:
        assert hit.get(field) is not None and hit.get(field) != "", f"hybrid-hit ohne {field}"
PY
```

Gate-Regel:

- Jeder Schritt in der Verifikationsstrecke muss real mit Exit-Code `0` laufen.
- `blocked` oder `failed` ist ein Abnahmefehler (kein gueltiger Teilerfolg).

## Nicht in dieser Spec

- Eval-Metrikdefinition im Detail
- Agent-Skill-Integration
- Full-Vault-Rollout

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-21 | Codex | Retrieval-Kern als separater Child-Spec mit hybrider Query-Anforderung ausgekoppelt. |
| 2026-04-22 | Codex | Konkrete Verifikationskommandos fuer Index-Build, semantisches/hybrides Retrieval und Scope-Gate ergaenzt. |
| 2026-04-22 | Codex | Default-vs-private Scope-Gate diskriminierender gemacht (beidseitige non-empty und Domain-Assertions). |
| 2026-04-23 | User + Codex | Verifikation um harten `rag`-Install-Preflight (`command -v`, `--version`, non-empty Nachweisdatei) und eindeutige `blocked/failed`-Gate-Regel erweitert. |
| 2026-04-23 | User + Codex | Verifikation auf Ergebnis-Contract gehaertet: Pflichtfelder im Response-Envelope sowie Pflichtfelder je `hits[]` fuer `semantic` und `hybrid` werden explizit geassertet. |
| 2026-04-23 | User + Codex | Status auf `🔵 Implemented` gesetzt: semantisches/hybrides Retrieval inkl. Envelope-Pflichtfeldern und Scope-Gates wurde runtime-seitig umgesetzt und vollstaendig verifiziert. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: erneuter Closeout-Run bestaetigt gruene Gates; OpenSpec-Change ist archiviert. |

SessionId: codex-desktop-current-thread
