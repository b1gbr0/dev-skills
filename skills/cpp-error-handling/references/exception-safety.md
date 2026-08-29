# Exception safety in C++17

Exception safety is a state guarantee, not merely the absence of leaks. Decide what a
caller may observe after failure, then structure the operation so ownership and the
commit point enforce that guarantee.

## Guarantee levels

### Nothrow guarantee

The operation will not emit an exception. This is required for destructors, cleanup
used during unwinding, and usually `swap` and move operations that support transactional
updates.

`noexcept` should state a guarantee already provided by the implementation; it does
not make throwing code safe.

### Strong guarantee

The operation either succeeds or has no observable effect. Build the next state away
from the object, then commit with a non-throwing operation:

```cpp
void Registry::replace(const Key& key, Value value) {
    auto next = entries_;
    next.insert_or_assign(key, std::move(value));
    entries_.swap(next);  // commit
}
```

The copy and mutation may throw, but `entries_` is unchanged until `swap`.

### Basic guarantee

After failure, invariants hold and no resources leak, but values may have changed.
The object remains usable within its documented state. This is often sufficient for a
large incremental operation where copying all state would be disproportionate.

### No guarantee

The operation may leave invariants broken or resources lost. Treat this as a defect
unless the program terminates immediately and the boundary documents that behavior.

## Establish the invariant in constructors

Acquire resources into RAII members or local owners before publishing the object.
If a constructor throws, fully constructed members are destroyed automatically; the
class destructor is not called for an object whose construction never completed.

```cpp
Connection::Connection(Address address)
    : socket_(open_socket()), peer_(connect(socket_, address)) {}
```

Do not acquire a raw resource and then perform another throwing operation before
placing it in an owner.

## Commit after all throwing work

Separate an operation into prepare and commit phases:

1. validate input;
2. allocate and calculate in local RAII-managed state;
3. perform all operations that may throw;
4. commit with `swap`, a non-throwing move, or another atomic state transition.

This pattern applies to configuration reloads, index rebuilds, and replacing a set of
resources. It often provides the strong guarantee without explicit rollback code.

## Copy-and-swap

Copy-and-swap is useful when copying the complete value is already the right operation
and `swap` is non-throwing:

```cpp
class Buffer {
public:
    Buffer& operator=(Buffer other) noexcept(noexcept(swap(other))) {
        swap(other);
        return *this;
    }

    void swap(Buffer& other) noexcept {
        data_.swap(other.data_);
    }

private:
    std::vector<std::byte> data_;
};
```

The parameter is prepared before entry, and the swap commits. Failure during copying
leaves the target unchanged.

Do not apply copy-and-swap mechanically. It can allocate unnecessarily, discard
reusable capacity, and make move assignment more expensive. Direct member-wise
assignment is preferable when it can provide the required guarantee more cheaply.

## Container caveats

Standard containers document their own guarantees per operation. Do not infer the
strong guarantee from the container name alone. In particular, reallocation may have
weaker guarantees when an element has a throwing move constructor and cannot be
copied.

A user-defined type intended for `std::vector` should make its move constructor
`noexcept` when that is truthful. This lets the container move elements during
reallocation without sacrificing its guarantee.

## Destructors and cleanup

A destructor runs during normal scope exit and may run while another exception is
already unwinding. Letting a second exception escape calls `std::terminate`.

- Keep destructors non-throwing.
- Offer an explicit `close`, `flush`, or `commit` operation when callers must observe
  cleanup failure.
- Make the destructor perform best-effort fallback cleanup.
- Do not silently claim durable success merely because the destructor suppressed an
  error.

## Exception-neutral layers

A reusable lower layer should normally preserve exceptions it cannot handle. Catch an
exception only to restore invariants, translate it at an abstraction boundary, or add
structured context. Use `throw;` after restoration to preserve the dynamic type.

Do not log and rethrow at every layer. Log once where the operation ends or where the
system has enough context to choose a retry, response, or shutdown policy.

## Testing the guarantee

Exercise failures at each allocation, I/O, and injected dependency boundary. After a
failure, assert the documented guarantee:

- no leaked handles or memory;
- invariants still hold;
- old state is unchanged for the strong guarantee;
- the object remains usable for the basic guarantee;
- no exception escapes a `noexcept` or C ABI boundary.

Sanitizers find leaks and invalid accesses, but they do not prove that a logical state
was rolled back. Add explicit state assertions.

## Review checklist

1. What is the required guarantee: nothrow, strong, or basic?
2. Which operations can throw before the commit point?
3. Is every acquired resource already in an RAII owner?
4. Is commit genuinely non-throwing?
5. Does a catch block recover, translate, or terminate at a boundary?
6. Can cleanup fail, and where is that failure reported?

Sources:

- <https://en.cppreference.com/w/cpp/language/exceptions>
- <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-errors>
