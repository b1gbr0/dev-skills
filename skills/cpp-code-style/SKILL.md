---
name: cpp-code-style
description: "C++17 code style for ordinary desktop and service code: naming, header/source organization, include hygiene, const-correctness, judicious auto and constexpr, namespaces, and [[nodiscard]]. Use when writing or reviewing .h/.hpp/.cc/.cpp files, establishing a C++ style guide, or configuring clang-format and clang-tidy. Follow an existing project's style instead of renaming foreign code. Does NOT decide ownership or lifetime (use cpp-memory-ownership), standard-library design choices (cpp-modern-stdlib), build wiring (cpp-build), or Russian terminology (cpp-russian)."
user-invocable: true
license: MIT
compatibility: C++17; GCC 9+, Clang 9+, or MSVC 19.2x. Linux/GCC is the primary profile.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# C++ Code Style

Make intent visible before optimizing for compactness. First preserve the established
style of the repository; for a new codebase, use the concrete conventions below.
Formatting belongs to clang-format, mechanical checks to clang-tidy, and design
judgment stays in review.

## Preserve local consistency

Do not rename foreign code merely to match this skill. Read neighbouring headers and
sources first; a consistent local convention is cheaper than two competing styles.
Use this default only when the project has no clear convention:

| Entity | Convention | Example |
|---|---|---|
| type, enum | `PascalCase` | `RequestParser` |
| function, variable | `snake_case` | `parse_request` |
| private data member | trailing underscore | `socket_` |
| constant | `kPascalCase` | `kMaxRetries` |
| namespace | `snake_case` | `http_client` |
| macro | `UPPER_SNAKE_CASE` | `PROJECT_TRACE` |

Failure mode this prevents: a patch spends its review budget renaming stable code
instead of making the requested behavioral change.

## Keep interfaces in headers and implementation in sources

Use `#pragma once` for project headers under the supported toolchains. A header owns
public declarations and the complete definitions required by its consumers. Put
non-template implementation in a `.cpp` file; keep templates and other definitions
that must be visible at the point of instantiation in the header.

```cpp
// request_parser.hpp
#pragma once

#include <string_view>

namespace http {

class RequestParser {
public:
    [[nodiscard]] bool parse(std::string_view input);
};

}  // namespace http
```

```cpp
// request_parser.cpp
#include "request_parser.hpp"

#include <charconv>
#include <system_error>
```

Include what the file uses directly. Do not depend on transitive includes. Order
includes as: corresponding header, C++ standard library, third-party libraries,
then project headers, with one blank line between groups.

Failure mode this prevents: a header compiles only because an unrelated include
happens to precede it in one translation unit.

## Make immutability explicit

Declare local values `const` when they are not reassigned. Mark member functions
`const` when they do not mutate observable state. Use `constexpr` when an operation
is valid both at compile time and at runtime; do not duplicate it with a separate
runtime helper.

```cpp
[[nodiscard]] constexpr int clamp_port(int port) noexcept {
    return port < 0 ? 0 : (port > 65535 ? 65535 : port);
}

const auto port = clamp_port(configured_port);
```

Do not apply `const` to a value that is immediately moved from or deliberately used
as mutable state. For ownership-bearing signatures and move decisions, load
`cpp-memory-ownership` instead of extending this style rule.

## Use `auto` when it removes repetition, not information

Use `auto` when the type is explicit on the right-hand side, mechanically verbose,
or intentionally abstracted by an iterator or structured binding:

```cpp
auto socket = std::make_unique<Socket>();
for (const auto& [name, endpoint] : endpoints) {
    connect(name, endpoint);
}
```

Spell the type when it communicates width, signedness, ownership, or a conversion
that the reader must notice:

```cpp
std::uint32_t timeout_ms = parse_timeout(text);
double ratio = completed / static_cast<double>(total);
```

Failure mode this prevents: `auto` silently hides truncation, an expensive copy, or
a borrowed-versus-owning distinction.

## Keep namespaces explicit

Use C++17 nested namespace definitions for new code:

```cpp
namespace project::transport {
// ...
}  // namespace project::transport
```

Never put `using namespace` in a header. A narrow `using std::string_view;` inside a
function or `.cpp` scope is acceptable when it removes noise without exporting names
to consumers.

Failure mode this prevents: including a header changes lookup and overload
resolution in code that never opted into those names.

## Mark results that must be consumed

Apply `[[nodiscard]]` when ignoring the result is almost certainly a bug: validation,
resource acquisition, parse results, and error-bearing return values. Do not annotate
fluent setters or deliberately ignorable observations merely to silence review.

```cpp
[[nodiscard]] ParseResult parse(std::string_view input);
```

A caller that intentionally discards such a result should make that decision visible,
for example with `static_cast<void>(parse(input));`.

## Keep control flow readable

Prefer early exits for errors and precondition failures. Do not compress conditionals,
loops, or non-trivial functions onto one line; let clang-format own line breaking.
Extract a named predicate when a condition encodes domain logic rather than syntax.

```cpp
if (!request.is_valid()) {
    return ParseError::InvalidRequest;
}

return parse_payload(request.payload());
```

## Tooling boundary

Use the checked-in configuration as a starting point, then tune it to the repository
rather than accumulating command-line exceptions. Read
[references/clang-format.md](references/clang-format.md) when adding `.clang-format`
or `.clang-tidy`, choosing the check set, or enforcing the C++17 boundary.

## Related skills

- Use `cpp-memory-ownership` for ownership, lifetime, references, and move semantics.
- Use `cpp-modern-stdlib` for choosing containers and C++17 library facilities.
- Use `cpp-build` for CMake targets, compile features, warnings, and dependencies.
- Use `cpp-russian` only for Russian terminology and documentation register.
