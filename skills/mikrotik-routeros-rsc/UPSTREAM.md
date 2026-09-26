# Upstream

Forked from [`alexandre-machado/ai-stuffs`](https://github.com/alexandre-machado/ai-stuffs),
path `skills/mikrotik-routeros-rsc`.

| | |
| --- | --- |
| Installed | 2026-07-03 via the agent skills installer (`~/.agents/.skill-lock.json`, `skillFolderHash: 8908b54366796c05540b361c93515551149717c0`) |
| Forked | 2026-09-26 |
| Upstream at fork time | `49c26e0` (2026-09-23), `diff -ru` against the local copy was empty — no merge debt |

Why fork rather than keep installing it: live-use lessons (see
`references/field-notes.md`) had to be recorded, and anything written into the
installer-managed copy is lost on the next skill update. The skill is used on one
workstation only, so it is deliberately **not** part of the cross-machine skills
delivery inventory.

## Updating from upstream

```bash
git clone --depth 1 https://github.com/alexandre-machado/ai-stuffs.git /tmp/ai-stuffs
diff -ru /tmp/ai-stuffs/skills/mikrotik-routeros-rsc skills/mikrotik-routeros-rsc
```

Apply upstream changes by hand and leave `references/field-notes.md`,
`UPSTREAM.md` and `evals/` alone — they are ours. Then rerun
`scripts/validate.py` and update the table above.
