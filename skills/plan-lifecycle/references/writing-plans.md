# Writing the plan file

A plan is written at the altitude of the outcome: what must become true, under what
constraints, and how anyone can tell it happened. It is not a script of steps — whoever
executes it, human or agent, knows their tools better than the plan does.

## Sections

```markdown
# Title naming the outcome

## Why

What is wrong today, with the evidence that makes it worth doing now. Numbers, log lines,
the observation that triggered it. Someone reading this in a year should understand the
motivation without reconstructing the session it came from.

## Constraints

The decisions already made and the boundaries the work must respect: what must not change,
what must stay cheap, what must keep working, what is explicitly out of scope. Each one as
a rule with its reason — a constraint whose reason is missing gets argued away later.

### Task 1: outcome of the first slice

- [ ] Observable property that will be true when this is done.
- [ ] Another one, verifiable without reading the implementation.

## Post-Completion

Work that finishes the picture but does not belong to the executing agent: a live check
under conditions that cannot be arranged on demand, deployment to a second machine,
a measurement that needs a real workload.
```

Checkboxes live only inside `Task` sections. Anything outside them is context, not work —
an executor that ticks boxes will otherwise tick a constraint and consider it done.

## Acceptance criteria

Each box states an observable property, not an action:

```
Bad:  - [ ] Add a fixture for the empty case.
Good: - [ ] The empty case is covered by a fixture, and the suite fails with a
            non-zero exit code when that case regresses.
```

Durable acceptance belongs in a make target or a script, not only in the plan — the plan
freezes, the target keeps being runnable.

## Post-completion that never happens

If the closing condition for a post-completion item does not arrive — the window passed,
the machine was busy, the workload never ran — close the plan and move the item to the
backlog. The plan describes work that is done; a pending check is work that is alive, and
those are two different lists.
