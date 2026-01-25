
ZKP Compiler
============

.. module:: charm.zkp_compiler
   :synopsis: Zero-Knowledge Proof Compiler

Overview
--------

The ZKP compiler provides secure, production-ready implementations of common
zero-knowledge proof protocols. It supports both interactive and non-interactive
(Fiat-Shamir) modes, with efficient batch verification capabilities.

**Key Features:**

- Schnorr, DLEQ, and Representation proofs
- AND/OR composition for complex statements
- Range proofs via bit decomposition
- Batch verification for improved performance
- Serialization for network transmission

Quick Start
-----------

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
    from charm.zkp_compiler import SchnorrProof

    # Setup
    group = PairingGroup('BN254')
    g = group.random(G1)
    x = group.random(ZR)  # Secret
    h = g ** x  # Public value

    # Prove knowledge of x such that h = g^x
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)

    # Verify
    valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
    print(f"Proof valid: {valid}")

Proof Types
-----------

SchnorrProof
^^^^^^^^^^^^

Proves knowledge of discrete logarithm: *"I know x such that h = g^x"*.

.. code-block:: python

    from charm.zkp_compiler import SchnorrProof

    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    valid = SchnorrProof.verify_non_interactive(group, g, h, proof)

DLEQProof
^^^^^^^^^

Proves discrete log equality (Chaum-Pedersen): *"I know x such that h1 = g1^x AND h2 = g2^x"*.

.. code-block:: python

    from charm.zkp_compiler import DLEQProof

    proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
    valid = DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)

RepresentationProof
^^^^^^^^^^^^^^^^^^^

Proves knowledge of representation: *"I know x1, x2, ... such that h = g1^x1 * g2^x2 * ..."*.

.. code-block:: python

    from charm.zkp_compiler import RepresentationProof

    proof = RepresentationProof.prove_non_interactive(group, [g1, g2], h, [x1, x2])
    valid = RepresentationProof.verify_non_interactive(group, [g1, g2], h, proof)

ANDProof
^^^^^^^^

Proves conjunction of multiple statements.

.. code-block:: python

    from charm.zkp_compiler import ANDProof

    statements = [
        {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
        {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
    ]
    proof = ANDProof.prove_non_interactive(group, statements)

    # For verification (without secrets)
    public_statements = [
        {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
        {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
    ]
    valid = ANDProof.verify_non_interactive(group, public_statements, proof)

ORProof
^^^^^^^

Proves disjunction using CDS94 technique: *"I know the DL of h1 OR h2"* (without revealing which).

.. code-block:: python

    from charm.zkp_compiler import ORProof

    # which=0 means prover knows DL of h1; which=1 means DL of h2
    proof = ORProof.prove_non_interactive(group, g, h1, h2, x, which=0)
    valid = ORProof.verify_non_interactive(group, g, h1, h2, proof)

RangeProof
^^^^^^^^^^

Proves a committed value is in range [0, 2^n) using bit decomposition.

.. code-block:: python

    from charm.zkp_compiler import RangeProof

    value = 42
    randomness = group.random(ZR)
    commitment = RangeProof.create_pedersen_commitment(group, g, h, value, randomness)

    proof = RangeProof.prove(group, g, h, value, randomness, num_bits=8)
    valid = RangeProof.verify(group, g, h, commitment, proof)

BatchVerifier
^^^^^^^^^^^^^

Efficiently verifies multiple proofs using random linear combination.

.. code-block:: python

    from charm.zkp_compiler import BatchVerifier

    verifier = BatchVerifier(group)
    verifier.add_schnorr_proof(g, h1, proof1)
    verifier.add_schnorr_proof(g, h2, proof2)
    verifier.add_dleq_proof(g1, h1, g2, h2, dleq_proof)

    all_valid = verifier.verify_all()
    verifier.clear()  # Reset for reuse

API Reference
-------------

**Common Methods (all proof types):**

- ``prove_non_interactive(group, ...)`` - Generate non-interactive proof
- ``verify_non_interactive(group, ...)`` - Verify non-interactive proof
- ``serialize_proof(proof, group)`` - Serialize proof to bytes
- ``deserialize_proof(data, group)`` - Deserialize bytes to proof object

**BatchVerifier Methods:**

- ``add_schnorr_proof(g, h, proof)`` - Add Schnorr proof to batch
- ``add_dleq_proof(g1, h1, g2, h2, proof)`` - Add DLEQ proof to batch
- ``verify_all()`` - Verify all proofs in batch
- ``clear()`` - Clear batch for reuse

Curve Selection Guide
---------------------

Use **BN254** for production (~128-bit security):

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup
    group = PairingGroup('BN254')

Other options: ``SS512`` (symmetric pairings), ``MNT224`` (smaller security margin).

See Also
--------

- :mod:`charm.toolbox.pairinggroup` - Pairing group operations
- ``charm/zkp_compiler/zk_demo.py`` - Additional usage examples

