# Embedding Charm via Python/C API

This directory contains the C/C++ embedding API for Charm-Crypto, allowing native applications to use Charm cryptographic schemes by embedding the Python interpreter.

**Supported Platforms:**
- Linux (Ubuntu/Debian, RHEL/CentOS, Arch)
- macOS (Intel x86_64 and Apple Silicon arm64)
- Windows (MinGW/MSYS2) - Experimental

**Tested with:** Python 3.8, 3.9, 3.10, 3.11, 3.12

## Requirements

| Dependency | Description |
|------------|-------------|
| Python 3.8+ | With development headers (`python3-dev` or `python3-devel`) |
| GMP | GNU Multiple Precision Arithmetic Library |
| PBC | Pairing-Based Cryptography library |
| OpenSSL | For cryptographic primitives (optional, for EC/Integer modules) |
| Charm-Crypto | Installed or available in PYTHONPATH |

## Quick Start

```bash
# From the charm root directory
./configure.sh --enable-darwin  # Use --enable-darwin on macOS
cd embed/
make
PYTHONPATH=/path/to/charm ./test
```

---

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libgmp-dev \
    libpbc-dev \
    libssl-dev

# Configure Charm (from root directory)
./configure.sh

# Build the embed API
cd embed/
make

# Run the test
PYTHONPATH=/path/to/charm ./test
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Install dependencies
sudo dnf install -y \
    gcc \
    python3-devel \
    gmp-devel \
    pbc-devel \
    openssl-devel

# Configure and build
./configure.sh
cd embed/
make
PYTHONPATH=/path/to/charm ./test
```

### macOS (Intel x86_64)

```bash
# Install dependencies via Homebrew
brew install gmp pbc openssl@3

# Configure Charm with Darwin support
./configure.sh --enable-darwin

# Build the embed API
cd embed/
make

# Run the test
PYTHONPATH=/path/to/charm ./test
```

**Library paths on Intel Mac:** Homebrew installs to `/usr/local/`. The Makefile automatically detects this.

### macOS (Apple Silicon M1/M2/M3)

```bash
# Install dependencies via Homebrew
brew install gmp pbc openssl@3

# Configure Charm with Darwin support
./configure.sh --enable-darwin

# Build the embed API
cd embed/
make

# Run the test
PYTHONPATH=/path/to/charm ./test
```

**Library paths on Apple Silicon:** Homebrew installs to `/opt/homebrew/`. The Makefile automatically detects this based on `uname -m`.

**Rosetta Compatibility:** If your terminal is running under Rosetta (x86_64 emulation) but your Python and libraries are native arm64, you may need to run:

```bash
arch -arm64 ./test
```

To check your terminal architecture: `uname -m` (should show `arm64` for native).

### Windows (MinGW/MSYS2) - Experimental

Windows support is experimental. Use MSYS2 with MinGW-w64.

#### Step 1: Install MSYS2

Download and install MSYS2 from https://www.msys2.org/

#### Step 2: Install Dependencies

Open "MSYS2 MinGW 64-bit" terminal and run:

```bash
# Update package database
pacman -Syu

# Install build tools and dependencies
pacman -S --noconfirm \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-gmp \
    mingw-w64-x86_64-openssl

# PBC library may need to be built from source
# See: https://crypto.stanford.edu/pbc/
```

#### Step 3: Configure and Build

```bash
# Configure Charm
./configure.sh --build-win-exe

# Build the embed API
cd embed/
make

# Run the test
PYTHONPATH=/path/to/charm ./test.exe
```

**Note:** Windows support requires PBC library to be built and installed manually. The `--build-win-exe` flag sets appropriate paths for Windows.

---

## Build Configuration

Run `make info` to display the detected build configuration:

```bash
cd embed/
make info
```

This shows:
- Detected platform (linux/macos/windows)
- Architecture (x86_64/arm64)
- Compiler and flags
- Library paths
- Python configuration

---

## API Overview

### Initialization

```c
#include "charm_embed_api.h"

int main() {
    // Initialize Python interpreter
    InitializeCharm();

    // Create a pairing group (BN254 provides 128-bit security)
    Charm_t *group = InitPairingGroup(NULL, "BN254");

    // ... use Charm schemes ...

    // Cleanup
    Free(group);
    CleanupCharm();
    return 0;
}
```

### Core Functions

| Function | Description |
|----------|-------------|
| `InitializeCharm()` | Initialize Python interpreter |
| `CleanupCharm()` | Cleanup and finalize Python |
| `InitPairingGroup(module, curve)` | Create pairing group (e.g., "BN254", "SS512") |
| `InitECGroup(module, curve_id)` | Create elliptic curve group |
| `InitIntegerGroup(module, bits)` | Create integer group |
| `InitScheme(module, class, group)` | Load a Charm scheme class |
| `InitAdapter(module, class, scheme, group)` | Load a Charm adapter |
| `CallMethod(obj, method, fmt, ...)` | Call method on Python object |
| `GetIndex(obj, index)` | Get item from tuple/list (returns new reference) |
| `GetDict(obj, key)` | Get item from dict (returns new reference) |
| `objectToBytes(obj, group)` | Serialize object to bytes |
| `bytesToObject(bytes, group)` | Deserialize bytes to object |
| `Free(obj)` | Release Python object reference |

### Format Specifiers for CallMethod

| Specifier | Type | Description |
|-----------|------|-------------|
| `%O` | Charm_t* | Python object |
| `%s` | char* | String |
| `%b` | char* | Bytes |
| `%I` | char* | Group element type (ZR, G1, G2, GT) |
| `%A` | char* | Attribute list string |
| `%i` | int | Integer |

### Example: Hybrid ABE Encryption

```c
// Initialize
Charm_t *group = InitPairingGroup(NULL, "BN254");
Charm_t *abe = InitScheme("charm.schemes.abenc.abenc_bsw07", "CPabe_BSW07", group);
Charm_t *hybrid = InitAdapter("charm.adapters.abenc_adapt_hybrid", "HybridABEnc", abe, group);

// Setup
Charm_t *keys = CallMethod(hybrid, "setup", "");
Charm_t *pk = GetIndex(keys, 0);
Charm_t *msk = GetIndex(keys, 1);

// Key generation
Charm_t *sk = CallMethod(hybrid, "keygen", "%O%O%A", pk, msk, "[ATTR1, ATTR2]");

// Encrypt
Charm_t *ct = CallMethod(hybrid, "encrypt", "%O%b%s", pk, "secret message", "(ATTR1 and ATTR2)");

// Decrypt
Charm_t *msg = CallMethod(hybrid, "decrypt", "%O%O%O", pk, sk, ct);

// Cleanup
Free(msg); Free(ct); Free(sk); Free(pk); Free(msk); Free(keys);
Free(hybrid); Free(abe); Free(group);
```

---

## Troubleshooting

### Common Issues

#### "Python.h not found"

Install Python development headers:
- **Ubuntu/Debian:** `sudo apt-get install python3-dev`
- **RHEL/Fedora:** `sudo dnf install python3-devel`
- **macOS:** Headers included with Python from Homebrew or python.org

#### "gmp.h not found" or "pbc.h not found"

Install GMP and PBC development libraries:
- **Ubuntu/Debian:** `sudo apt-get install libgmp-dev libpbc-dev`
- **macOS:** `brew install gmp pbc`

Or set include paths manually:
```bash
make CPPFLAGS="-I/path/to/gmp/include -I/path/to/pbc/include"
```

#### "cannot find -lgmp" or "cannot find -lpbc"

Set library paths:
```bash
make LDFLAGS="-L/path/to/gmp/lib -L/path/to/pbc/lib"
```

#### "libpython3.x.so not found" at runtime

Set `LD_LIBRARY_PATH` (Linux) or `DYLD_LIBRARY_PATH` (macOS):
```bash
export LD_LIBRARY_PATH=/path/to/python/lib:$LD_LIBRARY_PATH
./test
```

#### "ModuleNotFoundError: No module named 'charm'"

Set `PYTHONPATH` to the Charm root directory:
```bash
PYTHONPATH=/path/to/charm ./test
```

#### Segmentation fault on startup

1. Ensure Python version matches between compile and runtime
2. Check that all libraries (GMP, PBC) are the same architecture
3. On Apple Silicon, ensure you're not mixing arm64 and x86_64 binaries

#### "undefined symbol" errors

Ensure all libraries are linked. Check with:
```bash
make info  # Shows all linker flags
ldd ./test  # Linux: shows linked libraries
otool -L ./test  # macOS: shows linked libraries
```

### Debug Build

For debugging, build with debug symbols:
```bash
make clean
make OPTS="-g -O0 -DDEBUG=1"
```

### Architecture Mismatch (macOS)

If you see errors about wrong architecture:
```bash
# Check binary architecture
file ./test
file /opt/homebrew/lib/libgmp.dylib

# Force native architecture
arch -arm64 make clean
arch -arm64 make
```

---

## See Also

- `charm_embed_api.h` - Full API documentation in header comments
- `test.c` - Example usage with ABE encryption
- [Charm-Crypto Documentation](https://jhuisi.github.io/charm/)