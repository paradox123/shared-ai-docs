#!/usr/bin/env bun
/**
 * UpdateChangelog.ts
 *
 * Append changelog entries to NCG operations documentation files.
 *
 * Location: /Users/dh/.claude/skills/documentation/Tools/
 *
 * Usage:
 *   bun run UpdateChangelog.ts --file <filename> --entry "<changelog entry>"
 *   bun run UpdateChangelog.ts --file <filename> --title "<title>" --content "<content>"
 *
 * Examples:
 *   bun run UpdateChangelog.ts --file GitLab-CI-CD.md --entry "## 2026-01-03 - Pipeline optimization\n- Reduced build time by 30%"
 *   bun run UpdateChangelog.ts --file Databases.md --title "MongoDB Upgrade" --content "Upgraded to MongoDB 7.0.5"
 */

import { readFile, writeFile, appendFile } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const VAULT_ROOT = '/Users/dh/Documents/DanielsVault';
const DOCS_PATH = join(VAULT_ROOT, 'NCG', 'Ops');

interface ChangelogEntry {
  date: string;
  title: string;
  content: string;
}

function formatDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatChangelog(entry: ChangelogEntry): string {
  return `
## ${entry.date} - ${entry.title}

${entry.content}

`;
}

async function updateTimestamp(filePath: string): Promise<void> {
  const content = await readFile(filePath, 'utf-8');
  const today = formatDate();
  
  // Update "Last Updated" timestamp if it exists
  const timestampRegex = /\*\*Last Updated\*\*:\s*\d{4}-\d{2}-\d{2}/;
  
  if (timestampRegex.test(content)) {
    const updatedContent = content.replace(
      timestampRegex,
      `**Last Updated**: ${today}`
    );
    await writeFile(filePath, updatedContent, 'utf-8');
    console.log(`✅ Updated timestamp to ${today}`);
  } else {
    console.log(`⚠️  No timestamp found in file`);
  }
}

async function appendChangelog(
  filePath: string,
  entry: ChangelogEntry,
  section: string = 'changelog'
): Promise<void> {
  const content = await readFile(filePath, 'utf-8');
  const formattedEntry = formatChangelog(entry);
  
  // Look for "## Changelog" or "## Change History" section
  const changelogRegex = /^## (Changelog|Change History|Changes)/im;
  const match = content.match(changelogRegex);
  
  if (match) {
    // Insert after the changelog header
    const lines = content.split('\n');
    const headerIndex = lines.findIndex(line => changelogRegex.test(line));
    
    if (headerIndex !== -1) {
      // Insert after header (and any blank line)
      let insertIndex = headerIndex + 1;
      while (insertIndex < lines.length && lines[insertIndex].trim() === '') {
        insertIndex++;
      }
      
      lines.splice(insertIndex, 0, formattedEntry);
      await writeFile(filePath, lines.join('\n'), 'utf-8');
      console.log(`✅ Inserted changelog entry in existing Changelog section`);
    }
  } else {
    // Append to end of file
    await appendFile(filePath, '\n---\n\n## Changelog\n' + formattedEntry, 'utf-8');
    console.log(`✅ Created new Changelog section at end of file`);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help')) {
    console.log(`
Usage: bun run UpdateChangelog.ts [options]

Options:
  --file <filename>     Target documentation file (e.g., Databases.md)
  --entry "<text>"      Raw changelog entry (markdown format)
  --title "<text>"      Changelog entry title (used with --content)
  --content "<text>"    Changelog entry content (used with --title)
  --date <YYYY-MM-DD>   Custom date (default: today)
  --help                Show this help

Examples:
  # Using pre-formatted entry
  bun run UpdateChangelog.ts --file GitLab-CI-CD.md --entry "## 2026-01-03 - Pipeline optimization\\n- Reduced build time by 30%"

  # Using title and content (date added automatically)
  bun run UpdateChangelog.ts --file Databases.md --title "MongoDB Upgrade" --content "Upgraded to MongoDB 7.0.5\\n- Improved performance\\n- Security patches"

  # With custom date
  bun run UpdateChangelog.ts --file Certificates.md --title "Cert Renewal" --content "Renewed SSL certificates" --date 2026-01-15
`);
    process.exit(0);
  }

  // Parse arguments
  let filename = '';
  let rawEntry = '';
  let title = '';
  let content = '';
  let customDate = '';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--file' && i + 1 < args.length) {
      filename = args[i + 1];
      i++;
    } else if (args[i] === '--entry' && i + 1 < args.length) {
      rawEntry = args[i + 1];
      i++;
    } else if (args[i] === '--title' && i + 1 < args.length) {
      title = args[i + 1];
      i++;
    } else if (args[i] === '--content' && i + 1 < args.length) {
      content = args[i + 1];
      i++;
    } else if (args[i] === '--date' && i + 1 < args.length) {
      customDate = args[i + 1];
      i++;
    }
  }

  if (!filename) {
    console.error('❌ Error: --file is required');
    process.exit(1);
  }

  if (!rawEntry && (!title || !content)) {
    console.error('❌ Error: Either --entry OR (--title AND --content) are required');
    process.exit(1);
  }

  // Construct file path
  const filePath = join(DOCS_PATH, filename);

  if (!existsSync(filePath)) {
    console.error(`❌ Error: File not found: ${filename}`);
    console.error(`   Looked in: ${DOCS_PATH}`);
    process.exit(1);
  }

  console.log(`📝 Updating: ${filename}`);

  // Prepare changelog entry
  let entry: ChangelogEntry;

  if (rawEntry) {
    // Use raw entry as-is
    await appendFile(filePath, '\n' + rawEntry + '\n', 'utf-8');
    console.log(`✅ Appended raw entry to file`);
  } else {
    // Build structured entry
    entry = {
      date: customDate || formatDate(),
      title,
      content
    };

    await appendChangelog(filePath, entry);
  }

  // Update timestamp
  await updateTimestamp(filePath);

  console.log(`\n✅ Changelog updated successfully`);
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
