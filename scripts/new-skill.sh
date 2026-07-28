#!/usr/bin/env bash
# Scaffold skills/<name> from templates/skill.
set -euo pipefail

name="${1:-}"
if [ -z "$name" ]; then
  echo "usage: scripts/new-skill.sh <skill-name>" >&2
  exit 1
fi

if ! printf '%s' "$name" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "error: '$name' must be kebab-case (lowercase, digits, single hyphens)" >&2
  exit 1
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
dest="$root/skills/$name"

if [ -e "$dest" ]; then
  echo "error: $dest already exists" >&2
  exit 1
fi

cp -R "$root/templates/skill" "$dest"

author="$(git -C "$root" config user.name 2>/dev/null || echo "unknown")"
title="$(printf '%s' "$name" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"

python3 - "$dest" "$name" "$title" "$author" <<'PY'
import pathlib, sys

dest, name, title, author = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
for path in dest.rglob("*"):
    if path.is_file():
        text = path.read_text()
        replaced = (text.replace("{{SKILL_NAME}}", name)
                        .replace("{{SKILL_TITLE}}", title)
                        .replace("{{AUTHOR}}", author))
        if replaced != text:
            path.write_text(replaced)
PY

echo "created skills/$name"
echo "next: edit skills/$name/SKILL.md, then run scripts/validate.py"
