# Documentation Skill

**NCG infrastructure documentation system for KAI**

---

## Overview

The Documentation Skill enables PAI to query NCG infrastructure documentation and track changes in the Obsidian vault at `/Users/dh/Documents/DanielsVault/NCG/Ops`.

---

## Capabilities

This skill can:
- **Query infrastructure**: Find server IPs, service endpoints, configurations
- **Search documentation**: Full-text and regex search across all docs
- **Document changes**: Record deployments, config updates, new servers
- **Generate runbooks**: Create step-by-step operational procedures
- **Explain concepts**: Provide detailed explanations of infrastructure designs

---

## Workflows

### 1. QueryInfrastructure
**Use when**: User asks for server IPs, service endpoints, or infrastructure details

**Example queries**:
- "What's the IP of the prod database?"
- "Where is the Docker registry?"
- "Show me all dev servers"

**Workflow file**: `Workflows/QueryInfrastructure.md`
**Skill path**: `/Users/dh/.claude/skills/documentation/`

---

### 2. DocumentChange
**Use when**: Recording infrastructure changes in the vault

**Example queries**:
- "Document deployment of backend v2.1.0 to production"
- "Record new server at 10.1.0.12"
- "Document MongoDB password rotation"

**Workflow file**: `Workflows/DocumentChange.md`

---

### 3. GenerateRunbook
**Use when**: Creating operational procedures

**Example queries**:
- "Create a runbook for backend deployment"
- "Generate MongoDB backup procedure"
- "Create certificate renewal runbook"

**Workflow file**: `Workflows/GenerateRunbook.md`

---

### 4. SearchDocumentation
**Use when**: Finding information across documentation

**Example queries**:
- "Find all Docker commands"
- "Search for MongoDB configuration"
- "Show me all mentions of GitLab"

**Workflow file**: `Workflows/SearchDocumentation.md`

---

### 5. ExplainConcept
**Use when**: Understanding infrastructure concepts

**Example queries**:
- "Explain how our Docker registry works"
- "Explain the network architecture"
- "How does pfSense routing work?"

**Workflow file**: `Workflows/ExplainConcept.md`

---

## Tools

### SearchVault.ts
Full-text and regex search across documentation

```bash
# From skill directory: /Users/dh/.claude/skills/documentation/

# Basic search
bun run Tools/SearchVault.ts "MongoDB"

# Search specific file
bun run Tools/SearchVault.ts --file Databases.md "connection"

# Regex search
bun run Tools/SearchVault.ts --regex "10\.0\.0\.\d+"

# Detailed results with context
bun run Tools/SearchVault.ts --detailed "docker registry"
```

---

### UpdateChangelog.ts
Append changelog entries to documentation files

```bash
# Using title and content
bun run Tools/UpdateChangelog.ts --file GitLab-CI-CD.md --title "Pipeline Update" --content "Optimized build stage"

# Using pre-formatted entry
bun run Tools/UpdateChangelog.ts --file Databases.md --entry "## 2026-01-03 - MongoDB Upgrade\n- Upgraded to 7.0.5"

# With custom date
bun run Tools/UpdateChangelog.ts --file Certificates.md --title "Cert Renewal" --content "Renewed SSL certs" --date 2026-01-15
```

---

### GenerateServerMap.ts
Auto-generate ServerMap.md from infrastructure documentation

```bash
# Generate with default output
bun run Tools/GenerateServerMap.ts

# Custom output location
bun run Tools/GenerateServerMap.ts --output /tmp/ServerMap.md

# Experimental: Scan docs to extract server info
bun run Tools/GenerateServerMap.ts --scan
```

---

## Context Files

### ServerMap.md
Quick reference for all servers and services
- Development network (10.0.0.x)
- Production network (10.1.0.x)
- Service endpoints
- Connection strings
- SSH access commands

### VaultStructure.md
Documentation organization guide
- Directory structure
- File naming conventions
- Cross-referencing patterns
- Change documentation process
- Security policies

### DocumentationIndex.md
Comprehensive index of all documentation files
- File descriptions
- When to use each file
- Quick links by topic
- Documentation standards

---

## Integration with Obsidian Vault

### Vault Location
`/Users/dh/Documents/DanielsVault/NCG/Ops`

### Documentation Structure
```
NCG/Ops/
├── README.md
├── Infrastructure/
│   └── Hetzner-Infrastructure.md
├── Environments/
│   └── Development/
├── Security/
│   ├── Secrets-Management.md
│   └── Certificates.md
├── Services/
│   ├── Docker-Registry.md
│   ├── Databases.md
│   ├── GitLab-CI-CD.md
│   ├── RabbitMQ.md
│   └── Frontend-Services.md
├── Troubleshooting/
│   └── Network-Issues.md
├── Guides/
│   ├── Quick-Start-Developers.md
│   ├── Quick-Start-DevOps.md
│   ├── Routing-Setup-Guide.md
│   └── System-Updates.md
└── ARCHIVE/ (21 original files)
```

---

## Setup

### 1. Install Dependencies

```bash
cd /Users/dh/.claude/skills/documentation/Tools
bun install
```

### 2. Test Tools

```bash
# Test search
bun run SearchVault.ts "docker"

# Test server map generation
bun run GenerateServerMap.ts

# Test changelog update
bun run UpdateChangelog.ts --help
```

### 3. Verify Context Files

All context files should exist:
- ✅ `Context/ServerMap.md`
- ✅ `Context/VaultStructure.md`
- ✅ `Context/DocumentationIndex.md`

---

## Usage with PAI

Once PAI loads this skill, you can use natural language queries:

```
# Query infrastructure
"What's the IP of the production database?"
"Show me all development servers"
"Where is the Docker registry?"

# Search documentation
"Find all Docker commands"
"Search for MongoDB configuration"
"Show mentions of GitLab pipelines"

# Document changes
"Document deployment of backend v2.1.0"
"Record new server prod-monitoring at 10.1.0.12"
"Document MongoDB password rotation"

# Generate runbooks
"Create a runbook for backend deployment"
"Generate MongoDB backup procedure"
"Create disaster recovery runbook"

# Explain concepts
"Explain how our Docker registry works"
"Explain the network architecture"
"How does certificate management work?"
```

---

## Development

### Adding New Workflows

1. Create workflow file in `Workflows/[WorkflowName].md`
2. Update `SKILL.md` routing table
3. Add examples and use cases
4. Test with PAI

### Adding New Tools

1. Create TypeScript tool in `Tools/[ToolName].ts`
2. Add to `Tools/package.json` scripts
3. Reference in relevant workflows
4. Test standalone before integration

### Updating Context Files

Context files can be manually updated or regenerated:
- `ServerMap.md`: Auto-generate with `GenerateServerMap.ts`
- `VaultStructure.md`: Update manually when docs restructure
- `DocumentationIndex.md`: Update when adding new docs

---

## Best Practices

### Documentation Changes
- Always update "Last Updated" timestamps
- Use structured changelog format
- Reference GitLab pipeline IDs for deployments
- Never hardcode secrets (use GITLAB_CI: placeholders)

### Searching
- Start with ServerMap.md for quick lookups
- Use regex for patterns (IPs, versions, dates)
- Use --detailed for context around matches
- Search specific files when topic area is known

### Security
- Never commit actual credentials
- Always use GITLAB_CI: or VAULT: references
- Review changes before committing to git
- Keep ARCHIVE folder intact (don't delete)

---

## Troubleshooting

### Tools Not Working
```bash
# Ensure bun is installed
bun --version

# Reinstall dependencies
cd Tools/
rm -rf node_modules
bun install
```

### Search Returns No Results
- Check search term spelling
- Try broader terms first
- Use regex for flexible patterns
- Verify vault path is correct

### Cannot Update Documentation
- Check file permissions
- Verify vault path: `/Users/dh/Documents/DanielsVault/NCG/Ops`
- Ensure files exist (not moved or renamed)

---

## Future Enhancements

**Planned**:
- Automatic changelog generation from GitLab pipelines
- Diff tracking for configuration changes
- Automated backup verification
- Integration with monitoring systems
- Runbook execution tracking

**Considerations**:
- Integration with other KAI skills (DevOps, Database, Security)
- Git commit automation for documentation changes
- Notification system for documentation updates

---

## Related Skills

This skill integrates with other recommended PAI skills:

1. **DevOps Skill**: Service management, deployments
2. **DatabaseOps Skill**: Database operations, backups
3. **Security Skill**: Secret rotation, certificate management
4. **Troubleshooting Skill**: Incident response, diagnostics
5. **GitLabOps Skill**: CI/CD pipeline management

**Note**: GitLab handles automated deployments (10.0.0.10 dev, 10.1.0.10 prod), so no manual deployment skill is needed.

---

## Support

**Documentation**: See workflow and context files for detailed usage
**Issues**: Update SKILL.md or workflow files as needed
**Questions**: Reference VaultStructure.md and DocumentationIndex.md

---

**Last Updated**: 2026-01-03
**Version**: 1.0.0
**Status**: Production Ready ✅
