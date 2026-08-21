# 12: Den probare-crm-Piloten live aktivieren und Ende-zu-Ende beweisen

**What to build:** Der Orchestrator wird fuer den vollstaendigen geeigneten `probare-crm`-Backlog aktiviert und fuehrt ein reales Issue vom GitHub-Ereignis bis zu einem verifizierten Pull Request fuer Daniels menschliches Review.

**Blocked by:** 11: Den lokalen Piloten unter macOS automatisch betreiben

**Covers:** US 1-2, 9-12, 35, 39-44, 53-63, 66, 68-70

**Status:** ready-for-agent

- [ ] Vor der Aktivierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set, Rollback und direkte Live-Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] `probare-crm` ist mit den sichtbaren Workflow-Zustaenden `agent-running`, `verified`, `awaiting-review`, `needs-info` und `ready-for-human` sowie dem signierten Webhook fuer die erlaubten Ereignisse konfiguriert.
- [ ] Die Live-Konfiguration verwendet den in Ticket 07 definierten `RepositoryAdapter`; der zentrale Workflow bleibt in `shared-ai-docs` und enthaelt keine fest codierten `probare-crm`-Sonderpfade.
- [ ] Alle geeigneten Issue-Typen und der bestehende `ready-for-agent`-Backlog sind fuer den Piloten sichtbar; Blocker und das Limit von einem aktiven Implementierungslauf verhindern ungueltige Parallelstarts.
- [ ] Ein reales geeignetes Issue durchlaeuft GitHub, Cloudflare Queue, Tunnel, lokale Inbox, LangGraph, isolierten Codex-Worktree, deterministische Verifikation und alle drei unabhaengigen Reviews.
- [ ] Der resultierende PR ist fuer seinen aktuellen Head mit `verified` und `awaiting-review` markiert und enthaelt die Kriteriumsmatrix sowie entscheidende redigierte Screenshots, REST-Ausschnitte und korrelierte Logs direkt im Body.
- [ ] Der Live-Nachweis korreliert Delivery, Lauf, Checkpoints, Worker-Modell, Reasoning-Stufe, Skill-Versionen, Review-Verdicts und PR-Head, ohne Secrets oder personenbezogene Daten offenzulegen.
- [ ] Der Pilot merged, deployt oder released nicht; er endet fuer dieses Issue sichtbar bei Daniels menschlichem PR-Review.
- [ ] Die restlichen freigegebenen Issues bleiben nach Blocking-Kanten und Repository-Serialisierung agentisch bearbeitbar, ohne dass fuer sie ein neues Produktfreigabesignal erforderlich ist.
