# n8n Workflow Automation Setup

This directory contains the n8n workflow automation engine setup for managing personal workflows including email processing, document tracking, tax reporting, and more.

## Quick Start

### 1. Configure Credentials

Edit `.env` file and change the default password:

```bash
N8N_USER=admin
N8N_PASSWORD=your_secure_password_here
```

### 2. Start n8n

```bash
cd /Users/dh/Documents/DanielsVault/_shared/n8n
docker-compose up -d
```

### 3. Access n8n

Open your browser and navigate to:
- **URL**: http://localhost:5678
- **Username**: admin
- **Password**: (the password you set in .env)

### 4. Stop n8n

```bash
docker-compose down
```

## Features

- **Workspace Access**: n8n can read and write to `/Users/dh/Documents/DanielsVault` (mounted as `/workspace` in container)
- **Persistent Data**: All workflows and credentials are stored in `./data` directory
- **Timezone**: Configured for Europe/Berlin

## Planned Workflows

1. **Energetische Sanierung Email Tracking**
   - Fetch emails via IMAP
   - Extract contacts and action items
   - Update tracking documents
   - Create reminders

2. **Tax Reporting Automation**
   - Process tax documents
   - Extract relevant data
   - Generate reports

3. **Nebenkostenabrechnung Processing**
   - Process utility bills
   - Extract costs
   - Generate summaries

## Useful Commands

### View logs
```bash
docker-compose logs -f n8n
```

### Restart n8n
```bash
docker-compose restart
```

### Update n8n
```bash
docker-compose pull
docker-compose up -d
```

### Backup workflows
```bash
cp -r data data-backup-$(date +%Y%m%d)
```

## Next Steps

1. Set up email credentials in n8n (IMAP access)
2. Create first workflow for email processing
3. Configure file watchers for document automation
4. Set up scheduling for recurring tasks

## Security Notes

- Never commit `.env` file with real credentials
- Change default password immediately
- For production use, consider adding SSL/TLS
- Keep n8n updated regularly
