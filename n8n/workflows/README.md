# n8n Workflow Templates

This directory contains exported n8n workflow templates that can be imported into any n8n instance.

## How to Use Workflow Templates

### Export a Workflow
1. Open n8n UI (http://localhost:5678)
2. Open the workflow you want to export
3. Click the three-dot menu → "Download"
4. Save the JSON file to this directory
5. Commit and push to the repository

### Import a Workflow
1. Open n8n UI
2. Click "Add Workflow" → "Import from File"
3. Select a JSON file from this directory
4. Adjust any machine-specific settings (file paths should use `/workspace/...`)

## Workflow Best Practices

### Making Workflows Portable
- Use `/workspace/` as base path (maps to DanielsVault)
- Store machine-specific config in workflow variables
- Document required credentials in workflow description
- Use relative paths where possible

### Example Path Patterns
- ✅ `/workspace/private/Energetische Sanierung/emails/`
- ✅ `/workspace/ncg/ncg-docs/docs/`
- ❌ `/Users/dh/Documents/...` (not portable)

## Available Workflows

(Add workflow descriptions here as you create and export them)

### Template: Email Processing
- **File**: `email-processing-template.json`
- **Purpose**: Fetch emails via IMAP, extract data, update documents
- **Required Credentials**: IMAP account
- **Setup Notes**: Configure email filters and target folders

### Template: Document Automation
- **File**: `document-automation-template.json`
- **Purpose**: Watch for new documents, extract data, update tracking
- **Required Credentials**: None
- **Setup Notes**: Configure file patterns to watch
