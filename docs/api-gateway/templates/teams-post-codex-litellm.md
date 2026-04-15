Hi zusammen 👋

ich habe euch mal eine **LLM-Gateway-Config** zusammengestellt (LiteLLM + Compose) ✅

Die Idee dahinter: Wir **entkoppeln Agent und Subscription**.  
Heisst: Ihr koennt euren bevorzugten Agenten nutzen und das Modellrouting laeuft zentral ueber das Gateway (`http://localhost:4000`) statt pro Tool einzeln.

So kann man mit bestehenden Subscriptions (z. B. Copilot, je nach Mapping auch weitere Modelle wie Gemini etc.) deutlich flexibler arbeiten. 🚀

**Was es konkret loest**
- weniger Setup-Drift zwischen Tools/Clients
- einheitliche Auth + Modellnamen
- schnelleres Onboarding
- stabiler bei Neustarts/Recreate (persistente LiteLLM-Volumes)

**📦 Paketinhalt**
- `docker-compose.yml`
- `config.yaml`
- `.env.example`
- `codex.env.example`
- `README.md` (Quick Start + Smoke Test)

Wenn ihr wollt, kann ich als naechsten Schritt noch eine zweite Compose-Variante fuer VS Code Copilot Proxy (`:4001`) dazulegen. 🙌
