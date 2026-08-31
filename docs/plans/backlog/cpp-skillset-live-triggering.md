# C++ skillset live triggering is unverified

The six slice-1 skills are linked locally and their descriptions are visible to a fresh
session, but the eval prompts have not yet been run in a real C++ project to verify
automatic triggering and output quality. This check was deferred to avoid consuming the
remaining Claude allowance after the implementation review.

What to take into account:

- Run one agent/session at a time; do not fan out evals or let an agent delegate them.
- Use the existing prompts in each `evals/evals.json`, starting with one representative
  trap per skill.
- Verify that the relevant skill fires automatically and unrelated C++ skills do not all
  load for the same prompt.
- Fix under-triggering in `description`, not by making every router broader.
- Complete this check before promoting `cpp-skillset-slice-2.md` into an active plan.
