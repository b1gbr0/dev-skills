#!/usr/bin/env bash
# Symlink every skill in this repo into the agent skills directory for local testing.
# Override the target with CLAUDE_SKILLS_DIR=... scripts/link.sh
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

mkdir -p "$target"
linked=0

for dir in "$root"/skills/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  link="$target/$name"

  if [ -L "$link" ]; then
    rm "$link"
  elif [ -e "$link" ]; then
    echo "skip: $name exists in $target and is not a symlink" >&2
    continue
  fi

  ln -s "$root/skills/$name" "$link"
  echo "linked $name -> $link"
  linked=$((linked + 1))
done

echo "$linked skill(s) linked into $target"
echo "restart the agent session to pick them up"
