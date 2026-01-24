"""
Unit tests for OR Composition proof (CDS94) implementation.

Tests cover:
- Non-interactive OR proof generation and verification
- Witness indistinguishability property
- Serialization and deserialization
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.or_proof import ORProof, ORProofData


class TestORProofNonInteractive(unittest.TestCase):
    """Tests for non-interactive OR proof (CDS94)."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        # Create two public values with known discrete logs
        self.x1 = self.group.random(ZR)
        self.x2 = self.group.random(ZR)
        self.h1 = self.g ** self.x1
        self.h2 = self.g ** self.x2

    def test_prove_first_statement(self):
        """Test proving h1 = g^x (which=0)."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x1, which=0
        )

        self.assertIsNotNone(proof)
        self.assertIsNotNone(proof.commitment1)
        self.assertIsNotNone(proof.commitment2)
        self.assertIsNotNone(proof.challenge1)
        self.assertIsNotNone(proof.challenge2)
        self.assertIsNotNone(proof.response1)
        self.assertIsNotNone(proof.response2)

        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof
        )
        self.assertTrue(result)

    def test_prove_second_statement(self):
        """Test proving h2 = g^x (which=1)."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x2, which=1
        )

        self.assertIsNotNone(proof)
        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof
        )
        self.assertTrue(result)

    def test_wrong_secret_fails(self):
        """Test that wrong secret fails verification."""
        wrong_x = self.group.random(ZR)
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, wrong_x, which=0
        )

        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof
        )
        self.assertFalse(result)

    def test_wrong_which_fails(self):
        """Test that claiming wrong branch fails."""
        # x1 is secret for h1, but claim it's for h2 (which=1)
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x1, which=1
        )

        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof
        )
        self.assertFalse(result)

    def test_tampered_proof_fails(self):
        """Test that tampered proof fails verification."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x1, which=0
        )

        # Tamper with response1
        tampered = ORProofData(
            commitment1=proof.commitment1,
            commitment2=proof.commitment2,
            challenge1=proof.challenge1,
            challenge2=proof.challenge2,
            response1=proof.response1 + self.group.random(ZR),
            response2=proof.response2,
            proof_type=proof.proof_type
        )

        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, tampered
        )
        self.assertFalse(result)

    def test_challenges_sum_correctly(self):
        """Test that c1 + c2 equals main challenge."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x1, which=0
        )

        # Recompute expected challenge
        expected_c = ORProof._compute_challenge_hash(
            self.group, self.g, self.h1, self.h2,
            proof.commitment1, proof.commitment2
        )

        # Verify c1 + c2 = c
        actual_c = proof.challenge1 + proof.challenge2
        self.assertEqual(expected_c, actual_c)


class TestORProofWitnessIndistinguishability(unittest.TestCase):
    """Tests for witness indistinguishability property."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x1 = self.group.random(ZR)
        self.x2 = self.group.random(ZR)
        self.h1 = self.g ** self.x1
        self.h2 = self.g ** self.x2

    def test_proofs_look_similar(self):
        """Test that both branches produce valid-looking proofs."""
        proof0 = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x1, which=0
        )
        proof1 = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x2, which=1
        )

        # Both proofs should have same structure
        self.assertEqual(proof0.proof_type, proof1.proof_type)
        self.assertEqual(proof0.proof_type, 'or')

        # Both should be valid
        result0 = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof0
        )
        result1 = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, proof1
        )
        self.assertTrue(result0)
        self.assertTrue(result1)

    def test_verifier_cannot_distinguish(self):
        """Test that verifier accepts both without knowing which."""
        # Generate multiple proofs from each branch
        proofs = []
        for _ in range(3):
            proof0 = ORProof.prove_non_interactive(
                self.group, self.g, self.h1, self.h2, self.x1, which=0
            )
            proof1 = ORProof.prove_non_interactive(
                self.group, self.g, self.h1, self.h2, self.x2, which=1
            )
            proofs.extend([proof0, proof1])

        # Verifier should accept all proofs identically
        for proof in proofs:
            result = ORProof.verify_non_interactive(
                self.group, self.g, self.h1, self.h2, proof
            )
            self.assertTrue(result)


class TestORProofSerialization(unittest.TestCase):
    """Tests for OR proof serialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h1 = self.g ** self.x
        self.h2 = self.g ** self.group.random(ZR)

    def test_serialization_roundtrip(self):
        """Test serialize and deserialize proof."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x, which=0
        )

        # Serialize
        serialized = ORProof.serialize_proof(proof, self.group)
        self.assertIsInstance(serialized, bytes)
        self.assertGreater(len(serialized), 0)

        # Deserialize
        deserialized = ORProof.deserialize_proof(serialized, self.group)

        # Check all fields match
        self.assertEqual(proof.commitment1, deserialized.commitment1)
        self.assertEqual(proof.commitment2, deserialized.commitment2)
        self.assertEqual(proof.challenge1, deserialized.challenge1)
        self.assertEqual(proof.challenge2, deserialized.challenge2)
        self.assertEqual(proof.response1, deserialized.response1)
        self.assertEqual(proof.response2, deserialized.response2)
        self.assertEqual(proof.proof_type, deserialized.proof_type)

    def test_serialized_proof_verifies(self):
        """Test that deserialized proof still verifies."""
        proof = ORProof.prove_non_interactive(
            self.group, self.g, self.h1, self.h2, self.x, which=0
        )

        # Serialize and deserialize
        serialized = ORProof.serialize_proof(proof, self.group)
        deserialized = ORProof.deserialize_proof(serialized, self.group)

        # Deserialized proof should verify
        result = ORProof.verify_non_interactive(
            self.group, self.g, self.h1, self.h2, deserialized
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

