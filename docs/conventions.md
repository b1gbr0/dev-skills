# Skill conventions

## Frontmatter

```yaml
---
name: skill-name              # required, kebab-case, == directory name, <= 64 chars
description: ...              # required, <= 1024 chars, what + when (see below)
user-invocable: true          # optional, exposes /skill-name as a slash command
license: MIT                  # optional
compatibility: ...            # optional, e.g. "Requires Go 1.22+ and golangci-lint"
metadata:                     # optional, free-form
  author: b1gbr0
  version: "1.0.0"
---
```

Everything after the closing `---` is the instruction body.

## Writing the description

The description is the only part of a skill that is always in the agent's context. It is the
trigger, not a summary. A good one answers three questions:

1. **What** does the skill do — concrete verbs, not "helps with".
2. **When** should it fire — user phrases, file types, libraries, error messages, task shapes.
3. **When should it not** — name the neighbouring skill it is confused with, if any.

```
Bad:  "Helps with database code."
Good: "Golang database access — parameterized queries, struct scanning, NULL handling,
       transactions and isolation levels, connection pool tuning. Use whenever writing,
       reviewing or debugging Go code that talks to PostgreSQL, MySQL or SQLite, or when
       the code imports database/sql, sqlx or pgx. Does NOT generate schema migrations."
```

## Language

Default: English, including for conversations held in another language. Triggering depends on the
description matching the model's English-dominant sense of the task.

One exception: when the skill's subject *is* producing text in another language, write the body in
that language. The body then doubles as a register sample, priming the output it describes, and the
glossary it carries is native by necessity. Keep the `description` bilingual — an English clause so
triggering stays reliable, plus the phrases a user would actually type in that language.

`skills/cpp-russian` is the worked example: Russian body, bilingual description.

## Body structure

Aim for under 500 lines. A body that grows past that is really several skills, or a skill with
reference material inlined.

```markdown
# Skill Name

One paragraph: what this covers and the mental model behind it.

## <Task or decision>

Rule first, then a minimal correct example, then the failure mode it prevents.

## References

- [references/advanced.md](references/advanced.md) — read when X.
```

Progressive disclosure: the body carries the rules the agent needs every time; `references/`
carries what it needs occasionally. Link each reference with the condition for reading it,
otherwise it is either always loaded or never.

## Bundled resources

| Directory     | Contents                                    | Loaded |
|---------------|---------------------------------------------|--------|
| `references/` | Markdown deep dives, tables, API details    | On demand, when the body links to it |
| `scripts/`    | Executable helpers (`.py`, `.sh`)           | Executed, not read into context |
| `assets/`     | Templates, configs, boilerplate to copy     | Copied or read as needed |
| `evals/`      | `evals.json` test prompts                   | Never loaded by the agent |

Prefer a script over prose when the task is deterministic — an agent running a validated script
beats an agent re-deriving the steps. Prefer prose when the task needs judgement.

## Evals

`evals/evals.json` is an array of cases:

```json
[
  {
    "id": 1,
    "name": "short-slug",
    "description": "What this case checks",
    "prompt": "A realistic user request that should trigger the skill",
    "trap": "What a model without this skill does wrong here",
    "criteria": [
      "Uses X instead of Y",
      "Mentions the Z caveat"
    ]
  }
]
```

Write the `trap` first. If you cannot name a concrete mistake the skill prevents, the skill is
restating what the model already does and does not need to exist.

## Testing loop

1. `scripts/validate.py`
2. `scripts/link.sh`
3. Start a session in a real project and use the eval prompts verbatim — check that the skill
   *fires* before checking that the output is good. Under-triggering is the most common defect,
   and it is fixed in the `description`, not the body.
4. Iterate. The `skill-creator` skill automates steps 3-4 with batched runs and scoring.
