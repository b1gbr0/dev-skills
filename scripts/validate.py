#!/usr/bin/env python3
"""Validate every skill under skills/.

Checks frontmatter, naming, body size, links to bundled resources and evals.json.
Exits 1 on errors; --strict also fails on warnings. Stdlib only (no PyYAML).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|#)([^)]+)\)")
RESOURCE_RE = re.compile(r"`((?:references|scripts|assets)/[^`]+)`")

MAX_NAME = 64
MAX_DESC = 1024
MAX_BODY_LINES = 500
KNOWN_KEYS = {
    "name", "description", "license", "compatibility",
    "user-invocable", "allowed-tools", "metadata", "version",
}
TRIGGER_HINTS = ("use when", "use this", "apply when", "trigger", "whenever", "use it")


def parse_frontmatter(text):
    """Return (mapping of top-level scalar keys, body, error) — nested blocks are skipped."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, "missing YAML frontmatter (file must start with ---)"
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, text, "frontmatter is not closed with ---"

    data, key = {}, None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t"):  # nested value, or continuation of a folded scalar
            if key and isinstance(data.get(key), str) and data[key] in ("|", ">", "|-", ">-"):
                data[key] = line.strip()
            elif key and data.get(key, "") and not isinstance(data.get(key), dict):
                data[key] = f"{data[key]} {line.strip()}".strip()
            continue
        match = KEY_RE.match(line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key] = value
    return data, "\n".join(lines[end + 1:]), None


def check_evals(path, errors, warnings):
    try:
        cases = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"evals/evals.json: invalid JSON ({exc})")
        return
    if not isinstance(cases, list):
        errors.append("evals/evals.json: top level must be a list of cases")
        return
    if not cases:
        warnings.append("evals/evals.json: no eval cases")
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"evals/evals.json[{i}]: case must be an object")
            continue
        for field in ("name", "prompt"):
            if not case.get(field):
                errors.append(f"evals/evals.json[{i}]: missing '{field}'")
        if not case.get("trap") and not case.get("criteria"):
            warnings.append(f"evals/evals.json[{i}]: no 'trap' or 'criteria' — nothing to score")


def validate_skill(skill_dir):
    errors, warnings = [], []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ["missing SKILL.md"], []

    text = skill_md.read_text()
    front, body, err = parse_frontmatter(text)
    if err:
        return [err], []

    name = front.get("name", "")
    if not name:
        errors.append("frontmatter: missing 'name'")
    else:
        if name != skill_dir.name:
            errors.append(f"frontmatter: name '{name}' != directory '{skill_dir.name}'")
        if not NAME_RE.match(name):
            errors.append(f"frontmatter: name '{name}' is not kebab-case")
        if len(name) > MAX_NAME:
            errors.append(f"frontmatter: name is {len(name)} chars (max {MAX_NAME})")

    desc = front.get("description", "")
    if not desc:
        errors.append("frontmatter: missing 'description'")
    else:
        if len(desc) > MAX_DESC:
            errors.append(f"frontmatter: description is {len(desc)} chars (max {MAX_DESC})")
        if len(desc) < 60:
            warnings.append("frontmatter: description is very short — skills under-trigger")
        if not any(hint in desc.lower() for hint in TRIGGER_HINTS):
            warnings.append("frontmatter: description has no 'use when ...' trigger clause")

    for key in front:
        if key not in KNOWN_KEYS:
            warnings.append(f"frontmatter: unknown key '{key}'")

    body_lines = len(body.splitlines())
    if body_lines > MAX_BODY_LINES:
        warnings.append(f"body is {body_lines} lines (max {MAX_BODY_LINES}) — move detail to references/")

    targets = set(MD_LINK_RE.findall(text)) | set(RESOURCE_RE.findall(text))
    for target in targets:
        rel = target.split("#", 1)[0].strip()
        if not rel or rel.startswith("/"):
            continue
        if not (skill_dir / rel).exists():
            errors.append(f"broken link: {rel}")

    if "TODO" in text:
        warnings.append("SKILL.md still contains TODO placeholders")

    evals = skill_dir / "evals" / "evals.json"
    if evals.is_file():
        check_evals(evals, errors, warnings)
    else:
        warnings.append("no evals/evals.json")

    for script in (skill_dir / "scripts").glob("*"):
        if script.suffix in (".sh", ".py") and not script.stat().st_mode & 0o111:
            warnings.append(f"scripts/{script.name} is not executable")

    return errors, warnings


def main():
    strict = "--strict" in sys.argv
    if not SKILLS_DIR.is_dir():
        print(f"no skills directory at {SKILLS_DIR}")
        return 1

    skills = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skills:
        print("no skills yet — create one with scripts/new-skill.sh <name>")
        return 0

    total_errors = total_warnings = 0
    for skill in skills:
        errors, warnings = validate_skill(skill)
        total_errors += len(errors)
        total_warnings += len(warnings)
        status = "FAIL" if errors else ("WARN" if warnings else "ok")
        print(f"[{status}] {skill.name}")
        for message in errors:
            print(f"    error: {message}")
        for message in warnings:
            print(f"    warn:  {message}")

    print(f"\n{len(skills)} skill(s), {total_errors} error(s), {total_warnings} warning(s)")
    return 1 if total_errors or (strict and total_warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
