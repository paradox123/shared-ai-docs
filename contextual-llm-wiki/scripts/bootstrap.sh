#!/usr/bin/env bash
set -euo pipefail
base=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$base"
pin=34ca1df97b3e60a6700048c48c7cf70c92a9bfdb
npm install --prefix .runtime/node node@24.16.0 --no-audit --no-fund
export PATH="$base/.runtime/node/node_modules/node/bin:$PATH"
npm ci --no-audit --no-fund
if [[ ! -d .runtime/compiler/.git ]]; then
  git clone https://github.com/atomicstrata/llm-wiki-compiler.git .runtime/compiler
  git -C .runtime/compiler -c core.hooksPath=/dev/null checkout "$pin"
fi
[[ $(git -C .runtime/compiler rev-parse HEAD) == "$pin" ]] || { echo 'Compiler pin mismatch' >&2; exit 1; }
patch="$base/patches/0001-host-completion-without-embeddings.patch"
if git -C .runtime/compiler apply --check "$patch" 2>/dev/null; then
  git -C .runtime/compiler apply "$patch"
else
  git -C .runtime/compiler apply --reverse --check "$patch"
fi
HUSKY=0 npm --prefix .runtime/compiler ci --ignore-scripts --no-audit --no-fund
npm --prefix .runtime/compiler run build
