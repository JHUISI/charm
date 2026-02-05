# charm-crypto-lite

Lightweight elliptic curve cryptography from the [Charm Crypto Framework](https://github.com/JHUISI/charm).

## Overview

`charm-crypto-lite` provides **only** the OpenSSL-based elliptic curve operations from Charm, without GMP or PBC dependencies. This makes it:

- **Easy to install** - Only requires OpenSSL development libraries
- **Lightweight** - Minimal dependencies, fast installation
- **Focused** - EC operations only, no pairing-based cryptography

## Features

- Elliptic curve operations on standard curves (secp256k1, prime256v1, etc.)
- Hash-to-curve functionality
- Point serialization/deserialization
- Scalar multiplication and point addition
- Random element generation

## Installation

### Prerequisites

**macOS (Homebrew):**
```bash
brew install openssl
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libssl-dev python3-dev build-essential
```

### Install from PyPI

```bash
pip install charm-crypto-lite
```

### Build from Source

```bash
git clone https://github.com/JHUISI/charm.git
cd charm/lite
pip install -e .
```

## Usage

```python
from charm_lite.toolbox.ecgroup import ECGroup, ZR, G
from charm_lite.toolbox.eccurve import secp256k1

# Initialize group with secp256k1 curve
group = ECGroup(secp256k1)

# Generate random elements
g = group.random(G)   # Random point on curve
x = group.random(ZR)  # Random scalar

# Scalar multiplication
h = g ** x

# Hash to curve point
h = group.hash(b"message", G)

# Hash to scalar
s = group.hash(b"data", ZR)

# Serialization
data = group.serialize(h)
h2 = group.deserialize(data)
assert h == h2
```

## Supported Curves

All OpenSSL-supported curves are available, including:

- `secp256k1` (Bitcoin curve)
- `prime256v1` (NIST P-256)
- `secp384r1` (NIST P-384)
- `secp521r1` (NIST P-521)

See `charm_lite.toolbox.eccurve` for the full list.

## Migrating to Full Charm

If you later need pairing-based cryptography (ABE, IBE, etc.), you can migrate to the full Charm framework:

```bash
pip uninstall charm-crypto-lite
pip install charm-crypto-framework
```

The API is compatible - just change your imports:

```python
# From charm-crypto-lite
from charm_lite.toolbox.ecgroup import ECGroup

# To full Charm
from charm.toolbox.ecgroup import ECGroup
```

## License

LGPL-3.0-or-later (same as Charm Crypto Framework)

## Links

- [Charm Crypto Framework](https://github.com/JHUISI/charm)
- [Documentation](https://jhuisi.github.io/charm/)

