# Charm-Crypto C/C++ Embedding API

Embed Charm-Crypto's powerful cryptographic schemes directly into your C/C++ applications.

This API allows native applications to use Charm's attribute-based encryption (ABE), identity-based encryption (IBE), digital signatures, and other cryptographic primitives by embedding the Python interpreter.

---

## Table of Contents

- [Quick Start](#quick-start) — Get running in 5 minutes
- [Requirements](#requirements) — What you need before building
- [Installation](#installation) — Platform-specific build instructions
- [API Reference](#api-reference) — Functions and usage patterns
- [Examples](#examples) — Complete working code
- [Troubleshooting](#troubleshooting) — Common issues and solutions
- [Additional Resources](#additional-resources)

---

## Quick Start

**For experienced developers who want to get running immediately:**

```bash
# 1. Install dependencies (choose your platform)
# Linux:  sudo apt-get install build-essential python3-dev libgmp-dev libpbc-dev
# macOS:  brew install gmp pbc

# 2. Configure and build (from charm root directory)
./configure.sh --enable-darwin    # macOS only: add --enable-darwin
cd embed/
make

# 3. Run the test
PYTHONPATH=.. ./test
```

**Expected output:**
```
DEBUG: cpabe initialized.
DEBUG: hyb_abe initialized.
DEBUG: setup ok.
DEBUG: keygen ok.
DEBUG: encrypt ok.
DEBUG: decrypt ok.
original msg :=> 'this is a test message.'
rec msg :=>
bytes :=> 'this is a test message.'
```

If you see this output, the embed API is working correctly. Continue reading for detailed instructions and API documentation.

---

## Requirements

### Software Dependencies

| Dependency | Version | Purpose | Required |
|------------|---------|---------|----------|
| **Python** | 3.8 - 3.11 | Runtime interpreter | ✅ Yes |
| **Python dev headers** | Same as Python | `Python.h` for compilation | ✅ Yes |
| **GMP** | 5.0+ | Big number arithmetic | ✅ Yes |
| **PBC** | 1.0.0 | Pairing-based cryptography | ✅ Yes |
| **OpenSSL** | 3.x | Elliptic curves, hashing | Optional |
| **GCC/Clang** | C99 compatible | Compiler | ✅ Yes |
| **Make** | Any | Build system | ✅ Yes |

### Platform Support

| Platform | Architecture | Status |
|----------|--------------|--------|
| **Linux** (Ubuntu 20.04+, Debian 11+) | x86_64, arm64 | ✅ Fully supported |
| **Linux** (RHEL 8+, Fedora 35+) | x86_64, arm64 | ✅ Fully supported |
| **macOS** (11 Big Sur+) | Intel x86_64 | ✅ Fully supported |
| **macOS** (11 Big Sur+) | Apple Silicon arm64 | ✅ Fully supported |
| **Windows** (MSYS2/MinGW) | x86_64 | ⚠️ Experimental |

---

## Installation

Choose your platform below. Each section includes dependency installation, build commands, and verification steps.

### Linux (Ubuntu/Debian)

<details open>
<summary><strong>Click to expand Ubuntu/Debian instructions</strong></summary>

#### Step 1: Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libgmp-dev \
    libpbc-dev \
    libssl-dev
```

#### Step 2: Configure Charm

```bash
# From the charm root directory
./configure.sh
```

**Expected output (last few lines):**
```
python            /usr/bin/python3
libgmp found      yes
libpbc found      yes
```

#### Step 3: Build the Embed API

```bash
cd embed/
make
```

**Expected output:**
```
Compiling charm_embed_api.c...
Compiling test.c...
Linking test for linux (x86_64)...
Build complete: test
```

#### Step 4: Verify Installation

```bash
# Run from the embed/ directory
PYTHONPATH=.. ./test
```

**Expected output:** See [Quick Start](#quick-start) section above.

</details>

---

### Linux (RHEL/CentOS/Fedora)

<details>
<summary><strong>Click to expand RHEL/Fedora instructions</strong></summary>

#### Step 1: Install Dependencies

```bash
# Fedora / RHEL 8+
sudo dnf install -y \
    gcc \
    make \
    python3-devel \
    gmp-devel \
    pbc-devel \
    openssl-devel
```

> **Note:** On older CentOS/RHEL, use `yum` instead of `dnf`.

#### Step 2: Configure and Build

```bash
./configure.sh
cd embed/
make
```

#### Step 3: Verify Installation

```bash
PYTHONPATH=.. ./test
```

</details>

---

### macOS (Intel x86_64)

<details>
<summary><strong>Click to expand macOS Intel instructions</strong></summary>

#### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Dependencies

```bash
brew install gmp pbc openssl@3
```

#### Step 3: Configure Charm

```bash
# The --enable-darwin flag is REQUIRED on macOS
./configure.sh --enable-darwin
```

#### Step 4: Build the Embed API

```bash
cd embed/
make
```

#### Step 5: Verify Installation

```bash
PYTHONPATH=.. ./test
```

> **Library Paths:** On Intel Macs, Homebrew installs to `/usr/local/`. The Makefile detects this automatically.

</details>

---

### macOS (Apple Silicon M1/M2/M3/M4)

<details>
<summary><strong>Click to expand macOS Apple Silicon instructions</strong></summary>

#### Step 1: Install Dependencies

```bash
brew install gmp pbc openssl@3
```

#### Step 2: Configure Charm

```bash
./configure.sh --enable-darwin
```

#### Step 3: Build the Embed API

```bash
cd embed/
make
```

#### Step 4: Verify Installation

```bash
PYTHONPATH=.. ./test
```

> **Library Paths:** On Apple Silicon, Homebrew installs to `/opt/homebrew/`. The Makefile detects this automatically based on `uname -m`.

#### ⚠️ Rosetta Compatibility Warning

If your terminal runs under Rosetta (x86_64 emulation) but your Python and libraries are native arm64, you may encounter architecture mismatch errors.

**To check your terminal architecture:**
```bash
uname -m
# Should output: arm64 (native) or x86_64 (Rosetta)
```

**To force native arm64 execution:**
```bash
arch -arm64 make clean
arch -arm64 make
arch -arm64 ./test
```

</details>

---

### Windows (MSYS2/MinGW) — Experimental

<details>
<summary><strong>Click to expand Windows instructions</strong></summary>

> ⚠️ **Warning:** Windows support is experimental. Some features may not work correctly.

#### Step 1: Install MSYS2

Download and install from: https://www.msys2.org/

#### Step 2: Open the Correct Terminal

Open **"MSYS2 MinGW 64-bit"** (not "MSYS2 MSYS" or "UCRT").

#### Step 3: Install Dependencies

```bash
# Update package database
pacman -Syu

# Install build tools
pacman -S --noconfirm \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-make \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-gmp \
    mingw-w64-x86_64-openssl
```

#### Step 4: Build PBC Library (Manual)

PBC is not available in MSYS2 packages. You must build it from source:

```bash
# Download PBC
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar xzf pbc-0.5.14.tar.gz
cd pbc-0.5.14

# Configure and build
./configure --prefix=/mingw64
make
make install
```

#### Step 5: Configure and Build Charm

```bash
./configure.sh --build-win-exe
cd embed/
make
```

#### Step 6: Verify Installation

```bash
PYTHONPATH=.. ./test.exe
```

</details>

---

### Build Configuration Info

To see what the Makefile detected about your system:

```bash
cd embed/
make info
```

**Example output:**
```
============================================
Charm Embed API Build Configuration
============================================
Platform:        macos
Architecture:    arm64
Compiler:        gcc
Executable:      test
Homebrew prefix: /opt/homebrew
============================================
```

This is useful for debugging build issues.

---

## API Reference

### Lifecycle Functions

These functions manage the Python interpreter lifecycle.

```c
#include "charm_embed_api.h"

// Initialize the Python interpreter. Call once at program start.
int InitializeCharm(void);

// Cleanup and finalize Python. Call once at program end.
void CleanupCharm(void);
```

### Group Initialization

Create mathematical groups for cryptographic operations.

```c
// Create a pairing group for pairing-based crypto (ABE, IBE, etc.)
// curve: "BN254" (128-bit security, recommended) or "SS512" (80-bit, legacy)
Charm_t *InitPairingGroup(Charm_t *pModule, const char *curve);

// Create an elliptic curve group for EC-based crypto
// curve_id: OpenSSL curve NID (e.g., NID_secp256k1)
Charm_t *InitECGroup(Charm_t *pModule, int curve_id);

// Create an integer group for RSA-style crypto
// bits: Key size in bits (e.g., 2048)
Charm_t *InitIntegerGroup(Charm_t *pModule, int bits);
```

### Scheme and Adapter Loading

Load Charm cryptographic schemes and adapters.

```c
// Load a cryptographic scheme class
// class_file: Python module path (e.g., "charm.schemes.abenc.abenc_bsw07")
// class_name: Class name (e.g., "CPabe_BSW07")
// pObject: Group object from InitPairingGroup/InitECGroup
Charm_t *InitScheme(const char *class_file, const char *class_name, Charm_t *pObject);

// Load an adapter (wraps a scheme with additional functionality)
// pObject1: The underlying scheme
// pObject2: The group object
Charm_t *InitAdapter(const char *class_file, const char *class_name,
                     Charm_t *pObject1, Charm_t *pObject2);
```

### Method Invocation

Call methods on Python objects with type-safe argument passing.

```c
// Call a method on a Python object
// func_name: Method name (e.g., "setup", "encrypt", "decrypt")
// types: Format string specifying argument types (see table below)
// ...: Arguments matching the format string
Charm_t *CallMethod(Charm_t *pObject, const char *func_name, char *types, ...);
```

#### Format Specifiers

| Specifier | C Type | Python Type | Example |
|-----------|--------|-------------|---------|
| `%O` | `Charm_t*` | Any object | `CallMethod(obj, "foo", "%O", other_obj)` |
| `%s` | `char*` | `str` | `CallMethod(obj, "foo", "%s", "hello")` |
| `%b` | `char*` | `bytes` | `CallMethod(obj, "foo", "%b", "data")` |
| `%i` | `int` | `int` | `CallMethod(obj, "foo", "%i", 42)` |
| `%I` | `char*` | Group element type | `CallMethod(grp, "random", "%I", GT)` |
| `%A` | `char*` | Attribute list | `CallMethod(obj, "keygen", "%A", "[A, B]")` |

**Group element type constants:** `ZR`, `G1`, `G2`, `GT`, `G`

### Data Access

Extract values from Python containers.

```c
// Get item from tuple or list by index
// Returns a NEW reference — you must call Free() when done
Charm_t *GetIndex(Charm_t *pObject, int index);

// Get item from dictionary by key
// Returns a NEW reference — you must call Free() when done
Charm_t *GetDict(Charm_t *pObject, char *key);
```

### Serialization

Convert objects to/from bytes for storage or transmission.

```c
// Serialize a Charm object to bytes
Charm_t *objectToBytes(Charm_t *object, Charm_t *group);

// Deserialize bytes back to a Charm object
Charm_t *bytesToObject(Charm_t *object, Charm_t *group);
```

### Memory Management

```c
// Release a Python object reference
// Always call this when you're done with an object
#define Free(obj) Py_XDECREF(obj)
```

> **⚠️ Important:** Every object returned by `GetIndex()`, `GetDict()`, `CallMethod()`, `InitScheme()`, etc. must be freed with `Free()` to prevent memory leaks.

---

## Examples

### Minimal Example

The simplest possible program using the embed API:

```c
#include "charm_embed_api.h"

int main(void) {
    // Initialize Python
    InitializeCharm();

    // Create a pairing group with 128-bit security
    Charm_t *group = InitPairingGroup(NULL, "BN254");
    if (group == NULL) {
        printf("Failed to initialize pairing group\n");
        return 1;
    }

    // Generate a random group element
    Charm_t *element = CallMethod(group, "random", "%I", G1);

    // Print it
    printf("Random G1 element: ");
    PyObject_Print(element, stdout, 0);
    printf("\n");

    // Cleanup
    Free(element);
    Free(group);
    CleanupCharm();

    return 0;
}
```

### Complete ABE Example

Full attribute-based encryption with key generation, encryption, and decryption:

```c
#include "charm_embed_api.h"
#include <stdio.h>

int main(void) {
    // ========================================
    // Step 1: Initialize
    // ========================================
    InitializeCharm();

    // Create pairing group (BN254 = 128-bit security)
    Charm_t *group = InitPairingGroup(NULL, "BN254");
    if (group == NULL) {
        printf("ERROR: Failed to create pairing group\n");
        return 1;
    }

    // Load the CP-ABE scheme (Bethencourt-Sahai-Waters 2007)
    Charm_t *abe = InitScheme(
        "charm.schemes.abenc.abenc_bsw07",  // Python module
        "CPabe_BSW07",                       // Class name
        group                                // Pairing group
    );
    if (abe == NULL) {
        printf("ERROR: Failed to load ABE scheme\n");
        return 1;
    }

    // Wrap with hybrid adapter for encrypting arbitrary data
    Charm_t *hybrid = InitAdapter(
        "charm.adapters.abenc_adapt_hybrid",
        "HybridABEnc",
        abe,    // The underlying ABE scheme
        group   // The pairing group
    );
    if (hybrid == NULL) {
        printf("ERROR: Failed to load hybrid adapter\n");
        return 1;
    }

    // ========================================
    // Step 2: Setup (generate master keys)
    // ========================================
    Charm_t *keys = CallMethod(hybrid, "setup", "");
    Charm_t *public_key = GetIndex(keys, 0);   // Public parameters
    Charm_t *master_key = GetIndex(keys, 1);   // Master secret key

    printf("Setup complete. Keys generated.\n");

    // ========================================
    // Step 3: Key Generation (for a user)
    // ========================================
    // User has attributes: DEPARTMENT_ENGINEERING and CLEARANCE_SECRET
    char *user_attributes = "[DEPARTMENT_ENGINEERING, CLEARANCE_SECRET]";

    Charm_t *user_key = CallMethod(
        hybrid, "keygen",
        "%O%O%A",           // Format: object, object, attribute list
        public_key,
        master_key,
        user_attributes
    );

    printf("User key generated for attributes: %s\n", user_attributes);

    // ========================================
    // Step 4: Encryption
    // ========================================
    // Policy: Must have ENGINEERING dept AND (SECRET or TOP_SECRET clearance)
    char *policy = "(DEPARTMENT_ENGINEERING and (CLEARANCE_SECRET or CLEARANCE_TOP_SECRET))";
    char *message = "This is a classified engineering document.";

    Charm_t *ciphertext = CallMethod(
        hybrid, "encrypt",
        "%O%b%s",           // Format: object, bytes, string
        public_key,
        message,
        policy
    );

    printf("Message encrypted under policy: %s\n", policy);

    // ========================================
    // Step 5: Decryption
    // ========================================
    Charm_t *decrypted = CallMethod(
        hybrid, "decrypt",
        "%O%O%O",           // Format: three objects
        public_key,
        user_key,
        ciphertext
    );

    // Print the decrypted message
    printf("\nOriginal:  %s\n", message);
    printf("Decrypted: ");

    // Get the bytes from the Python bytes object
    char *result = PyBytes_AsString(decrypted);
    if (result) {
        printf("%s\n", result);
    }

    // ========================================
    // Step 6: Cleanup (IMPORTANT!)
    // ========================================
    Free(decrypted);
    Free(ciphertext);
    Free(user_key);
    Free(master_key);
    Free(public_key);
    Free(keys);
    Free(hybrid);
    Free(abe);
    Free(group);

    CleanupCharm();

    printf("\nSuccess! All resources cleaned up.\n");
    return 0;
}
```

### Serialization Example

Save and load cryptographic objects:

```c
// Serialize a secret key to bytes (for storage)
Charm_t *sk_bytes = objectToBytes(secret_key, group);

// Get the raw bytes
char *data = PyBytes_AsString(sk_bytes);
Py_ssize_t length = PyBytes_Size(sk_bytes);

// ... save 'data' to file or database ...

// Later: deserialize back to an object
Charm_t *restored_key = bytesToObject(sk_bytes, group);

Free(sk_bytes);
Free(restored_key);
```

---

## Troubleshooting

### Quick Diagnostic

Run these commands to diagnose common issues:

```bash
# Check build configuration
make info

# Check binary architecture (macOS)
file ./test

# Check linked libraries (Linux)
ldd ./test

# Check linked libraries (macOS)
otool -L ./test

# Check Python path
python3 -c "import charm; print(charm.__file__)"
```

---

### Build Errors

#### ❌ `Python.h: No such file or directory`

**Cause:** Python development headers not installed.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# RHEL/Fedora
sudo dnf install python3-devel

# macOS (Homebrew Python)
brew install python3
# Headers are included automatically
```

---

#### ❌ `gmp.h: No such file or directory` or `pbc/pbc.h: No such file or directory`

**Cause:** GMP or PBC development libraries not installed.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libgmp-dev libpbc-dev

# macOS
brew install gmp pbc
```

**Alternative:** Specify include paths manually:
```bash
make CPPFLAGS="-I/path/to/gmp/include -I/path/to/pbc/include"
```

---

#### ❌ `cannot find -lgmp` or `cannot find -lpbc`

**Cause:** Linker can't find library files.

**Solution:** Specify library paths:
```bash
make LDFLAGS="-L/path/to/gmp/lib -L/path/to/pbc/lib"
```

---

#### ❌ `ld: library not found for -lpython3.x`

**Cause:** Python library not in linker path.

**Solution (macOS):**
```bash
# Find Python library location
python3-config --ldflags --embed

# Add to LDFLAGS if needed
make LDFLAGS="-L$(python3 -c 'import sys; print(sys.prefix)')/lib"
```

---

### Runtime Errors

#### ❌ `ModuleNotFoundError: No module named 'charm'`

**Cause:** Python can't find the Charm package.

**Solution:** Set `PYTHONPATH` to the Charm root directory:
```bash
# If running from embed/ directory
PYTHONPATH=.. ./test

# If running from charm root directory
PYTHONPATH=. embed/test

# Or use absolute path
PYTHONPATH=/full/path/to/charm ./test
```

---

#### ❌ `error while loading shared libraries: libpython3.x.so`

**Cause:** Python shared library not in runtime library path.

**Solution (Linux):**
```bash
export LD_LIBRARY_PATH=$(python3 -c 'import sys; print(sys.prefix)')/lib:$LD_LIBRARY_PATH
./test
```

**Solution (macOS):**
```bash
export DYLD_LIBRARY_PATH=$(python3 -c 'import sys; print(sys.prefix)')/lib:$DYLD_LIBRARY_PATH
./test
```

---

#### ❌ Segmentation fault on startup

**Possible causes:**

1. **Python version mismatch:** Compiled with one Python version, running with another.
   ```bash
   # Check which Python was used for compilation
   make info | grep Python

   # Check runtime Python
   python3 --version
   ```

2. **Architecture mismatch (macOS):** Mixing arm64 and x86_64 binaries.
   ```bash
   # Check all binaries are same architecture
   file ./test
   file $(brew --prefix)/lib/libgmp.dylib
   file $(python3 -c 'import sys; print(sys.prefix)')/lib/libpython*.dylib
   ```

3. **Corrupted build:** Try a clean rebuild:
   ```bash
   make clean
   make
   ```

---

#### ❌ `mach-o file, but is an incompatible architecture` (macOS)

**Cause:** Binary architecture doesn't match library architecture.

**Solution:** Force native architecture build:
```bash
# On Apple Silicon
arch -arm64 make clean
arch -arm64 make
arch -arm64 ./test

# On Intel Mac
arch -x86_64 make clean
arch -x86_64 make
```

---

### Debug Build

For detailed debugging information:

```bash
make clean
make OPTS="-g -O0 -DDEBUG=1"

# Run with debugger
lldb ./test    # macOS
gdb ./test     # Linux
```

---

## Additional Resources

### Files in This Directory

| File | Description |
|------|-------------|
| `charm_embed_api.h` | Header file with full API documentation |
| `charm_embed_api.c` | Implementation of the embed API |
| `test.c` | Example program demonstrating ABE usage |
| `Makefile` | Cross-platform build configuration |

### Related Documentation

- **[Charm-Crypto Documentation](https://jhuisi.github.io/charm/)** — Full Python API reference
- **[PBC Library](https://crypto.stanford.edu/pbc/)** — Pairing-Based Cryptography library
- **[Python/C API](https://docs.python.org/3/c-api/)** — Python embedding documentation

### Available Schemes

The embed API can load any Charm scheme. Common ones include:

| Scheme | Module | Class | Type |
|--------|--------|-------|------|
| CP-ABE (BSW07) | `charm.schemes.abenc.abenc_bsw07` | `CPabe_BSW07` | Ciphertext-Policy ABE |
| KP-ABE (LSW08) | `charm.schemes.abenc.abenc_lsw08` | `KPabe` | Key-Policy ABE |
| IBE (Waters09) | `charm.schemes.ibenc.ibenc_waters09` | `IBE_N04` | Identity-Based Encryption |
| BLS Signatures | `charm.schemes.pksig.pksig_bls04` | `BLS01` | Short Signatures |

### Getting Help

- **GitHub Issues:** https://github.com/JHUISI/charm/issues
- **Email:** support@charm-crypto.com
