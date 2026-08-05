# Release versioning and the first tag

This repo has no tags at all, so anything installing these skills has to pin a
commit sha — which says nothing about what changed between two pins. This is a
backlog item, not a plan: when it is picked up it becomes
`docs/plans/YYYY-MM-DD-release-versioning.md` and this file is deleted in the
same commit.

What has to be decided first, because the tag is meaningless without it: what a
version *means* for a set of skills. A skill is prose that changes an agent's
output, so the usual "API compatibility" reading does not transfer. A workable
starting point, to be argued with rather than adopted as is:

- **major** — a skill is removed or renamed. The directory name is the skill's
  identity: renaming it silently stops the old name from ever firing again.
- **minor** — a skill is added, or an existing skill's rules change in a way
  that changes what the agent writes.
- **patch** — typos, dead links, formatting, anything that leaves the produced
  code identical.

Open sub-questions:

- One version for the whole repo, or a `version:` field per skill in the
  frontmatter (the way `samber/cc-skills-golang` does it), or both — the repo
  tag for consumers, the per-skill field for provenance?
- What goes in the tag annotation: a plain list of skills touched is probably
  enough at this size, but decide it once instead of improvising each time.
- Whether a `description` change deserves its own category. It is the one edit
  that changes *whether* the skill fires at all, which is louder than most body
  edits.

Deliverable: the scheme written into the repo's own conventions (one short
section, so a future release does not re-litigate it), and the first tag cut by
hand. No release automation — at this size a workflow costs more than it saves,
and it can be added the moment tagging by hand becomes annoying.
