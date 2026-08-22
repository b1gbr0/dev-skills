---
name: plan-lifecycle
description: "Track work as plan files whose directory is their status: backlog/ holds one-task-per-file candidates, the plans root holds active date-prefixed plans, completed/ holds frozen finished ones. Move files with git mv, delete the backlog entry in the same commit that creates its plan, and close a plan by moving it with a closing banner plus an outcome section carrying evidence. Turn what a run, review or live check surfaces into new backlog entries — one per defect, improvement or feature — that later grow into follow-up plans, never into edits of a finished plan. Use when opening, closing, splitting or reopening a plan, when a run surfaces problems, when a finished plan still sits in the active directory, when a post-completion check never happened, or when asked where some leftover work belongs. Not for writing the code a plan describes, and not an issue-tracker integration."
user-invocable: true
license: MIT
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# Plan Lifecycle

Work lives in plan files inside the repository, and a plan's directory *is* its status —
never a marker in its title, never a checkbox in an index. Three locations, one direction:
`docs/plans/backlog/` (candidates, one task per file, no date prefix), `docs/plans/`
(active, `YYYY-MM-DD-slug.md`), `docs/plans/completed/` (finished, frozen). Every status
change is a `git mv` in a commit. Read the tree and you know the state of the project;
there is nothing else to consult and nothing else to keep in sync.

## A task exists in exactly one place

A backlog entry that grows into a plan is *deleted from the backlog in the same commit*
that creates the plan. Never leave a copy behind, never close it in place with a note.

```
git rm docs/plans/backlog/slug.md
git add docs/plans/2026-08-22-slug.md
git commit -m "docs(plans): backlog entry <slug> became a plan"
```

Failure mode this prevents: the backlog stops being a list of live work and becomes a
graveyard nobody trusts, so real candidates get lost among finished ones.

## A plan holds only what it will close

Scope a plan to what this run of work actually finishes, plus a pointer to what comes
next. Anything that will not be closed goes to the backlog as its own file, or becomes a
separate plan.

Failure mode this prevents: the plan ships, moves to `completed/`, and the unfinished
slice freezes inside it — invisible to anyone reading the backlog.

## Findings become backlog entries, not edits

When a run, review or live check surfaces something, write one backlog file per finding,
typed by what it is: a defect, an improvement, or a feature. Those entries later grow into
follow-up plans by the rule above. A plan already in `completed/` is frozen: no retro-fixes,
no reopened checkboxes, no appended tasks.

Failure mode this prevents: a finished plan slowly turns into an open-ended ticket, and the
history of what was actually shipped stops being readable.

## Closing a plan

Move it, then record the outcome inside it — a banner at the top saying it is closed and
worked as intended, and a short outcome section with evidence: what ran, when, what the
numbers were, where the log lives. The banner is the last edit the plan ever receives.

## When the plan is done but a check never ran

Close the plan anyway and open a backlog entry for the check. A finished plan parked in the
active directory waiting for a verification is worse than both alternatives: the tree lies
about the project's state, and the pending check is invisible to anyone reading the backlog.

## References

- [references/lifecycle.md](references/lifecycle.md) — read when performing a transition:
  exact commands, commit message shapes, checkbox and banner handling, worked example.
- [references/backlog-entries.md](references/backlog-entries.md) — read when writing an
  entry or turning findings from a run into entries.
- [references/writing-plans.md](references/writing-plans.md) — read when authoring a plan:
  section anatomy, altitude, acceptance criteria, post-completion sections.
