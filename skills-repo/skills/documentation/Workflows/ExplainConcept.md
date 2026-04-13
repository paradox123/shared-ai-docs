# Explain Concept Workflow

**Provide detailed explanations of infrastructure concepts, architectures, and configurations**

---

## Purpose

Extract and explain complex concepts from documentation, helping users understand the "why" and "how" behind NCG infrastructure decisions and configurations.

---

## When to Use

- User asks "explain X"
- User asks "how does X work"
- User asks "why is X configured this way"
- User needs conceptual understanding (not just commands)
- Onboarding new team members

---

## Procedure

### Step 1: Identify the Concept

**Understand what needs explanation**:
- Infrastructure concept (networking, servers, architecture)
- Service configuration (Docker, databases, messaging)
- Security concept (certificates, secrets management, authentication)
- Operational workflow (deployments, backups, monitoring)

### Step 2: Gather Relevant Documentation

**Search for information about the concept**:

```bash
# Use SearchVault to find all mentions
bun run /Users/dh/.claude/skills/documentation/Tools/SearchVault.ts --detailed "[concept]"
```

**Check these key locations**:
- **Infrastructure**: Architecture and network topology
- **Services**: Service-specific details and configurations
- **Security**: Security implementations and rationale
- **Guides**: Operational procedures and best practices

### Step 3: Extract Key Information

**Identify essential elements**:
1. **What it is**: Definition and purpose
2. **Why it exists**: Business or technical rationale
3. **How it works**: Technical implementation details
4. **Where it's used**: Specific servers/services
5. **How to interact**: Commands, procedures, access methods
6. **Related concepts**: Dependencies and related systems

### Step 4: Structure the Explanation

**Use clear, hierarchical format**:

```markdown
# [Concept Name]

## Overview
[High-level definition and purpose]

## Why We Use It
[Business/technical rationale]

## How It Works
[Technical explanation]

## Architecture
[Diagrams, flow, components]

## Configuration
[Specific NCG implementation]

## Examples
[Practical usage examples]

## Related Concepts
[Links to related documentation]

## Common Questions
[FAQ-style clarifications]
```

### Step 5: Add Visual Aids

**Where helpful, include**:
- ASCII diagrams for architecture
- Flow charts for processes
- Tables for comparisons
- Command examples with outputs

### Step 6: Provide Context-Specific Details

**Make it actionable for NCG infrastructure**:
- Include actual IPs, servers, services from our environment
- Reference specific configuration files
- Show real commands with actual endpoints
- Link to relevant runbooks

---

## Examples

### Example 1: Explain Docker Registry

**User**: "Explain how our Docker registry works"

**Response**:

```markdown
# NCG Docker Registry

## Overview

The NCG Docker Registry is a private Docker image repository hosted on internal infrastructure. It stores all custom-built Docker images for NCG backend and frontend services.

**Purpose**: Centralized, secure storage of application images accessible only within the internal network.

---

## Why We Use It

**Benefits**:
1. **Security**: Images never leave internal network, no exposure to public registries
2. **Speed**: Fast pulls from local network (no internet bandwidth)
3. **Control**: We control image retention, access, and versioning
4. **Compliance**: Data sovereignty (images stored on our infrastructure)

**Alternative Rejected**: Docker Hub or GitLab Container Registry were considered but rejected due to security requirements for isolated infrastructure.

---

## How It Works

### Registry Service
- **Software**: Docker Registry v2
- **Protocol**: HTTP/HTTPS with basic authentication
- **Storage**: Local filesystem on registry servers

### Image Lifecycle
1. **Build**: GitLab CI builds image from Dockerfile
2. **Push**: CI pushes image to registry with authentication
3. **Pull**: Application servers pull images during deployment
4. **Tag**: Images tagged with version numbers for versioning

---

## Architecture

```
GitLab CI                Docker Registry           Application Servers
┌──────────────┐        ┌──────────────────┐      ┌─────────────────┐
│              │        │  10.0.0.11:5000  │      │   10.0.0.10     │
│ Build Image  │───────▶│ (Dev Registry)   │◀─────│  docker pull    │
│              │ push   │                  │ pull │                 │
└──────────────┘        └──────────────────┘      └─────────────────┘
                        
                        ┌──────────────────┐      ┌─────────────────┐
                        │  10.1.0.7:5000   │      │   10.1.0.10     │
                        │ (Prod Registry)  │◀─────│  docker pull    │
                        │                  │ pull │                 │
                        └──────────────────┘      └─────────────────┘
```

---

## Configuration

### Registry Servers

| Environment | Server | IP | Port | Public Access |
|-------------|--------|-----|------|---------------|
| Development | 03-docker-registry | 10.0.0.11 | 5000 | NO - Internal only |
| Production | 03-docker-registry | 10.1.0.7 | 5000 | NO - Internal only |

### DNS

**Domain**: `docker.auto-nagel-cloud.de`
- Points to pfSense firewall
- pfSense routes to appropriate registry based on source network

### Authentication

```bash
# Credentials stored in GitLab CI
REGISTRY_USER=ncg
REGISTRY_PASSWORD=<GITLAB_CI:REGISTRY_PASSWORD>

# Login command
docker login docker.auto-nagel-cloud.de -u ncg -p $REGISTRY_PASSWORD
```

### Storage Location

Images stored on registry server: `/var/lib/docker/registry/`

---

## Examples

### Push Image (from GitLab CI)

```bash
# Build image
docker build -t ncg-apigateway:v2.1.0 .

# Tag for registry
docker tag ncg-apigateway:v2.1.0 docker.auto-nagel-cloud.de/ncg/ncg-apigateway:v2.1.0
docker tag ncg-apigateway:v2.1.0 docker.auto-nagel-cloud.de/ncg/ncg-apigateway:latest

# Push to registry
docker push docker.auto-nagel-cloud.de/ncg/ncg-apigateway:v2.1.0
docker push docker.auto-nagel-cloud.de/ncg/ncg-apigateway:latest
```

### Pull Image (from app server)

```bash
# On development app server (10.0.0.10)
docker pull docker.auto-nagel-cloud.de/ncg/ncg-apigateway:latest

# Verify image
docker images | grep ncg-apigateway
```

### List Images in Registry

```bash
# SSH to registry server
ssh root@10.0.0.11

# View registry contents
ls -lh /var/lib/docker/registry/docker/registry/v2/repositories/ncg/
```

---

## Related Concepts

- **[Docker Compose](../Services/Docker-Registry.md)**: How images are deployed on app servers
- **[GitLab CI/CD](../Services/GitLab-CI-CD.md)**: Automated image building and pushing
- **[pfSense Routing](../Infrastructure/Hetzner-Infrastructure.md)**: Network routing to registry

---

## Common Questions

**Q: Why don't registry servers have public IPs?**
A: Security. Registry should only be accessible from within our networks. Public exposure would be a security risk.

**Q: How do dev and prod registries stay separate?**
A: They're completely separate servers on separate networks (10.0.0.x vs 10.1.0.x). DNS name is the same, but pfSense routes to the correct server based on source network.

**Q: What happens if registry goes down?**
A: Running containers continue to work. New deployments fail until registry is restored. Images are cached on app servers, so re-pulling existing versions will use cache.

**Q: How do we manage registry storage?**
A: Old images can be manually pruned. Currently no automatic cleanup. See [Docker Registry](../Services/Docker-Registry.md) for cleanup procedures.

---

**Documentation**: NCG/Ops/Services/Docker-Registry.md
**Last Updated**: 2026-01-03
```

### Example 2: Explain Network Architecture

**User**: "Explain our network architecture"

**Response**:

```markdown
# NCG Network Architecture

## Overview

NCG uses a dual-network architecture with completely separate development and production networks hosted on Hetzner Cloud.

**Key Principle**: Dev and prod are isolated; no direct communication between networks.

---

## Network Design

```
                        ┌─────────────────────┐
                        │   Hetzner Cloud     │
                        │   (eu-central)      │
                        └──────────┬──────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                                     │
        ┌───────▼──────────┐              ┌──────────▼────────┐
        │  Development     │              │  Production       │
        │  10.0.0.0/16     │              │  10.1.0.0/16      │
        │                  │              │                   │
        │  ┌────────────┐  │              │  ┌────────────┐   │
        │  │ App Server │  │              │  │ App Server │   │
        │  │ 10.0.0.10  │  │              │  │ 10.1.0.10  │   │
        │  └────────────┘  │              │  └────────────┘   │
        │                  │              │                   │
        │  ┌────────────┐  │              │  ┌────────────┐   │
        │  │ Database   │  │              │  │ Database   │   │
        │  │ 10.0.0.7   │  │              │  │ 10.1.0.8   │   │
        │  └────────────┘  │              │  └────────────┘   │
        │                  │              │                   │
        │  ┌────────────┐  │              │  ┌────────────┐   │
        │  │ Registry   │  │              │  │ Registry   │   │
        │  │ 10.0.0.11  │  │              │  │ 10.1.0.7   │   │
        │  └────────────┘  │              │  └────────────┘   │
        └──────────────────┘              └───────────────────┘
```

---

## Why This Design

**Isolation Benefits**:
1. **Safety**: Dev changes can't affect production
2. **Security**: Prod network has stricter access controls
3. **Testing**: Full environment replication for testing
4. **Compliance**: Production data isolation requirement

**Drawbacks Accepted**:
- Duplicate infrastructure (higher cost)
- Configuration must be synchronized manually
- Separate deployments required

---

## Network Segments

### Development Network (10.0.0.0/16)

**Purpose**: Application development and testing

**Key Servers**:
- 10.0.0.2: dev-gitlab-02
- 10.0.0.7: dev-database (MongoDB, MariaDB, PostgreSQL)
- 10.0.0.8: dev-gitlab-01 (GitLab server)
- 10.0.0.10: dev-app-server (Backend services)
- 10.0.0.11: Registry (Docker images)

**Access**: Developers have SSH access, less restrictive firewall

### Production Network (10.1.0.0/16)

**Purpose**: Live application serving customers

**Key Servers**:
- 10.1.0.5: prod-web-01 (Frontend)
- 10.1.0.7: Registry (Docker images)
- 10.1.0.8: prod-database (MongoDB, MariaDB, PostgreSQL)
- 10.1.0.10: prod-app-server (Backend services)

**Access**: Restricted, requires VPN and elevated permissions

---

## Routing and Connectivity

### Internet Access

Both networks can reach internet through Hetzner's network.

### Internal Communication

Servers within same network communicate directly via private IPs.

### Cross-Network Communication

**Not allowed** - Dev and prod cannot communicate. This is by design.

### External Access

**Development**:
- Developers access via VPN
- Some services exposed via pfSense (GitLab)

**Production**:
- Customer traffic through load balancer/reverse proxy
- Admin access via VPN only

---

## Configuration

**Full details**: NCG/Ops/Infrastructure/Hetzner-Infrastructure.md
**Routing setup**: NCG/Ops/Guides/Routing-Setup-Guide.md
**VPN access**: NCG/Ops/Ops/Setup-VPN.md

---

## Related Concepts

- **[Hetzner Cloud](../Infrastructure/Hetzner-Infrastructure.md)**: Server provisioning
- **[pfSense](../Ops/03_PfSense.md)**: Firewall and VPN
- **[Docker Networking](../Services/Docker-Registry.md)**: Container network isolation

```

---

## Explanation Categories

### Infrastructure Concepts
- Network architecture
- Server topology
- Load balancing
- High availability
- Disaster recovery

### Service Concepts
- Docker containerization
- Database replication
- Message queuing
- API gateway pattern
- Microservices architecture

### Security Concepts
- Certificate management
- Secrets management
- Authentication/authorization
- Network isolation
- VPN access

### Operational Concepts
- CI/CD pipelines
- Deployment strategies
- Backup procedures
- Monitoring and alerting
- Incident response

---

## Best Practices for Explanations

1. **Start simple**: Begin with high-level overview before diving into details
2. **Use analogies**: Relate complex concepts to familiar ones
3. **Show visuals**: ASCII diagrams help understanding
4. **Provide examples**: Real commands and outputs from our environment
5. **Explain trade-offs**: Discuss why we chose this approach
6. **Link liberally**: Reference related documentation
7. **Anticipate questions**: Include FAQ section

---

## Tips

- **Context matters**: Tailor explanation depth to user's role/experience
- **Be specific**: Use our actual IPs, servers, services (not generic examples)
- **Show the why**: Don't just explain how, explain why it's configured this way
- **Update regularly**: As infrastructure changes, update explanations
