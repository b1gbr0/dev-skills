# Linking `<filesystem>` on older C++17 libraries

GNU libstdc++ before GCC 9.1 may require `stdc++fs`; LLVM libc++ before LLVM
9.0 may require `c++fs`. A Clang frontend can use either standard library, so checking
only `CMAKE_CXX_COMPILER_ID` is insufficient.

Prefer a compile-and-link probe: first try without a compatibility library, then try the
known legacy libraries. Attach the successful result only to targets that use
`std::filesystem`.

```cmake
include(CheckCXXSourceCompiles)

function(project_link_filesystem target)
    if(NOT TARGET "${target}")
        message(FATAL_ERROR "unknown target: ${target}")
    endif()

    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_REQUIRED_QUIET TRUE)

    set(_filesystem_probe [[
        #include <filesystem>
        int main() {
            const auto path = std::filesystem::current_path();
            return path.empty() ? 1 : 0;
        }
    ]])

    check_cxx_source_compiles(
        "${_filesystem_probe}"
        PROJECT_FILESYSTEM_LINKS_WITHOUT_EXTRA_LIBRARY
    )
    if(PROJECT_FILESYSTEM_LINKS_WITHOUT_EXTRA_LIBRARY)
        return()
    endif()

    foreach(_library IN ITEMS stdc++fs c++fs)
        set(CMAKE_REQUIRED_LIBRARIES "${_library}")
        string(MAKE_C_IDENTIFIER
            "PROJECT_FILESYSTEM_LINKS_WITH_${_library}"
            _result
        )
        check_cxx_source_compiles("${_filesystem_probe}" "${_result}")
        if(${_result})
            target_link_libraries("${target}" PRIVATE "${_library}")
            return()
        endif()
    endforeach()

    message(FATAL_ERROR
        "std::filesystem did not link with the default library, stdc++fs, or c++fs"
    )
endfunction()
```

Call it after creating the target:

```cmake
add_executable(project_app src/main.cpp)
target_compile_features(project_app PRIVATE cxx_std_17)
project_link_filesystem(project_app)
```

The checks are cached per build directory. When switching compiler, standard library,
or sysroot, use a fresh build directory or preset so stale probe results are not reused.

Do not add both libraries “just in case”. Modern toolchains need neither, and a library
name valid for one standard-library implementation may not exist for another.

Sources:

- <https://en.cppreference.com/cpp/filesystem>
- <https://releases.llvm.org/9.0.0/projects/libcxx/docs/UsingLibcxx.html>
- <https://cmake.org/cmake/help/v3.20/module/CheckCXXSourceCompiles.html>
