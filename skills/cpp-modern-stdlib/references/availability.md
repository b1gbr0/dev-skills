# C++17 availability and library rough edges

The language mode and the standard library are separate. `clang++ -std=c++17` can
use either libc++ or libstdc++; the frontend version alone does not prove that a
library facility exists. Treat the rows below as minimum documented releases, then
compile a probe with the actual toolchain used by CI.

## Core language features

Versions come from the cppreference C++17 compiler-support table.

| Feature | Standard | GCC | Clang | MSVC |
|---|---:|---:|---:|---:|
| structured bindings | C++17 | 7 | 4 | 19.11 |
| `if constexpr` | C++17 | 7 | 3.9 | 19.11 |
| class template argument deduction | C++17 | 7 | 5 | 19.14 |
| fold expressions | C++17 | 6 | 3.6 | 19.12 |
| inline variables | C++17 | 7 | 3.9 | 19.12 |
| guaranteed copy elision | C++17 | 7 | 4 | 19.13 |

The skill baseline (GCC 9+, Clang 9+, MSVC 19.2x+) clears these language rows.
That does not clear every library row below.

## Standard-library facilities

| Facility | Standard | libstdc++ | libc++ | MSVC STL | Notes |
|---|---:|---:|---:|---:|---|
| `std::optional`, `std::variant`, `std::any` | C++17 | GCC 7.1 | LLVM 4 | 19.10 | C++17 headers |
| `std::string_view` | C++17 | GCC 7.1 | LLVM 4 | 19.11 | MSVC 19.10 was partial |
| `std::filesystem` | C++17 | GCC 8 | LLVM 7 | 19.14 | extra link library on older releases |
| integer `std::from_chars` | C++17 | GCC 8 | LLVM 7 | 19.14 | shipped before floating overloads |
| floating `std::from_chars` | C++17 | GCC 11 | LLVM 20 | 19.15 | library version, not frontend version |
| parallel algorithms and execution policies | C++17 | GCC 9 | LLVM 17 partial | 19.14 | backend and completeness caveats |

Do not reduce this table to “Clang N supports X”. A Clang frontend using libstdc++
inherits the libstdc++ row; Apple Clang uses Apple's separately shipped libc++.

## `<filesystem>` linking

The implementation existed before it was folded into the main standard-library
binary:

- GNU libstdc++ before GCC 9.1 requires `-lstdc++fs`.
- LLVM libc++ before LLVM 9.0 requires `-lc++fs`.

Do not add either library unconditionally. Detect the old toolchain in CMake and link
it only there; modern versions either do not need it or may not ship the compatibility
archive.

A compile-and-link probe must create and use a `std::filesystem::path`; compiling a
header-only snippet is insufficient because the failure occurs at link time.

## Parallel algorithms

GCC 9 added `<execution>` and parallel algorithms through a TBB 2018-or-newer backend.
The dependency affects both build wiring and deployment. A policy overload compiling
does not prove that parallel execution is enabled or useful.

libc++ 17 described its C++17 Parallel STL as experimental and only partially
implemented. Clang using libstdc++ follows the libstdc++ behavior instead. Therefore:

- do not promise portable parallel algorithms for the minimum Clang/libc++ baseline;
- verify every algorithm and policy used by compiling and linking the actual target;
- benchmark before retaining a parallel policy;
- wire TBB in `cpp-build`, not through a hidden global linker flag.

## `std::from_chars`

Integer parsing is available at the minimum project baseline. Floating-point support
is not:

- libstdc++ added floating overloads in GCC 11;
- libc++ added `float` and `double` overloads in LLVM 20;
- MSVC added them in 19.15, one release after integer support.

Do not use only `__cpp_lib_to_chars` or the presence of `<charconv>` as proof that a
specific overload exists. Compile a probe for the exact destination type. Keep one
fallback implementation selected at configure time; do not scatter version checks
through application code.

## Apple deployment targets

Apple's library availability depends on the deployment target, not only the Xcode or
Apple Clang version:

- `std::filesystem` requires macOS 10.15 according to Apple's C++ support table.
- throwing `std::visit` and related `std::variant` operations require macOS 10.13 when
  exceptions are enabled.

These constraints come from symbols in the operating system's `libc++.dylib`. A newer
compiler targeting an older macOS release does not make the symbols available.
Set and test `CMAKE_OSX_DEPLOYMENT_TARGET` explicitly when macOS is supported. Apple
Clang is a documented secondary platform for this skillset, not a locally verified
one.

## Probe before promising portability

For every library rough edge:

1. Configure with the same compiler, standard library, deployment target, and linker
   flags as CI.
2. Compile and link a minimal program using the exact overload or execution policy.
3. Run it where runtime library availability is relevant.
4. Record the supported combination in project CI rather than growing preprocessor
   guesses in production code.

## Sources

- <https://en.cppreference.com/cpp/compiler_support/17>
- <https://en.cppreference.com/cpp/filesystem>
- <https://gcc.gnu.org/gcc-9/changes.html>
- <https://gcc.gnu.org/gcc-11/changes.html>
- <https://libcxx.llvm.org/Status/Cxx17.html>
- <https://releases.llvm.org/17.0.1/projects/libcxx/docs/ReleaseNotes.html>
- <https://releases.llvm.org/17.0.1/projects/libcxx/docs/Status/PSTL.html>
- <https://developer.apple.com/xcode/cpp/>
