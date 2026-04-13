# Obsidian Vault Structure

**Organization of DanielsVault Documentation**

---

## Vault Root

**Location**: `/Users/dh/Documents/DanielsVault`

**Main Folders**:
- `NCG/` - Work/company documentation (primary focus for this skill)
- `Privat/` - Personal/household documents
- `Sparkle/` - Finance/administrative notes

---

## NCG Operations Documentation

**Location**: `/Users/dh/Documents/DanielsVault/NCG/Ops`

### Directory Structure

```
NCG/Ops/
├── README.md                          # Navigation hub
├── ARCHIVE/                           # Original files (preserved)
│   └── [21 original .md files]
├── Infrastructure/
│   └── Hetzner-Infrastructure.md     # 13 server inventory
├── Environments/
│   ├── Development/
│   │   └── Dev-Environment.md        # Dev config
│   └── Production/
│       └── [Future prod docs]
├── Security/
│   ├── Secrets-Management.md         # Credential inventory
│   └── Certificates.md               # SSL/TLS config
├── Services/
│   ├── Docker-Registry.md            # Private registry
│   ├── Databases.md                  # MongoDB/MariaDB/PostgreSQL
│   ├── GitLab-CI-CD.md              # CI/CD pipelines
│   ├── RabbitMQ.md                   # Message broker
│   └── Frontend-Services.md          # Frontend + OAuth
├── Troubleshooting/
│   └── Network-Issues.md             # Network diagnostics
├── Guides/
│   ├── Quick-Start-Developers.md     # Dev onboarding
│   ├── Quick-Start-DevOps.md         # Ops onboarding
│   ├── Routing-Setup-Guide.md        # pfSense routing
│   └── System-Updates.md             # Update procedures
└── Docker/
    └── [Future Docker docs]
```

---

## Documentation Standards

### File Naming
- Use hyphens for multi-word files: `Quick-Start-Developers.md`
- TitleCase for main words
- Descriptive names that match content

### Content Structure
Every documentation file includes:
1. **Title**: Clear, descriptive H1
2. **Table of Contents**: For files >100 lines
3. **Overview**: Brief introduction
4. **Main Content**: Organized with H2/H3 headings
5. **Related Documentation**: Links to related files
6. **Last Updated**: Date stamp
7. **Source Files**: Attribution to ARCHIVE sources

### Security Policy
- **Never** hardcode secrets in documentation
- Use placeholders: `GITLAB_CI: VARIABLE_NAME` or `VAULT: path/to/secret`
- Reference secrets in Secrets-Management.md

---

## Change Documentation Process

### When to Document Changes

**Always document**:
- New server provisioning
- Service deployments
- Configuration changes
- Security updates
- Network topology changes
- Database schema migrations

**Location for changes**:
- Infrastructure changes → Update relevant file in `Infrastructure/`
- Service updates → Update file in `Services/`
- New procedures → Create in `Guides/` or update existing
- Troubleshooting → Add to `Troubleshooting/`

### Changelog Format

**For major changes, add to file header**:
```markdown
**Last Updated**: 2026-01-03
**Change**: Deployed backend v2.1.0 to production
**By**: DevOps Team
```

**For running changelog** (if created):
```markdown
## 2026-01-03 - Backend Deployment v2.1.0
- Deployed to production (10.1.0.10)
- Updated Docker images: apigateway, store, security
- Database migrations applied
- Services restarted successfully
```

---

## Cross-Referencing

**Use relative links between files**:
```markdown
See [Secrets Management](../Security/Secrets-Management.md) for credentials.
```

**Common reference patterns**:
- Infrastructure details → `Infrastructure/Hetzner-Infrastructure.md`
- Secrets → `Security/Secrets-Management.md`
- Certificates → `Security/Certificates.md`
- Deployment → `Services/GitLab-CI-CD.md`
- Troubleshooting → `Troubleshooting/Network-Issues.md`

---

## Obsidian Features

### Wikilinks
Obsidian supports `[[File Name]]` syntax, but for portability use standard markdown links.

### Tags
Can use `#infrastructure #deployment` tags for categorization.

### Graph View
Files are interconnected via links - maintains knowledge graph.

---

## Backup and Version Control

**Git Repository**:
- Vault is a git repository
- Changes can be committed
- Track history of documentation updates

**Best Practices**:
- Commit meaningful changes
- Use descriptive commit messages
- Don't commit secrets (even though we don't hardcode them)

---

## Related Skills

- **Documentation Skill**: Query and update vault (this skill)
- **DevOps Skill**: Will reference vault for procedures
- **Security Skill**: Will update Secrets-Management.md
