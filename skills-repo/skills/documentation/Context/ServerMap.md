# NCG Server Map

**Quick reference for NCG infrastructure servers and services**

**Last Updated**: 2026-01-03
**Auto-generated**: This file can be regenerated from infrastructure documentation

---

## Development Network (10.0.0.0/16)

| Server | IP | Type | Services | Purpose |
|--------|-----|------|----------|----------|
| dev-gitlab-02 | 10.0.0.2 | CX21 | GitLab Runner | CI/CD runner |
| dev-database | 10.0.0.7 | CX23 | MongoDB, MariaDB, PostgreSQL | Database server |
| dev-gitlab-01 | 10.0.0.8 | CX31 | GitLab | Source control, CI/CD |
| dev-app-server | 10.0.0.10 | CX21 | Backend containers | Application services |
| 03-docker-registry | 10.0.0.11 | CX11 | Docker Registry | Private image repository |


---

## Production Network (10.1.0.0/16)

| Server | IP | Type | Services | Purpose |
|--------|-----|------|----------|----------|
| prod-web-01 | 10.1.0.5 | CX21 | Frontend | Web application |
| 03-docker-registry | 10.1.0.7 | CX11 | Docker Registry | Private image repository |
| prod-database | 10.1.0.8 | CX23 | MongoDB, MariaDB, PostgreSQL | Database server |
| prod-app-server | 10.1.0.10 | CX21 | Backend containers | Application services |


---

## Service Endpoints

### API Gateway (Ocelot)
- **Development**: http://10.0.0.10:9000
- **Production**: http://10.1.0.10:9000

### Databases

#### MongoDB
- **Development**: 10.0.0.7:27017
- **Production**: 10.1.0.8:27017
- **Connection**: `mongodb://dba:<GITLAB_CI:[ENV]_MONGODB_PASSWORD>@[IP]:27017`

#### MariaDB
- **Development**: 10.0.0.7:3306
- **Production**: 10.1.0.8:3306
- **Connection**: `mysql -h [IP] -u root -p`

#### PostgreSQL
- **Development**: 10.0.0.7:5432
- **Production**: 10.1.0.8:5432
- **Connection**: `psql -h [IP] -U postgres`

### Docker Registry
- **URL**: docker.auto-nagel-cloud.de
- **Development**: 10.0.0.11:5000 (internal only, NO public IP)
- **Production**: 10.1.0.7:5000 (internal only, NO public IP)
- **Authentication**: `docker login docker.auto-nagel-cloud.de -u ncg -p <GITLAB_CI:REGISTRY_PASSWORD>`

### GitLab
- **Development**: https://gitlab.auto-nagel-cloud.de
- **Server**: 10.0.0.8

---

## Backend Containers

### Development (10.0.0.10)
- **ncg-apigateway**: API Gateway (Ocelot) - Port 9000
- **ncg-store**: Store service
- **ncg-security**: Security/auth service

### Production (10.1.0.10)
- **ncg-apigateway**: API Gateway (Ocelot) - Port 9000
- **ncg-store**: Store service
- **ncg-security**: Security/auth service

---

## Credentials Location

**All passwords and secrets are stored in**:
- GitLab CI/CD Variables: https://gitlab.auto-nagel-cloud.de
- Documentation reference: `NCG/Ops/Security/Secrets-Management.md`

**Never hardcode credentials**. Always use:
- `GITLAB_CI:[VARIABLE_NAME]` for scripts
- `VAULT:[path]` for advanced secret management

---

## Quick SSH Access

```bash
# Development
ssh root@10.0.0.7   # Database server
ssh root@10.0.0.8   # GitLab server
ssh root@10.0.0.10  # App server
ssh root@10.0.0.11  # Docker registry

# Production (requires VPN)
ssh root@10.1.0.8   # Database server
ssh root@10.1.0.10  # App server
```

---

## Documentation References

- **Full infrastructure details**: `NCG/Ops/Infrastructure/Hetzner-Infrastructure.md`
- **Database configurations**: `NCG/Ops/Services/Databases.md`
- **Docker registry**: `NCG/Ops/Services/Docker-Registry.md`
- **GitLab CI/CD**: `NCG/Ops/Services/GitLab-CI-CD.md`
- **Network topology**: `NCG/Ops/Infrastructure/Hetzner-Infrastructure.md`

---

**Note**: This is a quick reference. For complete details, see the full documentation files referenced above.
