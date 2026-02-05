# charm-crypto-lite Package Exploration

## Overview

This document explores creating a minimal `charm-crypto-lite` PyPI package that provides only OpenSSL-based elliptic curve operations without GMP or PBC dependencies.

## Key Findings

### 1. EC Module Does NOT Require GMP

**Critical Discovery:** The EC module (`ecmodule.c`) does not use GMP at all. It exclusively uses OpenSSL's BIGNUM API.

- Searched `ecmodule.c` and `ecmodule.h` for `gmp|GMP|mpz_` - **zero matches**
- The `libraries=['gmp', 'crypto']` in setup.py line 351 is unnecessary
- For charm-crypto-lite, we only need: `libraries=['crypto']`

### 2. Dependency Analysis

| Component | External Dependencies | Notes |
|-----------|----------------------|-------|
| `ecmodule.c` | OpenSSL only (libcrypto) | Uses EC_GROUP, EC_POINT, BIGNUM, BN_CTX |
| `ecmodule.h` | OpenSSL headers | `<openssl/ec.h>`, `<openssl/bn.h>`, `<openssl/sha.h>`, `<openssl/evp.h>` |
| `base64.c` | None | Pure C with standard library |
| `benchmarkmodule.c` | None | Pure C with standard library |
| `ecgroup.py` | EC C extension only | No pyparsing, no other charm modules |
| `eccurve.py` | None | Pure Python curve NID constants |

### 3. Python Dependencies

**pyparsing is NOT needed** for charm-crypto-lite:
- pyparsing is only used for policy parsing in ABE/IBE schemes
- ECGroup has no policy parsing functionality
- The lite package has **zero Python dependencies**

---

## Answers to Questions

### Q1: Package Structure for `pyproject.toml` and `setup.py`

**Recommended structure:**

```
charm-crypto-lite/
├── pyproject.toml          # Modern build config
├── setup.py                # C extension compilation
├── VERSION                 # Version file
├── README.md               # Package documentation
├── charm_lite/             # New namespace to avoid conflicts
│   ├── __init__.py         # Import benchmark to preload symbols
│   ├── core/
│   │   ├── __init__.py
│   │   ├── math/
│   │   │   ├── __init__.py
│   │   │   └── elliptic_curve/   # C extension builds here
│   │   ├── utilities/
│   │   │   ├── base64.c
│   │   │   └── base64.h
│   │   └── benchmark/
│   │       ├── benchmarkmodule.c
│   │       └── benchmarkmodule.h
│   └── toolbox/
│       ├── __init__.py
│       ├── ecgroup.py      # ECGroup class
│       └── eccurve.py      # Curve NID constants
```

### Q2: Build System Modifications

**Option A: Separate setup.py (Recommended)**

Create a standalone `setup_lite.py`:

```python
from setuptools import setup, Extension

ecc_module = Extension(
    'charm_lite.core.math.elliptic_curve',
    include_dirs=['charm_lite/core/utilities', 'charm_lite/core/benchmark'],
    sources=[
        'charm_lite/core/math/elliptic_curve/ecmodule.c',
        'charm_lite/core/utilities/base64.c'
    ],
    libraries=['crypto'],  # Only OpenSSL, NO GMP
    define_macros=[('BENCHMARK_ENABLED', '1')]
)

benchmark_module = Extension(
    'charm_lite.core.benchmark',
    sources=['charm_lite/core/benchmark/benchmarkmodule.c']
)

setup(
    name='charm-crypto-lite',
    ext_modules=[ecc_module, benchmark_module],
    # ... rest of config
)
```

**Option B: Build variant in main repo**

Add a `--lite` flag to `configure.sh` that generates a minimal `config.mk` with only ECC_MOD enabled and modified library flags.

### Q3: Separate Repository vs Build Variant

**Recommendation: Build variant in main repo**

| Approach | Pros | Cons |
|----------|------|------|
| **Build variant** | Single source of truth, easier maintenance, shared bug fixes | More complex build system |
| **Separate repo** | Cleaner separation, simpler build | Code duplication, sync issues |

**Suggested implementation:**
1. Create a `lite/` subdirectory in the main charm repo
2. Use symbolic links or a build script to assemble the lite package
3. Publish to PyPI as a separate package from the same source

### Q4: Minimal Python Dependencies

**Answer: NONE**

The charm-crypto-lite package requires **zero Python dependencies**:
- No pyparsing (only used for policy parsing in ABE/IBE)
- No other third-party packages
- Only requires OpenSSL development libraries at build time

### Q5: API Compatibility with Full Charm

**Strategy: Use compatible import paths**

```python
# Option 1: Same namespace (may conflict if both installed)
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import secp256k1

# Option 2: Separate namespace with compatibility shim
from charm_lite.toolbox.ecgroup import ECGroup
from charm_lite.toolbox.eccurve import secp256k1

# For users who might upgrade, provide a compatibility layer:
try:
    from charm.toolbox.ecgroup import ECGroup
except ImportError:
    from charm_lite.toolbox.ecgroup import ECGroup
```

**Recommendation:** Use `charm_lite` namespace to:
1. Avoid conflicts if both packages are installed
2. Make migration path clear
3. Allow side-by-side installation for testing

---

## Implementation Checklist

- [ ] Create `lite/` directory structure
- [ ] Copy/symlink required source files
- [ ] Create `setup_lite.py` with EC-only build
- [ ] Create `pyproject_lite.toml` with zero dependencies
- [ ] Modify imports in `ecgroup.py` for new namespace
- [ ] Create compatibility shim (optional)
- [ ] Add tests for lite package
- [ ] Document installation and usage
- [ ] Set up separate PyPI publishing workflow

## Next Steps

1. Create prototype `pyproject.toml` for charm-crypto-lite
2. Test building EC module without GMP linkage
3. Verify all EC operations work correctly
4. Create minimal test suite

