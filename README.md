# Shared AI Documentation & Tools

This repository contains AI-related documentation, prompts, skills, hooks, and workflow automation tools that support various documentation repositories (ncg-docs, private, etc.).

## Contents

- **Repository maintenance**: [Renovate in each owning GitHub repository](docs/renovate-repository-standard.md) and [ADR 0011](docs/adr/0011-renovate-in-each-owning-github-repository.md)
- **contextual-llm-wiki/**: [Context-scoped Markdown wiki with Atomicstrata and QMD](contextual-llm-wiki/README.md), [daily Mac operations](contextual-llm-wiki/OPERATIONS.md), and [agent-context adoption catalog](docs/rag/llm-wiki-context-adoption-catalog.md)
- **n8n/**: Workflow automation engine setup
- **langgraph-github-issue-pilot/**: Local persistent GitHub issue workflow receiver
- **cloudflare-github-webhook-relay/**: Signed Cloudflare Worker, Queue, DLQ, and Tunnel relay for the local pilot
- (More sections to be added as the repository grows)

## Purpose

This repository serves as a central hub for:
- AI assistant skills and capabilities
- Prompt templates and hooks
- Workflow automation configurations
- Reusable automation patterns
- Documentation about AI-assisted workflows

## Getting Started

See individual directories for specific setup instructions.

## Repository Structure

```
shared-ai-docs/
├── n8n/                    # Workflow automation engine
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── README.md
│   └── workflows/          # Exported workflow templates (JSON)
└── README.md
```

## Related Repositories

- **ncg-docs**: Technical documentation for NCG project
- **private**: Personal documentation and management
