#!/bin/bash
# compile.sh — Wrapper for ConvertToPdf.cs or direct typst compile
# Handles cwd constraint: dotnet run requires a neutral working directory.
#
# Usage:
#   compile.sh <input.typ> <output.pdf>
#
# Falls back to direct typst compile if dotnet is unavailable.

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: compile.sh <input.typ> <output.pdf>" >&2
  exit 1
fi

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
  echo "Error: input file not found: $INPUT" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CS_TOOL="$SCRIPT_DIR/ConvertToPdf.cs"

# Try ConvertToPdf.cs via dotnet run (from /tmp to avoid cwd issues)
if command -v dotnet &>/dev/null && [ -f "$CS_TOOL" ]; then
  cd /tmp
  dotnet run "$CS_TOOL" -- "$INPUT" "$OUTPUT" 2>/dev/null && exit 0
  # Fall through to direct typst if dotnet run failed
fi

# Fallback: direct typst compile
if command -v typst &>/dev/null; then
  typst compile "$INPUT" "$OUTPUT" 2>&1 | grep -v "^warning:" >&2
  echo "✅ PDF created: $OUTPUT"
  exit 0
fi

echo "Error: neither dotnet nor typst found. Install typst: brew install typst" >&2
exit 1
