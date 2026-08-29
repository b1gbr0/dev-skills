# Lifetime traps in C++17

Use this reference when code stores or returns a pointer, reference, iterator,
`std::string_view`, or callback. Identify the owner first, then prove that every
borrow ends before the owner's storage is destroyed, moved, erased, or reallocated.

## Returning references and views

Never return a reference, pointer, or view into a local object:

```cpp
const std::string& bad_name() {
    const std::string name = build_name();
    return name;  // dangling
}

std::string_view bad_view() {
    return build_name();  // the temporary std::string is destroyed
}
```

Return an owning value when the result must survive independently:

```cpp
std::string name() {
    return build_name();
}
```

A reference may be returned into storage owned elsewhere only when the API contract
makes that lifetime visible. Prefer a stable owner object over an undocumented global
or cache entry.

## Temporary lifetime extension is narrow

Binding a local `const T&` or `T&&` directly to a temporary can extend that temporary's
lifetime to the lifetime of the reference:

```cpp
const std::string& text = build_name();  // valid while text is in scope
```

Do not generalize this rule:

- `std::string_view` is not a reference and does not extend the lifetime of a string.
- Returning a reference does not extend the lifetime of a local temporary.
- Passing a temporary through a reference parameter keeps it alive only through the
  full expression containing the call.
- Storing the address obtained through that parameter does not extend anything.

## Stored `std::string_view`

This value is valid only while the same character storage remains alive and
uninvalidated:

```cpp
std::string storage = load_text();
std::string_view view = storage;
consume(view);  // valid here
```

Mutating `storage` may reallocate or replace its buffer. Destroying, moving, or
assigning it can also invalidate the view according to the operation's contract.
Store an owning `std::string` when the consumer cannot prove the owner's lifetime.

A type that stores a view should make the relationship explicit in construction and
document which operations on the owner invalidate the view.

## Lambda captures and deferred work

Reference captures borrow local variables. They dangle when a callback outlives the
scope:

```cpp
std::function<void()> make_callback() {
    std::string message = load_message();
    return [&message] { send(message); };  // dangling after return
}
```

Capture an independent value when the callback owns what it needs:

```cpp
return [message = load_message()] { send(message); };
```

Capturing `this` copies a pointer, not the object. A callback stored by another object,
thread, or event loop must not run after the pointed-to object is destroyed. In C++17,
`[*this]` captures a copy of the object, but use it only when copying the whole object
is the intended ownership decision.

## Threads and asynchronous operations

A joined thread may borrow stack data only when the join is guaranteed before the data
leaves scope. A detached thread cannot safely borrow caller locals. Prefer moving owned
state into the thread function:

```cpp
std::thread worker([request = std::move(request)]() mutable {
    process(std::move(request));
});
worker.join();
```

Exception paths must preserve the join guarantee. Thread lifecycle and synchronization
patterns belong to `cpp-concurrency`; this reference covers only the borrowed state.

## Container invalidation

A container can stay alive while its elements move or disappear. Do not equate
container lifetime with element-reference lifetime.

Common C++17 rules:

- `std::vector` growth that reallocates invalidates every iterator, pointer, and
  reference; erase invalidates the erased element and everything after it.
- `std::basic_string` operations that reallocate invalidate pointers, references, and
  views into its character buffer.
- associative containers (`std::map`, `std::set`) keep references and iterators stable
  across insertion; erase invalidates handles to the erased element.
- unordered-container rehash invalidates iterators but not references or pointers to
  elements; erase still invalidates handles to the erased element.

Check the exact operation's invalidation table before retaining a handle. Do not rely
on reserved capacity unless the code also proves that no operation exceeds it.

```cpp
std::vector<Item> items;
items.push_back(first);
Item* selected = &items.front();
items.push_back(second);  // may reallocate; selected may now dangle
```

Use an index or stable owning indirection only when it matches the domain. Replacing
every element with `std::shared_ptr` is not a generic invalidation fix.

## Moved-from objects

A moved-from object is still alive. Its permitted operations come from the type's
contract; standard-library types are generally valid but in an unspecified state.
Do not read a value merely because a particular implementation leaves it unchanged.
Prefer assignment, reset, destruction, or an explicitly documented operation.

```cpp
std::string source = "payload";
std::string target = std::move(source);
source = "next";  // establishes a new known state
```

## Review checklist

For every borrow that escapes a full expression, answer:

1. Which object owns the referenced storage?
2. What event ends or invalidates that storage?
3. Can the borrow survive across a return, callback, thread, or suspension point?
4. Can a container operation move or erase the element first?
5. Does the signature communicate the ownership relationship?

If any answer depends on an undocumented implementation detail, return or store an
owning value instead.
