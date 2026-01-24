# ZKP Proof Types Design Document

## Overview

This document describes the design and implementation plan for zero-knowledge proof (ZKP) types in the Charm-Crypto library. It covers both the existing Schnorr protocol and planned future proof types.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Existing Proof Type: Schnorr Protocol](#existing-proof-type-schnorr-protocol)
3. [New Proof Type: Discrete Log Equality (DLEQ)](#new-proof-type-discrete-log-equality-dleq)
4. [New Proof Type: Knowledge of Representation](#new-proof-type-knowledge-of-representation)
5. [New Proof Type: Range Proofs](#new-proof-type-range-proofs)
6. [Proof Composition Techniques](#proof-composition-techniques)
7. [Migration Guide](#migration-guide)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Architecture Overview

### Base Classes

All ZKP implementations inherit from `ZKProofBase` (defined in `charm/toolbox/ZKProof.py`):

```python
from charm.toolbox.ZKProof import ZKProofBase, zkpSecDefs

class MyZKProof(ZKProofBase):
    def __init__(self):
        ZKProofBase.__init__(self)
        self.setProperty(secDef='NIZK', assumption='DL', secModel='ROM')
    
    def setup(self, group): ...
    def prove(self, statement, witness): ...
    def verify(self, statement, proof): ...
    def serialize(self, proof, group): ...
    def deserialize(self, data, group): ...
```

### Security Definitions

| Definition | Description | Use Case |
|------------|-------------|----------|
| `HVZK` | Honest-Verifier Zero-Knowledge | Interactive protocols with trusted verifier |
| `ZK` | Zero-Knowledge | Secure against malicious verifiers |
| `NIZK` | Non-Interactive Zero-Knowledge | Fiat-Shamir transformed proofs |
| `SIM` | Simulation Sound | Proofs unforgeable even with simulated proofs |

### Module Structure

```
charm/
├── toolbox/
│   └── ZKProof.py              # Base class and exceptions
└── zkp_compiler/
    ├── schnorr_proof.py        # Schnorr DL proof (v0.60)
    ├── dleq_proof.py           # DLEQ/Chaum-Pedersen proof (v0.61)
    ├── representation_proof.py # Knowledge of Representation (v0.61)
    ├── thread_safe.py          # Thread-safe wrappers (v0.61)
    ├── and_proof.py            # AND composition (v0.62)
    ├── or_proof.py             # OR composition/CDS94 (v0.62)
    ├── range_proof.py          # Range proofs (v0.62)
    ├── batch_verify.py         # Batch verification (v0.62)
    ├── zkp_factory.py          # Factory for creating proofs (v0.60)
    ├── zkparser.py             # Statement parser (multi-char vars v0.61)
    ├── zkp_generator.py        # Legacy compiler (deprecated)
    └── zknode.py               # AST node types (existing)
```

---

## Existing Proof Type: Schnorr Protocol

### Description

Schnorr's protocol is a Sigma protocol for proving knowledge of a discrete logarithm:
- **Statement**: "I know x such that h = g^x"
- **Security**: Honest-Verifier Zero-Knowledge (HVZK), or NIZK with Fiat-Shamir

### Protocol (Interactive)

```
Prover(x, g, h)              Verifier(g, h)
--------------               --------------
r ← random ZR
u = g^r
                    u
                ─────────>
                    c
                <─────────    c ← random ZR
z = r + c·x
                    z
                ─────────>
                              Verify: g^z == u · h^c
```

### API Usage

```python
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof
from charm.zkp_compiler.zkp_factory import ZKProofFactory

# Setup
group = PairingGroup('SS512')
g = group.random(G1)  # Generator
x = group.random(ZR)  # Secret
h = g ** x            # Public value

# Non-interactive proof (recommended)
proof = SchnorrProof.prove_non_interactive(group, g, h, x)
is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)

# Using the factory
instance = ZKProofFactory.create_schnorr_proof(group, g, h, x)
proof = instance.prove()
is_valid = instance.verify(proof)

# Interactive proof
prover = SchnorrProof.Prover(x, group)
verifier = SchnorrProof.Verifier(group)

commitment = prover.create_commitment(g)
challenge = verifier.create_challenge()
response = prover.create_response(challenge)
is_valid = verifier.verify(g, h, commitment, response)
```

### Serialization

```python
# Serialize for storage/transmission
data = SchnorrProof.serialize_proof(proof, group)

# Deserialize
recovered = SchnorrProof.deserialize_proof(data, group)
```

---

## New Proof Type: Discrete Log Equality (DLEQ)

### Description

DLEQ (Chaum-Pedersen) proves that two discrete logarithms are equal:
- **Statement**: "I know x such that h₁ = g₁^x AND h₂ = g₂^x"
- **Security**: HVZK/NIZK
- **Use Cases**: VRFs, ElGamal re-encryption proofs, threshold cryptography

### Protocol

```
Prover(x, g₁, h₁, g₂, h₂)         Verifier(g₁, h₁, g₂, h₂)
---

## New Proof Type: Knowledge of Representation

### Description

Proves knowledge of a representation in a given basis:
- **Statement**: "I know (x₁, x₂, ..., xₙ) such that h = g₁^x₁ · g₂^x₂ · ... · gₙ^xₙ"
- **Security**: HVZK/NIZK
- **Use Cases**: Anonymous credentials, Pedersen commitments, multi-attribute proofs

### Protocol

```
Prover(x₁...xₙ, g₁...gₙ, h)       Verifier(g₁...gₙ, h)
---------------------------       ----------------------
r₁...rₙ ← random ZR
u = ∏ᵢ gᵢ^rᵢ
                    u
                ─────────>
                    c
                <─────────        c ← random ZR
zᵢ = rᵢ + c·xᵢ (for all i)
                  z₁...zₙ
                ─────────>
                              Verify: ∏ᵢ gᵢ^zᵢ == u · h^c
```

### Proposed API

```python
class RepresentationProof(ZKProofBase):
    """Proof of knowledge of representation."""

    @classmethod
    def prove_non_interactive(cls, group, generators, h, witnesses):
        """Prove knowledge of witnesses for h = ∏ gᵢ^xᵢ."""
        ...

    @classmethod
    def verify_non_interactive(cls, group, generators, h, proof):
        """Verify a representation proof."""
        ...
```

---

## New Proof Type: Range Proofs

### Description

Proves that a committed value lies within a range:
- **Statement**: "I know x such that C = g^x · h^r AND 0 ≤ x < 2ⁿ"
- **Security**: NIZK
- **Use Cases**: Confidential transactions, age verification, voting

### Approach: Bit Decomposition

For simplicity, we use bit decomposition (O(n) proof size):

1. Commit to each bit: Cᵢ = g^bᵢ · h^rᵢ
2. Prove each Cᵢ commits to 0 or 1 (OR proof)
3. Prove ∑ 2^i · bᵢ = x

### Proposed API

```python
class RangeProof(ZKProofBase):
    """Range proof for committed values."""

    @classmethod
    def prove(cls, group, g, h, commitment, value, randomness, bits=32):
        """Prove value is in range [0, 2^bits)."""
        ...

    @classmethod
    def verify(cls, group, g, h, commitment, proof, bits=32):
        """Verify a range proof."""
        ...
```

---

## Proof Composition Techniques

### AND Composition (Conjunction)

To prove "Statement A AND Statement B":
1. Use the same challenge for both proofs
2. Combine commitments and responses

```python
# Example: Prove knowledge of x AND y
class ANDProof:
    @classmethod
    def prove(cls, group, proofs):
        """Combine multiple proofs with same challenge."""
        # All proofs share a single challenge (Fiat-Shamir over all commitments)
        ...
```

### OR Composition (Disjunction)

To prove "Statement A OR Statement B" (without revealing which):
- Uses the technique from Cramer-Damgård-Schoenmakers (CDS94)
- Simulator creates fake proof for unknown statement

```python
class ORProof:
    @classmethod
    def prove(cls, group, proof_a, proof_b, which_known):
        """Prove one of two statements without revealing which."""
        # Real proof for known, simulated for unknown
        # Challenges must sum to verifier's challenge
        ...
```

---

## Migration Guide

This section provides guidance for migrating from the legacy ZKP compiler API to the new secure proof type classes.

### Why Migrate

The legacy API (`executeIntZKProof()` and `executeNonIntZKProof()`) has **critical security vulnerabilities** that make it unsuitable for production use:

1. **Uses Python's `exec()` and `compile()`**: The legacy implementation dynamically generates and executes Python code at runtime, which:
   - Creates potential code injection vulnerabilities if any input is user-controlled
   - Makes security auditing extremely difficult
   - Prevents static analysis tools from detecting issues

2. **No input validation**: The legacy API lacks proper validation of group elements and proof structure

3. **Not thread-safe**: The legacy implementation uses shared global state that can cause race conditions

4. **Difficult to audit**: Dynamic code generation obscures the actual cryptographic operations

### Legacy vs New API Comparison

| Feature | Legacy API | New Secure API |
|---------|------------|----------------|
| Code execution | Uses `exec()`/`compile()` | Direct method calls |
| Input validation | None | Full group membership checks |
| Thread safety | Not thread-safe | Thread-safe by design |
| Serialization | Custom format | JSON with validation |
| Security auditable | Difficult | Easy to audit |

**Side-by-side example:**

```python
# BEFORE (Legacy - DEPRECATED)
from charm.zkp_compiler.zkp_generator import executeIntZKProof

result = executeIntZKProof(
    "h = g^x",
    {'g': g, 'h': h},
    {'x': x}
)

# AFTER (New Secure API)
from charm.zkp_compiler.schnorr_proof import SchnorrProof

proof = SchnorrProof.prove_non_interactive(group, g, h, x)
valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
```

```python
# BEFORE (Legacy non-interactive - DEPRECATED)
from charm.zkp_compiler.zkp_generator import executeNonIntZKProof

result = executeNonIntZKProof(
    {'g': g, 'h': h},          # public params
    {'x': x},                   # secret params
    "h = g^x",                  # statement
    {'prover': 'prover_id'}     # party info
)

# AFTER (New Secure API)
from charm.zkp_compiler.schnorr_proof import SchnorrProof

proof = SchnorrProof.prove_non_interactive(group, g, h, x)
valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
```

### Step-by-Step Migration

#### Step 1: Update Imports

```python
# BEFORE
from charm.zkp_compiler.zkp_generator import executeIntZKProof, executeNonIntZKProof

# AFTER
from charm.zkp_compiler.schnorr_proof import SchnorrProof
from charm.zkp_compiler.dleq_proof import DLEQProof
from charm.zkp_compiler.representation_proof import RepresentationProof
from charm.zkp_compiler.zkp_factory import ZKProofFactory  # Optional factory API
```

#### Step 2: Replace Proof Generation

```python
# BEFORE
result = executeIntZKProof("h = g^x", {'g': g, 'h': h}, {'x': x})
proof_data = result['proof']

# AFTER
proof = SchnorrProof.prove_non_interactive(group, g, h, x)
# proof is a dict with 'commitment' and 'response' keys
```

#### Step 3: Replace Verification

```python
# BEFORE
# Legacy verification was often bundled with proof generation
is_valid = result['verified']

# AFTER
is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
```

#### Step 4: Update Serialization (if used)

```python
# BEFORE (legacy custom format)
serialized = str(result)

# AFTER (JSON-based serialization)
serialized = SchnorrProof.serialize_proof(proof, group)
recovered = SchnorrProof.deserialize_proof(serialized, group)
```

### Common Migration Patterns

#### Pattern 1: Simple Discrete Log Proof → SchnorrProof

Use when proving knowledge of `x` in `h = g^x`:

```python
# Legacy
result = executeIntZKProof("h = g^x", {'g': g, 'h': h}, {'x': x})

# New
from charm.zkp_compiler.schnorr_proof import SchnorrProof
proof = SchnorrProof.prove_non_interactive(group, g, h, x)
valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
```

#### Pattern 2: Equality Proof → DLEQProof

Use when proving `h1 = g1^x` AND `h2 = g2^x` (same exponent):

```python
# Legacy (required complex statement parsing)
result = executeNonIntZKProof(
    {'g1': g1, 'h1': h1, 'g2': g2, 'h2': h2},
    {'x': x},
    "h1 = g1^x and h2 = g2^x",
    party_info
)

# New
from charm.zkp_compiler.dleq_proof import DLEQProof
proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
valid = DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)
```

#### Pattern 3: Multi-Exponent Proof → RepresentationProof

Use when proving `h = g1^x1 * g2^x2 * ... * gn^xn`:

```python
# Legacy (limited support, required custom parsing)
# Often not possible with legacy API

# New
from charm.zkp_compiler.representation_proof import RepresentationProof
generators = [g1, g2, g3]
witnesses = [x1, x2, x3]
proof = RepresentationProof.prove_non_interactive(group, generators, h, witnesses)
valid = RepresentationProof.verify_non_interactive(group, generators, h, proof)
```

#### Using the Factory for Statement-Based Creation

If you prefer statement-based syntax similar to the legacy API:

```python
from charm.zkp_compiler.zkp_factory import ZKProofFactory

# Create proof instance from statement
instance = ZKProofFactory.create_from_statement(
    group,
    "h = g^x",
    public_params={'g': g, 'h': h},
    secret_params={'x': x}
)
proof = instance.prove()
valid = instance.verify(proof)
```

### Deprecation Timeline

| Version | Status | Action |
|---------|--------|--------|
| **v0.60** | Current | New secure API introduced alongside legacy API |
| **v0.70** | Deprecation | Legacy API emits `DeprecationWarning` on every use |
| **v0.80** | Removal | Legacy API completely removed from codebase |

**Starting in v0.70**, using legacy functions will emit warnings:

```
DeprecationWarning: executeIntZKProof() is deprecated and will be removed in v0.80.
Use SchnorrProof.prove_non_interactive() instead. See migration guide at:
https://github.com/JHUISI/charm/blob/dev/doc/zkp_proof_types_design.md#migration-guide
```

**Recommended action**: Migrate to the new API before v0.80 to ensure continued compatibility.

---

## Implementation Roadmap

### Phase 1 (Current - v0.60) ✅
- [x] Create ZKProofBase class
- [x] Implement Schnorr proof without exec()
- [x] Create ZKProofFactory
- [x] Add deprecation warnings to legacy API
- [x] Comprehensive unit tests (>90% coverage)

### Phase 2 (v0.61) ✅
- [x] Implement DLEQ (Chaum-Pedersen) proof - `charm/zkp_compiler/dleq_proof.py`
- [x] Implement Knowledge of Representation proof - `charm/zkp_compiler/representation_proof.py`
- [x] Add support for multi-character variable names - Updated `zkparser.py`
- [x] Thread-safe implementation - `charm/zkp_compiler/thread_safe.py`

**Phase 2 Implementation Notes:**
- DLEQ proves h1 = g1^x AND h2 = g2^x for same secret x (Chaum-Pedersen protocol)
- Representation proof supports n generators: h = g1^x1 * g2^x2 * ... * gn^xn
- Parser now supports variable names like `x1`, `alpha`, `commitment` (was single-char only)
- Non-interactive proof methods are thread-safe by design
- Interactive provers/verifiers can use `ThreadSafeProver`/`ThreadSafeVerifier` wrappers

### Phase 3 (v0.62) ✅
- [x] Implement AND composition - `charm/zkp_compiler/and_proof.py`
- [x] Implement OR composition (CDS94) - `charm/zkp_compiler/or_proof.py`
- [x] Implement Range Proofs - `charm/zkp_compiler/range_proof.py`
- [x] Batch verification - `charm/zkp_compiler/batch_verify.py`

**Phase 3 Implementation Notes:**
- AND composition: Combines multiple proofs with shared Fiat-Shamir challenge
- OR composition: CDS94 technique - simulates unknown branch, challenges sum to main challenge
- Range proofs: Bit decomposition approach with O(n) proof size for [0, 2^n) ranges
- Batch verification: Random linear combination technique for efficient multi-proof verification
- All implementations include comprehensive tests and documentation

### Phase 4 (v0.70) - Production Hardening

#### 4.1 Legacy API Deprecation
- [x] Add `DeprecationWarning` to all legacy functions in `zkp_generator.py`:
  - `executeIntZKProof()` - emit warning on every call
  - `executeNonIntZKProof()` - emit warning on every call
  - `KoDLFixedBase()` and related internal functions
- [x] Update `__init__.py` to emit import-time deprecation warning for legacy modules
- [x] Add migration examples in deprecation messages pointing to new API
- [x] Document removal timeline (suggest v0.80 for complete removal)

#### 4.2 Security Audit Checklist
- [x] **Input Validation**: Verify all public inputs are validated before use
  - Check group membership for all elements
  - Validate proof structure before verification
  - Ensure challenge is computed correctly (Fiat-Shamir)
- [x] **Timing Attack Resistance**: Review for constant-time operations
  - Verify comparison operations don't leak timing info
  - Check exponentiation operations
- [x] **Random Number Generation**: Audit randomness sources
  - Verify group.random() uses cryptographically secure RNG
  - Check for proper seeding
- [x] **Serialization Security**: Review serialize/deserialize for injection attacks
  - Validate deserialized data before use
  - Check for buffer overflow vulnerabilities
- [x] **Error Handling**: Ensure errors don't leak sensitive information
  - Review exception messages
  - Verify failed proofs don't reveal witness info

#### 4.3 Performance Benchmarks
- [x] Create benchmark suite comparing curves:
  - BN254 vs SS512 vs MNT224
  - Measure: proof generation time, verification time, proof size
- [x] Benchmark each proof type:
  - Schnorr, DLEQ, Representation, AND, OR, Range, Batch
- [x] Compare batch verification speedup vs individual verification
- [x] Memory usage profiling
- [x] Document recommended use cases based on performance characteristics

#### 4.4 Documentation Updates
- [x] Complete API reference documentation for all proof types
- [x] Add usage examples for each proof type
- [x] Create "Choosing the Right Proof Type" guide
- [x] Document security considerations and threat model
- [x] Add curve selection guide (BN254 recommended for production)
- [x] Update README with ZKP compiler section
- [x] Create Jupyter notebook tutorials

#### 4.5 Additional Hardening
- [x] Add type hints to all public APIs
- [x] Improve error messages with actionable guidance
- [x] Add logging for debugging (configurable verbosity)
- [x] Consider adding proof composition helpers (e.g., prove_and_verify convenience functions)

---

## References

1. **Schnorr Protocol**: C.P. Schnorr, "Efficient Signature Generation by Smart Cards", 1991
2. **DLEQ (Chaum-Pedersen)**: Chaum & Pedersen, "Wallet Databases with Observers", 1992
3. **OR Composition (CDS94)**: Cramer, Damgård, Schoenmakers, "Proofs of Partial Knowledge", 1994
4. **Fiat-Shamir Transform**: Fiat & Shamir, "How to Prove Yourself", 1986
5. **Bulletproofs**: Bünz et al., "Bulletproofs: Short Proofs for Confidential Transactions", 2018

---

*Document Version: 1.0*
*Last Updated: 2026-01-24*
*Author: Charm-Crypto Team*---------------------          --------------------------
r ← random ZR
u₁ = g₁^r, u₂ = g₂^r
                    u₁, u₂
                  ─────────>
                    c
                  <─────────       c ← random ZR (or Fiat-Shamir)
z = r + c·x
                    z
                  ─────────>
                               Verify: g₁^z == u₁·h₁^c AND g₂^z == u₂·h₂^c
```

### Proposed API

```python
class DLEQProof(ZKProofBase):
    """Proof of discrete log equality (Chaum-Pedersen)."""
    
    @classmethod
    def prove_non_interactive(cls, group, g1, h1, g2, h2, x):
        """Prove knowledge of x such that h1 = g1^x and h2 = g2^x."""
        ...
    
    @classmethod
    def verify_non_interactive(cls, group, g1, h1, g2, h2, proof):
        """Verify a DLEQ proof."""
        ...
```

---

