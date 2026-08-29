---
name: cpp-modern-stdlib
description: "Modern C++ standard-library and language choices under a strict C++17 baseline: optional, variant, any, string_view, filesystem, chrono, charconv, structured bindings, if constexpr, CTAD, fold expressions, and associative-container insertion APIs. Use when replacing sentinel values or legacy C/C++ APIs, choosing a container or algorithm, reviewing code for C++17 modernization, or checking feature availability across GCC/libstdc++, Clang/libc++, and MSVC. Does NOT permit C++20/23 facilities, own lifetime policy (cpp-memory-ownership), or configure CMake (cpp-build)."
user-invocable: true
license: MIT
compatibility: C++17; GCC 9+, Clang 9+, or MSVC 19.2x, with library-specific caveats documented separately.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# Modern C++17 Standard Library

Use the strongest facility that is actually in C++17. Code written down to C++11
when C++17 has a direct answer is maintenance debt; code reaching forward into C++20
is a build defect. Check library support separately from compiler-language support.

## Model absence explicitly

Return `std::optional<T>` for value-or-nothing instead of a magic value, null output
pointer, or separate success flag:

```cpp
std::optional<User> find_user(UserId id);

if (auto user = find_user(id)) {
    render(*user);
}
```

Use `std::variant<A, B, ...>` for a closed set of alternatives and `std::visit` to
handle every case. Use `std::any` only when the set of stored types is intentionally
open and runtime type checks are part of the contract.

Do not use `std::optional` to hide actionable failure information. Error policy and
`std::error_code` belong to `cpp-error-handling`.

Failure mode this prevents: `-1`, empty strings, and null pointers acquire several
incompatible meanings across call sites.

## Borrow text without forcing allocation

Accept `std::string_view` when a function reads character data during the call and
does not retain it:

```cpp
bool has_prefix(std::string_view text, std::string_view prefix);
```

This accepts strings, literals, and substrings without allocation. It is not a drop-in
replacement for every `const std::string&`: a callee that stores the data needs an
owning `std::string`. Load `cpp-memory-ownership` for lifetime decisions.

C++17 `std::string_view` has no `starts_with` or `ends_with`; those are C++20.
Use `compare`, `substr`, or a small named helper rather than calling unavailable APIs.

## Use C++17 language features directly

Prefer structured bindings for pair- and tuple-like results:

```cpp
for (const auto& [name, endpoint] : endpoints) {
    connect(name, endpoint);
}
```

Use `if constexpr` when a compile-time branch would otherwise require simple tag
dispatch or SFINAE. Use class template argument deduction when constructor arguments
identify the class specialization, fold expressions for parameter-pack reductions,
and inline variables for header-defined constants.

```cpp
std::lock_guard lock{mutex};
std::pair endpoint{"localhost", 443};
```

Keep `std::make_unique<T>(args...)` and `std::make_shared<T>(args...)`: constructor
arguments describe `T`, but they do not let deduction infer the pointee type, and the
helpers keep allocation and construction in one expression.

```cpp
template <typename... Values>
auto sum(Values... values) {
    return (values + ...);
}

inline constexpr std::string_view kProtocol = "v1";
```

Do not force `if constexpr` into an interface that does not need a template. Template
architecture belongs to `cpp-templates-concepts` when that later skill is available.

## Represent time and paths as types

Use `<chrono>` durations and time points instead of integers with implied units:

```cpp
void set_timeout(std::chrono::milliseconds timeout);
set_timeout(std::chrono::seconds{5});
```

Use `std::filesystem::path` and filesystem operations instead of concatenating path
strings. Check `std::error_code` overloads when failure is expected and exceptions are
not the chosen shape.

Older standard libraries may need a separate filesystem link library. Read
[references/availability.md](references/availability.md) before promising support on
GCC 8, LLVM 8, Apple platforms, or mixed compiler/stdlib combinations.

## Prefer typed parsing with `<charconv>`

Use integer `std::from_chars` for locale-independent, allocation-free parsing when the
library version supports it:

```cpp
std::optional<int> parse_port(std::string_view text) {
    int port = 0;
    const auto [ptr, error] =
        std::from_chars(text.data(), text.data() + text.size(), port);
    if (error != std::errc{} || ptr != text.data() + text.size()) {
        return std::nullopt;
    }
    return port;
}
```

Do not assume floating-point overloads arrived with integer overloads. GCC/libstdc++,
libc++, and MSVC shipped them in different releases; consult the availability table.
For unsupported floating parsing, choose one project-wide fallback rather than
silently switching to locale-sensitive `std::stod` or `std::sscanf`.

## Use C++17 container operations

Use the operation that states the update policy:

- `try_emplace` constructs a mapped value only when the key is absent.
- `insert_or_assign` inserts a missing key or replaces the existing mapped value.
- `std::clamp` expresses bounded values directly.
- `std::size`, `std::data`, and `std::empty` work uniformly with containers and arrays.

```cpp
auto [it, inserted] = sessions.try_emplace(id, endpoint, timeout);
if (!inserted) {
    it->second.refresh();
}
```

Do not replace every loop with an algorithm when the loop carries clearer domain
intent. Choose algorithms where their name states the operation and the iterator
boundaries remain readable.

## Know the C++17 ceiling

The following are unavailable and must not appear as C++17 recommendations:

- C++20: `std::span`, ranges and views, `std::format`, `operator<=>`, concepts,
  `requires`, designated initializers, `std::jthread`, `std::stop_token`,
  `contains`, `starts_with`, `ends_with`, `std::ssize`, `std::bit_cast`,
  `constinit`, `consteval`, `std::atomic_ref`, modules, and coroutines.
- C++23: `std::expected`, `std::print`, `std::generator`, `std::flat_map`,
  `std::mdspan`, `std::stacktrace`, `views::zip`, and `views::enumerate`.

When the gap matters, use these defaults:

### Formatting: use `{fmt}` for non-trivial formatting

`{fmt}` is the direct predecessor of `std::format`, mature under C++17, and clearer
than assembling complex output with stream state. For one simple concatenation,
ordinary string operations or a stream are sufficient; do not add a dependency for a
single trivial call.

### Contiguous views: use pointer-and-size unless the API is view-heavy

For one internal function, pass `const T*` plus `std::size_t`. If contiguous borrowed
ranges are pervasive across a public API, adopt `gsl::span` consistently. Do not write
a home-grown span. Ownership and lifetime rules stay in `cpp-memory-ownership`.

### Pipelines: use algorithms and named helpers

Do not add range-v3 solely to imitate C++20 syntax. Under this baseline, iterator-based
standard algorithms plus small named predicates are the default. A project already
committed to range-v3 may keep it as an explicit dependency, but the skill does not
introduce it opportunistically.

## Related skills

- Use `cpp-memory-ownership` for borrowed storage, views, and smart pointers.
- Use `cpp-error-handling` for exceptions, error codes, and value-or-error designs.
- Use `cpp-build` for compile features, linking, and dependency wiring.
- Use `cpp-code-style` for naming, headers, and formatting.
