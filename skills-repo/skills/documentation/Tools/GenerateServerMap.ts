#!/usr/bin/env bun
/**
 * GenerateServerMap.ts
 *
 * Auto-generate ServerMap.md context file by scanning NCG infrastructure documentation.
 *
 * Location: /Users/dh/.claude/skills/documentation/Tools/
 *
 * Usage:
 *   bun run GenerateServerMap.ts [options]
 *
 * Options:
 *   --output <path>   Output file path (default: Context/ServerMap.md)
 *   --scan            Scan documentation files to extract server information
 *   --help            Show this help
 *
 * Examples:
 *   bun run GenerateServerMap.ts
 *   bun run GenerateServerMap.ts --output ../Context/ServerMap-generated.md
 *   bun run GenerateServerMap.ts --scan
 */

import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';

const VAULT_ROOT = '/Users/dh/Documents/DanielsVault';
const DOCS_PATH = join(VAULT_ROOT, 'NCG', 'Ops');
const DEFAULT_OUTPUT = '/Users/dh/.claude/skills/documentation/Context/ServerMap.md';

interface Server {
  name: string;
  ip: string;
  type?: string;
  services?: string;
  purpose?: string;
  environment: 'dev' | 'prod';
}

async function scanInfrastructure(): Promise<Server[]> {
  const servers: Server[] = [];
  
  // Read Infrastructure documentation
  const infraFile = join(DOCS_PATH, 'Infrastructure', 'Hetzner-Infrastructure.md');
  
  try {
    const content = await readFile(infraFile, 'utf-8');
    
    // Extract server tables (looking for markdown tables with IPs)
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Look for lines that start with | and contain IP pattern
      if (line.startsWith('|') && /10\.[0-1]\.\d+\.\d+/.test(line)) {
        // Skip table headers and separators
        if (line.includes('---') || line.toLowerCase().includes('server') && line.includes('IP')) {
          continue;
        }
        
        // Parse table row
        const columns = line.split('|').map(col => col.trim()).filter(col => col);
        
        if (columns.length >= 2) {
          const name = columns[0];
          const ip = columns[1];
          
          // Determine environment from IP
          const environment = ip.startsWith('10.0.') ? 'dev' : 'prod';
          
          const server: Server = {
            name,
            ip,
            environment,
            type: columns[2] || undefined,
            services: columns[3] || undefined,
            purpose: columns[4] || undefined
          };
          
          servers.push(server);
        }
      }
    }
    
    console.log(`✅ Scanned infrastructure, found ${servers.length} servers`);
  } catch (error) {
    console.error(`⚠️  Could not read infrastructure file: ${error.message}`);
  }
  
  return servers;
}

function generateServerMap(servers: Server[]): string {
  const devServers = servers.filter(s => s.environment === 'dev');
  const prodServers = servers.filter(s => s.environment === 'prod');
  
  const today = new Date().toISOString().split('T')[0];
  
  return `# NCG Server Map

**Quick reference for NCG infrastructure servers and services**

**Last Updated**: ${today}
**Auto-generated**: This file can be regenerated from infrastructure documentation

---

## Development Network (10.0.0.0/16)

${generateServerTable(devServers)}

---

## Production Network (10.1.0.0/16)

${generateServerTable(prodServers)}

---

## Service Endpoints

### API Gateway (Ocelot)
- **Development**: http://10.0.0.10:9000
- **Production**: http://10.1.0.10:9000

### Databases

#### MongoDB
- **Development**: 10.0.0.7:27017
- **Production**: 10.1.0.8:27017
- **Connection**: \`mongodb://dba:<GITLAB_CI:[ENV]_MONGODB_PASSWORD>@[IP]:27017\`

#### MariaDB
- **Development**: 10.0.0.7:3306
- **Production**: 10.1.0.8:3306
- **Connection**: \`mysql -h [IP] -u root -p\`

#### PostgreSQL
- **Development**: 10.0.0.7:5432
- **Production**: 10.1.0.8:5432
- **Connection**: \`psql -h [IP] -U postgres\`

### Docker Registry
- **URL**: docker.auto-nagel-cloud.de
- **Development**: 10.0.0.11:5000 (internal only, NO public IP)
- **Production**: 10.1.0.7:5000 (internal only, NO public IP)
- **Authentication**: \`docker login docker.auto-nagel-cloud.de -u ncg -p <GITLAB_CI:REGISTRY_PASSWORD>\`

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
- Documentation reference: \`NCG/Ops/Security/Secrets-Management.md\`

**Never hardcode credentials**. Always use:
- \`GITLAB_CI:[VARIABLE_NAME]\` for scripts
- \`VAULT:[path]\` for advanced secret management

---

## Quick SSH Access

\`\`\`bash
# Development
ssh root@10.0.0.7   # Database server
ssh root@10.0.0.8   # GitLab server
ssh root@10.0.0.10  # App server
ssh root@10.0.0.11  # Docker registry

# Production (requires VPN)
ssh root@10.1.0.8   # Database server
ssh root@10.1.0.10  # App server
\`\`\`

---

## Documentation References

- **Full infrastructure details**: \`NCG/Ops/Infrastructure/Hetzner-Infrastructure.md\`
- **Database configurations**: \`NCG/Ops/Services/Databases.md\`
- **Docker registry**: \`NCG/Ops/Services/Docker-Registry.md\`
- **GitLab CI/CD**: \`NCG/Ops/Services/GitLab-CI-CD.md\`
- **Network topology**: \`NCG/Ops/Infrastructure/Hetzner-Infrastructure.md\`

---

**Note**: This is a quick reference. For complete details, see the full documentation files referenced above.
`;
}

function generateServerTable(servers: Server[]): string {
  if (servers.length === 0) {
    return '_No servers found_';
  }
  
  let table = '| Server | IP | Type | Services | Purpose |\n';
  table += '|--------|-----|------|----------|----------|\n';
  
  for (const server of servers) {
    table += `| ${server.name} | ${server.ip} | ${server.type || ''} | ${server.services || ''} | ${server.purpose || ''} |\n`;
  }
  
  return table;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help')) {
    console.log(`
Usage: bun run GenerateServerMap.ts [options]

Options:
  --output <path>   Output file path (default: Context/ServerMap.md)
  --scan            Scan documentation to extract server info (experimental)
  --help            Show this help

Examples:
  # Generate with default output
  bun run GenerateServerMap.ts

  # Custom output location
  bun run GenerateServerMap.ts --output /tmp/ServerMap.md

  # Scan infrastructure files (experimental)
  bun run GenerateServerMap.ts --scan
`);
    process.exit(0);
  }

  // Parse arguments
  let outputPath = DEFAULT_OUTPUT;
  let scanMode = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--output' && i + 1 < args.length) {
      outputPath = args[i + 1];
      i++;
    } else if (args[i] === '--scan') {
      scanMode = true;
    }
  }

  console.log(`📝 Generating Server Map...`);

  let servers: Server[] = [];

  if (scanMode) {
    console.log(`🔍 Scanning infrastructure documentation...`);
    servers = await scanInfrastructure();
  } else {
    // Use hardcoded server list (from existing documentation)
    console.log(`ℹ️  Using predefined server list`);
    
    servers = [
      // Development
      { name: 'dev-gitlab-02', ip: '10.0.0.2', environment: 'dev', type: 'CX21', services: 'GitLab Runner', purpose: 'CI/CD runner' },
      { name: 'dev-database', ip: '10.0.0.7', environment: 'dev', type: 'CX23', services: 'MongoDB, MariaDB, PostgreSQL', purpose: 'Database server' },
      { name: 'dev-gitlab-01', ip: '10.0.0.8', environment: 'dev', type: 'CX31', services: 'GitLab', purpose: 'Source control, CI/CD' },
      { name: 'dev-app-server', ip: '10.0.0.10', environment: 'dev', type: 'CX21', services: 'Backend containers', purpose: 'Application services' },
      { name: '03-docker-registry', ip: '10.0.0.11', environment: 'dev', type: 'CX11', services: 'Docker Registry', purpose: 'Private image repository' },
      
      // Production
      { name: 'prod-web-01', ip: '10.1.0.5', environment: 'prod', type: 'CX21', services: 'Frontend', purpose: 'Web application' },
      { name: '03-docker-registry', ip: '10.1.0.7', environment: 'prod', type: 'CX11', services: 'Docker Registry', purpose: 'Private image repository' },
      { name: 'prod-database', ip: '10.1.0.8', environment: 'prod', type: 'CX23', services: 'MongoDB, MariaDB, PostgreSQL', purpose: 'Database server' },
      { name: 'prod-app-server', ip: '10.1.0.10', environment: 'prod', type: 'CX21', services: 'Backend containers', purpose: 'Application services' },
    ];
  }

  // Generate map
  const mapContent = generateServerMap(servers);

  // Write to file
  await writeFile(outputPath, mapContent, 'utf-8');

  console.log(`\n✅ Server Map generated successfully`);
  console.log(`📄 Output: ${outputPath}`);
  console.log(`📊 Servers: ${servers.length} (${servers.filter(s => s.environment === 'dev').length} dev, ${servers.filter(s => s.environment === 'prod').length} prod)`);
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
