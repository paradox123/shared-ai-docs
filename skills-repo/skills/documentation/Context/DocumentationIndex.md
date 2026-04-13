# Documentation Index

**Quick reference index to all NCG operations documentation**

**Last Updated**: 2026-01-03

---

## 📚 Documentation Overview

This index provides a quick reference to all documentation files with brief descriptions of their content.

---

## Core Documentation

### README.md
**Purpose**: Navigation hub for all NCG operations documentation
**Contains**: 
- Documentation structure overview
- Quick links to all major sections
- Getting started guides

**When to use**: Starting point for any documentation search

---

## Infrastructure

### Infrastructure/Hetzner-Infrastructure.md
**Purpose**: Complete infrastructure inventory and architecture
**Contains**:
- All 13 servers with IPs, specs, purposes
- Network topology (10.0.0.0/16 dev, 10.1.0.0/16 prod)
- Hardware specifications (CX11, CX21, CX23, CX31)
- Network architecture diagrams

**When to use**: 
- Looking up server IPs
- Understanding network design
- Planning capacity changes
- Onboarding new team members

**Key sections**:
- Development servers (10.0.0.x)
- Production servers (10.1.0.x)
- Network isolation
- Server provisioning

---

## Environments

### Environments/Development/Dev-Environment.md
**Purpose**: Development environment configuration and setup
**Contains**:
- Dev server details (10.0.0.7, 10.0.0.8, 10.0.0.10, 10.0.0.11)
- Service endpoints and ports
- Development workflows
- Local development setup

**When to use**:
- Setting up development environment
- Debugging dev issues
- Finding dev service endpoints
- Understanding dev deployment process

**Key sections**:
- Backend services (API Gateway port 9000)
- Database connections
- Docker registry access
- GitLab development instance

---

## Security

### Security/Secrets-Management.md
**Purpose**: Credential storage and secret management practices
**Contains**:
- GitLab CI/CD variables reference
- Secret naming conventions
- Credential rotation procedures
- Security best practices

**When to use**:
- Looking for credentials
- Rotating passwords
- Adding new secrets
- Understanding secret management

**Key sections**:
- GitLab CI variables list
- Database passwords
- Docker registry credentials
- API keys and tokens

### Security/Certificates.md
**Purpose**: SSL/TLS certificate management
**Contains**:
- Certificate inventory
- Certificate renewal procedures
- Certificate installation guides
- Certificate troubleshooting

**When to use**:
- Renewing certificates
- Installing new certificates
- Debugging SSL/TLS issues
- Understanding certificate architecture

**Key sections**:
- Certificate locations
- Expiration tracking
- Renewal process
- Docker secrets integration

---

## Services

### Services/Docker-Registry.md
**Purpose**: Private Docker registry configuration and usage
**Contains**:
- Registry endpoints (10.0.0.11:5000 dev, 10.1.0.7:5000 prod)
- Authentication procedures
- Image push/pull workflows
- Registry maintenance

**When to use**:
- Pushing images to registry
- Debugging registry access
- Understanding registry architecture
- Registry maintenance tasks

**Key sections**:
- Registry access (docker.auto-nagel-cloud.de)
- Image naming conventions
- Authentication methods
- Storage management

### Services/Databases.md
**Purpose**: Database server configuration and management
**Contains**:
- MongoDB, MariaDB, PostgreSQL configurations
- Connection strings and ports
- Database backup procedures
- Performance tuning

**When to use**:
- Connecting to databases
- Database troubleshooting
- Backup/restore operations
- Schema migrations

**Key sections**:
- Connection strings (27017, 3306, 5432)
- Authentication
- Backup procedures
- Replication setup

### Services/GitLab-CI-CD.md
**Purpose**: GitLab CI/CD pipeline configuration
**Contains**:
- Pipeline structure and stages
- Deployment automation
- Runner configuration
- CI/CD best practices

**When to use**:
- Understanding deployments
- Modifying pipelines
- Debugging CI/CD issues
- Adding new deployment targets

**Key sections**:
- Pipeline stages (build, push, deploy)
- GitLab runners
- Automated deployments to 10.0.0.10 (dev) and 10.1.0.10 (prod)
- Environment variables

### Services/RabbitMQ.md
**Purpose**: RabbitMQ message queue configuration
**Contains**:
- RabbitMQ server details
- Queue configurations
- Management interface access
- Troubleshooting

**When to use**:
- Message queue operations
- Debugging async communication
- Monitoring message flow
- Queue management

### Services/Frontend-Services.md
**Purpose**: Frontend deployment and configuration
**Contains**:
- Frontend server details (10.1.0.5)
- Deployment procedures
- Static asset serving
- Frontend troubleshooting

**When to use**:
- Frontend deployments
- Web server configuration
- Performance optimization
- Frontend debugging

---

## Troubleshooting

### Troubleshooting/Network-Issues.md
**Purpose**: Network problem diagnosis and resolution
**Contains**:
- Common network issues
- Diagnostic commands
- Resolution procedures
- Container networking

**When to use**:
- Services can't communicate
- Connection timeouts
- DNS issues
- Container network problems

**Key sections**:
- Connectivity testing
- Docker network debugging
- pfSense routing issues
- Common error patterns

---

## Guides

### Guides/Quick-Start-Developers.md
**Purpose**: Onboarding guide for developers
**Contains**:
- Development environment setup
- Access requirements
- Common workflows
- Development best practices

**When to use**:
- Onboarding new developers
- Setting up development machine
- Understanding development workflow
- Quick reference for common tasks

### Guides/Quick-Start-DevOps.md
**Purpose**: Onboarding guide for DevOps/operations team
**Contains**:
- Infrastructure access
- Deployment procedures
- Monitoring and alerting
- Operational responsibilities

**When to use**:
- Onboarding DevOps engineers
- Understanding operational procedures
- Quick reference for deployments
- Incident response guide

### Guides/Routing-Setup-Guide.md
**Purpose**: Network routing and pfSense configuration
**Contains**:
- pfSense setup procedures
- Routing rules
- VPN configuration
- Network troubleshooting

**When to use**:
- Setting up routing
- Configuring VPN access
- Network architecture changes
- pfSense administration

### Guides/System-Updates.md
**Purpose**: Server and system update procedures
**Contains**:
- OS update procedures
- Service update workflows
- Update scheduling
- Rollback procedures

**When to use**:
- Planning system updates
- Applying security patches
- Updating Docker
- Service version upgrades

---

## ARCHIVE

### ARCHIVE/
**Purpose**: Original documentation files before restructuring
**Contains**: 21 original files backed up before major restructure
**Status**: Read-only, preserved for reference

**When to use**: 
- Historical reference
- Recovering information not transferred to new docs
- Comparing old vs new structure

**Note**: Do not edit ARCHIVE files. All updates should go to current documentation.

---

## File Organization

```
NCG/Ops/
├── README.md                          # Navigation hub
├── Infrastructure/
│   └── Hetzner-Infrastructure.md      # Server inventory
├── Environments/
│   └── Development/
│       └── Dev-Environment.md         # Dev configuration
├── Security/
│   ├── Secrets-Management.md          # Credentials
│   └── Certificates.md                # SSL/TLS certs
├── Services/
│   ├── Docker-Registry.md             # Image registry
│   ├── Databases.md                   # MongoDB/MariaDB/PostgreSQL
│   ├── GitLab-CI-CD.md                # CI/CD pipelines
│   ├── RabbitMQ.md                    # Message queue
│   └── Frontend-Services.md           # Web frontend
├── Troubleshooting/
│   └── Network-Issues.md              # Network diagnostics
├── Guides/
│   ├── Quick-Start-Developers.md      # Dev onboarding
│   ├── Quick-Start-DevOps.md          # Ops onboarding
│   ├── Routing-Setup-Guide.md         # Network routing
│   └── System-Updates.md              # Update procedures
└── ARCHIVE/                           # Original files (backup)
    └── [21 original .md files]
```

---

## Documentation Standards

### File Naming
- Use hyphens for word separation
- TitleCase for main words
- Descriptive names (e.g., `Docker-Registry.md` not `registry.md`)

### Content Structure
All documentation files follow this structure:
1. Title and metadata (Last Updated)
2. Table of Contents
3. Overview section
4. Detailed sections
5. Examples
6. Troubleshooting
7. Related documentation links

### Cross-References
- Use relative markdown links: `[Link Text](../path/to/file.md)`
- Reference specific sections: `[Section](file.md#section-name)`
- Always provide context for links

### Security Policy
- **Never hardcode secrets** in documentation
- Use placeholders: `GITLAB_CI:[VARIABLE_NAME]` or `VAULT:[path]`
- Reference Secrets-Management.md for credential locations

---

## Change Documentation

### When to Document Changes
- ✅ Server provisioning/deprovisioning
- ✅ Configuration changes
- ✅ Deployments (major versions)
- ✅ Credential rotations
- ✅ Network topology changes
- ✅ New procedures or runbooks

### Where to Document
- Infrastructure changes → Infrastructure/Hetzner-Infrastructure.md
- Service changes → Respective Services/*.md file
- Security changes → Security/*.md files
- New procedures → Create in Guides/

### Changelog Format
```markdown
## YYYY-MM-DD - [Change Title]
- **Change**: [What was changed]
- **Environment**: Dev / Prod
- **Impact**: [What this affects]
- **Details**: [Additional information]
```

---

## Quick Links by Topic

### Need to find...
- **Server IP**: Infrastructure/Hetzner-Infrastructure.md or Context/ServerMap.md
- **Database connection**: Services/Databases.md
- **Docker registry access**: Services/Docker-Registry.md
- **Credential/password**: Security/Secrets-Management.md
- **Deploy procedure**: Services/GitLab-CI-CD.md
- **Network issue**: Troubleshooting/Network-Issues.md
- **Getting started**: Guides/Quick-Start-*.md

---

**Note**: This index is maintained manually. Update when adding new documentation files or significantly changing existing ones.
