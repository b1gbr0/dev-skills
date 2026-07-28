# Skills

A monorepo for authoring, testing and distributing agent skills (Claude Code / compatible agents).

## Layout

```
skills/<skill-name>/         one skill = one directory
  SKILL.md                   frontmatter + instructions (the only required file)
  references/                deep-dive docs, loaded on demand
  scripts/                   executable helpers the agent may run
  assets/                    templates, boilerplate, sample files
  evals/evals.json           test prompts + expected behaviour

templates/skill/             copy-me starting point for a new skill
scripts/                     repo tooling (new-skill, validate, link, unlink)
docs/conventions.md          writing rules for skills in this repo
.claude-plugin/              optional: makes the repo installable via /plugin
```

## Workflow

```bash
scripts/new-skill.sh my-skill   # scaffold skills/my-skill from the template
scripts/validate.py             # check frontmatter, links, evals (CI runs this too)
scripts/link.sh                 # symlink skills/* into ~/.claude/skills for local testing
scripts/unlink.sh               # remove those symlinks
```

Then open a Claude Code session in another project and check that the skill triggers on the
prompts listed in its `evals/evals.json`. The bundled `skill-creator` skill can run the eval
loop for you.

## Installing from this repo

Local development — symlink into the skills directory:

```bash
scripts/link.sh                          # defaults to ~/.claude/skills
CLAUDE_SKILLS_DIR=~/.agents/skills scripts/link.sh
```

As a plugin marketplace, once the repo is pushed to a git host:

```
/plugin marketplace add <owner>/<repo>
/plugin install skills@dev-skills
```

## License

MIT — see [LICENSE](LICENSE).
