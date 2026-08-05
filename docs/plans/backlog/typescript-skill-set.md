# TypeScript skill set

The TypeScript skills currently in use — code style, API conventions, Jest
conventions, Vitest conventions — come from `otwld/cortex-skills`, and that
source is dead for our purposes: upstream migrated to its own Cortex format and
no longer ships `SKILL.md` at those paths. The last commit where they are still
installable is `6bad7c8b52217171127d971552f69c754733340e`; everything after it
is unusable. So those four are frozen forever at a June 2026 snapshot and will
never receive a fix.

That leaves one decision: adopt TypeScript into this repo as its own language
set, or drop it. This is a backlog item, not a plan — when it is picked up it
becomes `docs/plans/YYYY-MM-DD-typescript-skillset.md` and this file is deleted
in the same commit.

Adoption is not a copy. The frozen skills are a starting inventory of topics,
nothing more; anything kept has to be rewritten to this repo's rules — router
plus `references/`, an explicit "does NOT cover" clause in every `description`,
rule → example → failure mode, 3–5 evals with the `trap` written first, and
every claim verified against the primary source (the TypeScript handbook, the
`typescript-eslint` and Vitest/Jest documentation) rather than recalled.

Two things to settle while scoping it:

- **The baseline**, the same way the C++ set has one: which TypeScript version,
  and — the part that actually changes the advice — Node versus browser,
  ESM versus CJS, and whether `strict` is assumed on. A style skill written
  without that stated ends up hedging in every paragraph.
- **A house style norm.** A third-party skill for the Google TypeScript Style
  Guide was evaluated and rejected: forty-two lines with no rules in the body,
  just a pointer to the guide and a review-comment template written for
  Gerrit's changelist process. If that guide is wanted as the norm, it belongs
  as a section inside the own style skill, where the rules are actually
  written down, not as a wrapper around a link.

Independent of the C++ slices — it can be picked up before or after them.
