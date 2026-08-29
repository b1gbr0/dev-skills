---
name: cpp-error-handling
description: "C++17 error-handling policy for desktop and service code: choose exceptions versus error_code or value results, design exception types, catch at real boundaries, apply noexcept honestly, separate assertions from input validation, and preserve exception-safety guarantees. Use when writing or reviewing throw/catch, std::exception hierarchies, std::system_error, callbacks, thread entry points, destructors, or APIs returning errors. Does NOT manage resource ownership (cpp-memory-ownership), testing strategy (cpp-testing), or suggest C++23 std::expected."
user-invocable: true
license: MIT
compatibility: C++17; ordinary desktop and service code with exceptions and RTTI enabled.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# C++ Error Handling

Use exceptions for failures that prevent an operation from fulfilling its contract and
cannot be handled meaningfully at the immediate call site. RAII makes stack unwinding
the natural cleanup path for this profile. Use value-shaped errors only when absence or
failure is an expected branch that callers routinely inspect.

## Throw values with recognizable types

Throw exception objects by value and catch them by `const&`:

```cpp
if (config.port() <= 0) {
    throw std::invalid_argument("port must be positive");
}

try {
    start(config);
} catch (const std::system_error& error) {
    report_startup_failure(error);
}
```

Use the standard hierarchy when it communicates the category:

- `std::invalid_argument` and `std::out_of_range` for violated API value
  requirements that are checked at runtime;
- `std::runtime_error` for a simple runtime failure without structured system data;
- `std::system_error` when an operation fails with a meaningful `std::error_code`;
- a custom type derived from `std::exception` when callers need stable structured
  fields or a domain-specific catch boundary.

Do not throw integers, strings, pointers, or heap-allocated exceptions. Do not encode
information that callers need to branch on only inside `what()` text.

Failure mode this prevents: a caller must catch everything and parse prose to discover
what happened.

## Catch only where recovery or translation is possible

A catch block must do one of these:

1. recover and continue with a valid state;
2. translate the exception into a more appropriate abstraction while preserving the
   cause;
3. terminate the operation at a boundary and report the failure once.

```cpp
try {
    repository_.save(record);
} catch (const std::system_error& error) {
    std::throw_with_nested(StorageError{"saving record"});
}
```

Use `throw;` to rethrow the current exception. `throw error;` copies it and may slice a
derived exception.

Never write an empty catch block. Logging and rethrowing at every layer produces the
same failure many times; add context where the abstraction changes, then log at the
boundary that owns the operation.

## Establish exception boundaries

Exceptions must not escape places whose caller cannot participate in C++ unwinding:

- `main` or the application/service command boundary;
- the entry function of every `std::thread`;
- callbacks invoked through a C ABI or another API that forbids exceptions;
- destructors and cleanup callbacks, especially during stack unwinding.

```cpp
extern "C" int plugin_entry(Request* request) noexcept {
    try {
        return handle(*request);
    } catch (const std::exception& error) {
        report_plugin_error(error);
        return kPluginFailure;
    } catch (...) {
        report_unknown_plugin_error();
        return kPluginFailure;
    }
}
```

A thread exception that reaches the top calls `std::terminate`; catch inside the thread
and communicate failure through owned shared state, `std::promise`, or another explicit
channel.

## Treat `noexcept` as a contract

Mark a function `noexcept` only when it cannot allow an exception to escape and
termination is the correct response if the contract is broken. Do not add it as style
decoration.

```cpp
Widget(Widget&&) noexcept = default;
void swap(Widget& other) noexcept;
```

A truthful non-throwing move operation lets standard containers move elements during
reallocation while preserving their guarantees. If a called operation may throw,
either remove `noexcept`, handle the failure inside, or redesign the operation. An
exception leaving a `noexcept` function calls `std::terminate`.

Destructors should not emit exceptions. If cleanup can fail, provide an explicit
operation such as `close()` that reports failure before destruction; the destructor
performs best-effort cleanup without throwing.

## Use `error_code` for expected system failures

Use the non-throwing overload and inspect `std::error_code` when I/O failure is an
ordinary branch at that call site:

```cpp
std::error_code error;
const bool removed = std::filesystem::remove(path, error);
if (error) {
    return RemoveResult{error};
}
```

Use `std::system_error` when the same failure prevents the current operation from
fulfilling its contract and should propagate through exception handling:

```cpp
if (error) {
    throw std::system_error(error, "removing cache entry");
}
```

Do not ignore an `error_code` merely because the overload did not throw. Check it in
the same scope or return it in a documented result type.

## Separate absence, value errors, and exceptions

- Return `std::optional<T>` only for value-or-nothing when no explanation is needed.
- Use `std::variant<T, E>` when success-or-error is deliberately part of the value and
  callers are expected to branch on it.
- Throw when failure aborts the requested operation and local recovery is unavailable.

`std::expected` is C++23 and unavailable. Under C++17, prefer exceptions for this
profile; use `std::variant<T, E>` for the occasional value-shaped result. Adopt a
third-party expected implementation only when such results dominate the public API
and the project accepts that dependency consistently. Do not create a one-off
home-grown expected type.

## Assertions protect invariants, not inputs

Use `assert` for programmer errors and internal invariants that must already be true.
Validate user, network, file, and configuration input in release builds and report a
normal error.

```cpp
void RingBuffer::pop() {
    assert(!empty());  // internal precondition enforced by the caller
    // ...
}
```

Do not rely on an assertion for a condition that an external caller can violate;
`NDEBUG` removes it.

## Preserve state when operations fail

Choose and document the needed exception guarantee. Use RAII members, perform work in
temporary state, and commit only after all throwing operations succeed. Read
[references/exception-safety.md](references/exception-safety.md) when implementing a
mutating operation, swap, assignment, constructor, or cleanup path.

## Related skills

- Use `cpp-memory-ownership` for RAII owners, lifetime, and move semantics.
- Use `cpp-modern-stdlib` for `optional`, `variant`, and C++17 availability.
- Use `cpp-testing` for exercising failure paths and sanitizer runs.
- Use `cpp-code-style` for naming and mechanical formatting.
