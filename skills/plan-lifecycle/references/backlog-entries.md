# Backlog entries

The backlog is the list of work that is alive but not started. One task, one file,
kebab-case slug, no date prefix.

## Shape of an entry

```markdown
# Short title naming the problem, not the fix

Two or three sentences: what is wrong or missing, and how it showed up. Name the
observation, not the theory.

What to take into account:

- Constraints that any solution must respect.
- What was already ruled out, and why.
- What would make this ripe for a plan.
```

Keep it at the level of "someone picking this up in a month understands the problem".
Design decisions belong in the plan that grows from it, not here — they age badly while
the problem statement does not.

## Turning a run into entries

After a run, review or live check surfaces something, split by *kind*, one file each:

| Kind | Test | Example title |
|---|---|---|
| Defect | Something behaves against its own stated intent | `hint-names-the-wrong-language` |
| Improvement | It works, but costs more than it should | `stop-signal-retries-twice` |
| Feature | It never existed and someone now wants it | `per-repo-quiet-hours` |

One finding per file even when three findings share a cause: they get scheduled
separately, and a merged entry either blocks on its weakest part or ships half-done.

Do not write an entry for something already fixed in the same session — the fix landed,
there is nothing alive to track.

## When an entry is ripe

An entry becomes a plan when the work is worth doing *now* and the shape of the outcome is
clear enough to write acceptance criteria. Two signals it is not ripe: the entry still says
"investigate whether", or every acceptance criterion would be "decide X".

An entry that has been unripe for months is usually a decision nobody wants to make. Say so
in the entry, rather than rewriting it repeatedly.

## Splitting

When a plan takes only part of an entry, the remainder is rewritten as a new entry with its
own slug describing what is left. Never leave the original file as a stub with the taken
part crossed out — the backlog is read as a list of whole tasks.
