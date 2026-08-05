# Working in this repo

This repo contains agent skills. Each skill is a directory under `skills/` whose only required
file is `SKILL.md`. Nothing here is application code — the deliverable is prose that changes how
an agent behaves.

## Rules

- One skill per directory; directory name == `name:` in the frontmatter, kebab-case, <= 64 chars.
- `SKILL.md` body stays under ~500 lines. Anything longer moves to `references/` and gets linked
  from the body with a one-line description of when to read it (progressive disclosure).
- Write the `description:` for triggering: what the skill does **and** the concrete situations,
  phrases and file types that should activate it. Be slightly pushy — skills under-trigger.
- Instructions are imperative and specific ("run `go test -race ./...`"), not aspirational
  ("consider testing"). Show a correct example rather than describing one.
- Skills are written in English, even when the conversation is not — triggering depends on it.
  Exception: a skill whose subject *is* writing in another language (`cpp-russian`) has its body
  in that language, because the body doubles as a register sample. Its `description` stays
  bilingual — an English clause for triggering plus the native-language trigger phrases.
- This repo is public, so everything committed to it is in English — plans, docs and commit
  messages included, not just skills. The conversation that produces them can be in any language.
- Never invent tool names, flags or APIs in a skill. Verify them first; a wrong flag in a skill
  is repeated by the agent every time it fires.

## Before committing

```bash
scripts/validate.py       # fails on frontmatter, link and evals errors
```

Commit messages follow Conventional Commits, scoped by skill:
`feat(my-skill): add coverage section`, `fix(my-skill): correct gotestsum flag`.

## Plans

Work larger than one commit gets a plan under `docs/plans/YYYY-MM-DD-slug.md`. Status is
location, not a marker in the heading: a finished plan is `git mv`d into
`docs/plans/completed/` and is frozen there — follow-ups become new plans, never retro-edits.

Anything that is not being worked on yet lives in `docs/plans/backlog/slug.md`, one item per
file, no date prefix. When an item is picked up it becomes a plan in `docs/plans/` and the
backlog file is deleted in the same commit — it never exists in both places.

Never park future work at the tail of an active plan. When that plan moves to `completed/` the
parked work freezes with it and drops out of sight. An active plan holds only what it will
actually close, plus a pointer to the backlog file that holds the rest.

## Adding a skill

```bash
scripts/new-skill.sh my-skill
```

Fill in `SKILL.md`, then write 3-5 entries in `evals/evals.json`: a realistic prompt plus the
trap a model without the skill falls into. Test by running `scripts/link.sh` and starting a
session in a real project — not by re-reading the file.
