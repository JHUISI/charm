"""
Unit tests for DLEQ (Discrete Log Equality) ZK proof implementation.

Tests cover:
- Interactive proof protocol
- Non-interactive (Fiat-Shamir) proof
- Serialization and deserialization
- Different pairing groups
- Edge cases and error handling
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.dleq_proof import DLEQProof, DLEQProofData


class TestDLEQProofInteractive(unittest.TestCase):
    """Tests for interactive DLEQ protocol."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h1 = self.g1 ** self.x
        self.h2 = self.g2 ** self.x

    def test_prove_and_verify_interactive(self):
        """Test complete interactive proof cycle."""
        # Create prover and verifier
        prover = DLEQProof.Prover(self.x, self.group)
        verifier = DLEQProof.Verifier(self.group)

        # Step 1: Prover creates commitments
        commitment1, commitment2 = prover.create_commitment(self.g1, self.g2)
        self.assertIsNotNone(commitment1)
        self.assertIsNotNone(commitment2)

        # Step 2: Verifier creates challenge
        challenge = verifier.create_challenge()
        self.assertIsNotNone(challenge)

        # Step 3: Prover creates response
        response = prover.create_response(challenge)
        self.assertIsNotNone(response)

        # Step 4: Verifier verifies
        result = verifier.verify(
            self.g1, self.h1, self.g2, self.h2, commitment1, commitment2, response
        )
        self.assertTrue(result)

    def test_invalid_proof_fails_interactive(self):
        """Test that wrong secret fails verification."""
        wrong_x = self.group.random(ZR)
        prover = DLEQProof.Prover(wrong_x, self.group)
        verifier = DLEQProof.Verifier(self.group)

        commitment1, commitment2 = prover.create_commitment(self.g1, self.g2)
        challenge = verifier.create_challenge()
        response = prover.create_response(challenge)

        # Should fail because wrong secret
        result = verifier.verify(
            self.g1, self.h1, self.g2, self.h2, commitment1, commitment2, response
        )
        self.assertFalse(result)

    def test_prover_commitment_before_response(self):
        """Test that prover must create commitment before response."""
        prover = DLEQProof.Prover(self.x, self.group)

        # Try to create response without commitment
        with self.assertRaises(ValueError):
            prover.create_response(self.group.random(ZR))

    def test_different_exponents_fail(self):
        """Test that using different x for h1 and h2 should fail."""
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h1_wrong = self.g1 ** x1
        h2_wrong = self.g2 ** x2

        # Prover knows x1 but tries to prove h1 = g1^x1 AND h2 = g2^x1
        # But h2 = g2^x2 (not g2^x1), so verification should fail
        prover = DLEQProof.Prover(x1, self.group)
        verifier = DLEQProof.Verifier(self.group)

        commitment1, commitment2 = prover.create_commitment(self.g1, self.g2)
        challenge = verifier.create_challenge()
        response = prover.create_response(challenge)

        result = verifier.verify(
            self.g1, h1_wrong, self.g2, h2_wrong, commitment1, commitment2, response
        )
        self.assertFalse(result)


class TestDLEQProofNonInteractive(unittest.TestCase):
    """Tests for non-interactive (Fiat-Shamir) DLEQ proof."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h1 = self.g1 ** self.x
        self.h2 = self.g2 ** self.x

    def test_non_interactive_proof_valid(self):
        """Test Fiat-Shamir transformed proof."""
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, self.x
        )

        self.assertIsNotNone(proof)
        self.assertIsNotNone(proof.commitment1)
        self.assertIsNotNone(proof.commitment2)
        self.assertIsNotNone(proof.challenge)
        self.assertIsNotNone(proof.response)

        result = DLEQProof.verify_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, proof
        )
        self.assertTrue(result)

    def test_non_interactive_wrong_secret_fails(self):
        """Test that wrong secret fails non-interactive verification."""
        wrong_x = self.group.random(ZR)
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, wrong_x
        )

        result = DLEQProof.verify_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, proof
        )
        self.assertFalse(result)

    def test_non_interactive_tampered_proof_fails(self):
        """Test that tampered proof fails verification."""
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, self.x
        )

        # Tamper with the response
        tampered = DLEQProofData(
            commitment1=proof.commitment1,
            commitment2=proof.commitment2,
            challenge=proof.challenge,
            response=proof.response + self.group.random(ZR),
            proof_type=proof.proof_type
        )

        result = DLEQProof.verify_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, tampered
        )
        self.assertFalse(result)

    def test_proof_deterministic_verification(self):
        """Test that same proof verifies consistently."""
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, self.x
        )

        # Verify multiple times
        for _ in range(5):
            result = DLEQProof.verify_non_interactive(
                self.group, self.g1, self.h1, self.g2, self.h2, proof
            )
            self.assertTrue(result)

    def test_mismatched_bases_fail(self):
        """Test that h1 = g1^x but h2 = g2^y (different exponents) should fail."""
        x = self.group.random(ZR)
        y = self.group.random(ZR)
        h1 = self.g1 ** x
        h2 = self.g2 ** y

        # Try to prove with x, but h2 was computed with different y
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, h1, self.g2, h2, x
        )

        result = DLEQProof.verify_non_interactive(
            self.group, self.g1, h1, self.g2, h2, proof
        )
        self.assertFalse(result)


class TestDLEQProofSerialization(unittest.TestCase):
    """Tests for DLEQ proof serialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h1 = self.g1 ** self.x
        self.h2 = self.g2 ** self.x

    def test_serialization_roundtrip(self):
        """Test serialize and deserialize proof."""
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, self.x
        )

        # Serialize
        serialized = DLEQProof.serialize_proof(proof, self.group)
        self.assertIsInstance(serialized, bytes)
        self.assertGreater(len(serialized), 0)

        # Deserialize
        deserialized = DLEQProof.deserialize_proof(serialized, self.group)
        self.assertIsNotNone(deserialized)
        self.assertEqual(deserialized.proof_type, proof.proof_type)

    def test_serialized_proof_verifies(self):
        """Test that deserialized proof still verifies."""
        proof = DLEQProof.prove_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, self.x
        )

        # Serialize and deserialize
        serialized = DLEQProof.serialize_proof(proof, self.group)
        deserialized = DLEQProof.deserialize_proof(serialized, self.group)

        # Verify the deserialized proof
        result = DLEQProof.verify_non_interactive(
            self.group, self.g1, self.h1, self.g2, self.h2, deserialized
        )
        self.assertTrue(result)


class TestDLEQProofWithDifferentGroups(unittest.TestCase):
    """Test DLEQ proofs with different pairing groups."""

    def test_with_bn254_group(self):
        """Test with BN254 pairing group."""
        self._test_with_group('BN254')

    def test_with_mnt224_group(self):
        """Test with MNT224 pairing group."""
        self._test_with_group('MNT224')

    def _test_with_group(self, curve_name):
        """Helper to test with a specific group."""
        group = PairingGroup(curve_name)
        g1 = group.random(G1)
        g2 = group.random(G1)
        x = group.random(ZR)
        h1 = g1 ** x
        h2 = g2 ** x

        proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
        result = DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

