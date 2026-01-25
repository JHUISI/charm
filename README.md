Charm-Crypto
============

| Branch      | Status                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| `dev`       | ![Build Status](https://github.com/JHUISI/charm/actions/workflows/ci.yml/badge.svg?branch=dev) |

Charm is a framework for rapidly prototyping advanced cryptosystems. Based on the Python language, it was designed from the ground up to minimize development time and code complexity while promoting the reuse of components.

Charm uses a hybrid design: performance-intensive mathematical operations are implemented in native C modules, while cryptosystems themselves are written in a readable, high-level language. Charm additionally provides a number of new components to facilitate the rapid development of new schemes and protocols.

## Features

* **Mathematical Settings**: Integer rings/fields, bilinear (BN254) and non-bilinear Elliptic Curve groups
* **Base Crypto Library**: Symmetric encryption, hash functions, PRNGs
* **Standard APIs**: Digital signatures, encryption, commitments
* **Protocol Engine**: Simplifies multi-party protocol implementation
* **ZKP Compiler**: Production-ready compiler for interactive and non-interactive zero-knowledge proofs
  - Discrete Log Equality (DLEQ) proofs
  - Knowledge of Representation proofs
  - AND/OR composition
  - Range proofs
  - Batch verification
* **C/C++ Embed API**: Native applications can embed Charm via the Python C API
* **Integrated Benchmarking**: Built-in performance measurement

## Installation

### Quick Install (pip)

Once published to PyPI:

```bash
pip install charm-crypto
```

> **Note:** System libraries (GMP, PBC, OpenSSL) must be installed first. See [Prerequisites](#prerequisites) below.

### Prerequisites

Charm requires the following system libraries:

| Library | Version | Purpose |
|---------|---------|---------|
| [GMP](http://gmplib.org/) | 5.0+ | Arbitrary precision arithmetic |
| [PBC](http://crypto.stanford.edu/pbc/download.html) | 1.0.0 | Pairing-based cryptography |
| [OpenSSL](http://www.openssl.org/source/) | 3.0+ | Cryptographic primitives |

**Ubuntu/Debian:**
```bash
sudo apt-get install libgmp-dev libssl-dev libpbc-dev flex bison
```

**macOS (Homebrew):**
```bash
brew install gmp openssl@3 pbc
```

**PBC from Source** (if not available via package manager):
```bash
wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz
tar xzf pbc-1.0.0.tar.gz
cd pbc-1.0.0
./configure && make && sudo make install
```

### From Source (Development)

```bash
git clone https://github.com/JHUISI/charm.git
cd charm
./configure.sh  # add --enable-darwin on macOS
pip install -e ".[dev]"
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

# Threshold ECDSA (DKLS23) tests
pytest charm/test/schemes/threshold_test.py -v

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

### Threshold ECDSA (DKLS23) with XRPL testnet

Charm also includes a threshold ECDSA scheme based on DKLS23, together with an XRPL
testnet demo that shows how to use it end to end.

```python
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.ecgroup import ECGroup
from charm.core.math.elliptic_curve import G
from charm.schemes.threshold.dkls23_sign import DKLS23
from charm.schemes.threshold.xrpl_wallet import (
    XRPLThresholdWallet,
    XRPLClient,
    sign_xrpl_transaction,
    create_payment_with_memo,
    get_secp256k1_generator,
)

group = ECGroup(secp256k1)
dkls = DKLS23(group, threshold=2, num_parties=3)
g = get_secp256k1_generator(group)
key_shares, public_key = dkls.distributed_keygen(g)
wallet = XRPLThresholdWallet(group, public_key)
client = XRPLClient(is_testnet=True)
```

See `examples/xrpl_memo_demo.py` for a complete XRPL testnet flow (fund account, create
threshold wallet, send payment with memo).

## Schemes

Charm includes implementations of many cryptographic schemes:

| Category | Examples |
|----------|----------|
| **ABE** | CP-ABE (BSW07), KP-ABE, FAME |
| **IBE** | Waters05, BB04 |
| **Signatures** | BLS, Waters, CL04 |
| **Commitments** | Pedersen |
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
