# Changelog

All notable changes to Charm-Crypto will be documented in this file.

## [0.63] - 2026-04-19

### Added
- **Lattice-based (post-quantum) cryptography module**
  - C++ extension (`charm.core.math.lattice`) backed by NTL library
    - Polynomial ring arithmetic in R_q = Z_q[X]/(X^n+1)
    - CDT-based discrete Gaussian sampling
    - Vector/matrix operations for Module-LWE schemes
    - Compress/decompress, CBD sampling, matrix transpose
    - SHA-256 deterministic hashing to ring elements
    - Full serialization/deserialization
  - Python wrapper (`charm.toolbox.latticegroup.LatticeGroup`)
    - API consistent with `PairingGroup` / `ECGroup` / `IntegerGroup`
    - Named parameter sets: `RLWE-256-7681`, `RLWE-512-12289`, `KYBER-512/768/1024`, `DILITHIUM-2/3/5`
    - Custom parameters via `LatticeGroup(n=512, q=12289)`
  - `LatticeKEM` and `LatticeSig` abstract base classes
  - Four lattice-based schemes:
    - **RLWE-PKE** (`rlwe_pke.py`): Ring-LWE public key encryption (LPR)
    - **Kyber KEM** (`kyber_kem.py`): Simplified ML-KEM (FIPS 203) key encapsulation
    - **Dilithium Sig** (`dilithium_sig.py`): Simplified ML-DSA (FIPS 204) digital signatures
    - **Lattice IBE** (`lattice_ibe_abb10.py`): Simplified ABB10 identity-based encryption
  - 44 new tests for lattice module and schemes
  - Opt-in build via `LAT_MOD=yes` (requires NTL library)
- NTL library detection in build system (pkg-config, Homebrew, standard paths)
- `--enable-lattice` flag in `configure.sh`
- NTL install and lattice module build in all CI jobs

### Fixed
- **Python 3.13+ compatibility**: Fixed enum name-mangling crash where `EnumValue.__value` was mangled to `_EnumValue__value` in nested classes
- **Python 3.13+ pairing config**: Fixed `param_info` being `None` when `config.py` is unconfigured, now raises clear `ImportError` with build instructions
- **Python 3.12 segfault**: Fixed crash during interpreter shutdown in C extensions
- **Benchmark timing units** (#309): Renamed `cpu_time_ms`/`real_time_ms` to `cpu_time_secs`/`real_time_secs` (both were already in seconds); fixed `Benchmark_print` CPU label from `ms` to `s`
- **Kyber-512 decapsulation**: Fixed noise parameter — use `sqrt(eta/2)` as Gaussian sigma to match CBD variance
- **config.dist.py**: Restored trailing spaces required by `setup.py` string replacement

### Changed
- Removed obsolete `.travis.yml`
- Updated Dockerfile maintainer

### Security
- Fixed 13 vulnerabilities identified in security audit
- Disabled unsafe pickle deserialization by default in protocol module

## [0.62] - 2026-03-15

### Added
- ZKP compiler with Schnorr, DLEQ, AND/OR composition, range proofs, batch verification
- BLS signatures and Schnorr signatures with NIST test vectors
- Threshold sharing (Feldman VSS, Pedersen VSS)
- Hypothesis-based property tests for ABE schemes
- Cross-platform install script (`install_charm.sh`)

### Fixed
- Policy parser robustness improvements
- Cross-platform compatibility in install script

### Security
- Weak curve deprecation warnings (SS512, MNT159, MNT201)
