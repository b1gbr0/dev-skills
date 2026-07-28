#!/usr/bin/env bash
# Remove symlinks created by link.sh. Only touches links pointing into this repo.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

[ -d "$target" ] || { echo "$target does not exist"; exit 0; }

removed=0
for link in "$target"/*; do
  [ -L "$link" ] || continue
  resolved="$(cd "$(dirname "$link")" && readlink "$link")"
  case "$resolved" in
    "$root"/skills/*)
      rm "$link"
      echo "unlinked $(basename "$link")"
      removed=$((removed + 1))
      ;;
  esac
done

echo "$removed symlink(s) removed from $target"
