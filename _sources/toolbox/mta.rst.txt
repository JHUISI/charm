
mta - Multiplicative-to-Additive Conversion
===========================================

Overview
--------

The ``mta`` module implements **Multiplicative-to-Additive (MtA)** share conversion,
a fundamental building block for threshold ECDSA protocols. MtA enables two parties
holding multiplicative shares (a, b) to convert them into additive shares (α, β)
such that **a·b = α + β (mod q)**, without revealing their individual shares.

This implementation is based on the DKLS23 paper ("Threshold ECDSA from ECDSA
Assumptions: The Multiparty Case") and uses real oblivious transfer (OT) for
security rather than simulation.

Key Features
------------

* **Secure Share Conversion**: Converts multiplicative to additive shares without revealing inputs
* **OT-Based Security**: Uses real SimpleOT for cryptographic security guarantees
* **MtA with Check (MtAwc)**: Includes zero-knowledge proofs for malicious security
* **Curve Agnostic**: Works with any DDH-hard elliptic curve group
* **Bit-Level OT**: Uses correlated OT with one OT per bit of the secret

Security Properties
-------------------

* **Sender Privacy**: Receiver learns nothing about sender's share beyond the additive output
* **Receiver Privacy**: Sender learns nothing about receiver's share
* **Correctness**: The additive shares always sum to the original product
* **Malicious Security** (MtAwc): Zero-knowledge proofs detect cheating parties

Use Cases
---------

* **DKLS23 Presigning**: Core component for generating presignatures
* **Threshold ECDSA**: Enables secure multiplication of secret shares
* **Two-Party Computation**: General-purpose secure multiplication protocol

Example Usage
-------------

**Basic MtA Conversion:**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, ZR
    from charm.toolbox.eccurve import secp256k1
    from charm.toolbox.mta import MtA

    group = ECGroup(secp256k1)

    # Create separate MtA instances for Alice and Bob
    alice_mta = MtA(group)
    bob_mta = MtA(group)

    # Alice has share a, Bob has share b
    a = group.random(ZR)
    b = group.random(ZR)

    # Run the 4-round MtA protocol
    sender_msg = alice_mta.sender_round1(a)
    receiver_msg, _ = bob_mta.receiver_round1(b, sender_msg)
    alpha, ot_data = alice_mta.sender_round2(receiver_msg)
    beta = bob_mta.receiver_round2(ot_data)

    # Verify: a*b = alpha + beta (mod q)
    assert a * b == alpha + beta

**MtA with Correctness Check (MtAwc):**

.. code-block:: python

    from charm.toolbox.mta import MtAwc

    mta_wc = MtAwc(group)

    a = group.random(ZR)
    b = group.random(ZR)

    # Commitment phase
    sender_commit = mta_wc.sender_commit(a)
    receiver_commit = mta_wc.receiver_commit(b)

    # MtA with ZK proofs
    sender_msg = mta_wc.sender_round1(a, receiver_commit)
    receiver_msg, _ = mta_wc.receiver_round1(b, sender_commit, sender_msg)
    alpha, proof = mta_wc.sender_round2(receiver_msg)
    beta, valid = mta_wc.receiver_verify(proof)

    assert valid  # Proof verified
    assert a * b == alpha + beta

Protocol Details
----------------

The MtA protocol works as follows:

1. **Sender Setup**: Sender decomposes share `a` into bits and creates OT sender instances
2. **Receiver Choose**: Receiver uses bits of `b` to select OT messages (learns only selected values)
3. **Sender Transfer**: Sender encrypts correlated messages via OT
4. **Receiver Output**: Receiver decrypts selected messages and computes additive share

For each bit position i, the correlation is: m₁ = m₀ + a·2ⁱ, ensuring the sum of
selected values equals a·b.

Related Modules
---------------

* :doc:`mpc_utils` - Bit decomposition utilities used by MtA
* :doc:`threshold_sharing` - Threshold sharing for key distribution
* :doc:`broadcast` - Broadcast primitives for consistency

API Reference
-------------

.. automodule:: mta
    :show-inheritance:
    :members:
    :undoc-members:
