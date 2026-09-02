---
name: cpp-build
description: "C++17 build engineering with target-based CMake: target_compile_features, PUBLIC/PRIVATE/INTERFACE usage requirements, warning and sanitizer options, optional CMakePresets configure/build/test entry points, find_package versus FetchContent, and vcpkg/Conan integration. Use when creating or reviewing CMakeLists.txt, CMakePresets.json, compile/link flags, dependency wiring, compile_commands.json, or filesystem link failures. Preserve an existing project's minimum CMake version and documented entry point. Does NOT choose application APIs (cpp-modern-stdlib), code style (cpp-code-style), or testing semantics/frameworks (cpp-testing)."
user-invocable: true
license: MIT
compatibility: Target-based guidance works with CMake 3.13+; CMakePresets and the bundled starter require CMake 3.20+; C++17.
metadata:
  author: b1gbr0
  version: "0.1.0"
---

# C++ Build

Model the build as targets and their usage requirements. A target declares the C++
features, include paths, definitions, options, and libraries it needs; consumers inherit
only what its public interface requires.

In an existing repository, preserve its minimum CMake version, generator matrix, and
documented developer entry point. Do not raise the minimum or replace a Makefile,
package-manager command, or CI wrapper merely to adopt this skill's preferred tooling.
The examples below are defaults for a new build or an explicitly approved migration.

## Require C++17 on each target

Use `target_compile_features`, not a handwritten global `-std=` flag:

```cmake
add_library(project_core src/core.cpp)
target_compile_features(project_core PUBLIC cxx_std_17)
```

`PUBLIC` means consumers must also compile as C++17 because the public headers expose
that requirement. Use `PRIVATE` when only implementation files need it. Do not set
`CMAKE_CXX_FLAGS` or append compiler flags globally; that bypasses compiler portability,
configuration handling, and dependency boundaries.

Failure mode this prevents: a dependency inherits project-only flags or one target
quietly compiles under a different language standard.

## Express usage requirements with target scope

```cmake
add_library(project_core src/core.cpp)
add_library(project::core ALIAS project_core)

target_include_directories(project_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(project_core
    PUBLIC Threads::Threads
    PRIVATE project_warnings
)
```

- `PRIVATE`: needed to build this target only.
- `PUBLIC`: needed by this target and by consumers of its public interface.
- `INTERFACE`: not used to build this target, but required by consumers.

Prefer imported targets such as `Threads::Threads` and `fmt::fmt` over raw library
names and manually copied include directories. Never use directory-wide
`include_directories`, `link_libraries`, or `add_definitions` for target-specific needs.

## Keep warnings on owned targets

Put warning flags in a small interface target and link it `PRIVATE` to project targets.
Select flags by compiler family; never apply `-Werror` or `/WX` to dependencies.

```cmake
add_library(project_warnings INTERFACE)

if(MSVC)
    target_compile_options(project_warnings INTERFACE /W4 /permissive-)
else()
    target_compile_options(project_warnings INTERFACE
        -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
    )
endif()
```

Promote warnings to errors through a project option used only by owned targets. Keep
it off while adopting a new compiler; turn it on in the CI preset once the supported
matrix is clean.

## Use presets when the project baseline permits them

For a new project on CMake 3.20+, check in `CMakePresets.json` and use named
configure, build, and test presets:

```sh
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

Schema version 2 and CMake 3.20 are the minimum for build and test presets. Do not add
a presets file or raise `cmake_minimum_required` when an existing project intentionally
supports an older CMake. Keep its documented Makefile or other wrapper as the stable
entry point until a baseline migration is explicitly approved.

For a presets-capable project, keep machine-local paths and secrets out of the shared
file; developers may add an ignored `CMakeUserPresets.json` that inherits project
presets. Use separate build directories per preset. A sanitizer preset inherits the
normal debug configuration and changes only sanitizer-specific cache variables.

The working starter in [assets/](assets/) intentionally requires CMake 3.20. Copy it
only for a new project or approved migration, then rename its targets and source files.

## Wire sanitizers through targets

For GCC and Clang, add sanitizer compile and link options together. Do not place them in
`CMAKE_CXX_FLAGS`, and do not combine AddressSanitizer with ThreadSanitizer in one
binary.

```cmake
target_compile_options(project_sanitizers INTERFACE
    -fsanitize=address,undefined -fno-omit-frame-pointer
)
target_link_options(project_sanitizers INTERFACE
    -fsanitize=address,undefined
)
```

Link this interface target privately to owned executables and libraries. Sanitizer test
strategy and report interpretation belong to `cpp-testing`.

## Choose dependency delivery deliberately

Use `find_package` when a dependency is supplied by the system, a package manager, or a
preinstalled SDK and exposes a versioned imported target:

```cmake
find_package(fmt 10 CONFIG REQUIRED)
target_link_libraries(project_app PRIVATE fmt::fmt)
```

Use `FetchContent` for a source dependency that must be built with the project. Pin an
immutable release tag or full commit; never track a branch:

```cmake
include(FetchContent)
FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 10.2.1
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(fmt)
```

Use vcpkg or Conan when the project needs a repeatable dependency graph across many
packages or platforms. Integrate the package manager through its CMake toolchain and
keep consuming dependencies via `find_package` imported targets. Do not mix three
ownership models for the same dependency.

## Handle old `<filesystem>` at link time

GNU libstdc++ before GCC 9.1 may need `stdc++fs`; LLVM libc++ before LLVM 9.0 may need
`c++fs`. Do not add either globally or infer the standard library solely from the
frontend name. Probe a complete compile-and-link first, then try compatibility
libraries and attach the successful one privately to the target.

Read [references/filesystem-linking.md](references/filesystem-linking.md) when the
supported matrix includes GCC 8, LLVM 8, or a Clang frontend whose standard library is
not fixed.

## Generate tooling data from the real build

Set `CMAKE_EXPORT_COMPILE_COMMANDS=ON` in development presets for Ninja or Makefile
generators. clang-tidy and language servers must read the same includes, definitions,
and C++17 mode as the build; do not maintain a second list of flags by hand.

Multi-config generators such as Visual Studio and Xcode ignore `CMAKE_BUILD_TYPE`.
Use the build preset's `configuration` field for those generators instead of assuming
a single-config layout.

## Related skills

- Use `cpp-testing` for CTest registration, framework choice, mocks, and sanitizers.
- Use `cpp-modern-stdlib` for feature availability and library choices.
- Use `cpp-code-style` for `.clang-format` and `.clang-tidy` policy.
- Use `cpp-memory-ownership` for lifetime and RAII design.
