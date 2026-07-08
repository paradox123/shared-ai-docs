#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"
hooks_dir="$repo_root/.git/hooks"
sync_script="$repo_root/skills-repo/tools/sync-codex-skill-links.sh"

if [[ ! -d "$hooks_dir" ]]; then
  echo "Missing git hooks directory: $hooks_dir" >&2
  exit 1
fi

if [[ ! -x "$sync_script" ]]; then
  echo "Missing executable sync script: $sync_script" >&2
  exit 1
fi

cat > "$hooks_dir/post-merge" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
"$repo_root/skills-repo/tools/sync-codex-skill-links.sh"
HOOK

cat > "$hooks_dir/post-checkout" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
"$repo_root/skills-repo/tools/sync-codex-skill-links.sh"
HOOK

chmod +x "$hooks_dir/post-merge" "$hooks_dir/post-checkout"

echo "Installed shared skill hooks in $hooks_dir"
