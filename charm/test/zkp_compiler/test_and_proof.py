"""
Unit tests for AND Composition ZK proof implementation.

Tests cover:
- Non-interactive AND proof protocol
- Multiple proof types (Schnorr, DLEQ)
- Serialization and deserialization
- Edge cases and error handling
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.and_proof import ANDProof, ANDProofData


class TestANDProofNonInteractive(unittest.TestCase):
    """Tests for non-interactive AND proof."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_two_schnorr_proofs(self):
        """Test AND of two Schnorr proofs."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2

        # Create statements with secrets for proving
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        self.assertIsNotNone(proof)
        self.assertIsNotNone(proof.sub_proofs)
        self.assertIsNotNone(proof.shared_challenge)
        self.assertEqual(len(proof.sub_proofs), 2)

        # Create public statements for verification
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
        ]
        result = ANDProof.verify_non_interactive(self.group, statements_public, proof)
        self.assertTrue(result)

    def test_three_schnorr_proofs(self):
        """Test AND of three Schnorr proofs."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        x3 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2
        h3 = g ** x3

        # Create statements with secrets for proving
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h3, 'x': x3}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.sub_proofs), 3)

        # Create public statements for verification
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h3}},
        ]
        result = ANDProof.verify_non_interactive(self.group, statements_public, proof)
        self.assertTrue(result)

    def test_mixed_proof_types(self):
        """Test AND of Schnorr + DLEQ proofs."""
        g = self.group.random(G1)
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x = self.group.random(ZR)
        y = self.group.random(ZR)
        h = g ** x
        h1 = g1 ** y
        h2 = g2 ** y

        # Create statements: Schnorr proof AND DLEQ proof
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h, 'x': x}},
            {'type': 'dleq', 'params': {'g1': g1, 'h1': h1, 'g2': g2, 'h2': h2, 'x': y}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.sub_proofs), 2)
        self.assertEqual(proof.sub_proofs[0]['type'], 'schnorr')
        self.assertEqual(proof.sub_proofs[1]['type'], 'dleq')

        # Create public statements for verification
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h}},
            {'type': 'dleq', 'params': {'g1': g1, 'h1': h1, 'g2': g2, 'h2': h2}},
        ]
        result = ANDProof.verify_non_interactive(self.group, statements_public, proof)
        self.assertTrue(result)

    def test_wrong_secret_fails(self):
        """Test that wrong secret in one proof fails entire AND."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        wrong_x2 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2

        # Create statements with WRONG secret for second proof
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': wrong_x2}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        # Create public statements for verification
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
        ]
        result = ANDProof.verify_non_interactive(self.group, statements_public, proof)
        self.assertFalse(result)

    def test_tampered_proof_fails(self):
        """Test that tampered proof fails verification."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2

        # Create valid statements
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        # Tamper with the shared challenge
        tampered_proof = ANDProofData(
            sub_proofs=proof.sub_proofs,
            shared_challenge=proof.shared_challenge + self.group.random(ZR),
            proof_type=proof.proof_type
        )

        # Create public statements for verification
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
        ]
        result = ANDProof.verify_non_interactive(
            self.group, statements_public, tampered_proof
        )
        self.assertFalse(result)

    def test_empty_statements_fails(self):
        """Test that empty statement list should fail."""
        with self.assertRaises(ValueError):
            ANDProof.prove_non_interactive(self.group, [])


class TestANDProofSerialization(unittest.TestCase):
    """Tests for AND proof serialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_serialization_roundtrip(self):
        """Test serialize and deserialize proof."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2

        # Create statements and proof
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        # Serialize
        serialized = ANDProof.serialize_proof(proof, self.group)
        self.assertIsNotNone(serialized)
        self.assertIsInstance(serialized, bytes)

        # Deserialize
        deserialized = ANDProof.deserialize_proof(serialized, self.group)
        self.assertIsNotNone(deserialized)
        self.assertIsInstance(deserialized, ANDProofData)
        self.assertEqual(len(deserialized.sub_proofs), len(proof.sub_proofs))
        self.assertEqual(deserialized.proof_type, proof.proof_type)

    def test_serialized_proof_verifies(self):
        """Test that deserialized proof still verifies."""
        g = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h1 = g ** x1
        h2 = g ** x2

        # Create statements and proof
        statements = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': x2}},
        ]
        proof = ANDProof.prove_non_interactive(self.group, statements)

        # Serialize and deserialize
        serialized = ANDProof.serialize_proof(proof, self.group)
        deserialized = ANDProof.deserialize_proof(serialized, self.group)

        # Verify the deserialized proof
        statements_public = [
            {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
            {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
        ]
        result = ANDProof.verify_non_interactive(
            self.group, statements_public, deserialized
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

