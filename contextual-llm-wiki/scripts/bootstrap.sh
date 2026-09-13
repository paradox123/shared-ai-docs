#!/usr/bin/env bash
set -euo pipefail
base=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$base"
pin=$(python3 -c 'import json; print(json.load(open("compiler-release.json"))["commit"])')
repository=$(python3 -c 'import json; print(json.load(open("compiler-release.json"))["repository"])')
npm install --prefix .runtime/node node@24.16.0 --no-audit --no-fund
export PATH="$base/.runtime/node/node_modules/node/bin:$PATH"
npm ci --no-audit --no-fund
if [[ ! -d .runtime/compiler/.git ]]; then
  git clone "https://github.com/$repository.git" .runtime/compiler
  git -C .runtime/compiler -c core.hooksPath=/dev/null checkout "$pin"
fi
[[ $(git -C .runtime/compiler rev-parse HEAD) == "$pin" ]] || { echo 'Compiler pin mismatch' >&2; exit 1; }
for patch in "$base"/patches/*.patch; do
  if git -C .runtime/compiler apply --check "$patch" 2>/dev/null; then
    git -C .runtime/compiler apply "$patch"
  else
    git -C .runtime/compiler apply --reverse --check "$patch"
  fi
done
HUSKY=0 npm --prefix .runtime/compiler ci --ignore-scripts --no-audit --no-fund
npm --prefix .runtime/compiler run build
