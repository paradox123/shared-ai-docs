#!/usr/bin/env bun
/**
 * SearchVault.ts
 *
 * Full-text search across NCG operations documentation in the Obsidian vault.
 * * Location: /Users/dh/.claude/skills/documentation/Tools/
 * * Usage:
 *   bun run SearchVault.ts "search term"
 *   bun run SearchVault.ts --file "filename" "search term"
 *   bun run SearchVault.ts --regex "pattern"
 *
 * Examples:
 *   bun run SearchVault.ts "MongoDB authentication"
 *   bun run SearchVault.ts --file Databases.md "connection string"
 *   bun run SearchVault.ts --regex "10\\.0\\.0\\.\\d+"
 */

import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const VAULT_ROOT = '/Users/dh/Documents/DanielsVault';
const DOCS_PATH = join(VAULT_ROOT, 'NCG', 'Ops');

interface SearchResult {
  file: string;
  relativePath: string;
  lineNumber: number;
  line: string;
  context: string[];
}

async function findMarkdownFiles(dir: string, files: string[] = []): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = join(dir, entry.name);

    if (entry.isDirectory()) {
      // Skip ARCHIVE folder and hidden folders
      if (entry.name === 'ARCHIVE' || entry.name.startsWith('.')) {
        continue;
      }
      await findMarkdownFiles(fullPath, files);
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(fullPath);
    }
  }

  return files;
}

async function searchInFile(
  filePath: string,
  searchTerm: string,
  isRegex: boolean = false,
  contextLines: number = 2
): Promise<SearchResult[]> {
  const content = await readFile(filePath, 'utf-8');
  const lines = content.split('\n');
  const results: SearchResult[] = [];
  
  const pattern = isRegex ? new RegExp(searchTerm, 'gi') : searchTerm.toLowerCase();

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const matches = isRegex
      ? pattern.test(line)
      : line.toLowerCase().includes(pattern);

    if (matches) {
      const contextStart = Math.max(0, i - contextLines);
      const contextEnd = Math.min(lines.length - 1, i + contextLines);
      const context = lines.slice(contextStart, contextEnd + 1);

      results.push({
        file: filePath,
        relativePath: filePath.replace(DOCS_PATH + '/', ''),
        lineNumber: i + 1,
        line: line.trim(),
        context
      });
    }
  }

  return results;
}

function formatResults(results: SearchResult[], limit: number = 20): string {
  if (results.length === 0) {
    return '❌ No results found.';
  }

  let output = `📚 Found ${results.length} result(s)\n\n`;

  const displayResults = results.slice(0, limit);

  for (const result of displayResults) {
    output += `📄 ${result.relativePath}:${result.lineNumber}\n`;
    output += `   ${result.line}\n\n`;
  }

  if (results.length > limit) {
    output += `... and ${results.length - limit} more results.\n`;
    output += `Use --limit ${results.length} to see all results.\n`;
  }

  return output;
}

function formatDetailedResults(results: SearchResult[], limit: number = 10): string {
  if (results.length === 0) {
    return '❌ No results found.';
  }

  let output = `📚 Found ${results.length} result(s)\n\n`;

  const displayResults = results.slice(0, limit);

  for (const result of displayResults) {
    output += `${'='.repeat(80)}\n`;
    output += `📄 ${result.relativePath} (Line ${result.lineNumber})\n`;
    output += `${'-'.repeat(80)}\n`;
    
    for (let i = 0; i < result.context.length; i++) {
      const lineNum = result.lineNumber - Math.floor(result.context.length / 2) + i;
      const prefix = lineNum === result.lineNumber ? '➤ ' : '  ';
      output += `${prefix}${lineNum}: ${result.context[i]}\n`;
    }
    
    output += '\n';
  }

  if (results.length > limit) {
    output += `... and ${results.length - limit} more results.\n`;
  }

  return output;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help')) {
    console.log(`
Usage: bun run SearchVault.ts [options] "search term"

Options:
  --file <filename>    Search only in specific file (e.g., --file Databases.md)
  --regex              Treat search term as regular expression
  --detailed           Show context around matches
  --limit <n>          Limit number of results (default: 20, detailed: 10)
  --help               Show this help

Examples:
  bun run SearchVault.ts "MongoDB authentication"
  bun run SearchVault.ts --file Databases.md "connection string"
  bun run SearchVault.ts --regex "10\\.0\\.0\\.\\d+"
  bun run SearchVault.ts --detailed "docker registry"
  bun run SearchVault.ts --limit 50 "GitLab"
`);
    process.exit(0);
  }

  // Parse arguments
  let searchTerm = '';
  let specificFile: string | null = null;
  let isRegex = false;
  let detailed = false;
  let limit = 20;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--file' && i + 1 < args.length) {
      specificFile = args[i + 1];
      i++;
    } else if (args[i] === '--regex') {
      isRegex = true;
    } else if (args[i] === '--detailed') {
      detailed = true;
      limit = 10; // Detailed view shows fewer results by default
    } else if (args[i] === '--limit' && i + 1 < args.length) {
      limit = parseInt(args[i + 1], 10);
      i++;
    } else if (!args[i].startsWith('--')) {
      searchTerm = args[i];
    }
  }

  if (!searchTerm) {
    console.error('❌ Error: Search term required.');
    process.exit(1);
  }

  if (!existsSync(DOCS_PATH)) {
    console.error(`❌ Error: Documentation path not found: ${DOCS_PATH}`);
    process.exit(1);
  }

  // Get files to search
  let filesToSearch: string[];

  if (specificFile) {
    // Search only in specific file
    const specificPath = join(DOCS_PATH, specificFile);
    if (!existsSync(specificPath)) {
      console.error(`❌ Error: File not found: ${specificFile}`);
      process.exit(1);
    }
    filesToSearch = [specificPath];
  } else {
    // Search all markdown files
    filesToSearch = await findMarkdownFiles(DOCS_PATH);
  }

  // Perform search
  let allResults: SearchResult[] = [];

  for (const file of filesToSearch) {
    const results = await searchInFile(file, searchTerm, isRegex);
    allResults = allResults.concat(results);
  }

  // Sort by relevance (file path alphabetically, then line number)
  allResults.sort((a, b) => {
    const fileCompare = a.relativePath.localeCompare(b.relativePath);
    return fileCompare !== 0 ? fileCompare : a.lineNumber - b.lineNumber;
  });

  // Format and display results
  const output = detailed
    ? formatDetailedResults(allResults, limit)
    : formatResults(allResults, limit);

  console.log(output);

  // Exit code based on results
  process.exit(allResults.length > 0 ? 0 : 1);
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
