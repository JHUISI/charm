
threshold_test - DKLS23 Threshold ECDSA Tests
=============================================

Overview
--------

The ``threshold_test`` module provides comprehensive test coverage for the DKLS23
threshold ECDSA implementation. It validates all components of the threshold
signature protocol including oblivious transfer, MtA conversion, secret sharing,
distributed key generation, presigning, and signing.

These tests ensure correctness, security properties, and proper error handling
across the entire threshold ECDSA stack.

Test Categories
---------------

The test suite is organized into the following categories:

**Oblivious Transfer Tests (TestSimpleOT, TestOTExtension)**
  * Basic OT correctness for choice bits 0 and 1
  * Multiple independent OT transfers
  * Invalid point rejection (identity element attacks)
  * OT extension with 256+ OTs
  * Base OT setup verification

**MtA Tests (TestMtA, TestMtAwc)**
  * Multiplicative-to-additive correctness: a·b = α + β
  * Real OT security (receiver never sees both messages)
  * Edge cases near curve order boundary
  * MtAwc zero-knowledge proof verification
  * Proof structure validation (no secret leakage)

**Threshold Sharing Tests (TestThresholdSharing, TestPedersenVSS)**
  * Basic Shamir sharing and reconstruction
  * Feldman VSS verification
  * Tampered share detection
  * Various threshold configurations (2-of-3, 3-of-5)
  * Pedersen VSS with blinding factors

**DKG Tests (TestDKLS23_DKG)**
  * 2-of-3 distributed key generation
  * Public key consistency across parties
  * Correct public key computation
  * Session ID validation

**Presigning Tests (TestDKLS23_Presign)**
  * Valid presignature generation
  * Consistent r values across participants
  * Session ID requirements

**Signing Tests (TestDKLS23_Sign)**
  * Signature share generation
  * Standard ECDSA verification
  * Wrong message detection
  * Invalid signature share detection

**End-to-End Tests (TestDKLS23_Complete)**
  * Complete 2-of-3 signing flow
  * Different participant combinations
  * Standard ECDSA format output
  * DER encoding validation
  * Multiple messages with same keys

**Security Tests (TestMaliciousParties)**
  * Invalid share detection during DKG
  * Commitment mismatch detection
  * Malicious party identification

Running the Tests
-----------------

Run all threshold tests with pytest:

.. code-block:: bash

    pytest charm/test/schemes/threshold_test.py -v

Run specific test class:

.. code-block:: bash

    pytest charm/test/schemes/threshold_test.py::TestDKLS23_Complete -v

Run with coverage:

.. code-block:: bash

    pytest charm/test/schemes/threshold_test.py --cov=charm.schemes.threshold --cov-report=html

Key Test Scenarios
------------------

**Complete Signing Flow:**

.. code-block:: python

    def test_complete_2_of_3_signing(self):
        dkls = DKLS23(self.group, threshold=2, num_parties=3)
        g = self.group.random(G)

        # Step 1: Distributed Key Generation
        key_shares, public_key = dkls.distributed_keygen(g)

        # Step 2: Generate presignatures
        presignatures = dkls.presign([1, 2], key_shares, g)

        # Step 3: Sign a message
        message = b"Hello, threshold ECDSA!"
        signature = dkls.sign([1, 2], presignatures, key_shares, message, g)

        # Step 4: Verify signature
        assert dkls.verify(public_key, signature, message, g)

**Curve Agnosticism:**

.. code-block:: python

    def test_curve_agnostic_prime256v1(self):
        from charm.toolbox.eccurve import prime256v1
        group = ECGroup(prime256v1)

        dkls = DKLS23(group, threshold=2, num_parties=3)
        # Protocol works with P-256 curve

**Malicious Party Detection:**

.. code-block:: python

    def test_dkg_invalid_share_detected(self):
        # Tamper with a share during DKG
        tampered_share = original_share + one

        # Victim party detects the invalid share
        key_share, complaint = dkg.keygen_round3(victim_id, state, received, msgs)

        assert key_share is None  # Verification failed
        assert complaint is not None  # Complaint generated

Related Modules
---------------

* :doc:`../toolbox/threshold_sharing` - Threshold sharing implementation
* :doc:`../toolbox/mta` - MtA conversion tested here
* :doc:`../toolbox/broadcast` - Broadcast primitives
* :doc:`../toolbox/mpc_utils` - MPC utilities

API Reference
-------------

.. automodule:: threshold_test
    :show-inheritance:
    :members:
    :undoc-members:
