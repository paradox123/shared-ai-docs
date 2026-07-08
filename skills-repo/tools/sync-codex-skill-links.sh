#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
shared_skills_dir="$repo_root/skills"
codex_home="${CODEX_HOME:-$HOME/.codex}"
codex_skills_dir="$codex_home/skills"

mkdir -p "$codex_skills_dir"

if [[ ! -d "$shared_skills_dir" ]]; then
  echo "Missing shared skills directory: $shared_skills_dir" >&2
  exit 1
fi

# Remove stale Codex skill links previously managed by this repo.
find "$codex_skills_dir" -mindepth 1 -maxdepth 1 -type l | while IFS= read -r link_path; do
  target="$(readlink "$link_path")"
  case "$target" in
    "$repo_root/skills/"*|"$repo_root/active-skills/"*|../Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/*)
      rm "$link_path"
      ;;
  esac
done

find "$shared_skills_dir" -mindepth 1 -maxdepth 1 \( -type d -o -type l \) | sort | while IFS= read -r skill_path; do
  skill_name="$(basename "$skill_path")"
  target_path="$codex_skills_dir/$skill_name"

  if [[ -e "$target_path" && ! -L "$target_path" ]]; then
    echo "Skipping non-symlink Codex skill path: $target_path" >&2
    continue
  fi

  ln -sfn "$skill_path" "$target_path"
done

echo "Synced Codex skill links from $shared_skills_dir to $codex_skills_dir"
