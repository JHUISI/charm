# charm-crypto-lite

**Minimal elliptic curve cryptography for Python** — a lightweight subset of the [Charm Crypto Framework](https://github.com/JHUISI/charm).

## Why charm-crypto-lite?

| | charm-crypto-lite | charm-crypto-framework |
|---|---|---|
| **Python dependencies** | **None** | pyparsing |
| **C library dependencies** | OpenSSL only | OpenSSL + GMP + PBC |
| **Scope** | secp256k1 EC operations | Full crypto toolkit |
| **Use case** | ECDSA, Schnorr, ECDH | ABE, IBE, pairing-based crypto |

**Use charm-crypto-lite if you:**
- Only need elliptic curve operations on secp256k1 (Bitcoin/Ethereum curve)
- Want zero Python dependencies and minimal C dependencies
- Need a lightweight package for serverless/containerized environments

**Use [charm-crypto-framework](https://pypi.org/project/charm-crypto-framework/) if you:**
- Need pairing-based cryptography (ABE, IBE, signatures)
- Need multiple curve types or pairing groups
- Are building advanced cryptographic protocols

## Installation

```bash
pip install charm-crypto-lite
```

**Prerequisites:** OpenSSL development libraries

```bash
# macOS
brew install openssl

# Ubuntu/Debian
sudo apt-get install libssl-dev python3-dev build-essential
```

## Quick Start

```python
from charm_lite.toolbox.ecgroup import ECGroup, ZR, G
from charm_lite.toolbox.eccurve import secp256k1

group = ECGroup(secp256k1)

# Get the generator point
g = group.generator()

# Generate random scalar (private key)
x = group.random(ZR)

# Scalar multiplication: public_key = g^x
pk = g ** x

# Point addition (multiplicative notation): p = h * k
h = g ** group.random(ZR)
p = pk * h

# Serialization
data = group.serialize(pk)
pk2 = group.deserialize(data)
assert pk == pk2
```

## API Reference

### ECGroup Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| Generator | `group.generator()` | Get curve generator point G |
| Random scalar | `group.random(ZR)` | Random scalar in field |
| Random point | `group.random(G)` | Random point on curve |
| Scalar multiply | `g ** x` | Point × scalar |
| Point add | `h * k` | Point + point (multiplicative notation) |
| Point negate | `-h` | Additive inverse |
| Scalar add | `x + y` | Field addition |
| Scalar multiply | `x * y` | Field multiplication |
| Scalar invert | `~x` | Multiplicative inverse |
| Serialize | `group.serialize(elem)` | To bytes |
| Deserialize | `group.deserialize(data)` | From bytes |
| Group order | `group.order()` | Curve order n |

### PKEnc Base Class

For building encryption schemes:

```python
from charm_lite.toolbox.PKEnc import PKEnc

class MyScheme(PKEnc):
    def keygen(self): ...
    def encrypt(self, pk, msg): ...
    def decrypt(self, sk, ct): ...
```

## Migrating to Full Charm

```bash
pip uninstall charm-crypto-lite
pip install charm-crypto-framework
```

Change imports from `charm_lite` to `charm`:

```python
# Before
from charm_lite.toolbox.ecgroup import ECGroup

# After
from charm.toolbox.ecgroup import ECGroup
```

## License

LGPL-3.0-or-later

## Links

- [Charm Crypto Framework](https://github.com/JHUISI/charm)
- [Documentation](https://jhuisi.github.io/charm/)

