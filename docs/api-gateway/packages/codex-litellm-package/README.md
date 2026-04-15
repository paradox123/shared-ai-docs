# Codex + LiteLLM Share Package

Dieses Paket enthaelt eine funktionierende lokale Basis fuer:

- LiteLLM Proxy via Docker Compose (`http://localhost:4000`)
- Codex CLI ueber LiteLLM (`OPENAI_BASE_URL` + `OPENAI_API_KEY`)

## Inhalt

- `docker-compose.yml`
- `config.yaml`
- `.env.example`
- `codex.env.example`

## Quick Start

```bash
cp .env.example .env
docker compose up -d
docker compose logs -f
```

Beim ersten Start erscheint in den Logs ein GitHub Device Code:

1. `https://github.com/login/device` oeffnen
2. Code bestaetigen
3. Danach ist der Login im Volume `litellm-config` persistent

## Codex an den Proxy haengen

```bash
export OPENAI_BASE_URL="http://localhost:4000"
export OPENAI_API_KEY="$(sed -n 's/^LITELLM_MASTER_KEY=//p' .env)"
codex --model copilot-gpt-5.1-codex
```

Alternative:

```bash
codex --model copilot-gpt-4.1
```

## Smoke Test

```bash
export LITELLM_MASTER_KEY="$(sed -n 's/^LITELLM_MASTER_KEY=//p' .env)"
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

Erwartung: HTTP `200` mit Modellliste.
