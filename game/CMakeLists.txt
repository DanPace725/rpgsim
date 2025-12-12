cmake_minimum_required(VERSION 3.15)
project(RPGameSim VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler warnings
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Core library sources
set(CORE_SOURCES
    src/core/Entity.cpp
    src/core/Relation.cpp
    src/core/World.cpp
    src/core/RPEngine.cpp
    src/spatial/SpatialIndex.cpp
    src/primitives/EntityTemplates.cpp
)

# Create the RPE core library
add_library(rpe_core STATIC ${CORE_SOURCES})
target_include_directories(rpe_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Example executable
add_executable(ecosystem_demo
    examples/ecosystem_demo.cpp
)
target_link_libraries(ecosystem_demo PRIVATE rpe_core)

# Enable testing
enable_testing()

# Optional: Add tests subdirectory if you create tests
# add_subdirectory(tests)

# Installation rules
install(TARGETS rpe_core ecosystem_demo
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)
