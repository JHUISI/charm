sigmaprotocol - Sigma Protocols (Zero-Knowledge Proofs)
========================================================

.. module:: charm.toolbox.sigmaprotocol
   :synopsis: Base class for Sigma protocol implementations

This module provides the base class for implementing Sigma protocols (three-move
zero-knowledge proofs) in the Charm cryptographic library.

Overview
--------

Sigma protocols are a class of three-move interactive proof systems where a
prover convinces a verifier of knowledge of a secret witness (such as a discrete
logarithm) without revealing the witness itself. The "sigma" name comes from the
Greek letter Σ, representing the three-move structure.

**The Three Moves:**

1. **Commitment (a)**: Prover sends a commitment based on random values
2. **Challenge (c)**: Verifier sends a random challenge
3. **Response (z)**: Prover sends a response computed from witness and challenge

The verifier accepts if a verification equation holds.

**Example - Schnorr Protocol:**

To prove knowledge of x such that h = g^x:

1. Prover: Pick random r, send a = g^r
2. Verifier: Send random challenge c
3. Prover: Send z = r + cx
4. Verifier: Check g^z = a · h^c

Security Properties
-------------------

Sigma protocols provide the following security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Property
     - Description
   * - **Completeness**
     - An honest prover with a valid witness always convinces the verifier.
   * - **Special Soundness**
     - Given two accepting transcripts (a, c₁, z₁) and (a, c₂, z₂) with the
       same commitment but different challenges, the witness can be extracted.
       This implies soundness: a cheating prover succeeds with negligible probability.
   * - **HVZK (Honest-Verifier Zero-Knowledge)**
     - There exists a simulator that produces transcripts indistinguishable
       from real ones, without knowing the witness. Security holds when the
       verifier follows the protocol honestly.
   * - **NIZK (via Fiat-Shamir)**
     - By replacing the verifier's random challenge with a hash of the
       commitment and statement, the protocol becomes non-interactive.
       Security holds in the Random Oracle Model.

Typical Use Cases
-----------------

1. **Authentication Protocols**

   Prove knowledge of a secret key without revealing it. Used in smart card
   authentication, password-authenticated key exchange, and identity protocols.

   .. code-block:: python

       # Prover demonstrates knowledge of secret key x
       # where public key y = g^x
       prover_state1()  # Send commitment a = g^r
       # Receive challenge c from verifier
       prover_state3()  # Send response z = r + cx
       # Verifier checks: g^z == a * y^c

2. **Digital Signatures**

   Schnorr signatures are Sigma protocols made non-interactive via Fiat-Shamir.
   The challenge is derived by hashing the commitment and message.

3. **Verifiable Encryption**

   Prove that a ciphertext encrypts a value satisfying certain properties
   (e.g., within a range) without revealing the value.

Example Schemes
---------------

The following Sigma protocol implementations are available in Charm:

**Schnorr Zero-Knowledge Protocol:**

- :mod:`charm.schemes.protocol_schnorr91` - **SchnorrZK**: Classic Schnorr
  identification protocol proving knowledge of discrete log.

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, G
    from charm.toolbox.eccurve import prime192v1
    from charm.schemes.protocol_schnorr91 import SchnorrZK

    # Setup
    group = ECGroup(prime192v1)
    sp = SchnorrZK(group)

    # Interactive protocol (simplified)
    # Prover state 1: generate commitment
    # t = g^r, send (t, g, y=g^x) to verifier

    # Verifier state 2: generate challenge c

    # Prover state 3: compute response s = r + c*x

    # Verifier state 4: verify g^s == t * y^c

**Pairing-Based Sigma Protocols:**

- :mod:`charm.schemes.sigma1` - **SigmaProtocol1**: Sigma protocol for
  pairing-based settings
- :mod:`charm.schemes.sigma2` - **SigmaProtocol2**: Verifiable encryption
  protocol
- :mod:`charm.schemes.sigma3` - **SigmaProtocol3**: Proof of membership
  protocol

**Modern ZKP Compiler:**

For more advanced zero-knowledge proofs, see the ZKP compiler:

- :mod:`charm.zkp_compiler.schnorr_proof` - Non-interactive Schnorr proofs
- :mod:`charm.zkp_compiler.dleq_proof` - Discrete log equality proofs
- :mod:`charm.zkp_compiler.representation_proof` - Knowledge of representation

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
    from charm.zkp_compiler.schnorr_proof import SchnorrProof

    group = PairingGroup('BN254')
    g = group.random(G1)
    x = group.random(ZR)
    h = g ** x

    # Non-interactive proof (Fiat-Shamir)
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
    assert is_valid == True

API Reference
-------------

.. automodule:: sigmaprotocol
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.ZKProof` - Base class for zero-knowledge proofs
- :mod:`charm.toolbox.Commit` - Commitment schemes (used in Sigma protocols)
- :mod:`charm.core.engine.protocol` - Protocol engine for interactive proofs
- :mod:`charm.zkp_compiler` - Modern ZKP compiler framework
