# C++ skill set — slice 2

Four more C++ skills, to be picked up once slice 1 is shipped and has been
through a live triggering session. This is a backlog item, not a plan: when it
is picked up it becomes `docs/plans/YYYY-MM-DD-cpp-skillset-slice-2.md` and
this file is deleted in the same commit.

Same baseline as slice 1, restated here so this file stands on its own:
**C++17**, ordinary desktop and service code, toolchains where C++17 is
complete in practice (GCC 9+, Clang 9+, MSVC 19.2x+), Linux/GCC primary, with
Apple Clang and MSVC secondary and unverified — named only where a
recommendation actually differs. Not embedded, not HPC/GPU. Same form (router +
`references/`), same rule about verifying every version, flag and stdlib name
against the primary source instead of recalling it.

- **`cpp-concurrency`** — threads and joining without `std::jthread`, mutex
  patterns and lock ordering, `std::atomic` and the memory orders, condition
  variables and the lost-wakeup shape, what `<execution>` parallel algorithms
  are actually usable for under this baseline.
- **`cpp-templates-concepts`** — `if constexpr`, CTAD, variadic templates and
  fold expressions, SFINAE and the C++17 stand-ins for concepts
  (`std::enable_if_t`, `void_t`, tag dispatch), and — the part that matters
  most — when a template is not needed at all.
- **`cpp-api-design`** — value semantics, what belongs in a public header,
  interface boundaries and ABI, PIMPL and its cost, designing for the caller
  rather than the implementation.
- **`cpp-performance`** — measuring before changing, google/benchmark and perf,
  data layout and cache behaviour, allocation patterns, and the optimisations
  that are folklore rather than measurement.

Splitting this into more than one plan is fine if it turns out to be too much
for one run — `cpp-concurrency` on its own is a plausible first plan, since it
is the one most likely to be needed while writing real code.

Beyond these four, nothing is committed. Whether the set grows past C++ at all
is an open question, not a plan.
