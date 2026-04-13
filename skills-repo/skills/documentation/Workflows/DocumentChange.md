# Document Change Workflow

**Record infrastructure changes in the Obsidian vault**

---

## Purpose

Maintain accurate documentation by recording all infrastructure changes, deployments, and configuration updates in the appropriate documentation files.

---

## When to Use

- After deploying code to dev/prod
- After changing server configuration
- After updating credentials
- After provisioning new servers
- After network topology changes
- After database schema migrations

---

## Procedure

### Step 1: Identify Change Type

**Categorize the change to determine documentation location**:

| Change Type | Documentation File |
|-------------|-------------------|
| Deployment (backend) | Create changelog entry, update relevant service doc |
| Server provisioning | `Infrastructure/Hetzner-Infrastructure.md` |
| Service configuration | Relevant file in `Services/` |
| Credential rotation | `Security/Secrets-Management.md` |
| Certificate renewal | `Security/Certificates.md` |
| Network change | `Infrastructure/Hetzner-Infrastructure.md` |
| New procedure | Create in `Guides/` or `Troubleshooting/` |

### Step 2: Read Current Documentation

**Before updating, read the current state**:
```bash
# Read the file that needs updating
cat /Users/dh/Documents/DanielsVault/NCG/Ops/[relevant-file].md
```

**Understand**:
- Current structure
- Where to add information
- What sections exist

### Step 3: Prepare Update

**Format the change appropriately**:

**For changelog entries**:
```markdown
## YYYY-MM-DD - [Change Title]
- **Change**: [What was changed]
- **Environment**: Dev / Prod
- **Deployed by**: [Person/System]
- **GitLab Pipeline**: #[pipeline-id]
- **Details**: [Additional information]
```

**For configuration updates**:
```markdown
### [Section to Update]

[Existing content...]

**Updated YYYY-MM-DD**: [New information or changed configuration]
```

**For new servers**:
```markdown
| server-name | IP | Type | Purpose |
|-------------|-----|------|---------|
| new-server | 10.x.x.x | CX23 | [Purpose] |
```

### Step 4: Apply Update

**Use the appropriate method**:

**Option A: Small inline update**
```bash
# Add entry to existing file
echo "\n## 2026-01-03 - Backend Deployment v2.1.0" >> /path/to/file.md
echo "- Deployed to production (10.1.0.10)" >> /path/to/file.md
```

**Option B: Edit existing section**
Use `replace_string_in_file` to update specific sections while preserving structure.

**Option C: Create new file**
For new runbooks or procedures, create complete new markdown file.

### Step 5: Update "Last Updated" Timestamp

**Always update the timestamp at file header**:
```markdown
**Last Updated**: 2026-01-03
```

### Step 6: Verify Changes

**Check the update**:
```bash
# View the changed file
tail -20 /Users/dh/Documents/DanielsVault/NCG/Ops/[updated-file].md

# Or read specific section
grep -A 10 "Last Updated" [file].md
```

### Step 7: Commit to Git (Optional)

**If vault is version controlled**:
```bash
cd /Users/dh/Documents/DanielsVault
git add NCG/Ops/[updated-file].md
git commit -m "docs: [brief description of change]"
```

---

## Examples

### Example 1: Document Backend Deployment

**User**: "Document deployment of backend v2.1.0 to production"

**Steps**:
1. Identify: This is a deployment change
2. Create changelog entry in a deployment log or at top of relevant service doc
3. Update:
```markdown
## 2026-01-03 - Backend Deployment v2.1.0

**Environment**: Production (10.1.0.10)

**Services Updated**:
- ncg-apigateway:latest → v2.1.0
- ncg-store:latest → v2.1.0
- ncg-security:latest → v2.1.0

**Deployment Method**: GitLab Pipeline #1234

**Changes**:
- Added new authentication endpoints
- Updated MongoDB connection pooling
- Performance improvements

**Verification**:
- Health check: ✅ All services responding
- Logs: No errors in first 10 minutes
- Database: Migrations applied successfully

**Rollback Plan**: Previous images tagged as v2.0.8 available in registry
```

**Location**: Could add to `Services/GitLab-CI-CD.md` or create `DEPLOYMENT-LOG.md`

### Example 2: Document New Server

**User**: "Document new server prod-monitoring at 10.1.0.12"

**Steps**:
1. Read `Infrastructure/Hetzner-Infrastructure.md`
2. Add to production servers table:
```markdown
| prod-monitoring | 10.1.0.12 | CX21 | Prometheus, Grafana | Monitoring stack |
```
3. Update server count: "13 servers" → "14 servers"
4. Update "Last Updated" timestamp

### Example 3: Document Credential Rotation

**User**: "Document rotation of MongoDB dev password"

**Steps**:
1. Read `Security/Secrets-Management.md`
2. Update rotation history:
```markdown
### Database Credentials

#### MongoDB (Development)
- **Last Rotated**: 2026-01-03
- **Location**: GITLAB_CI: DEV_MONGODB_PASSWORD
- **Scope**: dev-database (10.0.0.7)
- **Updated By**: DevOps Team
- **Services Restarted**: All backend containers on 10.0.0.10
```
3. Update "Last Updated" at top of file

### Example 4: Document Configuration Change

**User**: "Document enabling RabbitMQ management plugin"

**Steps**:
1. Read `Services/RabbitMQ.md`
2. Add to configuration section:
```markdown
### Management Plugin

**Enabled**: 2026-01-03

```bash
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl restart rabbitmq-server
```

**Access**: http://10.0.0.X:15672
**Credentials**: GITLAB_CI: RABBITMQ_ADMIN_PASSWORD
```

---

## Documentation Templates

### Deployment Log Entry
```markdown
## YYYY-MM-DD - [Service] Deployment [Version]

**Environment**: Dev / Prod
**Server**: 10.x.x.x
**Docker Images**:
- service-name:tag

**Changes**:
- [List of changes]

**Database Migrations**: Yes / No
**Services Restarted**: [List]
**Verification**: [Health checks performed]
**Issues**: None / [List any issues]
```

### Configuration Change Entry
```markdown
### [Component] Configuration Update

**Updated**: YYYY-MM-DD

**Change**: [What was changed]

**Configuration**:
```[language]
[New configuration]
```

**Impact**: [What services/features this affects]
**Documentation**: [Link to relevant docs]
```

### New Server Entry
```markdown
| [server-name] | 10.x.x.x | [type] | [services] | [purpose] |
```

---

## Best Practices

1. **Be specific**: Include exact versions, IPs, timestamps
2. **Include verification**: Note that changes were tested
3. **Reference GitLab**: Include pipeline IDs for deployments
4. **Maintain structure**: Follow existing file formatting
5. **Update timestamps**: Always update "Last Updated" field
6. **Cross-reference**: Link to related documentation
7. **Security-first**: Never hardcode secrets in changes

---

## Related Files

- Vault structure: `Context/VaultStructure.md`
- Change locations: See "When to Use" table above
- Commit changes: Optional Git workflow
