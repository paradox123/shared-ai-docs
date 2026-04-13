# Query Infrastructure Workflow

**Quickly find server details, IPs, configurations, and service information**

---

## Purpose

Retrieve specific infrastructure information from NCG documentation without manual searching.

---

## When to Use

- User asks "what is the IP of X"
- User asks "where is X service running"
- User asks "show me X server details"
- User needs quick infrastructure lookup

---

## Procedure

### Step 1: Identify Query Type

**Determine what information is needed**:
- Server IP address
- Service endpoint
- Database connection string
- Credential location
- Service port
- Network information

### Step 2: Check ServerMap.md First

**For common queries, use quick reference**:
```
Read: /Users/dh/.claude/skills/documentation/Context/ServerMap.md
```

**Quick lookups**:
- Dev app server: 10.0.0.10
- Dev database: 10.0.0.7
- Prod app server: 10.1.0.10
- Prod database: 10.1.0.8

### Step 3: Search Detailed Documentation

**If ServerMap.md doesn't have details, search specific files**:

| Information Needed | File to Check |
|-------------------|---------------|
| Server inventory, specs | `NCG/Ops/Infrastructure/Hetzner-Infrastructure.md` |
| Dev environment config | `NCG/Ops/Environments/Development/Dev-Environment.md` |
| Database details | `NCG/Ops/Services/Databases.md` |
| Docker registry | `NCG/Ops/Services/Docker-Registry.md` |
| GitLab CI/CD | `NCG/Ops/Services/GitLab-CI-CD.md` |
| Network topology | `NCG/Ops/Infrastructure/Hetzner-Infrastructure.md` |
| Credentials | `NCG/Ops/Security/Secrets-Management.md` |

### Step 4: Format Response

**Provide concise, actionable information**:

```markdown
📍 SERVER: dev-database
🔹 IP: 10.0.0.7
🔹 Services: MongoDB (27017), MariaDB (3306), PostgreSQL (5432)
🔹 SSH: ssh root@10.0.0.7
🔹 Credentials: See Secrets-Management.md

For full details: NCG/Ops/Services/Databases.md
```

### Step 5: Suggest Related Information

**Offer additional context when relevant**:
- Related services on same server
- Connection examples
- Documentation links
- Common operations

---

## Examples

### Example 1: Find Database IP

**User**: "What's the IP of the production database?"

**Response**:
```
📍 SERVER: prod-database
🔹 IP: 10.1.0.8
🔹 Services: MongoDB (27017), MariaDB (3306), PostgreSQL (5432)

Connection strings:
- MongoDB: mongodb://dba:<GITLAB_CI:PROD_MONGODB_PASSWORD>@10.1.0.8:27017
- MariaDB: mysql -h 10.1.0.8 -u root -p
- PostgreSQL: psql -h 10.1.0.8 -U postgres

Documentation: NCG/Ops/Services/Databases.md
```

### Example 2: Find Registry Location

**User**: "Where is the Docker registry?"

**Response**:
```
📍 SERVICE: Docker Registry (03-docker-registry)

Development:
🔹 IP: 10.0.0.11:5000 (internal only, NO public IP)
🔹 URL: docker.auto-nagel-cloud.de

Production:
🔹 IP: 10.1.0.7:5000 (internal only, NO public IP)

Authentication:
- Username: ncg
- Password: GITLAB_CI: REGISTRY_PASSWORD

Usage:
docker login docker.auto-nagel-cloud.de -u ncg
docker push docker.auto-nagel-cloud.de/ncg/service:tag

Documentation: NCG/Ops/Services/Docker-Registry.md
```

### Example 3: Find API Gateway Port

**User**: "What port is the API gateway on?"

**Response**:
```
📍 SERVICE: API Gateway (Ocelot)

Development:
🔹 http://10.0.0.10:9000

Production:
🔹 http://10.1.0.10:9000

The gateway is the only exposed port (9000) from the backend services.
All other services (store, security) communicate internally via Docker network.

Documentation: NCG/Ops/Environments/Development/Dev-Environment.md
```

---

## Tool Usage

**Use SearchVault.ts for complex queries**:
```bash
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts "MongoDB authentication"
```

**Returns**: File paths and relevant sections containing the search term.

---

## Tips

- **Be precise**: Return exact IPs and ports, not ranges
- **Include credentials reference**: Always point to Secrets-Management.md, never expose actual secrets
- **Provide context**: Mention related services or configuration
- **Link to docs**: Reference full documentation for details
- **Use emojis**: Makes information scannable

---

## Common Queries Reference

```
"dev app server" → 10.0.0.10
"dev database" → 10.0.0.7
"dev gitlab" → 10.0.0.8
"dev registry" → 10.0.0.11 (no public IP)

"prod app server" → 10.1.0.10
"prod database" → 10.1.0.8
"prod registry" → 10.1.0.7 (no public IP)

"api gateway" → Port 9000 (both dev and prod)
"mongodb port" → 27017
"mariadb port" → 3306
"postgresql port" → 5432
"docker registry" → Port 5000 (internal)
```
