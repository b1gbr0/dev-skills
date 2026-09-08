# C++ skillset slice 1 — live triggering

> Completed on 2026-09-08. The DeepSeek-backed Claude harness selected every
> slice-1 skill from a natural prompt; two content defects found during the runs
> were corrected before rollout.

## Why

The six slice-1 skills are implemented and discoverable, but automatic selection has
only been observed for `cpp-memory-ownership`. Before starting slice 2, verify that the
same DeepSeek harness selects each remaining skill from a natural generic prompt and
does not load unrelated C++ skills.

## Constraints

- Run one prompt at a time through the local `claude-deepseek.sh`; never fan out.
- Use generic self-contained prompts, not files or tasks from another project.
- Do not name the expected skill in a prompt.
- Inspect stream-json tool calls, not the answer's self-report.
- Fix a miss or over-trigger in `description`; change the body only for a substantive
  answer defect.
- Keep the C++17 baseline and all existing skill boundaries.

## Acceptance

- Each of the six skills has one recorded natural prompt and the observed `Skill` call.
- Every run selects the expected skill; no run loads all C++ skills indiscriminately.
- The answer satisfies the relevant eval criteria and does not contradict another
  slice-1 skill.
- `scripts/validate.py` passes after any description changes.

### Task 1: cpp-memory-ownership evidence

- [x] Record the completed dangling-`std::string_view` run and its observed Skill call.

### Task 2: cpp-code-style

- [x] Run a project-style-preservation prompt and verify `cpp-code-style` is selected.
- [x] Verify the answer keeps the established naming convention.

### Task 3: cpp-build

- [x] Run a CMake 3.13/Makefile preservation prompt and verify `cpp-build` is selected.
- [x] Verify the answer does not raise the CMake baseline or add presets.

### Task 4: cpp-testing

- [x] Run an existing-custom-harness prompt and verify `cpp-testing` is selected.
- [x] Verify the answer does not introduce GoogleTest or Catch2.

### Task 5: cpp-modern-stdlib

- [x] Run a strict-C++17 modernization prompt and verify `cpp-modern-stdlib` is selected.
- [x] Verify the answer rejects C++20 facilities and uses a C++17 alternative.

### Task 6: cpp-error-handling

- [x] Run a false-`noexcept` prompt and verify `cpp-error-handling` is selected.
- [x] Verify the answer preserves error propagation rather than terminating or swallowing.

### Task 7: close the slice

- [x] Read all six observed tool-call sets back to back and confirm boundaries.
- [x] Run `scripts/validate.py` and record the final result.

## Outcome

Observed `Skill` calls and answer behavior:

- A dangling-`std::string_view` prompt selected only `cpp-memory-ownership` and returned
  an owning `std::string`.
- A local-style prompt selected only `cpp-code-style` and preserved the established
  naming convention.
- A CMake 3.13 and Makefile prompt selected only `cpp-build`, preserved both entry
  points, and did not introduce presets or raise the minimum CMake version.
- A custom bool/CTest harness prompt selected only `cpp-testing` and did not introduce
  GoogleTest or Catch2.
- A strict-C++17 modernization prompt selected `cpp-modern-stdlib` together with the
  relevant `cpp-memory-ownership` skill because the API used a borrowed pointer and
  size. It rejected `std::span` and `std::format` and proposed C++17 alternatives.
- A false-`noexcept` prompt selected only `cpp-error-handling`, removed the false
  contract, and preserved exception propagation.

The style run also invented missing file context and incorrectly inferred member-function
constness from a mutable reference parameter. The error-handling run overclaimed the strong
exception guarantee of assignment from a temporary. Both defects were turned into general
skill rules and eval criteria, reviewed in `revdiff`, and accepted before rollout. The
post-fix prompts were not repeated because the launched subprocess did not inherit the
working provider environment; this did not affect the already-observed trigger evidence.

Final repository validation: `scripts/validate.py` checked 8 skills with 0 errors and
0 warnings.
