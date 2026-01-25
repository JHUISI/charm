Embedding Charm via Python/C API
================================

This directory contains the C/C++ embedding API for Charm-Crypto, allowing native applications to use Charm cryptographic schemes by embedding the Python interpreter.

Tested with Python 3.8+ on Linux and macOS.

## Requirements

- Python 3.8+ with development headers
- GMP library
- PBC library (for pairing-based cryptography)
- Charm-Crypto installed or in PYTHONPATH

## Compiling

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get install libgmp-dev libpbc-dev python3-dev

# Configure and build
./configure.sh
cd embed/
make

# Run test (set PYTHONPATH to charm root)
PYTHONPATH=/path/to/charm ./test
```

### macOS (Homebrew)

```bash
# Install dependencies
brew install gmp pbc

# Configure and build
./configure.sh --enable-darwin
cd embed/
make

# Run test (use arch -arm64 on Apple Silicon if needed)
PYTHONPATH=/path/to/charm ./test
```

**Note for Apple Silicon Macs**: If your shell is running under Rosetta but Python and libraries are native arm64, use `arch -arm64 ./test` to run in native mode.

### Windows

Not currently supported.

## API Overview

The embed API provides:

- `InitializeCharm()` / `CleanupCharm()` - Initialize/cleanup Python interpreter
- `InitPairingGroup()` / `InitECGroup()` / `InitIntegerGroup()` - Create group objects
- `InitScheme()` - Load a Charm scheme class
- `InitAdapter()` - Load a Charm adapter (e.g., hybrid encryption)
- `CallMethod()` - Call methods on Python objects
- `GetIndex()` / `GetDict()` - Access tuple/list/dict elements
- `objectToBytes()` / `bytesToObject()` - Serialization

See `charm_embed_api.h` for full API documentation.