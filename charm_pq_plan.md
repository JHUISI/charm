# Lattice-Based Crypto Abstraction for Charm — Development Plan

## Overview

Add a fourth group abstraction layer to Charm for lattice-based cryptography, backed by the NTL C++ library. Follows the existing 3-layer pattern:

```
C++ Extension (NTL)  →  Python Wrapper  →  Scheme Implementations
latticemodule.cpp       latticegroup.py     rlwe_pke.py, kyber_kem.py, ...
```

### Element Types

| Type | NTL Backing | Purpose |
|------|-------------|---------|
| `ZQ` | `ZZ_p` | Scalar in ℤ_q |
| `POLY` | `ZZ_pX` mod (Xⁿ+1) | Polynomial in R_q |
| `VEC` | `Vec<ZZ_pX>` | Vector of polynomials (MLWE) |
| `MAT` | custom `Vec<ZZ_pX>` + dims | Matrix of polynomials (public keys) |

### Success Criteria
- NTL-backed C++ Python extension with polynomial ring arithmetic in R_q = Z_q[X]/(X^n + 1)
- Pythonic `LatticeGroup` wrapper consistent with `PairingGroup`/`ECGroup`/`IntegerGroup` APIs
- Discrete Gaussian sampling, RLWE/MLWE primitives
- At least one working scheme (basic RLWE encryption) with tests
- Stretch: Kyber (ML-KEM) and Dilithium (ML-DSA) implementations

### Scope Boundaries
- **In scope:** Core polynomial ring types, vector/matrix types, Gaussian sampling, RLWE/MLWE, Kyber, Dilithium, lattice-based IBE
- **Out of scope:** FHE schemes, NTRU, non-ring lattice schemes, constant-time hardening (noted as future work)

---

## Prerequisites

- **NTL 11.6.0+** installed with shared library (`libntl.so` / `libntl.dylib`)
- **GMP** (already a Charm dependency; NTL compiled with `NTL_GMP_LIP=on`)
- **C++14 or later** compiler (g++ or clang++)
- Python 3.8+ with development headers (existing requirement)

---

## Phase 0: Infrastructure — NTL Detection & Build System

**Dependencies:** None
**Complexity:** M (Medium) · **Effort:** 1-2 days

### Tasks

| Task | File | Details |
|------|------|---------|
| Add `--enable-lattice` flag | `configure.sh` | NTL header/lib detection, C++ compiler check |
| Add lattice `Extension()` | `setup.py` | Link `-lntl -lgmp -lpthread`, `language='c++'`, `-std=c++14` |
| Add `ntl` to libs enum | `charm/config.py`, `config.dist.py` | `lattice_lib` variable |
| Add `LAT_MOD` default | `setup.py` | `'LAT_MOD': 'no'` in `get_default_config()` |

Module is **opt-in** (`--enable-lattice`) — existing builds unaffected.

### Testing
- `./configure.sh --enable-lattice` produces correct `config.mk`
- `python setup.py build` finds NTL headers/libs

---

## Phase 1: C++ Extension Module — Core Types & Arithmetic

**Dependencies:** Phase 0
**Complexity:** L (Large) · **Effort:** 2-3 weeks

### Files

| File | Description |
|------|-------------|
| `charm/core/math/lattice/latticemodule.h` | Type definitions: `LatticeContext`, `LatticeElement`, `NTLContextGuard` |
| `charm/core/math/lattice/latticemodule.cpp` | ~1500-2000 lines: types, arithmetic, module functions |
| `charm/core/math/lattice.pyi` | Type stubs for IDE support |

### LatticeContext Struct
- `n` (ring dimension, power of 2)
- `q` (modulus as `NTL::ZZ`)
- `modulus` (cyclotomic X^n+1 as `NTL::ZZ_pX`)
- `group_init` flag

### LatticeElement Struct
- `ctx` pointer, `elem_type` (ZQ/POLY/VEC/MAT)
- Union of `NTL::ZZ_p*`, `NTL::ZZ_pX*`, `NTL::vec_ZZ_pX*`
- Custom matrix wrapper for MAT (NTL lacks `mat_ZZ_pX`)

### NTL Thread-Local Context Guard

NTL uses thread-local global modulus (`ZZ_p::init(q)`). Each operation needs:

```cpp
class NTLContextGuard {
    ZZ_pContext saved;
public:
    NTLContextGuard(const LatticeContext *ctx) { saved.save(); ZZ_p::init(ctx->q); }
    ~NTLContextGuard() { saved.restore(); }
};
```

### Arithmetic Operators (`tp_as_number`)

| Slot | POLY | VEC | MAT | ZQ |
|------|------|-----|-----|-----|
| `nb_add` | poly+poly mod(X^n+1,q) | componentwise | componentwise | ZZ_p add |
| `nb_subtract` | poly-poly | componentwise | componentwise | ZZ_p sub |
| `nb_multiply` | poly*poly mod(X^n+1) | scalar*vec / inner product | mat*vec, mat*mat | ZZ_p mul |
| `nb_negative` | -poly | -vec | -mat | -zq |

Cross-type: `POLY*ZQ` → scalar mul, `MAT*VEC` → mat-vec product, `VEC*POLY` → componentwise.

### Module Functions

| Function | Description |
|----------|-------------|
| `init(ctx, type, value=None)` | Create element of given type |
| `random(ctx, type)` | Uniform random element |
| `hash(ctx, data, type)` | Hash bytes → element |
| `serialize(ctx, elem)` / `deserialize(ctx, data)` | Element ↔ bytes |
| `ismember(ctx, elem)` | Membership test |
| `order(ctx)` / `degree(ctx)` | Returns q / n |
| `ntt(ctx, elem)` / `intt(ctx, elem)` | Forward/inverse NTT (via NTL FFT) |
| `lll(basis)` | LLL lattice reduction |

Exports constants: `ZQ=0, POLY=1, VEC=2, MAT=3`

### Testing
- Element creation and arithmetic for each type (ZQ, POLY, VEC, MAT)
- Polynomial correctness: `(X+1) * (X-1) = X² - 1` mod X^n+1
- Serialization roundtrip
- NTL context isolation (two LatticeContexts don't interfere)


---

## Phase 2: Python LatticeGroup Wrapper

**Dependencies:** Phase 1
**Complexity:** M (Medium) · **Effort:** 3-5 days

### Files

| File | Description |
|------|-------------|
| `charm/toolbox/latticegroup.py` | Main wrapper class matching existing group API |
| `charm/toolbox/LatticeKEM.py` | Base class: `keygen()`, `encapsulate(pk)`, `decapsulate(sk, ct)` |
| `charm/toolbox/LatticeSig.py` | Base class: `keygen()`, `sign(sk, msg)`, `verify(pk, msg, sig)` |

### LatticeGroup API

- `__init__(param_id)` — named parameter sets or custom `(n, q)` kwargs
- `order()`, `degree()`, `random(type, count)`, `gaussian(type, sigma, count)`
- `init(type, value)`, `hash(data, type)`, `encode(msg)`, `decode(elem)`
- `serialize(obj)`, `deserialize(data)`, `ismember(obj)`
- `ntt(elem)`, `intt(elem)`, `lll_reduce(basis)`
- `groupSetting() → 'lattice'`, `groupType() → param_id`
- Benchmark hooks: `InitBenchmark`, `StartBenchmark`, `EndBenchmark`

### Named Parameter Sets

| Name | n | q | Use Case |
|------|---|---|----------|
| `RLWE-256-7681` | 256 | 7681 | Basic RLWE |
| `RLWE-512-12289` | 512 | 12289 | Basic RLWE |
| `RLWE-1024-12289` | 1024 | 12289 | Basic RLWE |
| `KYBER-512` | 256 | 3329 | ML-KEM (k=2) |
| `KYBER-768` | 256 | 3329 | ML-KEM (k=3) |
| `KYBER-1024` | 256 | 3329 | ML-KEM (k=4) |
| `DILITHIUM-2` | 256 | 8380417 | ML-DSA (k=4, l=4) |
| `DILITHIUM-3` | 256 | 8380417 | ML-DSA (k=6, l=5) |
| `DILITHIUM-5` | 256 | 8380417 | ML-DSA (k=8, l=7) |

### Testing
- Construction with named params and custom params
- Arithmetic through wrapper: `a + b`, `a * b`
- Serialize/deserialize roundtrip
- Error handling (bad parameters, wrong types)

---

## Phase 3: Gaussian Sampling + RLWE Primitives

**Dependencies:** Phases 1-2
**Complexity:** M (Medium) · **Effort:** 1-2 weeks

### Additions to `latticemodule.cpp`

| Function | Description |
|----------|-------------|
| `gaussian_sample(ctx, type, sigma)` | Discrete Gaussian sampler |
| `rlwe_keygen(ctx)` | a ← uniform, s,e ← Gaussian, b = a·s + e |
| `rlwe_encrypt(ctx, pk, m)` | r,e₁,e₂ ← Gaussian, c₁ = a·r+e₁, c₂ = b·r+e₂+⌊q/2⌋·m |
| `rlwe_decrypt(ctx, sk, ct)` | Threshold each coefficient of c₂ - c₁·s |
| `vec_random(ctx, k)` | Random vector of k polynomials |
| `vec_gaussian(ctx, k, sigma)` | Gaussian vector |
| `vec_inner_product(a, b)` | Inner product of polynomial vectors |
| `mat_vec_mul(A, v)` | Matrix-vector multiply |

### Gaussian Sampling Strategy
- **CDT (Cumulative Distribution Table)** for small σ ≤ 10
- **Rejection sampling** for larger σ
- Sample each polynomial coefficient independently from D_{Z,σ}

### Testing
- Statistical tests: mean ≈ 0, stddev ≈ σ, chi-squared
- RLWE roundtrip: `decrypt(encrypt(m)) == m`

---

## Phase 4: First Scheme — Basic RLWE Encryption

**Dependencies:** Phase 3
**Complexity:** S (Small) · **Effort:** 3-5 days

### Files

| File | Description |
|------|-------------|
| `charm/schemes/latenc/__init__.py` | Package init |
| `charm/schemes/latenc/rlwe_pke.py` | LPR encryption, extends `PKEnc` |

### Scheme (LPR Encryption)

```
KeyGen: a ← uniform, s,e ← Gaussian(σ), pk = (a, b = a·s + e), sk = s
Encrypt(pk, m): r,e₁,e₂ ← Gaussian(σ), c₁ = a·r + e₁, c₂ = b·r + e₂ + ⌊q/2⌋·m
Decrypt(sk, ct): m' = c₂ - c₁·s, threshold each coefficient around q/2
```

### Testing
- Encrypt/decrypt roundtrip with random messages
- Multiple parameter sets
- Edge cases: all-zero, all-one messages
- Decryption failure rate measurement (should be negligible)

---

## Phase 5: Advanced Schemes — Kyber & Dilithium

**Dependencies:** Phase 4
**Complexity:** L (Large) · **Effort:** 3-4 weeks

### Step 5.1: Kyber (ML-KEM) — `charm/schemes/latenc/kyber_kem.py`

MLWE-based KEM following FIPS 203.

**New C++ functions:**
- `cbd_sample(ctx, eta)` — Centered Binomial Distribution sampling
- `compress(elem, d)` / `decompress(elem, d)` — lossy compression
- `xof_sample_matrix(ctx, seed, k)` — XOF-based matrix generation

### Step 5.2: Dilithium (ML-DSA) — `charm/schemes/latenc/dilithium_sig.py`

MLWE-based signatures following FIPS 204.

**New C++ functions:**
- `power2round(r, d)`, `highbits(r, alpha)`, `lowbits(r, alpha)`
- `make_hint(z, r, alpha)`, `use_hint(h, r, alpha)`
- `sample_in_ball(seed, tau)` — sparse polynomial sampling
- `check_norm(v, bound)` — infinity norm check

### Step 5.3: Lattice IBE (ABB10) — `charm/schemes/latenc/lattice_ibe_abb10.py`

Lattice-based Identity-Based Encryption using trapdoor sampling.

### Testing
- NIST FIPS 203 (ML-KEM) test vectors, all security levels
- NIST FIPS 204 (ML-DSA) test vectors, all security levels
- Key/ciphertext/signature serialization roundtrips

---

## Phase 6: Testing, Benchmarks, Documentation

**Dependencies:** Phases 0-5
**Complexity:** M (Medium) · **Effort:** 1-2 weeks

### Test Files

| File | Coverage |
|------|----------|
| `charm/test/toolbox/latticegroup_test.py` | Group API, arithmetic, serialization |
| `charm/test/schemes/latenc/__init__.py` | Package init |
| `charm/test/schemes/latenc/rlwe_pke_test.py` | RLWE encrypt/decrypt roundtrip |
| `charm/test/schemes/latenc/kyber_test.py` | FIPS 203 test vectors |
| `charm/test/schemes/latenc/dilithium_test.py` | FIPS 204 test vectors |
| `charm/test/benchmark/lattice_bench.py` | Performance benchmarks |

Integrate with existing benchmark framework (`InitBenchmark`/`StartBenchmark`/`EndBenchmark`).

---

## File Changes Summary

### New Files (17)

| File | Phase |
|------|-------|
| `charm/core/math/lattice/latticemodule.h` | 1 |
| `charm/core/math/lattice/latticemodule.cpp` | 1, 3, 5 |
| `charm/core/math/lattice.pyi` | 1 |
| `charm/toolbox/latticegroup.py` | 2 |
| `charm/toolbox/LatticeKEM.py` | 2 |
| `charm/toolbox/LatticeSig.py` | 2 |
| `charm/schemes/latenc/__init__.py` | 4 |
| `charm/schemes/latenc/rlwe_pke.py` | 4 |
| `charm/schemes/latenc/kyber_kem.py` | 5 |
| `charm/schemes/latenc/dilithium_sig.py` | 5 |
| `charm/schemes/latenc/lattice_ibe_abb10.py` | 5 |
| `charm/test/toolbox/latticegroup_test.py` | 6 |
| `charm/test/schemes/latenc/__init__.py` | 6 |
| `charm/test/schemes/latenc/rlwe_pke_test.py` | 6 |
| `charm/test/schemes/latenc/kyber_test.py` | 6 |
| `charm/test/schemes/latenc/dilithium_test.py` | 6 |
| `charm/test/benchmark/lattice_bench.py` | 6 |

### Modified Files (4)

| File | Phase | Changes |
|------|-------|---------|
| `configure.sh` | 0 | `--enable-lattice`, NTL detection, CXX detection |
| `setup.py` | 0 | Lattice `Extension()`, packages list |
| `charm/config.py` | 0 | `ntl` in libs enum, `lattice_lib` |
| `config.dist.py` | 0 | `lattice_lib` placeholder |

---

## Timeline

| Phase | Effort | Cumulative |
|-------|--------|------------|
| Phase 0: Build system | 1-2 days | 2 days |
| Phase 1: C++ extension | 2-3 weeks | 3.5 weeks |
| Phase 2: Python wrapper | 3-5 days | 4.5 weeks |
| Phase 3: Gaussian/RLWE | 1-2 weeks | 6.5 weeks |
| Phase 4: First scheme | 3-5 days | 7.5 weeks |
| Phase 5: Kyber/Dilithium | 3-4 weeks | 11 weeks |
| Phase 6: Testing | 1-2 weeks | **~13 weeks** |

---

## Risk Factors

1. **NTL thread-local state** — global modulus context requires careful save/restore via `ZZ_pContext`
2. **C++ ↔ Python memory management** — NTL objects must be properly freed in `tp_dealloc`
3. **NTL lacks `mat_ZZ_pX`** — needs custom matrix type wrapper
4. **Not constant-time** — NTL operations are variable-time; document as security limitation
5. **NIST conformance** — Kyber/Dilithium have exact byte encodings that must match FIPS 203/204

## Rollback Plan

- Module is opt-in via `--enable-lattice` / `LAT_MOD=yes`
- All new files; delete to revert
- No existing code modified beyond Phase 0 build system changes
- No data migrations or persistent state