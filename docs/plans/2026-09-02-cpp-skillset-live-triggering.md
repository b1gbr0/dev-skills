# C++ skillset slice 1 — live triggering

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

- [ ] Record the completed dangling-`std::string_view` run and its observed Skill call.

### Task 2: cpp-code-style

- [ ] Run a project-style-preservation prompt and verify `cpp-code-style` is selected.
- [ ] Verify the answer keeps the established naming convention.

### Task 3: cpp-build

- [ ] Run a CMake 3.13/Makefile preservation prompt and verify `cpp-build` is selected.
- [ ] Verify the answer does not raise the CMake baseline or add presets.

### Task 4: cpp-testing

- [ ] Run an existing-custom-harness prompt and verify `cpp-testing` is selected.
- [ ] Verify the answer does not introduce GoogleTest or Catch2.

### Task 5: cpp-modern-stdlib

- [ ] Run a strict-C++17 modernization prompt and verify `cpp-modern-stdlib` is selected.
- [ ] Verify the answer rejects C++20 facilities and uses a C++17 alternative.

### Task 6: cpp-error-handling

- [ ] Run a false-`noexcept` prompt and verify `cpp-error-handling` is selected.
- [ ] Verify the answer preserves error propagation rather than terminating or swallowing.

### Task 7: close the slice

- [ ] Read all six observed tool-call sets back to back and confirm boundaries.
- [ ] Run `scripts/validate.py` and record the final result.
