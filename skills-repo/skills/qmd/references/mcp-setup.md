# QMD MCP Server Setup

## Install

```bash
npm install -g @tobilu/qmd
qmd collection add ~/path/to/markdown --name myknowledge
qmd embed
```

## Configure MCP Client

**Claude Code** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "qmd": { "command": "qmd", "args": ["mcp"] }
  }
}
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "qmd": { "command": "qmd", "args": ["mcp"] }
  }
}
```

**OpenClaw** (`~/.openclaw/openclaw.json`):
```json
{
  "mcp": {
    "servers": {
      "qmd": { "command": "qmd", "args": ["mcp"] }
    }
  }
}
```

## HTTP Mode

```bash
qmd mcp --http              # Port 8181
qmd mcp --http --daemon     # Background
qmd mcp stop                # Stop daemon
```
