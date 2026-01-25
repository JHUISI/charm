Charm-Crypto
============

| Branch      | Status                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| `dev`       | \![Build Status](https://github.com/JHUISI/charm/actions/workflows/ci.yml/badge.svg?branch=dev) |

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
```

## Documentation

* [Installation Guide](https://jhuisi.github.io/charm/install_source.html)
* [Scheme Examples](https://jhuisi.github.io/charm/schemes.html)
* [API Reference](https://jhuisi.github.io/charm/)
* [C/C++ Embed API](embed/README.md)

## Quick Example

BLS signatures (Boneh-Lynn-Shacham) — a pairing-based signature scheme standardized in
[IETF RFC 9380](https://datatracker.ietf.org/doc/rfc9380/) and used in Ethereum 2.0:

```python
from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.pksig.pksig_bls04 import BLS01

# Initialize pairing group (BN254 curve, ~128-bit security)
group = PairingGroup('BN254')
bls = BLS01(group)

# Key generation
(pk, sk) = bls.keygen()

# Sign a message
message = {'msg': 'hello world'}
signature = bls.sign(sk['x'], message)

# Verify signature
assert bls.verify(pk, signature, message)
print("BLS signature verified!")
```

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
@inproceedings{charm,
  author = {Akinyele, Joseph A. and others},
  title = {Charm: A Framework for Rapidly Prototyping Cryptosystems},
  booktitle = {Journal of Cryptographic Engineering},
  year = {2013}
}
```
