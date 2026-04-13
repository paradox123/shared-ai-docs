# Generate Runbook Workflow

**Create step-by-step operational procedures from infrastructure documentation**

---

## Purpose

Extract and formalize procedures into reusable runbooks for common operations like deployments, backups, troubleshooting, and maintenance tasks.

---

## When to Use

- User asks "create a runbook for X"
- User asks "how do I do X step-by-step"
- Documenting a new procedure
- Formalizing tribal knowledge
- Creating disaster recovery procedures

---

## Procedure

### Step 1: Identify Procedure Type

**Common runbook categories**:
- **Deployment**: Application releases, rollbacks
- **Backup/Restore**: Database backups, disaster recovery
- **Maintenance**: Updates, certificate renewal, log rotation
- **Troubleshooting**: Service restart, debugging steps
- **Provisioning**: New server setup, service installation

### Step 2: Gather Information

**Search existing documentation for procedure details**:

```bash
# Use SearchVault to find related information
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts "[procedure topic]"
```

**Check these locations**:
- `Services/` - Service-specific procedures
- `Guides/` - Existing procedures and quick-starts
- `Troubleshooting/` - Problem-resolution steps
- `Security/` - Security-related operations

### Step 3: Structure the Runbook

**Use this template**:

```markdown
# [Procedure Name] Runbook

**Purpose**: [Brief description of what this accomplishes]
**Frequency**: [Daily/Weekly/Monthly/On-Demand/Emergency]
**Duration**: [Estimated time]
**Risk Level**: [Low/Medium/High]

---

## Prerequisites

- [ ] Access to [servers/services]
- [ ] Credentials: GITLAB_CI: [variable name]
- [ ] Tools: [Required software]
- [ ] Permissions: [Required access level]

---

## Pre-Checks

1. [Verification step before starting]
2. [Health check to perform]
3. [Backup or snapshot recommendation]

---

## Procedure

### Step 1: [First Major Step]

**Action**: [What to do]

```bash
[Commands to run]
```

**Expected Output**: [What success looks like]

**If it fails**: [Troubleshooting steps or rollback]

---

### Step 2: [Second Major Step]

[Continue pattern...]

---

## Verification

**Check that the procedure succeeded**:

1. [Health check command]
2. [Log check]
3. [Service status check]

```bash
[Verification commands]
```

---

## Rollback

**If something goes wrong**:

1. [Step to undo changes]
2. [Restore from backup]
3. [Restart services]

---

## Post-Procedure

- [ ] Document completion in [changelog location]
- [ ] Verify monitoring alerts
- [ ] Notify team if required
- [ ] Update this runbook if steps changed

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| [Common problem 1] | [Fix] |
| [Common problem 2] | [Fix] |

---

## Related Documentation

- [Link to related docs]
- [Link to service documentation]

**Last Updated**: YYYY-MM-DD
```

### Step 4: Populate with Specific Details

**Extract from existing documentation**:
- Commands from various service docs
- IP addresses from ServerMap.md
- Credentials references from Secrets-Management.md
- Configuration from relevant service files

**Add operational details**:
- Actual command syntax with correct IPs
- Expected outputs
- Common failure modes
- Timing expectations

### Step 5: Add Safety Measures

**Critical for production procedures**:
- Pre-checks to verify system state
- Rollback instructions
- Impact assessment
- Downtime warnings

### Step 6: Save Runbook

**Determine location**:
- General procedures → `Guides/Runbooks/`
- Service-specific → `Services/[service]/Runbooks/`
- Emergency procedures → `Guides/Runbooks/Emergency/`

**File naming**: `[Category]-[Action]-Runbook.md`

Examples:
- `Database-Backup-Runbook.md`
- `Backend-Deployment-Runbook.md`
- `Certificate-Renewal-Runbook.md`

### Step 7: Link from Main Documentation

**Update relevant documentation**:
- Add link to runbook from service documentation
- Update README.md if it's a commonly used procedure
- Cross-reference in troubleshooting docs

---

## Examples

### Example 1: Backend Deployment Runbook

**User**: "Create a runbook for deploying the backend to production"

**Runbook Content**:

```markdown
# Backend Deployment to Production Runbook

**Purpose**: Deploy NCG backend services to production environment
**Frequency**: On-Demand (typically weekly)
**Duration**: 15-20 minutes
**Risk Level**: Medium

---

## Prerequisites

- [ ] Access to prod-app-server (10.1.0.10)
- [ ] Access to GitLab CI/CD
- [ ] Credentials: GITLAB_CI: PROD_DEPLOY_TOKEN
- [ ] Docker images built and pushed to registry
- [ ] Migrations tested in dev environment

---

## Pre-Checks

1. Verify dev deployment succeeded
```bash
curl http://10.0.0.10:9000/health
```

2. Check prod is currently healthy
```bash
ssh root@10.1.0.10
docker ps
curl localhost:9000/health
```

3. Backup database
```bash
ssh root@10.1.0.8
mongodump --out=/backups/pre-deploy-$(date +%Y%m%d)
```

---

## Procedure

### Step 1: Trigger GitLab Pipeline

**Action**: Deploy via GitLab CI/CD

1. Navigate to: https://gitlab.auto-nagel-cloud.de/ncg/backend
2. Go to CI/CD → Pipelines
3. Click "Run Pipeline"
4. Select branch: `main`
5. Add variable: `ENVIRONMENT=prod`
6. Click "Run Pipeline"

**Expected Output**: Pipeline starts, shows "Deploying to production"

**If it fails**: Check pipeline logs, verify registry access

---

### Step 2: Monitor Deployment

**Action**: Watch containers update on prod server

```bash
ssh root@10.1.0.10
watch -n 2 'docker ps'
```

**Expected Output**: 
- Old containers stop gracefully
- New containers start with latest tags
- All show "Up" status within 2 minutes

---

### Step 3: Run Database Migrations

**Action**: Apply schema changes (if any)

```bash
# GitLab pipeline handles this automatically
# Verify in pipeline logs: "Migrations completed"
```

---

## Verification

**Check that deployment succeeded**:

1. Health check
```bash
curl http://10.1.0.10:9000/health
# Expected: HTTP 200, {"status": "healthy"}
```

2. Check logs
```bash
ssh root@10.1.0.10
docker logs ncg-apigateway --tail 50
docker logs ncg-store --tail 50
docker logs ncg-security --tail 50
# Expected: No errors, services started successfully
```

3. Verify database connectivity
```bash
curl http://10.1.0.10:9000/api/stores | jq
# Expected: Returns store data
```

4. Check service versions
```bash
docker inspect ncg-apigateway | grep -i version
```

---

## Rollback

**If deployment fails**:

1. Revert to previous images
```bash
ssh root@10.1.0.10
docker-compose pull --tag v2.0.8  # Previous version
docker-compose up -d
```

2. Restore database (if migrations ran)
```bash
ssh root@10.1.0.8
mongorestore /backups/pre-deploy-YYYYMMDD
```

3. Verify rollback succeeded
```bash
curl http://10.1.0.10:9000/health
```

---

## Post-Procedure

- [ ] Document deployment in Services/GitLab-CI-CD.md
- [ ] Monitor for 15 minutes for errors
- [ ] Notify team in Slack/Teams
- [ ] Update version in documentation

```bash
# Document the deployment
echo "## $(date +%Y-%m-%d) - Backend Deployment v2.1.0" >> /path/to/changelog.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container fails to start | Check logs: `docker logs [container]`, verify registry access |
| Database connection fails | Verify MongoDB is running on 10.1.0.8:27017 |
| Health check returns 503 | Wait 30 seconds for services to fully start |
| Registry authentication fails | Check GITLAB_CI: PROD_DEPLOY_TOKEN is valid |

---

## Related Documentation

- [GitLab CI/CD](../Services/GitLab-CI-CD.md)
- [Docker Registry](../Services/Docker-Registry.md)
- [Troubleshooting Network Issues](../Troubleshooting/Network-Issues.md)

**Last Updated**: 2026-01-03
```

**Save to**: `NCG/Ops/Guides/Runbooks/Backend-Deployment-Runbook.md`

### Example 2: Database Backup Runbook

**User**: "Create a runbook for backing up MongoDB"

**Runbook outline**:
- Prerequisites: SSH access to database servers
- Pre-checks: Verify disk space, check MongoDB status
- Procedure:
  1. Create backup directory
  2. Run mongodump
  3. Compress backup
  4. Transfer to backup storage
  5. Verify backup integrity
- Verification: Test restore on dev
- Rollback: N/A (backup operation)
- Post-procedure: Update backup log
- Troubleshooting: Out of disk space, connection timeout

**Save to**: `NCG/Ops/Services/Databases/MongoDB-Backup-Runbook.md`

### Example 3: Certificate Renewal Runbook

**User**: "Create runbook for renewing SSL certificates"

**Runbook outline**:
- Prerequisites: Access to cert authority, domain DNS control
- Pre-checks: Check current cert expiration, verify DNS
- Procedure:
  1. Generate CSR
  2. Submit to certificate authority
  3. Update DNS for validation
  4. Download new certificate
  5. Install on servers
  6. Update Docker secrets
  7. Restart affected services
- Verification: Check cert validity, test HTTPS
- Rollback: Keep old cert until verified
- Post-procedure: Document in Security/Certificates.md
- Troubleshooting: DNS validation fails, cert mismatch

**Save to**: `NCG/Ops/Security/Certificate-Renewal-Runbook.md`

---

## Runbook Categories

```
Guides/Runbooks/
├── Deployment/
│   ├── Backend-Deployment-Runbook.md
│   ├── Frontend-Deployment-Runbook.md
│   └── Rollback-Runbook.md
├── Database/
│   ├── MongoDB-Backup-Runbook.md
│   ├── MongoDB-Restore-Runbook.md
│   └── Database-Migration-Runbook.md
├── Maintenance/
│   ├── System-Updates-Runbook.md
│   ├── Certificate-Renewal-Runbook.md
│   └── Log-Rotation-Runbook.md
├── Emergency/
│   ├── Service-Recovery-Runbook.md
│   ├── Disaster-Recovery-Runbook.md
│   └── Security-Incident-Runbook.md
└── Provisioning/
    ├── New-Server-Setup-Runbook.md
    └── Service-Installation-Runbook.md
```

---

## Best Practices

1. **Use checklists**: Make procedures actionable with checkboxes
2. **Include commands**: Provide exact commands, not just descriptions
3. **Show expected outputs**: Help operators verify each step
4. **Plan for failure**: Always include rollback procedures
5. **Keep updated**: Review and update after each execution
6. **Link documentation**: Reference related docs for context
7. **Risk awareness**: Clearly mark high-risk procedures
8. **Time estimates**: Help with planning and scheduling

---

## Tips

- **Start simple**: Basic runbooks are better than no runbooks
- **Iterate**: Improve runbooks each time they're used
- **Test**: Verify procedures in dev before documenting for prod
- **Automate**: If a runbook is complex, consider automation
- **Review**: Have someone else review critical runbooks
