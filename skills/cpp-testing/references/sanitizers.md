# Sanitizer builds and reports

Sanitizers instrument the program and runtime to expose memory errors, undefined
behavior, and data races. Run them in separate build directories with debug information
and the same tests used by the normal build.

## AddressSanitizer plus UndefinedBehaviorSanitizer

For GCC or Clang, apply flags at compile and link time:

```cmake
add_library(project_asan_ubsan INTERFACE)
target_compile_options(project_asan_ubsan INTERFACE
    -fsanitize=address,undefined
    -fno-omit-frame-pointer
    -g
)
target_link_options(project_asan_ubsan INTERFACE
    -fsanitize=address,undefined
)
```

Link the interface target privately to every owned target participating in the test.
Instrumenting only the test executable while leaving the project library uninstrumented
misses defects inside that library.

Useful Linux CI defaults:

```sh
ASAN_OPTIONS=halt_on_error=1:detect_leaks=1
UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
ctest --preset asan-ubsan --output-on-failure
```

Leak detection availability differs by platform. Verify the runtime rather than
assuming an option accepted on Linux behaves identically on Apple platforms.

## ThreadSanitizer

Use a separate build:

```cmake
add_library(project_tsan INTERFACE)
target_compile_options(project_tsan INTERFACE
    -fsanitize=thread
    -fno-omit-frame-pointer
    -g
)
target_link_options(project_tsan INTERFACE -fsanitize=thread)
```

```sh
TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1
ctest --preset tsan --output-on-failure
```

Never combine `-fsanitize=thread` with `-fsanitize=address`. The runtimes are
incompatible. A TSan run is slower and changes scheduling, so retain deterministic
synchronization in tests and keep a normal build in CI.

## MSVC boundary

MSVC supports AddressSanitizer through `/fsanitize=address` on supported targets, but
the GCC/Clang UBSan and TSan flags above are not portable to MSVC. Use a separate MSVC
preset and official compiler options rather than translating flags by spelling.
The skillset's primary sanitizer profile is Linux with GCC or Clang; MSVC is documented,
not locally verified.

## Read the first report first

One invalid write can create many later symptoms. Start with the first sanitizer report
in process order:

1. identify the error class and accessed address;
2. read the top project-owned frame where the invalid operation occurs;
3. find the allocation or object-construction stack;
4. find the free, destruction, or competing-access stack;
5. reconstruct the ownership or happens-before relationship;
6. add a focused regression test before changing code.

Do not start by editing the last crash frame when ASan already reports an earlier
use-after-free.

## Typical report meanings

| Report | First question |
|---|---|
| heap-use-after-free | Which owner destroyed or reallocated the storage? |
| stack-use-after-scope | Which pointer, reference, view, or lambda capture escaped? |
| heap-buffer-overflow | Which bound or element count disagrees with the allocation? |
| signed-integer-overflow | Is overflow forbidden, or should the operation use an unsigned/wider checked type? |
| data race | Which two accesses conflict, and what synchronization should order them? |
| lock-order-inversion | Which global lock order is violated? |

Load `cpp-memory-ownership` for dangling storage and `cpp-concurrency` for the final
synchronization design when that skill is available.

## Symbolization

Build with debug information and keep frame pointers. Ensure `llvm-symbolizer` or the
compiler's supported symbolizer is available in CI. An unsymbolized address-only report
is not sufficient evidence for a fix.

Do not strip the test binary before sanitizer execution. Preserve the exact binary and
log as CI artifacts when a failure is intermittent.

## Suppressions

Fix project-owned findings. A suppression is acceptable only for a confirmed issue in
third-party or platform code that cannot be upgraded immediately. Scope it to the
narrowest symbol or library and record:

- the upstream issue;
- affected versions and platforms;
- why the call remains safe for this project;
- the condition for removing the suppression.

Never suppress a whole sanitizer or wildcard all project namespaces to make CI green.

## Reproducing TSan failures

Do not replace synchronization with sleeps. Expose explicit barriers or latches in the
test harness so the conflicting operations overlap deterministically. Under C++17,
use a condition variable or test-only barrier implementation rather than `std::latch`
or `std::barrier`, which are C++20.

Record the random seed, worker count, and iteration count. A larger loop can improve
detection probability, but the regression test should still assert a behavioral or
synchronization contract.

## CI matrix

A practical minimum matrix contains:

- normal Debug tests;
- normal Release tests;
- ASan+UBSan Debug tests;
- TSan Debug tests on Linux;
- one supported compiler/standard-library combination per portability promise.

Run sanitizers on project tests, not on an unrelated smoke binary. Keep framework and
sanitizer pins in build configuration owned by `cpp-build`.

Sources:

- <https://clang.llvm.org/docs/AddressSanitizer.html>
- <https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html>
- <https://clang.llvm.org/docs/ThreadSanitizer.html>
- <https://learn.microsoft.com/cpp/sanitizers/asan>
