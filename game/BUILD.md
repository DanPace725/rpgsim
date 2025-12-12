# Build Guide

## Prerequisites

You'll need the following tools installed:

### Windows
- **CMake** (3.15+): Download from https://cmake.org/download/
- **C++ Compiler** - Choose one:
  - Visual Studio 2017+ (includes MSVC compiler)
  - MinGW-w64 (GCC for Windows)
  - Clang for Windows

### Linux
```bash
# Ubuntu/Debian
sudo apt install cmake g++ build-essential

# Fedora/RHEL
sudo dnf install cmake gcc-c++ make
```

### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install CMake via Homebrew
brew install cmake
```

## Building the Project

### Method 1: Command Line (Cross-platform)

```bash
# Navigate to the game directory
cd game

# Create build directory
mkdir build
cd build

# Configure with CMake
cmake ..

# Build
cmake --build .

# Run the demo
./ecosystem_demo        # Linux/Mac
ecosystem_demo.exe      # Windows
```

### Method 2: Visual Studio (Windows)

1. Open Visual Studio
2. Select "Open a local folder"
3. Navigate to the `game` directory
4. Visual Studio will detect CMakeLists.txt and configure automatically
5. Select the target `ecosystem_demo` and build
6. Run from the output directory

### Method 3: Visual Studio Code

1. Install the "CMake Tools" extension
2. Open the `game` folder in VS Code
3. Press `Ctrl+Shift+P` and select "CMake: Configure"
4. Press `F7` to build
5. Press `Ctrl+Shift+P` and select "CMake: Run Without Debugging"

## Build Options

### Debug Build
```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
```

### Release Build (Optimized)
```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
```

### Parallel Build (faster)
```bash
# Use all CPU cores
cmake --build . -j$(nproc)  # Linux/Mac
cmake --build . -j%NUMBER_OF_PROCESSORS%  # Windows
```

## Troubleshooting

### CMake not found
- Ensure CMake is installed and in your PATH
- On Windows, you may need to restart your terminal after installation

### Compiler not found
- **Windows**: Install Visual Studio with C++ workload
- **Linux**: Install `build-essential` package
- **macOS**: Run `xcode-select --install`

### Build fails with C++17 errors
- Your compiler may be too old
- Update to: GCC 7+, Clang 5+, or MSVC 2017+

### Missing include directories
- Make sure you're building from the `game` directory
- Try deleting the `build` folder and starting fresh

## Project Structure After Build

```
game/
├── build/
│   ├── rpe_core.a / rpe_core.lib    # Static library
│   ├── ecosystem_demo               # Executable
│   └── CMakeFiles/                  # Build artifacts
├── include/                         # Header files
├── src/                             # Source files
└── examples/                        # Example programs
```

## Running the Demo

After building:

```bash
cd build

# Linux/Mac
./ecosystem_demo

# Windows
ecosystem_demo.exe

# Or with verbose output
./ecosystem_demo --verbose  # (not implemented yet)
```

## Next Steps

After successful build:

1. Review the output - you should see simulation tick messages
2. Check that agents survive for multiple ticks
3. Observe emergent clustering around resources
4. Experiment with modifying rules in `examples/ecosystem_demo.cpp`
5. Try creating your own entity types in `EntityTemplates.cpp`

## Development Workflow

For active development:

```bash
# Make changes to source files
vim src/core/RPEngine.cpp

# Rebuild (from build directory)
cmake --build .

# Run
./ecosystem_demo
```

CMake will automatically detect changed files and rebuild only what's necessary.

## Performance Tips

- Use Release builds for testing at scale (100+ entities)
- Profile with your compiler's tools:
  - **GCC**: `-pg` flag and `gprof`
  - **Clang**: `-ftime-trace`
  - **MSVC**: Visual Studio Profiler
- The spatial index is optimized for ~1000 entities; beyond that, consider a quadtree

## Integration with Game Engines

The RPE core library (`rpe_core`) can be integrated with:

- **Unreal Engine 5**: Include headers, link library, call `RPEngine::tick()` in game loop
- **Unity**: Use C# P/Invoke or create a C++/CLI wrapper
- **Godot**: Use GDNative or create a module
- **Custom Engine**: Just link against `rpe_core.a`

See the README.md for integration examples (coming in v0.2).
