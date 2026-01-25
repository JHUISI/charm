# v0.60: Production-Ready Python 3.8+/OpenSSL 3.x with Security Hardening

## Summary

This PR brings Charm-Crypto to production readiness for modern Python (3.8-3.12) and OpenSSL 3.x environments, with comprehensive security hardening and a complete ZKP compiler overhaul.

## Major Changes

### 🔒 Security Hardening
- Fixed timing-unsafe HMAC comparison (CVE-level)
- Fixed command injection vulnerability in FSA.py
- Fixed file handle leaks
- Replaced all `sprintf` with `snprintf` in C extensions
- Added NULL checks after all malloc calls
- Added bandit security scanning to CI

### 🐍 Python 3.8+ Compatibility
- Fixed PY_SSIZE_T_CLEAN issues causing segfaults
- Removed Python 2.x dead code
- Fixed deprecated `platform.linux_distribution()`
- Fixed deprecated `PyUnicode_GET_SIZE`

### 🔐 OpenSSL 3.x Compatibility
- Migrated all C modules from deprecated SHA256_Init/Update/Final to EVP API
- Removed all deprecated low-level OpenSSL APIs

### 🧮 ZKP Compiler Overhaul
- **Removed insecure `exec()` usage** - replaced with secure class-based API
- New proof types: Schnorr, DLEQ, Representation, Range, AND/OR composition
- Batch verification support
- Thread-safe implementation
- Migrated default curve from SS512 (80-bit) to BN254 (128-bit security)
- Legacy API deprecated with clear migration path

### 🧪 Testing Infrastructure
- **441 tests** (up from ~100)
- Cryptographic test vectors for BLS, Schnorr, Pedersen
- AddressSanitizer (ASan) CI job
- Valgrind memory checking CI job
- Atheris fuzzing infrastructure
- Bandit security scanning

### 📚 Documentation
- Updated INSTALL for modern Ubuntu/macOS
- Updated README with pip installation instructions
- Complete ZKP compiler API documentation
- Migration guides for deprecated APIs

### 🔧 Build System
- GitHub Actions CI/CD pipeline
- Multi-platform support (Linux, macOS, experimental Windows)
- PBC 1.0.0 (updated from 0.5.14)

## Test Results

```
441 tests collected
434 passed, 7 skipped, 1 warning
```

## Breaking Changes
- Minimum Python version: 3.8 (was 2.7/3.x)
- Minimum OpenSSL version: 3.x (was 1.x)
- Legacy ZKP API deprecated (will be removed in v0.80)

---

**Ready for review and merge.**

