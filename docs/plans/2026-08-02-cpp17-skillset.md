# C++17 skill set — slice 1

## Why

No authoritative skill set for modern C++ exists (checked 2026-08-02: samber
ships Go only; `crazyguitar/cppcheatsheet` is a WebFetch router to a website
plus a readability skill; `llnl/smith` encodes one project's house style;
everything else in the aggregators is the same `cpp-pro` cloned over and over).
Authority in C++ lives in the primary sources, not in someone else's skill, so
this set is built here from those sources.

Target profile: **C++17 as the baseline, ordinary desktop and service code.**
Not embedded (exceptions and RTTI are available, freestanding is out of scope),
not HPC/GPU.

Slice 1 is the six skills that change what the agent writes in every file. The
continuation is listed under Post-Completion and is not part of this plan.

## Baseline

Skills are written against **C++17**, for toolchains where C++17 is complete in
practice: GCC 9+, Clang 9+, MSVC 19.2x+. Linux/GCC is the primary platform and
Windows/MSVC is fully in scope. Apple Clang counts as a **limited** platform:
its library support carries availability annotations tied to the deployment
target, and wherever that changes the recommendation the skill must name the
constraint instead of staying silent about it.

C++17 is old enough that the language side is uniform, but the library side is
not. These are known rough edges the skills must name rather than gloss over —
each one verified against the primary source at writing time, not from memory:

- `<filesystem>` needs an extra link library on older GCC and Clang
  (`-lstdc++fs` / `-lc++fs`); find the exact version cutoff.
- `<execution>` parallel algorithms depend on TBB under libstdc++ and were
  absent from libc++ for a long time.
- `std::from_chars` shipped its integer overloads long before its
  floating-point ones.
- Apple Clang gates `<filesystem>` and `std::visit` on the macOS deployment
  target.

If the baseline is wrong, it is fixed in one place — here — before the run.

## Constraints

1. **Skills are in English.** Repo rule (`CLAUDE.md`, `docs/conventions.md`):
   triggering depends on an English `description`. This repo is public, so
   plans and docs are in English as well.
2. **Form is router + `references/`.** `SKILL.md` carries what is needed every
   time (aim for 120–180 lines, hard ceiling 500); tables, walkthroughs and
   long examples move into `references/*.md`, and every link states the
   condition for reading it. No duplication between the body and references.
3. **Invent nothing.** Repo rule: a wrong flag in a skill is repeated by the
   agent every single time it fires. Every claim about a feature being
   available, a compiler version, a flag or a name from the standard library is
   checked against the primary source at the moment of writing — cppreference
   (including its compiler support page), the C++ Core Guidelines, the
   clang-tidy / clang-format / CMake documentation. Verify, do not recall.
4. **The C++17 boundary is a mandatory topic.** Under this baseline the
   following are **not available**, and a skill that offers any of them as
   "modern C++" is considered broken:
   - C++20: `std::span`, ranges and view adapters, `std::format`, `operator<=>`,
     concepts and `requires`, designated initializers, `std::jthread` and
     `std::stop_token`, `contains()` on associative containers, `starts_with` /
     `ends_with` on strings, `std::ssize`, `std::bit_cast`, `constinit` /
     `consteval`, `std::atomic_ref`, modules, coroutines.
   - C++23: `std::expected`, `std::print`, `std::generator`, `std::flat_map`,
     `std::mdspan`, `std::stacktrace`, `views::zip`, `views::enumerate`.

   The mirror image matters just as much, because a model reaches either too
   far forward or too far back: C++17 **does** give `std::optional`,
   `std::variant`, `std::any`, `std::string_view`, `<filesystem>`, structured
   bindings, `if constexpr`, class template argument deduction, fold
   expressions, inline variables, `[[nodiscard]]` / `[[maybe_unused]]` /
   `[[fallthrough]]`, guaranteed copy elision, `std::invoke` / `std::apply`,
   `std::scoped_lock` and `std::shared_mutex`, `std::byte`, nested namespace
   definitions, `std::clamp` / `std::size` / `std::data` / `std::empty`,
   `try_emplace` / `insert_or_assign`, and `std::from_chars` / `std::to_chars`.
   Code written down to C++11 where C++17 has a direct answer is as much a
   defect as code reaching forward into C++20.
5. **Boundaries between skills are explicit.** Every `description` carries a
   clause naming what the skill does NOT cover and where to go instead. The six
   must not all fire at once on the same `.cpp` file.
6. **Rule > example > failure mode.** The body format from
   `docs/conventions.md`: the rule first, then a minimal correct example, then
   the failure mode it prevents. Imperative, never "consider".
7. **3–5 evals per skill**, with the `trap` written first. If the concrete
   mistake a model makes without the skill cannot be named, the section or the
   skill is redundant.
8. **Leave the existing `cpp-russian` alone.** It is about the language of
   exposition, not about writing code; there must be no overlap.

## Acceptance

- `python3 scripts/validate.py` — 7 skill(s), 0 errors, 0 warnings.
- `shellcheck scripts/*.sh` — clean (this is CI's second step).
- No `SKILL.md` body longer than 500 lines.
- Every `description` is 1024 characters or fewer (measure with `wc -m`, not
  `wc -c`).
- Grepping all six skills for `std::span`, `std::format`, `<=>`, `ranges::`,
  `std::expected`, `std::print`, `std::mdspan` and `std::flat_map` finds them
  only in an explicit "not available under our baseline" context.
- Commits follow Conventional Commits scoped by skill
  (`feat(cpp-build): add preset section`), one commit per skill.

### Task 1: cpp-code-style

- [ ] `skills/cpp-code-style` created (`scripts/new-skill.sh cpp-code-style`)
- [ ] Body covers: naming (types / functions / members / constants) with one
      scheme picked explicitly and a note that foreign code is not renamed;
      header organisation (`#pragma once`, what belongs in the header and what
      stays in the `.cpp`); include order and grouping, include-what-you-use;
      const-correctness and `constexpr` by default; where `auto` helps
      readability and where it hides the type; namespace structure, nested
      namespace definitions, and the ban on `using namespace` in headers;
      `[[nodiscard]]` on functions whose result must not be dropped
- [ ] `references/clang-format.md` exists — a working `.clang-format` plus a
      `.clang-tidy` with a check set (`cppcoreguidelines-*`, `bugprone-*`,
      `modernize-*`, and the noisy ones explicitly disabled), check names
      verified against the clang-tidy documentation
- [ ] The tooling config is consistent with the C++17 baseline: the standard is
      stated where the tools take one, and any `modernize-*` check that
      rewrites code into C++20 constructs is disabled or called out
- [ ] `description` sends resource-ownership questions to
      `cpp-memory-ownership` and build wiring to `cpp-build`
- [ ] 3–5 evals with a `trap`
- [ ] `python3 scripts/validate.py` passes

### Task 2: cpp-memory-ownership

- [ ] `skills/cpp-memory-ownership` created
- [ ] Body covers: ownership expressed in the signature (by value, `T&`,
      `const T&`, `T*` as an optional non-owning parameter, `unique_ptr` as
      transfer of ownership, `shared_ptr` only for genuinely shared lifetime,
      `string_view` as a non-owning view); RAII, the rule of zero, and when the
      rule of five is unavoidable; `std::move` — what it does and what it does
      not, including the usual mistakes (moving from a const object, moving a
      returned local, use after move); lifetime rules for `string_view` —
      dangling views over temporaries and over the result of `std::string`
- [ ] The absence of `std::span` under C++17 is addressed head-on: what to pass
      instead for a contiguous range, and whether pulling in a third-party span
      is worth it — a verdict with a reason, not a menu
- [ ] `references/lifetime-traps.md` exists — a walkthrough of dangling
      references, including lambda captures by reference and references to
      container elements after reallocation
- [ ] `description` explicitly claims ownership and lifetime, and sends
      container and algorithm choice to `cpp-modern-stdlib`
- [ ] 3–5 evals with a `trap`; at least one about a `string_view` over a
      temporary, at least one about `unique_ptr` being swapped for `shared_ptr`
- [ ] `python3 scripts/validate.py` passes

### Task 3: cpp-modern-stdlib

- [ ] `skills/cpp-modern-stdlib` created
- [ ] Body covers what replaces what under C++17: `string_view` instead of
      `const std::string&` parameters, `std::optional` and `std::variant`
      instead of sentinel values and unions, structured bindings instead of
      `.first` / `.second` and `std::tie`, `if constexpr` instead of tag
      dispatch and SFINAE for the simple cases, class template argument
      deduction instead of `make_*` helpers (and where a `make_*` is still
      required), `<chrono>` instead of integers with implied units,
      `<filesystem>` instead of string paths, `std::clamp` / `std::size`,
      `try_emplace` / `insert_or_assign`, `std::from_chars` instead of
      `stoi` / `sscanf`
- [ ] The C++17 boundary is spelled out as an explicit list: what looks modern
      but is unavailable under the baseline, and what to do instead. The three
      real gaps — formatting (no `std::format`), contiguous views (no
      `std::span`), pipelines (no ranges) — each get a named verdict with a
      justification, including whether a third-party dependency earns its place
- [ ] `references/availability.md` exists — a table of feature → standard →
      the GCC/Clang/MSVC version where it actually works, rows checked against
      the compiler support page on cppreference; separate rows for the library
      rough edges listed in the Baseline section above
- [ ] 3–5 evals with a `trap`; at least one catching a `std::format` or
      `std::span` suggestion under C++17, at least one catching C++11-era code
      written where C++17 has a direct answer
- [ ] `python3 scripts/validate.py` passes

### Task 4: cpp-error-handling

- [ ] `skills/cpp-error-handling` created
- [ ] Body covers: exceptions as the default choice for this profile and what
      exactly makes them acceptable here; what to throw (a hierarchy rooted at
      `std::exception`, when a custom type is warranted) and what not to throw;
      `noexcept` as a contract rather than decoration, and the cost of breaking
      it; catching by `const&` and never swallowing; the boundaries where an
      exception must be caught (main, a thread, a callback from a C API, a
      destructor); `std::error_code` and `system_error` for expected I/O
      failures; invariants and asserts versus input validation
- [ ] `std::expected` is covered as **unavailable** (C++23), with what stands in
      for it under C++17 when a result-as-value really is the right shape —
      `std::optional` for value-or-nothing, `std::variant` for value-or-error,
      and a stated position on third-party alternatives
- [ ] `references/exception-safety.md` exists — the guarantee levels
      (basic / strong / nothrow), copy-and-swap, where the strong guarantee
      comes from and when it is not needed
- [ ] 3–5 evals with a `trap`
- [ ] `python3 scripts/validate.py` passes

### Task 5: cpp-build

- [ ] `skills/cpp-build` created
- [ ] Body covers: CMake driven by targets rather than global variables
      (`target_*`, `PUBLIC` / `PRIVATE` / `INTERFACE`, no `include_directories`
      and no editing `CMAKE_CXX_FLAGS` at the top level); setting the standard
      through `target_compile_features` / `cxx_std_17` instead of a hand-written
      `-std=`; `CMakePresets.json` as the entry point (configure / build / test
      presets, a separate sanitizer preset); a warning set and `-Werror` applied
      to your own targets only, never to dependencies; pulling in dependencies
      (`find_package` versus `FetchContent`, and where vcpkg and conan fit)
- [ ] The linking requirements C++17 imposes are covered: the extra
      `<filesystem>` library on older toolchains, and how to express it in CMake
      without hardcoding it for every compiler
- [ ] `assets/` holds a working skeleton — `CMakeLists.txt` and
      `CMakePresets.json` — that actually configures, verified by running
      `cmake --preset`, not by eye
- [ ] The minimum CMake version and every command and property used are checked
      against the CMake documentation
- [ ] 3–5 evals with a `trap`; at least one about `CMAKE_CXX_FLAGS` at the top
      level
- [ ] `python3 scripts/validate.py` passes

### Task 6: cpp-testing

- [ ] `skills/cpp-testing` created
- [ ] Body covers: picking a framework (GoogleTest versus Catch2 — decided by
      concrete properties of the project, not "both are fine"); test structure,
      fixtures, parameterisation; registering with CTest and running a subset;
      when a mock is needed and when it is noise; sanitizers (ASan / UBSan /
      TSan) as part of the test run — flags checked against the compiler
      documentation, with the note that ASan and TSan cannot be built together
- [ ] The framework version is pinned against the C++17 baseline: the minimum
      standard each candidate version requires is verified, so the skill does
      not recommend a release that demands a newer standard
- [ ] `references/sanitizers.md` exists — what a typical sanitizer report turns
      into and where to start reading it
- [ ] `description` sends presets and build wiring to `cpp-build`
- [ ] 3–5 evals with a `trap`
- [ ] `python3 scripts/validate.py` passes

### Task 7: boundary check

- [ ] The six `description` fields are read back to back; for every pair that
      could fire on the same file, the owner is decided and reflected in the
      "does NOT cover" clause
- [ ] No section is repeated in two skills; a duplicate is removed from
      whichever skill it is secondary to and replaced by a pointer
- [ ] Sweep across all six: `wc -m` of every `description` is ≤ 1024, `wc -l` of
      every `SKILL.md` is ≤ 500
- [ ] Grep for the out-of-baseline names (`std::span`, `std::format`, `<=>`,
      `ranges::`, `std::expected`, `std::print`, `std::mdspan`,
      `std::flat_map`) — every occurrence sits in a "not available under C++17"
      context
- [ ] `python3 scripts/validate.py` and `shellcheck scripts/*.sh` pass

## Post-Completion

Done by hand, outside the run:

- `scripts/link.sh` plus a live session in a real C++ project: run the eval
  prompts verbatim and check that the skill *fires* before judging the quality
  of its output. Under-triggering is fixed in the `description`, not the body.
- Decide whether to link the set into the agent skills directory permanently.

What comes after this slice is not listed here — it lives in
[docs/plans/backlog/cpp-skillset-slice-2.md](backlog/cpp-skillset-slice-2.md)
and stays visible when this plan moves into `completed/`.
