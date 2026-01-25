.. _test_vectors:

Schemes with Test Vectors
=========================

This section documents cryptographic schemes that have formal test vectors verifying
their mathematical correctness and security properties. Test vectors are essential for:

- **Verification**: Ensuring implementations match theoretical specifications
- **Interoperability**: Validating consistency across different implementations
- **Security Auditing**: Demonstrating resistance to known attacks

Each scheme below includes test vectors that verify fundamental properties from the
original papers and relevant standards.

BLS Signatures
--------------

**Implementation**: :mod:`charm.schemes.pksig.pksig_bls04`

**Test Vectors**: ``charm/test/vectors/test_bls_vectors.py``

**References**:

- Boneh, Lynn, Shacham: "Short Signatures from the Weil Pairing" (2004)
- IETF draft-irtf-cfrg-bls-signature

Mathematical Properties
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Vector ID
     - Property
     - Description
   * - BLS-1
     - Verification Equation
     - :math:`e(\sigma, g) = e(H(m), pk)` where :math:`\sigma = H(m)^{sk}`
   * - BLS-2
     - Determinism
     - Same (sk, m) always produces identical signature
   * - BLS-3
     - Message Binding
     - Different messages produce different signatures
   * - BLS-4
     - Key Binding
     - Signature under sk₁ does not verify under pk₂
   * - BLS-5
     - Message Integrity
     - Modified message fails verification
   * - BLS-6
     - Bilinearity
     - :math:`e(g^a, h^b) = e(g, h)^{ab}`
   * - BLS-7
     - Non-degeneracy
     - :math:`e(g, h) \neq 1` for generators g, h

Known Answer Tests (KATs)
^^^^^^^^^^^^^^^^^^^^^^^^^

- **BLS-KAT-1**: Signature structure (valid G1 element)
- **BLS-KAT-2**: Empty message handling
- **BLS-KAT-3**: Large message handling (10KB+)

Security Tests
^^^^^^^^^^^^^^

- **BLS-SEC-1**: Identity element rejection
- **BLS-SEC-2**: Random signature rejection

Pedersen Commitments
--------------------

**Implementation**: :mod:`charm.schemes.commit.commit_pedersen92`

**Test Vectors**: ``charm/test/vectors/test_pedersen_vectors.py``

**References**:

- Pedersen: "Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing" (1992)

Mathematical Properties
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Vector ID
     - Property
     - Description
   * - PEDERSEN-1
     - Commitment Correctness
     - :math:`C = g^m \cdot h^r`
   * - PEDERSEN-2
     - Decommitment Verification
     - Valid (C, r, m) tuple verifies
   * - PEDERSEN-3
     - Binding Property
     - Cannot decommit to different message
   * - PEDERSEN-4
     - Randomness Binding
     - Cannot decommit with wrong randomness
   * - PEDERSEN-5
     - Hiding Property
     - Same message, different randomness → different commitments
   * - PEDERSEN-6
     - Homomorphic Property
     - :math:`C(m_1, r_1) \cdot C(m_2, r_2) = C(m_1+m_2, r_1+r_2)`
   * - PEDERSEN-7
     - Homomorphic Decommitment
     - Product of commitments decommits with sum of values

Edge Cases
^^^^^^^^^^

- **PEDERSEN-EDGE-1**: Zero message
- **PEDERSEN-EDGE-2**: Message = 1
- **PEDERSEN-EDGE-3**: Negative message (modular arithmetic)

Security Tests
^^^^^^^^^^^^^^

- **PEDERSEN-SEC-1**: Generator independence (g ≠ h)
- **PEDERSEN-SEC-2**: Non-trivial commitment (not identity)
- **PEDERSEN-SEC-3**: Random commitment rejection

Schnorr Zero-Knowledge Proofs
-----------------------------

**Implementation**: :mod:`charm.zkp_compiler.schnorr_proof`

**Test Vectors**: ``charm/test/vectors/test_schnorr_vectors.py``

**References**:

- Schnorr: "Efficient Signature Generation by Smart Cards" (1991)
- RFC 8235: Schnorr Non-interactive Zero-Knowledge Proof
- Fiat-Shamir heuristic for non-interactive proofs

Mathematical Properties
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Vector ID
     - Property
     - Description
   * - SCHNORR-1
     - Completeness (Interactive)
     - Honest prover always convinces honest verifier
   * - SCHNORR-2
     - Completeness (Non-Interactive)
     - Valid non-interactive proof always verifies
   * - SCHNORR-3
     - Soundness
     - Wrong witness cannot produce valid proof
   * - SCHNORR-4
     - Verification Equation
     - :math:`g^z = u \cdot h^c` where :math:`z = r + c \cdot x`
   * - SCHNORR-5
     - Challenge Binding
     - Challenge deterministically derived via Fiat-Shamir
   * - SCHNORR-6
     - Zero-Knowledge (Simulation)
     - Proofs can be simulated without witness

Edge Cases
^^^^^^^^^^

- **SCHNORR-EDGE-1**: Identity commitment rejection
- **SCHNORR-EDGE-2**: Zero secret (x = 0)
- **SCHNORR-EDGE-3**: Secret = 1
- **SCHNORR-EDGE-4**: Large secret (near group order)

Serialization Tests
^^^^^^^^^^^^^^^^^^^

- **SCHNORR-SER-1**: Serialize/deserialize roundtrip
- **SCHNORR-SER-2**: Serialization format (bytes)

Running Test Vectors
--------------------

Run all test vectors::

    pytest charm/test/vectors/ -v

Run specific scheme vectors::

    pytest charm/test/vectors/test_bls_vectors.py -v
    pytest charm/test/vectors/test_pedersen_vectors.py -v
    pytest charm/test/vectors/test_schnorr_vectors.py -v

