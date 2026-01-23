# Building Charm-Crypto on macOS

A step-by-step guide to building and installing the Charm-Crypto framework on macOS.

## Prerequisites

Before you begin, ensure you have:
- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools installed
- Homebrew package manager

```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Step 1: Install System Dependencies

Install the required libraries using Homebrew:

```bash
# Core dependencies
brew install gmp openssl@3 wget

# Build tools
brew install m4 flex bison
```

### Install PBC (Pairing-Based Cryptography Library)

PBC may be available via Homebrew, but building from source ensures compatibility:

```bash
# Download PBC 1.0.0
cd /tmp
wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
tar xzf pbc-1.0.0.tar.gz
cd pbc-1.0.0

# Configure and build
./configure LDFLAGS="-lgmp"
make

# Install (requires sudo)
sudo make install
cd -
```

---

## Step 2: Set Environment Variables

The build system needs to find the installed libraries. Create these exports based on your MacOS architecture.

### For Apple Silicon (M1/M2/M3/M4)

```bash
export CFLAGS="-I/opt/homebrew/include -I/opt/homebrew/opt/gmp/include -I/opt/homebrew/opt/openssl@3/include"
export CPPFLAGS="$CFLAGS"
export LDFLAGS="-L/opt/homebrew/lib -L/opt/homebrew/opt/gmp/lib -L/opt/homebrew/opt/openssl@3/lib"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/gmp/lib/pkgconfig:/opt/homebrew/opt/openssl@3/lib/pkgconfig"
export CPATH="/opt/homebrew/include:/opt/homebrew/opt/gmp/include:/opt/homebrew/opt/openssl@3/include"
export LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/gmp/lib:/opt/homebrew/opt/openssl@3/lib"
```

### For Intel Macs

```bash
export CFLAGS="-I/usr/local/include -I/usr/local/opt/gmp/include -I/usr/local/opt/openssl@3/include"
export CPPFLAGS="$CFLAGS"
export LDFLAGS="-L/usr/local/lib -L/usr/local/opt/gmp/lib -L/usr/local/opt/openssl@3/lib"
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/usr/local/opt/gmp/lib/pkgconfig:/usr/local/opt/openssl@3/lib/pkgconfig"
```

> **Tip:** Add these to your `~/.zshrc` or `~/.bash_profile` to make them permanent.

---

## Step 3: Create a Python Virtual Environment

Isolate the Charm installation from your system Python:

```bash
# Navigate to the Charm directory
cd /path/to/charm

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip and install Python dependencies
pip install --upgrade pip setuptools
pip install pyparsing==2.1.5 hypothesis pytest
```

---

## Step 4: Configure Charm

Run the configuration script to detect your system and prepare the build:

```bash
# For macOS (recommended)
./configure.sh --enable-darwin

# Or specify your Python explicitly
./configure.sh --enable-darwin --python=$(which python3)
```

You should see output indicating that GMP, PBC, and OpenSSL were found.

---

## Step 5: Build Charm

Compile the Charm framework:

```bash
make
```

This builds the C extensions and Python modules. The process takes 1-2 minutes.

---

## Step 6: Install Charm

Install Charm into your Python environment:

```bash
# If using a virtual environment (no sudo needed)
make install

# If installing system-wide
sudo make install
```

---

## Step 7: Verify the Installation

Set the library path and test the import:

```bash
# Set library path for runtime
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH

# Test the installation
python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Charm installed successfully!')"
```

---

## Step 8: Run the Test Suite

Verify everything works by running the tests:

```bash
# Run all tests
make test

# Run scheme-specific tests
make test-schemes

# Run toolbox tests
make test-charm

# Or use pytest directly
pytest -v
```

---

## Troubleshooting

### "Library not loaded: libpbc"

```bash
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH
```

### "gmp.h not found"

Ensure environment variables from Step 2 are set, then reconfigure:
```bash
./configure.sh --enable-darwin --extra-cflags="-I/opt/homebrew/include"
```

### Permission denied during install

Use a virtual environment (Step 3) or install to a user directory:
```bash
./configure.sh --prefix=$HOME/.local
```

### Clean build (start fresh)

```bash
make clean
./configure.sh --enable-darwin
make
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `./configure.sh --enable-darwin` | Configure for macOS |
| `make` | Build Charm |
| `make install` | Install Charm |
| `make test` | Run test suite |
| `make clean` | Remove build artifacts |

---

## Next Steps

- Explore the `charm/schemes/` directory for cryptographic scheme implementations
- Check `charm/test/` for usage examples
- Read the documentation in `doc/` or visit [https://jhuisi.github.io/charm/](https://jhuisi.github.io/charm/)

