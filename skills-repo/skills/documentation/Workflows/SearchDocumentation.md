# Search Documentation Workflow

**Find information across all NCG operations documentation**

---

## Purpose

Quickly locate specific information, commands, configurations, or procedures across the entire documentation set without manually browsing files.

---

## When to Use

- User asks "where is X documented"
- User needs to find all mentions of a topic
- User wants to see examples of a command
- Looking for configuration patterns
- Finding related documentation

---

## Procedure

### Step 1: Determine Search Strategy

**Choose the right search approach**:

| Need | Tool | Example |
|------|------|---------|
| Quick server/service lookup | ServerMap.md | "What's the IP of prod database?" |
| Keyword search | SearchVault.ts | "Find all Docker commands" |
| Regex pattern | SearchVault.ts --regex | Find IP addresses: `10\.0\.0\.\d+` |
| Specific file search | SearchVault.ts --file | Search only in Databases.md |
| Concept understanding | ExplainConcept workflow | "Explain pfSense routing" |

### Step 2: Use SearchVault Tool

**Basic search**:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts "search term"
```

**Search specific file**:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --file "Databases.md" "MongoDB"
```

**Regex search** (for patterns like IPs, emails, versions):
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --regex "10\\.0\\.0\\.\\d+"
```

**Detailed results** (with context):
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --detailed "docker registry"
```

**More results**:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --limit 50 "GitLab"
```

### Step 3: Analyze Results

**Review the output**:
```
📚 Found 5 result(s)

📄 Services/Databases.md:42
   MongoDB connection: mongodb://dba:<GITLAB_CI:PROD_MONGODB_PASSWORD>@10.1.0.8:27017

📄 Security/Secrets-Management.md:18
   - PROD_MONGODB_PASSWORD: MongoDB production database password
```

**Identify**:
- Which files contain the information
- Line numbers for precise location
- Context around the match

### Step 4: Read Relevant Sections

**For deeper understanding, read the full context**:
- Use the file paths and line numbers from search results
- Read surrounding sections for complete information
- Check cross-references to related documentation

### Step 5: Synthesize Information

**Combine information from multiple sources**:
- If search returns multiple files, summarize key points from each
- Show relationships between different documentation files
- Provide complete answer with all relevant sources

### Step 6: Provide Structured Response

**Format the answer clearly**:

```markdown
📚 Found in [N] files:

## [File 1]: [Section Name]
[Relevant information from file 1]

**Location**: NCG/Ops/[path/to/file.md]

## [File 2]: [Section Name]
[Relevant information from file 2]

**Location**: NCG/Ops/[path/to/file.md]

## Related Documentation
- [Link to related file 1]
- [Link to related file 2]
```

---

## Examples

### Example 1: Find Docker Commands

**User**: "Find all Docker commands in the documentation"

**Steps**:
1. Run search:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts "docker"
```

2. Results show matches in:
   - Services/Docker-Registry.md (authentication, push/pull)
   - Guides/Quick-Start-Developers.md (local development)
   - Troubleshooting/Network-Issues.md (debugging containers)

3. Synthesize:

```markdown
📚 Docker Commands Found

## Authentication
**Location**: Services/Docker-Registry.md

```bash
docker login docker.auto-nagel-cloud.de -u ncg -p <GITLAB_CI:REGISTRY_PASSWORD>
```

## Push/Pull Images
**Location**: Services/Docker-Registry.md

```bash
docker tag myimage docker.auto-nagel-cloud.de/ncg/myimage:tag
docker push docker.auto-nagel-cloud.de/ncg/myimage:tag
docker pull docker.auto-nagel-cloud.de/ncg/myimage:tag
```

## Debugging
**Location**: Troubleshooting/Network-Issues.md

```bash
docker ps                          # List containers
docker logs <container>            # View logs
docker exec -it <container> bash   # Enter container
docker inspect <container>         # View configuration
```

## Related Documentation
- [Docker Registry](NCG/Ops/Services/Docker-Registry.md)
- [Quick Start for Developers](NCG/Ops/Guides/Quick-Start-Developers.md)
```

### Example 2: Find All Production IPs

**User**: "Show me all production server IPs"

**Steps**:
1. Run regex search:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --regex "10\\.1\\.0\\.\\d+"
```

2. Results show IPs across multiple files

3. Consolidate and format:

```markdown
📍 Production Network (10.1.0.0/16)

| IP | Server | Purpose | Documentation |
|----|--------|---------|---------------|
| 10.1.0.5 | prod-web-01 | Frontend | Infrastructure/Hetzner-Infrastructure.md |
| 10.1.0.7 | 03-docker-registry | Docker Registry | Services/Docker-Registry.md |
| 10.1.0.8 | prod-database | MongoDB, MariaDB, PostgreSQL | Services/Databases.md |
| 10.1.0.10 | prod-app-server | Backend services | Environments/Production |

Complete inventory: NCG/Ops/Infrastructure/Hetzner-Infrastructure.md
Network map: /Users/dh/.claude/skills/documentation/Context/ServerMap.md
```

### Example 3: Find Certificate Configuration

**User**: "Where is certificate configuration documented?"

**Steps**:
1. Search for certificates:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts "certificate"
```

2. Results in Security/Certificates.md

3. Provide summary:

```markdown
📄 Certificate Configuration

**Main Documentation**: Security/Certificates.md

## Certificate Types
- **SSL/TLS**: Web server certificates
- **Docker Registry**: Internal registry certificates
- **VPN**: pfSense certificates

## Configuration Locations
- **Dev**: Certificates on individual services
- **Prod**: Centralized certificate management

## Key Operations
1. Generate CSR
2. Certificate signing
3. Installation on services
4. Renewal procedures

**Full Details**: NCG/Ops/Security/Certificates.md
**Related**: Security/Secrets-Management.md (private keys storage)
```

### Example 4: Find GitLab Pipeline Configuration

**User**: "How are GitLab pipelines configured?"

**Steps**:
1. Search GitLab:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --file "GitLab-CI-CD.md" "pipeline"
```

2. Read Services/GitLab-CI-CD.md

3. Extract and format:

```markdown
⚙️ GitLab CI/CD Configuration

**Location**: Services/GitLab-CI-CD.md

## Pipeline Structure
- Build stage: Compile and test
- Push stage: Push images to registry
- Deploy stage: Deploy to dev/prod

## Deployment Targets
- **Development**: 10.0.0.10 (automatic on main branch)
- **Production**: 10.1.0.10 (manual trigger)

## Configuration File
Location: Repository root `.gitlab-ci.yml`

## Runners
- Shared runners enabled
- Docker-based executors

**Full Details**: NCG/Ops/Services/GitLab-CI-CD.md
**Related**: Services/Docker-Registry.md (image storage)
```

---

## Search Patterns

### Common Keywords

```
# Infrastructure
"server", "IP", "network", "hetzner", "cloud"

# Services
"docker", "mongodb", "mariadb", "postgresql", "gitlab", "rabbitmq"

# Security
"certificate", "password", "secret", "credential", "authentication"

# Operations
"deployment", "backup", "restore", "migration", "update"

# Troubleshooting
"error", "failed", "debug", "logs", "restart"
```

### Regex Patterns

```bash
# IP addresses
SearchVault.ts --regex "\d+\.\d+\.\d+\.\d+"

# Development IPs (10.0.0.x)
SearchVault.ts --regex "10\.0\.0\.\d+"

# Production IPs (10.1.0.x)
SearchVault.ts --regex "10\.1\.0\.\d+"

# Ports
SearchVault.ts --regex ":\d{4,5}"

# Docker images
SearchVault.ts --regex "docker\.auto-nagel-cloud\.de/\w+/\w+"

# GitLab CI variables
SearchVault.ts --regex "GITLAB_CI:\w+"

# Email addresses
SearchVault.ts --regex "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

# Dates (YYYY-MM-DD)
SearchVault.ts --regex "\d{4}-\d{2}-\d{2}"
```

---

## Tips for Effective Searching

1. **Start broad, then narrow**: Begin with general term, then add specifics
2. **Use file-specific search**: If you know the topic area, search specific files
3. **Leverage regex**: For structured data (IPs, versions, dates)
4. **Check ServerMap first**: For quick infrastructure lookups
5. **Use detailed mode**: When you need context around matches
6. **Combine searches**: Search multiple related terms to build complete picture

---

## Search Result Interpretation

**When results show**:
- **Multiple files**: Topic is covered across documentation, synthesize the information
- **No results**: Term might be phrased differently, try synonyms or related terms
- **Too many results**: Refine with more specific search term or use --file flag
- **Outdated information**: Check "Last Updated" timestamp in files

---

## Related Tools

- **SearchVault.ts**: Full-text and regex search
- **ServerMap.md**: Quick infrastructure reference
- **VaultStructure.md**: Documentation organization guide
- **ExplainConcept workflow**: Deep-dive into specific topics
