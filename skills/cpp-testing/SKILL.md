---
name: cpp-testing
description: "C++17 testing with GoogleTest or Catch2, CTest registration and filtering, focused fixtures and parameterized tests, mock-versus-fake decisions, and separate ASan/UBSan/TSan runs. Use when adding or reviewing *_test.cpp files, choosing a C++ test framework, configuring gtest_discover_tests or catch_discover_tests, debugging sanitizer reports, or deciding what to mock. Does NOT own general CMake/preset wiring (cpp-build), production error policy (cpp-error-handling), or benchmark methodology (cpp-performance)."
user-invocable: true
license: MIT
compatibility: C++17; GoogleTest v1.18.0 or Catch2 v3.16.0; CTest through CMake 3.20+.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# C++ Testing

Test observable contracts at the cheapest useful boundary. Keep tests deterministic,
small enough to diagnose from one failure, and registered with CTest so developers and
CI use the same entry point. Use sanitizers as separate test configurations, not as a
substitute for assertions.

## Choose one framework for concrete reasons

For a new desktop or service project, default to **GoogleTest** when any of these are
true:

- GoogleMock is needed for a narrow external boundary;
- typed, value-parameterized, or death tests are important;
- the organization already has GoogleTest tooling and conventions.

Choose **Catch2** when the project wants compact section- or scenario-oriented tests,
needs no integrated mocking framework, and its contributors already prefer Catch2's
assertion/reporting style.

Do not create a local assertion framework. Do not add both libraries to one test suite
without a migration plan.

Pinned versions for this C++17 baseline:

- GoogleTest `v1.18.0` requires C++17.
- Catch2 `v3.16.0` requires C++14 and therefore works under C++17.

Re-check the upstream requirement before changing either pin; “latest” is not a
reproducible dependency version.

## Register every test with CTest

GoogleTest:

```cmake
add_executable(project_tests
    parser_test.cpp
    repository_test.cpp
)
target_compile_features(project_tests PRIVATE cxx_std_17)
target_link_libraries(project_tests PRIVATE project_core GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(project_tests)
```

Catch2 with `FetchContent`:

```cmake
add_executable(project_tests parser_test.cpp)
target_compile_features(project_tests PRIVATE cxx_std_17)
target_link_libraries(project_tests PRIVATE project_core Catch2::Catch2WithMain)

list(APPEND CMAKE_MODULE_PATH "${catch2_SOURCE_DIR}/extras")
include(Catch)
catch_discover_tests(project_tests)
```

`Catch.cmake` is not made discoverable merely by creating the imported targets. The
module path depends on how Catch2 was acquired; the snippet above uses the
`catch2_SOURCE_DIR` populated by `FetchContent`. For an installed package, add its
installed CMake-module directory instead.

Dependency acquisition, presets, and sanitizer target options belong to `cpp-build`.
This skill requires only that the framework is pinned and exposed through imported
CMake targets.

Run through CTest:

```sh
ctest --preset dev --output-on-failure
ctest --preset dev -R 'Parser' --output-on-failure
ctest --preset dev -L integration --output-on-failure
```

Failure mode this prevents: a test passes when invoked directly but is absent from the
CI test graph.

## Test one contract per case

Name the behavior and condition, not the implementation function being exercised:

```cpp
TEST(Parser, RejectsPortAboveMaximum) {
    const auto result = parse_endpoint("localhost:70000");

    ASSERT_TRUE(std::holds_alternative<ParseError>(result));
    EXPECT_EQ(std::get<ParseError>(result), ParseError::PortOutOfRange);
}
```

Use `ASSERT_*` only when the rest of the test cannot proceed safely; use `EXPECT_*` to
report independent mismatches in one run. Keep arrange, act, and assert visible without
turning them into mandatory comments.

Test public behavior. Reach private state only through observable effects; making a
member public or adding friendship solely for a test couples the suite to every
refactor.

## Use fixtures for lifecycle, not convenience inheritance

A fixture earns its place when several tests require the same non-trivial setup and
teardown. Keep state minimal and reset for every test. Prefer free helper functions or
small builders for reusable data.

```cpp
class RepositoryTest : public ::testing::Test {
protected:
    TemporaryDirectory directory;
    Repository repository{directory.path()};
};
```

Do not hide the behavior under test behind a deep fixture hierarchy or perform
assertions in constructors and destructors.

## Parameterize repeated behavior

Use value-parameterized tests for the same contract across input/output rows. Use typed
tests only when several types must satisfy the same interface contract. A table is not
an excuse to combine unrelated branches into one opaque test.

```cpp
class ValidPortTest : public ::testing::TestWithParam<int> {};

TEST_P(ValidPortTest, AcceptsPort) {
    EXPECT_TRUE(is_valid_port(GetParam()));
}

INSTANTIATE_TEST_SUITE_P(
    Boundaries,
    ValidPortTest,
    ::testing::Values(1, 80, 443, 65535)
);
```

## Mock only a real boundary

A mock is justified when a dependency performs external side effects, has
non-deterministic timing, is prohibitively slow, or must be forced through rare failure
paths. Prefer a small interface at that boundary.

Use a real value, in-memory fake, or temporary filesystem/database when it is cheap and
more faithful. Do not mock containers, value objects, the class under test, or every
internal collaborator. A test that repeats the implementation's call sequence blocks
safe refactoring without protecting behavior.

Verify only interactions that are part of the contract. Avoid blanket expectations for
incidental getter calls or ordering unless order itself matters.

## Separate sanitizer configurations

Run at least these GCC/Clang configurations:

- AddressSanitizer plus UndefinedBehaviorSanitizer for memory and undefined behavior;
- ThreadSanitizer in its own build for data races.

Never combine ASan and TSan in one binary; their runtimes are incompatible. Keep a
normal unsanitized test run because sanitizer builds change timing and resource usage.
Read [references/sanitizers.md](references/sanitizers.md) when adding flags, interpreting
a report, suppressing third-party findings, or diagnosing a flaky sanitizer-only test.

## Make failure paths controllable

Inject the narrow operation that can fail: clock, filesystem call, transport, or
repository boundary. Then test the documented post-failure state, not only the returned
error.

For exception-safety guarantees, assert that resources remain owned, invariants hold,
and old state is preserved when the strong guarantee is promised. Use
`cpp-error-handling` for the production policy itself.

## Keep tests deterministic

- Do not sleep to wait for concurrency; wait on an explicit signal with a timeout.
- Seed randomized tests explicitly and print the seed on failure.
- Use temporary directories and unique resources; do not depend on developer state.
- Compare times with controlled clocks, not wall-clock delays.
- Isolate integration tests with CTest labels and explicit prerequisites.

A retry can collect evidence for a known flaky external system, but it must not turn a
non-deterministic unit test green.

## Related skills

- Use `cpp-build` for CMake targets, dependency pins, presets, and sanitizer flags.
- Use `cpp-error-handling` for exception boundaries and failure contracts.
- Use `cpp-memory-ownership` for lifetime defects found by sanitizers.
- Use `cpp-performance` for benchmarks when that later skill is available.
