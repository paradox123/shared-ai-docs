# Agent- und Extension-Konfiguration fuer LiteLLM

Siehe auch:

- [API Gateway Index](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/index.md)
- [LiteLLM API Gateway](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/litellm-api-gateway.md)
- [LiteLLM API Gateway auf Azure](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/litellm-api-gateway-azure.md)

## Ziel

Diese Seite beschreibt, wie die bereits installierten Agenten und IDE-Integrationen an das lokale LiteLLM-Gateway unter `http://localhost:4000` angebunden werden koennen.

Behandelt werden:

- Codex CLI
- Claude Code
- GitHub Copilot in VS Code
- GitHub Copilot CLI
- GitHub Copilot in Rider / JetBrains IDEs

## Gemeinsame Grundlage

Das lokale Gateway verwendet:

- Base URL: `http://localhost:4000`
- Auth: `Authorization: Bearer <LITELLM_MASTER_KEY>`
- Modellnamen aus `config.yaml`, zum Beispiel:
- `copilot-gpt-4.1`
- `copilot-gpt-5`
- `copilot-gpt-5.1-codex`
- `copilot-sonnet-4.5`

Master Key laden:

```bash
cd "/Users/dh/Documents/Dev/ai-gateway"
export LITELLM_MASTER_KEY=$(sed -n 's/^LITELLM_MASTER_KEY=//p' .env)
```

## Codex CLI

### Status

Direkte Anbindung an LiteLLM ist dokumentiert.

LiteLLM beschreibt fuer OpenAI Codex explizit:

- `OPENAI_BASE_URL=http://0.0.0.0:4000`
- `OPENAI_API_KEY=<LiteLLM key>`

Quelle:

- [LiteLLM OpenAI Codex Tutorial](https://docs.litellm.ai/docs/tutorials/openai_codex)

### Konfiguration

```bash
cd "/Users/dh/Documents/Dev/ai-gateway"
export OPENAI_BASE_URL="http://localhost:4000"
export OPENAI_API_KEY="$(sed -n 's/^LITELLM_MASTER_KEY=//p' .env)"
```

### Nutzung

```bash
codex --model copilot-gpt-5.1-codex
```

oder

```bash
codex --model copilot-gpt-4.1
```

Wichtig:

- Verwende die Modellnamen aus der lokalen `config.yaml`
- Fuer Responses-faehige Modelle ist `copilot-gpt-5.1-codex` der naheliegende Startpunkt

## Claude Code

### Status

Direkte Anbindung an ein LLM-Gateway ist offiziell dokumentiert.

Anthropic dokumentiert fuer Claude Code:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`

Quelle:

- [Claude Code LLM-Gateway-Konfiguration](https://code.claude.com/docs/de/llm-gateway)

### Konfiguration

```bash
cd "/Users/dh/Documents/Dev/ai-gateway"
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="$(sed -n 's/^LITELLM_MASTER_KEY=//p' .env)"
```

### Hinweise

- Claude Code erwartet laut Anthropic ein Gateway, das das benoetigte Anthropic-kompatible API-Format bereitstellt
- Das lokale LiteLLM-Gateway ist dafuer der vorgesehene Integrationsweg
- Falls Modellnamen gemappt werden muessen, sollte das an der LiteLLM-Konfiguration ausgerichtet werden

## GitHub Copilot in VS Code

### Status

Eine direkte Proxy-Umleitung ueber LiteLLM ist in der LiteLLM-Doku fuer VS Code beschrieben.

Quelle:

- [LiteLLM GitHub Copilot Integration](https://docs.litellm.ai/docs/tutorials/github_copilot_integration)

Die relevante VS-Code-Einstellung ist:

```json
{
  "github.copilot.advanced": {
    "debug.overrideProxyUrl": "http://localhost:4000",
    "debug.testOverrideProxyUrl": "http://localhost:4000"
  }
}
```

### Einordnung

- Das ist ein VS-Code-spezifischer Weg
- Die Schalter liegen unter `debug.*`
- Deshalb sollte man das als experimentell oder zumindest integrationsnah betrachten

### Offener Punkt

Die LiteLLM-Seite zeigt die Proxy-URL, aber nicht sauber, wie Copilot dabei einen LiteLLM-`master_key` mitsendet.

Deshalb gilt:

- URL-Override ist dokumentiert
- Auth gegen einen geschuetzten LiteLLM-Proxy muss im praktischen Test verifiziert werden

## GitHub Copilot CLI

### Status

Fuer die normale Copilot-CLI-Dokumentation ist ein direkter LiteLLM-Base-URL-Switch nicht klar dokumentiert.

Was GitHub fuer Copilot CLI klar dokumentiert:

- Custom Agents
- MCP-Server
- Hooks
- Instructions

Quellen:

- [Creating and using custom agents for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [Adding MCP servers for GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)

### Einordnung

Aktuell ist fuer Copilot CLI am saubersten dokumentiert:

- Erweiterung ueber MCP
- Erweiterung ueber Custom Agents

Nicht sauber belegt ist in den geprueften offiziellen Quellen:

- ein einfacher `OPENAI_BASE_URL`-aehnlicher Schalter wie bei Codex CLI

### Empfehlung

- Copilot CLI nicht als ersten direkten LiteLLM-Client behandeln
- statt dessen MCP und Agents nutzen, wenn du dieselben Tools und Kontexte in Copilot CLI verfuegbar machen willst

## GitHub Copilot in Rider / JetBrains IDEs

### Status

Fuer JetBrains IDEs ist in den geprueften offiziellen Quellen dokumentiert:

- GitHub Copilot Custom Agents sind in JetBrains IDEs verfuegbar, aktuell als Public Preview

Quellen:

- [About custom agents](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)
- [Creating custom agents for Copilot coding agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)

### Was dokumentiert ist

- Nutzung von Copilot Custom Agents in JetBrains IDEs
- gemeinsame Agent-Profile ueber `.github/agents/*.agent.md`

### Was nicht sauber belegt ist

- ein Rider-spezifischer LiteLLM-Proxy-Override analog zu VS Code `debug.overrideProxyUrl`

### Empfehlung

- Rider derzeit nicht als sicher dokumentierten direkten LiteLLM-Client behandeln
- wenn du in Rider dieselben Verhaltensweisen willst, setze auf gemeinsame Copilot Custom Agents
- fuer echtes Modell-Routing ueber LiteLLM erst dann umstellen, wenn ein belastbarer Rider-spezifischer Endpoint-Mechanismus dokumentiert ist

## Praktische Empfehlung fuer den aktuellen Stack

### Direkt ueber LiteLLM anschliessen

- Codex CLI
- Claude Code
- VS Code Copilot, aber mit vorsichtigem Test wegen Auth und `debug.overrideProxyUrl`

### Eher indirekt ueber gemeinsame Konfiguration erweitern

- GitHub Copilot CLI
- Rider / JetBrains Copilot

### Gemeinsamer Hebel fuer Copilot-Umgebungen

Wenn du ueber Copilot CLI, VS Code und Rider hinweg einheitliches Verhalten willst, ist die robusteste gemeinsame Ebene aktuell:

- `.github/agents/*.agent.md` fuer Copilot Custom Agents
- MCP-Server fuer gemeinsam nutzbare Tools

Das ersetzt nicht automatisch das Modell-Backend durch LiteLLM, vereinheitlicht aber Verhalten, Tooling und Arbeitsweise.

## Vorschlag fuer die naechste Umsetzungsstufe

1. Codex CLI verbindlich auf LiteLLM setzen
2. Claude Code auf LiteLLM setzen
3. VS Code Copilot testweise ueber `debug.overrideProxyUrl` pruefen
4. fuer Copilot CLI und Rider gemeinsame Custom Agents und MCP nutzen

## Weiterfuehrende Links

- [API Gateway Index](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/index.md)
- [LiteLLM API Gateway](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/litellm-api-gateway.md)
- [LiteLLM API Gateway auf Azure](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/litellm-api-gateway-azure.md)
