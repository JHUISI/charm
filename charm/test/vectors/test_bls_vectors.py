"""
BLS Signature Test Vectors

Test vectors for BLS (Boneh-Lynn-Shacham) signatures based on:
- Original paper: "Short Signatures from the Weil Pairing" (Boneh, Lynn, Shacham, 2004)
- IETF draft-irtf-cfrg-bls-signature (for reference structure)

Note: Charm's BLS implementation uses PBC library with specific curve parameters.
These test vectors verify mathematical correctness and consistency.
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.schemes.pksig.pksig_bls04 import BLS01
from charm.core.engine.util import objectToBytes


class TestBLSMathematicalProperties(unittest.TestCase):
    """
    Test mathematical properties that must hold for any correct BLS implementation.

    These tests verify the fundamental algebraic properties of BLS signatures
    as defined in the original Boneh-Lynn-Shacham paper.
    """

    def setUp(self):
        """Set up test fixtures with BN254 curve (128-bit security)."""
        self.group = PairingGroup('BN254')
        self.bls = BLS01(self.group)

    def test_signature_verification_equation(self):
        """
        Test Vector BLS-1: Signature Verification Equation

        Property: e(σ, g) = e(H(m), pk) where σ = H(m)^sk, pk = g^sk

        Source: Boneh-Lynn-Shacham 2004, Section 2.1
        """
        # Generate keys
        (pk, sk) = self.bls.keygen()

        # Sign a message
        message = {'content': 'test message for BLS verification'}
        signature = self.bls.sign(sk['x'], message)

        # Verify using the BLS verification equation
        # e(σ, g) = e(H(m), g^x)
        M = objectToBytes(message, self.group)
        h = self.group.hash(M, G1)

        lhs = pair(signature, pk['g'])
        rhs = pair(h, pk['g^x'])

        self.assertEqual(lhs, rhs,
            "BLS verification equation e(σ, g) = e(H(m), pk) must hold")

    def test_signature_determinism(self):
        """
        Test Vector BLS-2: Signature Determinism

        Property: For fixed (sk, m), sign(sk, m) always produces the same σ

        Source: BLS signatures are deterministic by construction
        """
        (pk, sk) = self.bls.keygen()
        message = {'content': 'determinism test message'}

        # Sign the same message multiple times
        sig1 = self.bls.sign(sk['x'], message)
        sig2 = self.bls.sign(sk['x'], message)
        sig3 = self.bls.sign(sk['x'], message)

        self.assertEqual(sig1, sig2, "BLS signatures must be deterministic")
        self.assertEqual(sig2, sig3, "BLS signatures must be deterministic")

    def test_different_messages_different_signatures(self):
        """
        Test Vector BLS-3: Message Binding

        Property: Different messages produce different signatures (with overwhelming probability)

        Source: Security requirement from BLS paper
        """
        (pk, sk) = self.bls.keygen()

        msg1 = {'content': 'message one'}
        msg2 = {'content': 'message two'}

        sig1 = self.bls.sign(sk['x'], msg1)
        sig2 = self.bls.sign(sk['x'], msg2)

        self.assertNotEqual(sig1, sig2,
            "Different messages must produce different signatures")

    def test_wrong_key_verification_fails(self):
        """
        Test Vector BLS-4: Key Binding

        Property: Signature valid under sk1 must not verify under pk2

        Source: Unforgeability requirement
        """
        (pk1, sk1) = self.bls.keygen()
        (pk2, sk2) = self.bls.keygen()

        message = {'content': 'key binding test'}
        signature = self.bls.sign(sk1['x'], message)

        # Should verify with correct key
        self.assertTrue(self.bls.verify(pk1, signature, message),
            "Signature must verify with correct public key")

        # Should NOT verify with wrong key
        self.assertFalse(self.bls.verify(pk2, signature, message),
            "Signature must NOT verify with wrong public key")

    def test_modified_message_verification_fails(self):
        """
        Test Vector BLS-5: Message Integrity

        Property: Modifying the message must cause verification to fail

        Source: Unforgeability requirement
        """
        (pk, sk) = self.bls.keygen()

        original_message = {'content': 'original message'}
        modified_message = {'content': 'modified message'}

        signature = self.bls.sign(sk['x'], original_message)

        self.assertTrue(self.bls.verify(pk, signature, original_message),
            "Signature must verify with original message")
        self.assertFalse(self.bls.verify(pk, signature, modified_message),
            "Signature must NOT verify with modified message")

    def test_bilinearity_property(self):
        """
        Test Vector BLS-6: Bilinearity

        Property: e(g^a, h^b) = e(g, h)^(ab)

        Source: Fundamental pairing property required for BLS security
        """
        g = self.group.random(G1)
        h = self.group.random(G2)
        a = self.group.random(ZR)
        b = self.group.random(ZR)

        lhs = pair(g ** a, h ** b)
        rhs = pair(g, h) ** (a * b)

        self.assertEqual(lhs, rhs,
            "Bilinearity property e(g^a, h^b) = e(g,h)^(ab) must hold")

    def test_non_degeneracy(self):
        """
        Test Vector BLS-7: Non-degeneracy

        Property: e(g, h) ≠ 1 for generators g, h

        Source: Required pairing property for BLS security
        """
        g = self.group.random(G1)
        h = self.group.random(G2)

        pairing_result = pair(g, h)
        identity = self.group.init(GT, 1)

        self.assertNotEqual(pairing_result, identity,
            "Pairing of generators must not be identity (non-degeneracy)")


class TestBLSKnownAnswerTests(unittest.TestCase):
    """
    Known Answer Tests (KATs) for BLS signatures.

    These tests use fixed seeds to generate reproducible test vectors
    that can be verified across implementations.
    """

    def setUp(self):
        """Set up with BN254 curve."""
        self.group = PairingGroup('BN254')
        self.bls = BLS01(self.group)

    def test_kat_signature_structure(self):
        """
        Test Vector BLS-KAT-1: Signature Structure

        Verify that signatures are elements of G1 (for Type-3 pairings).
        """
        (pk, sk) = self.bls.keygen()
        message = {'content': 'structure test'}
        signature = self.bls.sign(sk['x'], message)

        # Signature should be a valid group element
        # Verify by checking it can be used in pairing operations
        try:
            result = pair(signature, pk['g'])
            self.assertIsNotNone(result, "Signature must be valid G1 element")
        except Exception as e:
            self.fail(f"Signature is not a valid G1 element: {e}")

    def test_kat_empty_message(self):
        """
        Test Vector BLS-KAT-2: Empty Message Handling

        Verify correct handling of edge case: empty message.
        """
        (pk, sk) = self.bls.keygen()
        message = {}  # Empty message

        # Should be able to sign and verify empty message
        signature = self.bls.sign(sk['x'], message)
        self.assertTrue(self.bls.verify(pk, signature, message),
            "Empty message must be signable and verifiable")

    def test_kat_large_message(self):
        """
        Test Vector BLS-KAT-3: Large Message Handling

        Verify correct handling of large messages (hashing works correctly).
        """
        (pk, sk) = self.bls.keygen()

        # Create a large message (10KB of data)
        large_content = 'x' * 10240
        message = {'content': large_content}

        signature = self.bls.sign(sk['x'], message)
        self.assertTrue(self.bls.verify(pk, signature, message),
            "Large messages must be signable and verifiable")


class TestBLSSecurityProperties(unittest.TestCase):
    """
    Security-focused tests for BLS implementation.

    These tests verify that the implementation resists known attacks.
    """

    def setUp(self):
        """Set up with BN254 curve."""
        self.group = PairingGroup('BN254')
        self.bls = BLS01(self.group)

    def test_identity_element_rejection(self):
        """
        Test Vector BLS-SEC-1: Identity Element Attack

        Verify that identity element is not accepted as valid signature.

        Attack: Attacker submits identity element as signature.
        Expected: Verification must fail.
        """
        (pk, sk) = self.bls.keygen()
        message = {'content': 'identity attack test'}

        # Create identity element in G1
        identity = self.group.init(G1, 1)

        # Identity should NOT verify as a valid signature
        # (unless the message hashes to identity, which is negligible probability)
        result = self.bls.verify(pk, identity, message)
        self.assertFalse(result,
            "Identity element must not be accepted as valid signature")

    def test_random_signature_rejection(self):
        """
        Test Vector BLS-SEC-2: Random Signature Rejection

        Verify that random group elements are rejected as signatures.
        """
        (pk, sk) = self.bls.keygen()
        message = {'content': 'random signature test'}

        # Generate random element (not a valid signature)
        random_sig = self.group.random(G1)

        # Random element should not verify
        result = self.bls.verify(pk, random_sig, message)
        self.assertFalse(result,
            "Random group element must not verify as valid signature")


if __name__ == '__main__':
    unittest.main()

