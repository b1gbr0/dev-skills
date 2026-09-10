cmake_minimum_required(VERSION 3.20)

project(cpp_service VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CTest)

option(PROJECT_WARNINGS_AS_ERRORS "Treat project warnings as errors" OFF)
option(PROJECT_ENABLE_SANITIZERS "Enable AddressSanitizer and UBSan" OFF)

add_library(project_warnings INTERFACE)
if(MSVC)
    target_compile_options(project_warnings INTERFACE /W4 /permissive-)
    if(PROJECT_WARNINGS_AS_ERRORS)
        target_compile_options(project_warnings INTERFACE /WX)
    endif()
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
    target_compile_options(project_warnings INTERFACE
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wsign-conversion
    )
    if(PROJECT_WARNINGS_AS_ERRORS)
        target_compile_options(project_warnings INTERFACE -Werror)
    endif()
endif()

add_library(project_sanitizers INTERFACE)
if(PROJECT_ENABLE_SANITIZERS)
    if(MSVC)
        message(FATAL_ERROR "The bundled sanitizer preset supports GCC and Clang only")
    endif()
    target_compile_options(project_sanitizers INTERFACE
        -fsanitize=address,undefined
        -fno-omit-frame-pointer
    )
    target_link_options(project_sanitizers INTERFACE
        -fsanitize=address,undefined
    )
endif()

add_executable(cpp_service src/main.cpp)
target_compile_features(cpp_service PRIVATE cxx_std_17)
target_link_libraries(cpp_service PRIVATE project_warnings project_sanitizers)

if(BUILD_TESTING)
    add_executable(cpp_service_smoke tests/smoke.cpp)
    target_compile_features(cpp_service_smoke PRIVATE cxx_std_17)
    target_link_libraries(cpp_service_smoke
        PRIVATE project_warnings project_sanitizers
    )
    add_test(NAME cpp_service.smoke COMMAND cpp_service_smoke)
endif()
