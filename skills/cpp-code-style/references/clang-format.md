# clang-format and clang-tidy for C++17

Use this starting point when the repository has no checked-in configuration. If a
project already has one, preserve it and change only rules that have a concrete
failure mode.

## `.clang-format`

```yaml
BasedOnStyle: LLVM
Language: Cpp
Standard: Cpp17

IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100

BreakBeforeBraces: Attach
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false

DerivePointerAlignment: false
PointerAlignment: Left

SortIncludes: CaseSensitive
IncludeBlocks: Regroup
```

`Standard: Cpp17` controls syntax-sensitive formatting; it does not add `-std=c++17`
to compilation. Format only files owned by the project:

```sh
clang-format --dry-run --Werror src/request.cpp include/project/request.hpp
clang-format -i src/request.cpp include/project/request.hpp
```

Do not recursively format vendored code or third-party headers. A formatting-only
change belongs in a separate commit so semantic review is not buried in whitespace.

## `.clang-tidy`

```yaml
Checks: >
  -*,
  bugprone-*,
  cppcoreguidelines-*,
  modernize-*,
  performance-*,
  portability-*,
  -cppcoreguidelines-avoid-magic-numbers,
  -cppcoreguidelines-owning-memory,
  -cppcoreguidelines-pro-bounds-pointer-arithmetic,
  -cppcoreguidelines-pro-type-reinterpret-cast,
  -cppcoreguidelines-pro-type-union-access,
  -modernize-use-constraints,
  -modernize-use-designated-initializers,
  -modernize-use-ranges,
  -modernize-use-starts-ends-with,
  -modernize-use-std-bit,
  -modernize-use-std-format,
  -modernize-use-std-numbers,
  -modernize-use-std-print
WarningsAsErrors: ''
HeaderFilterRegex: '(^|.*/)(src|include)/'
FormatStyle: file
```

The disabled `modernize-*` checks can rewrite code toward C++20 or C++23 facilities.
They are defects under a strict C++17 baseline even when the local compiler happens
to accept them as extensions.

The remaining disabled checks are intentionally noisy or encode an ownership model
that cannot be inferred mechanically. Re-enable one only after running it on the
repository and reviewing its actual findings.

clang-tidy gets the language standard from the compile command, not from
`.clang-tidy`. Generate `compile_commands.json` with CMake and make C++17 explicit on
the target:

```cmake
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
target_compile_features(project_core PUBLIC cxx_std_17)
```

Then run it against owned sources:

```sh
clang-tidy -p build src/request.cpp
run-clang-tidy -p build '(^|.*/)(src|include)/'
```

Compilation databases commonly contain absolute paths, so a regex anchored directly
at `src/` can match nothing. Confirm that `run-clang-tidy` lists real project
translation units before treating a silent run as success.

Do not set `WarningsAsErrors: '*'` in a shared local configuration before the check
set is clean. CI may promote stable findings to errors for project code, but never
for dependencies.

## Verification

Before committing either file:

1. Run `clang-format --dry-run --Werror` on representative headers and sources.
2. Configure the real build so `compile_commands.json` contains `-std=c++17` or the
   compiler-equivalent flag.
3. Run clang-tidy on at least one translation unit from each project target.
4. Inspect fixes before applying them; do not combine bulk `--fix` output with a
   behavioral change.

Official option and check references:

- <https://clang.llvm.org/docs/ClangFormatStyleOptions.html>
- <https://clang.llvm.org/extra/clang-tidy/checks/list.html>
