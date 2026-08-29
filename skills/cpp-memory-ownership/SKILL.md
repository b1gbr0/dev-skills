---
name: cpp-memory-ownership
description: "C++17 ownership and lifetime design: express owning and borrowed parameters in signatures, choose value/reference/pointer/unique_ptr/shared_ptr/string_view, apply RAII and the rule of zero, use std::move correctly, and prevent dangling views, references, captures, and container-element handles. Use when writing or reviewing C++ APIs, fixing leaks or use-after-free, discussing move semantics, or seeing raw new/delete and smart pointers. Does NOT choose containers and algorithms (cpp-modern-stdlib), general code style (cpp-code-style), or exception policy (cpp-error-handling)."
user-invocable: true
license: MIT
compatibility: C++17; ordinary desktop and service code with exceptions and RTTI enabled.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# C++ Memory Ownership

Make ownership visible in types and let object lifetime release resources. A caller
should be able to tell from a signature whether an argument is copied, borrowed,
mutated, or consumed. Prefer value semantics and the rule of zero; introduce explicit
owners only at real ownership boundaries.

## Encode the contract in the signature

Use these defaults unless the surrounding project documents a stronger convention:

| Form | Meaning |
|---|---|
| `T` | independent value; copy or move into the callee |
| `const T&` | required read-only borrow for the duration of the call |
| `T&` | required mutable borrow for the duration of the call |
| `const T*` / `T*` | optional borrow; `nullptr` has documented meaning |
| `std::unique_ptr<T>` | transfer exclusive ownership into the callee |
| `std::shared_ptr<T>` | share lifetime ownership with the callee |
| `std::string_view` | borrowed character sequence; lifetime stays elsewhere |

```cpp
void render(const Document& document);
void normalize(Document& document);
void set_parent(Node* parent);  // nullptr means no parent
void install(std::unique_ptr<Plugin> plugin);
```

Do not accept `const std::unique_ptr<T>&` merely to borrow `T`; accept `const T&` or
`const T*`. The smart pointer type is relevant only when ownership itself participates
in the operation.

Failure mode this prevents: callers create heap objects and shared ownership only to
satisfy a signature that never needed either.

## Prefer the rule of zero

Wrap every resource in a type whose destructor releases it, then compose those types.
If all members already manage themselves, declare no destructor, copy constructor,
move constructor, or assignment operator.

```cpp
class Session {
public:
    Session(Socket socket, std::string peer)
        : socket_(std::move(socket)), peer_(std::move(peer)) {}

private:
    Socket socket_;
    std::string peer_;
};
```

Write the rule-of-five operations only when the class directly owns a raw resource or
has semantics that member-wise operations cannot express. Prefer a small dedicated
RAII wrapper over spreading custom cleanup across a larger domain class.

Failure mode this prevents: adding a destructor suppresses implicit move operations and
turns an otherwise movable type into a surprising copy-only type.

## Use `std::unique_ptr` by default for heap ownership

Choose `std::unique_ptr` when exactly one owner controls destruction. Transfer it by
value and `std::move`; return it by value without `std::move`.

```cpp
std::unique_ptr<Connection> open_connection();

void Server::accept(std::unique_ptr<Connection> connection) {
    connections_.push_back(std::move(connection));
}
```

Use `std::shared_ptr` only when independent objects must extend the same lifetime and
no single owner can be named. Document cycles and break observer links with
`std::weak_ptr`.

Do not replace `std::unique_ptr` with `std::shared_ptr` to make copying compile. That
changes destruction timing, adds shared mutable state, and hides the missing ownership
decision.

## `std::move` grants permission; it does not move

`std::move` casts an expression to an xvalue so overload resolution may choose a move
operation. The selected constructor or assignment operator performs the actual work.

```cpp
std::string source = "payload";
std::string target = std::move(source);
```

After the move, use `source` only for operations allowed by its type's moved-from
contract, commonly destruction or assignment. Do not assume it is empty.

Avoid these common mistakes:

```cpp
const std::string source = load();
auto copy = std::move(source);  // usually copies: source is const

std::string make_name() {
    std::string name = build_name();
    return name;                // NRVO or implicit move
}
```

Adding `std::move(name)` to the return can prevent NRVO. Moving from `const` usually
cannot call a move operation that needs to modify the source.

## Treat views as borrows

`std::string_view` never extends the lifetime of character storage. Use it for input
that is consumed during the call, or return it only when the backing storage has a
clear, sufficiently long contract.

```cpp
std::size_t count_lines(std::string_view text);

std::string_view bad_name() {
    const std::string name = build_name();
    return name;  // dangling
}
```

Do not store a caller-provided `std::string_view` unless the owner outlives the stored
view by construction. If the callee must retain text independently, store an owning
`std::string`.

Read [references/lifetime-traps.md](references/lifetime-traps.md) when returning or
storing views/references, capturing locals in callbacks, or retaining handles to
container elements.

## C++17 has no `std::span`

Do not suggest `std::span` under this baseline. For an isolated contiguous-buffer API,
pass a pointer plus a count and keep them adjacent:

```cpp
std::uint32_t checksum(const std::byte* data, std::size_t size);
```

When non-owning contiguous ranges are pervasive across a public API, adopt a mature
C++17-compatible span such as `gsl::span` consistently. One dependency is safer than
many hand-written pointer/count wrappers; for a single internal function, the
dependency does not earn its cost. Never implement an ad hoc span type.

For a generic algorithm that does not require contiguous storage, accept an iterator
pair instead. Container and algorithm selection belongs to `cpp-modern-stdlib`.

## Keep raw allocation inside an owner

A raw pointer is a non-owning observer by default. If an external C API returns a raw
resource, acquire it immediately into an RAII owner with the correct deleter.

```cpp
using File = std::unique_ptr<FILE, decltype(&std::fclose)>;

File open_file(const char* path) {
    return File(std::fopen(path, "rb"), &std::fclose);
}
```

Do not scatter matching `new`/`delete`, `malloc`/`free`, or open/close calls across
control-flow branches. The owning object must be established before another operation
can fail.

## Related skills

- Use `cpp-modern-stdlib` for container, algorithm, and C++17 facility choices.
- Use `cpp-error-handling` for exception boundaries and exception safety.
- Use `cpp-code-style` for naming, includes, and formatting.
- Use `cpp-russian` only for Russian terminology and documentation register.
