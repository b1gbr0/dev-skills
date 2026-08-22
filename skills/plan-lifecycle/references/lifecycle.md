# Transitions

Four moves, each one commit. Nothing else changes a plan's status.

## 1. Something worth doing appears

It goes to the backlog, one file per task, no date prefix — the date means "started", and
this has not started.

```
docs/plans/backlog/lsp-hint-wrong-language.md
```

## 2. A backlog entry becomes a plan

Same commit: the plan appears, the entry disappears.

```bash
git rm docs/plans/backlog/<slug>.md
git add docs/plans/<YYYY-MM-DD>-<slug>.md
git commit -m "docs(plans): backlog entry <slug> became a plan"
```

The plan may narrow the entry — take part of it now and leave the rest. The rest stays in
the backlog as a *separate, rewritten* file, not as the leftovers of the old one.

## 3. The plan is executed

Checkboxes get ticked as the work lands, in the commits that do the work. A plan whose
boxes are all ticked but which still sits in the active directory is an unfinished
transition, not a state.

## 4. The plan closes

```bash
git mv docs/plans/<YYYY-MM-DD>-<slug>.md docs/plans/completed/
# then edit the moved file: banner at the top, outcome section at the bottom
git commit -m "docs(plans): ship <slug>"
```

Banner goes directly under the H1, before the first section:

```markdown
# <Plan title>

> **Ran 2026-08-22 and closed.** The plan verified what it was opened for:
> <one sentence on the result>. Details at the end of the file.
```

Outcome section goes last, and carries evidence rather than adjectives:

```markdown
## Outcome

- **12:46:55** — first action denied by the hook; the agent emitted the stop signal.
- **12:47:24** — `Failed: … after retry`, 59 seconds from start.

Cost: two attempts, 4 488 output tokens. Log: `.ralphex/progress/<run>.txt`.
```

After this commit the file is frozen. Corrections to what it describes are new backlog
entries, not edits here.

## Worked example

A hook was shipped by an earlier plan, but the live check never ran because the run ended
before the conditions appeared. The check does not belong in the shipped plan, and it is
not urgent enough to be a plan of its own:

1. `docs/plans/backlog/peak-stop-live-verification.md` — what is unverified, how to check
   it, what a failure would mean.
2. Conditions appear. The entry becomes `docs/plans/2026-08-22-peak-stop-live-check.md`;
   the backlog file is removed in the same commit.
3. The check runs. The plan moves to `completed/` with a banner and the timings.
4. Had it failed, the failures would have become new backlog entries — one per defect —
   and the plan would still have closed, describing what actually happened.

## Hierarchical plans

A plan too large for one file becomes a date-prefixed directory with `NN-` ordered parts.
It closes as a unit: the whole directory moves to `completed/`. Parts do not close
individually — if one part is genuinely independent, it was a separate plan.
