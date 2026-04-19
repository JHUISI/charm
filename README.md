Charm-Crypto
============

| Branch      | Status                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| `dev`       | ![Build Status](https://github.com/JHUISI/charm/actions/workflows/ci.yml/badge.svg?branch=dev) |

Charm is a framework for rapidly prototyping advanced cryptosystems. Based on the Python language, it was designed from the ground up to minimize development time and code complexity while promoting the reuse of components.

Charm uses a hybrid design: performance-intensive mathematical operations are implemented in native C modules, while cryptosystems themselves are written in a readable, high-level language. Charm additionally provides a number of new components to facilitate the rapid development of new schemes and protocols.

## Features

### Advanced Cryptographic Schemes

* **Attribute-Based Encryption (ABE)**: Fine-grained access control encryption
  - Ciphertext-Policy ABE (CP-ABE): BSW07, Waters09, FAME
  - Key-Policy ABE (KP-ABE): LSW08, GPSW06
  - Multi-Authority ABE, Decentralized ABE
* **Identity-Based Encryption (IBE)**: Encryption using identities as public keys
  - Waters05, Boneh-Boyen (BB04), Boneh-Franklin
* **Pairing-Based Cryptography**: BN254, BLS12-381 curve support (~128-bit security)
  - Bilinear pairings for advanced protocols
  - Efficient implementation via PBC library
* **Digital Signatures**: Comprehensive signature scheme library
  - Pairing-based: BLS (Ethereum 2.0), Waters, CL04, Boyen
  - Elliptic curve: ECDSA, Schnorr, EdDSA
  - Standard: RSA, DSA, Lamport
  - Aggregate/Multi-signatures: BLS aggregation, MuSig
* **Public-Key Encryption**: Standard and advanced PKE schemes
  - ElGamal, RSA, Paillier (homomorphic), Cramer-Shoup
* **Post-Quantum / Lattice-Based Cryptography**: NTL-backed lattice schemes *(optional module)*
  - Ring-LWE Public Key Encryption (LPR)
  - Kyber-style KEM (simplified ML-KEM / FIPS 203)
  - Dilithium-style Signatures (simplified ML-DSA / FIPS 204)
  - Lattice-based Identity-Based Encryption (ABB10)
  - Polynomial ring arithmetic in R_q = Z_q[X]/(X^n+1)
* **Commitments & Secret Sharing**: Pedersen commitments, Feldman/Pedersen VSS

### Threshold Cryptography / MPC

* **Threshold ECDSA**: Production-ready t-of-n distributed signing
  - GG18 (Gennaro-Goldfeder 2018) — Classic Paillier-based threshold ECDSA
  - CGGMP21 (Canetti et al. 2021) — UC-secure with identifiable aborts
  - DKLS23 (Doerner et al. 2023) — Non-interactive presigning with OT-based MtA
  - Supports secp256k1 (Bitcoin, XRPL) and other curves

### Zero-Knowledge Proofs

* **ZKP Compiler**: Production-ready compiler for interactive and non-interactive proofs
  - Schnorr proofs, Discrete Log Equality (DLEQ)
  - Knowledge of Representation proofs
  - AND/OR composition for complex statements
  - Range proofs via bit decomposition
  - Batch verification for improved performance

### Infrastructure & Tools

* **Mathematical Settings**: Integer rings/fields, bilinear and non-bilinear EC groups
* **Base Crypto Library**: Symmetric encryption (AES), hash functions, PRNGs
* **Protocol Engine**: Simplifies multi-party protocol implementation
* **C/C++ Embed API**: Native applications can embed Charm via the Python C API
* **Integrated Benchmarking**: Built-in performance measurement

## Requirements

| Component | Supported Versions |
|-----------|-------------------|
| **Python** | 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 |
| **Operating Systems** | Linux, macOS, Windows |
| **OpenSSL** | 3.0+ |

## Installation

### One-Line Install (Recommended)

The easiest way to install Charm is using the automated install script, which handles all system dependencies:

```bash
curl -sSL https://raw.githubusercontent.com/JHUISI/charm/dev/install.sh | bash
```

**Supported platforms:**
- Ubuntu/Debian (and derivatives: Linux Mint, Pop!_OS)
- Fedora/RHEL/CentOS (and derivatives: Rocky, Alma, Oracle Linux)
- Arch Linux (and derivatives: Manjaro, EndeavourOS)
- macOS (Intel and Apple Silicon)

**Install options:**
```bash
# Default: install from PyPI (recommended)
curl -sSL ... | bash

# Install from source (for development)
curl -sSL ... | bash -s -- --from-source

# Only install system dependencies (for manual pip install)
curl -sSL ... | bash -s -- --deps-only

# See all options
./install.sh --help
```

### Quick Install (pip)

If you prefer to install dependencies manually:

```bash
pip install charm-crypto-framework
```

> **Note:** System libraries (GMP, PBC, OpenSSL) must be installed first. See [Prerequisites](#prerequisites) below.

### Prerequisites

Charm requires the following system libraries:

| Library | Version | Purpose |
|---------|---------|---------|
| [GMP](http://gmplib.org/) | 5.0+ | Arbitrary precision arithmetic |
| [PBC](http://crypto.stanford.edu/pbc/download.html) | 1.0.0 | Pairing-based cryptography |
| [OpenSSL](http://www.openssl.org/source/) | 3.0+ | Cryptographic primitives |
| [NTL](https://libntl.org/) | 11.0+ | Lattice-based cryptography *(optional)* |

**Ubuntu/Debian:**
```bash
sudo apt-get install libgmp-dev libssl-dev libpbc-dev flex bison

# Optional: for lattice-based crypto module
sudo apt-get install libntl-dev
```

**macOS (Homebrew):**
```bash
brew install gmp openssl@3 pbc

# Optional: for lattice-based crypto module
brew install ntl
```

**PBC from Source** (if not available via package manager):
```bash
wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
tar xzf pbc-1.0.0.tar.gz
cd pbc-1.0.0
./configure && make && sudo make install
```

**NTL from Source** (if not available via package manager):
```bash
wget https://libntl.org/ntl-11.6.0.tar.gz
tar xzf ntl-11.6.0.tar.gz
cd ntl-11.6.0/src
./configure NTL_GMP_LIP=on SHARED=on
make && sudo make install
```

### From Source (Development)

```bash
git clone https://github.com/JHUISI/charm.git
cd charm
./configure.sh  # add --enable-darwin on macOS
pip install -e ".[dev]"
```

To include the lattice-based crypto module (requires NTL):

```bash
./configure.sh --enable-lattice  # add --enable-darwin on macOS
LAT_MOD=yes pip install -e ".[dev]"
```

### Verify Installation

```bash
python -c "from charm.toolbox.pairinggroup import PairingGroup; print('Charm installed successfully\!')"
```

## Testing

Charm includes comprehensive test suites:

```bash
# Run all tests
make test-all

# Run specific test categories
make test-unit       # Unit tests (toolbox, serialize, vectors)
make test-schemes    # Cryptographic scheme tests
make test-zkp        # ZKP compiler tests
make test-adapters   # Adapter tests
make test-embed      # C/C++ embed API tests

# Threshold ECDSA tests (GG18, CGGMP21, DKLS23)
pytest charm/test/schemes/threshold_test.py -v -k "GG18 or CGGMP21 or DKLS23"

# Run with coverage
pytest --cov=charm charm/test/ -v
```

## Documentation

* [Installation Guide](https://jhuisi.github.io/charm/install_source.html)
* [Scheme Examples](https://jhuisi.github.io/charm/schemes.html)
* [API Reference](https://jhuisi.github.io/charm/)
* [C/C++ Embed API](embed/README.md)

## Quick Examples

### BLS Signatures (Pairing-Based)

BLS signatures (Boneh-Lynn-Shacham) — standardized in [IETF RFC 9380](https://datatracker.ietf.org/doc/rfc9380/) and used in Ethereum 2.0:

```python
from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.pksig.pksig_bls04 import BLS01

# Initialize pairing group (BN254 curve, ~128-bit security)
group = PairingGroup('BN254')
bls = BLS01(group)

# Ethereum 2.0 validator attestation
attestation = {'slot': 1234, 'epoch': 38, 'beacon_block_root': '0xabc...'}

(pk, sk) = bls.keygen()
signature = bls.sign(sk['x'], attestation)
assert bls.verify(pk, signature, attestation)
```

### ECDSA with secp256k1 (Bitcoin)

ECDSA on secp256k1 — the curve used by Bitcoin ([SEC 2](https://www.secg.org/sec2-v2.pdf), [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)):

```python
import hashlib
import json
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import secp256k1
from charm.schemes.pksig.pksig_ecdsa import ECDSA

group = ECGroup(secp256k1)
ecdsa = ECDSA(group)

# Bitcoin transaction (simplified)
tx = {
    'inputs': [{'txid': 'a1b2c3...', 'vout': 0, 'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}],
    'outputs': [{'address': '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', 'satoshis': 50000}],
    'fee': 1000
}

# Serialize and double SHA-256 (SHA-256d) per Bitcoin protocol
tx_bytes = json.dumps(tx, sort_keys=True).encode('utf-8')
tx_hash = hashlib.sha256(hashlib.sha256(tx_bytes).digest()).hexdigest()

(pk, sk) = ecdsa.keygen(0)
signature = ecdsa.sign(pk, sk, tx_hash)
assert ecdsa.verify(pk, signature, tx_hash)
```

> **Note:** Production Bitcoin implementations should use proper transaction serialization
> per [Bitcoin Developer Documentation](https://developer.bitcoin.org/reference/transactions.html).

### ECDSA with secp256k1 (XRPL)

ECDSA on secp256k1 — also used by XRP Ledger ([SEC 2](https://www.secg.org/sec2-v2.pdf)):

```python
import hashlib
import json
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import secp256k1
from charm.schemes.pksig.pksig_ecdsa import ECDSA

group = ECGroup(secp256k1)
ecdsa = ECDSA(group)

# XRPL Payment transaction
tx = {
    'TransactionType': 'Payment',
    'Account': 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh',
    'Destination': 'rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe',
    'Amount': '1000000',  # drops of XRP
    'Sequence': 1
}

# Serialize and hash (XRPL uses canonical binary + SHA-512Half)
tx_bytes = json.dumps(tx, sort_keys=True).encode('utf-8')
tx_hash = hashlib.sha512(tx_bytes).hexdigest()[:64]  # SHA-512Half

(pk, sk) = ecdsa.keygen(0)
signature = ecdsa.sign(pk, sk, tx_hash)
assert ecdsa.verify(pk, signature, tx_hash)
```

> **Note:** Production XRPL implementations should use canonical binary serialization
> per [XRPL documentation](https://xrpl.org/serialization.html).

### Threshold ECDSA

Charm provides three production-ready threshold ECDSA implementations for MPC-based signing.
All support secp256k1 (Bitcoin, XRPL) and other elliptic curves.

**GG18 (2-of-3 threshold signing):**

```python
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import secp256k1
from charm.schemes.threshold import GG18

group = ECGroup(secp256k1)
gg18 = GG18(group, threshold=2, num_parties=3)

# Distributed key generation
key_shares, public_key = gg18.keygen()

# Sign with 2 of 3 parties (interactive, 4 rounds)
message = b"Bitcoin transaction hash"
signature = gg18.sign(key_shares[:2], message)
assert gg18.verify(public_key, message, signature)
```

**CGGMP21 with presigning (UC-secure, identifiable aborts):**

```python
from charm.schemes.threshold import CGGMP21

cggmp = CGGMP21(group, threshold=2, num_parties=3)
key_shares, public_key = cggmp.keygen()

# Optional presigning (can be done offline)
presignatures = cggmp.presign(key_shares[:2])

# Fast online signing with presignature
message = b"XRPL payment"
signature = cggmp.sign(key_shares[:2], message, presignatures)
assert cggmp.verify(public_key, message, signature)
```

**DKLS23 with XRPL testnet:**

```python
from charm.schemes.threshold import DKLS23
from charm.schemes.threshold.xrpl_wallet import XRPLThresholdWallet, XRPLClient

dkls = DKLS23(group, threshold=2, num_parties=3)
key_shares, public_key = dkls.keygen()
wallet = XRPLThresholdWallet(group, public_key)
client = XRPLClient(is_testnet=True)
```

See `examples/xrpl_memo_demo.py` for a complete XRPL testnet flow.

**Comparison of Threshold ECDSA Schemes:**

| Feature | GG18 | CGGMP21 | DKLS23 |
|---------|------|---------|--------|
| **Security Model** | ROM | UC (composable) | ROM |
| **DKG Rounds** | 3 | 3 | 3 |
| **Signing Rounds** | 4 (interactive) | 3 presign + 1 sign | 3 presign + 1 sign |
| **Presigning** | ❌ No | ✅ Yes | ✅ Yes |
| **Identifiable Aborts** | ❌ No | ✅ Yes | ❌ No |
| **MtA Protocol** | Paillier | Paillier | OT-based |
| **Best For** | Simple deployments | High security needs | Low-latency signing |

**References:**
- GG18: [Gennaro & Goldfeder 2018](https://eprint.iacr.org/2019/114.pdf)
- CGGMP21: [Canetti et al. 2021](https://eprint.iacr.org/2021/060)
- DKLS23: [Doerner et al. 2023](https://eprint.iacr.org/2023/765)

### Lattice-Based Cryptography (Post-Quantum)

Charm includes a lattice-based crypto module backed by [NTL](https://libntl.org/), providing polynomial ring arithmetic in R_q = Z_q[X]/(X^n+1). Requires building with `LAT_MOD=yes` (see [Installation](#installation)).

**Ring-LWE Encryption (LPR scheme):**

```python
from charm.toolbox.latticegroup import LatticeGroup
from charm.schemes.latenc.rlwe_pke import RLWE_PKE

# R_q = Z_7681[X]/(X^256 + 1), ~128-bit post-quantum security
group = LatticeGroup('RLWE-256-7681')
rlwe = RLWE_PKE(group, sigma=3.0)

(pk, sk) = rlwe.keygen()
ciphertext = rlwe.encrypt(pk, b"Post-quantum secure!")
plaintext = rlwe.decrypt(sk, ciphertext)[:20]
assert plaintext == b"Post-quantum secure!"
```

**Kyber KEM (simplified ML-KEM / FIPS 203):**

```python
from charm.toolbox.latticegroup import LatticeGroup
from charm.schemes.latenc.kyber_kem import KyberKEM

# ML-KEM-768 parameters (n=256, q=3329, k=3)
group = LatticeGroup('KYBER-768')
kem = KyberKEM(group, 'KYBER-768')

(pk, sk) = kem.keygen()
(ciphertext, shared_secret_enc) = kem.encapsulate(pk)
shared_secret_dec = kem.decapsulate(sk, ciphertext)
assert shared_secret_enc == shared_secret_dec  # 32-byte shared key
```

**Dilithium Signatures (simplified ML-DSA / FIPS 204):**

```python
from charm.toolbox.latticegroup import LatticeGroup
from charm.schemes.latenc.dilithium_sig import DilithiumSig

# ML-DSA-44 parameters (n=256, q=8380417, k=4, l=4)
group = LatticeGroup('DILITHIUM-2')
signer = DilithiumSig(group, 'DILITHIUM-2')

(pk, sk) = signer.keygen()
signature = signer.sign(sk, b"Quantum-resistant signature")
assert signer.verify(pk, b"Quantum-resistant signature", signature)
assert not signer.verify(pk, b"Tampered message", signature)
```

**Working with ring elements directly:**

```python
from charm.toolbox.latticegroup import LatticeGroup, POLY, ZQ, VEC

group = LatticeGroup('RLWE-256-7681')

# Polynomial arithmetic in R_q = Z_7681[X]/(X^256 + 1)
a = group.random(POLY)
b = group.random(POLY)
c = a * b          # polynomial multiplication mod X^n+1
d = a + b          # polynomial addition
e = a * 3          # scalar multiplication

# Discrete Gaussian sampling (for LWE-based schemes)
noise = group.gaussian(sigma=3.0)

# Vectors and matrices (for Module-LWE schemes like Kyber)
v = group.random_vec(3)           # vector of 3 random polynomials
A = group.random_mat(3, 3)       # 3x3 matrix of random polynomials
result = A * v                    # matrix-vector product
inner = v * group.random_vec(3)   # inner product -> polynomial

# Deterministic hashing and serialization
h = group.hash(b"input data", POLY)
data = group.serialize(a)
a_restored = group.deserialize(data)
assert a == a_restored
```

> **Note:** These are simplified implementations for prototyping and education.
> They implement the core algebraic structure of ML-KEM and ML-DSA but omit
> some hardening steps (e.g., Fujisaki-Okamoto transform for IND-CCA,
> constant-time operations). See the NIST standards
> ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final),
> [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final)) for production requirements.

## Schemes

Charm includes implementations of many cryptographic schemes:

| Category | Examples |
|----------|----------|
| **ABE** | CP-ABE (BSW07), KP-ABE, FAME |
| **IBE** | Waters05, BB04 |
| **Signatures** | BLS, Waters, CL04, ECDSA, Schnorr |
| **Threshold Signatures** | GG18, CGGMP21, DKLS23 (threshold ECDSA) |
| **Commitments** | Pedersen, Feldman VSS |
| **Lattice (PQ)** | RLWE-PKE, Kyber KEM, Dilithium Sig, Lattice IBE |
| **Group Signatures** | BBS+, PS16 |

See the [schemes directory](charm/schemes/) for all available implementations.

## Contributing

We welcome contributions\! Please note:

* All schemes must include doctests for inclusion in `make test`
* Follow the existing code style
* Add tests for new functionality
* Update documentation as needed

## Security

Charm uses the BN254 curve which provides approximately **128-bit security**. For production use:

* Keep dependencies updated
* Use the production-ready ZKP compiler (not the legacy `exec()`-based version)
* Review scheme implementations for your specific security requirements

## Support

* **Issues**: [GitHub Issues](https://github.com/JHUISI/charm/issues)
* **Email**: jakinye3@jhu.edu

## License

Charm is released under the **LGPL version 3** license. See [LICENSE.txt](LICENSE.txt) for details.

## Citation

If you use Charm in academic work, please cite:

```bibtex
@article{charm,
  author = {Akinyele, Joseph A. and Garman, Christina and Miers, Ian and Pagano, Matthew W. and Rushanan, Michael and Green, Matthew and Rubin, Aviel D.},
  title = {Charm: A Framework for Rapidly Prototyping Cryptosystems},
  journal = {Journal of Cryptographic Engineering},
  year = {2013}
}
```
