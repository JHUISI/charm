"""
Unit tests for Representation ZK proof implementation.

Tests cover:
- Interactive proof protocol with multiple generators
- Non-interactive (Fiat-Shamir) proof
- Serialization/deserialization
- Different pairing groups
- Edge cases and error handling
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.representation_proof import RepresentationProof, RepresentationProofData


class TestRepresentationProofInteractive(unittest.TestCase):
    """Tests for interactive Representation protocol."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_prove_and_verify_interactive_two_generators(self):
        """Test complete interactive proof cycle with two generators (Pedersen commitment style)."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        # Create prover and verifier
        prover = RepresentationProof.Prover([x1, x2], self.group)
        verifier = RepresentationProof.Verifier(self.group)

        # Step 1: Prover creates commitment
        commitment = prover.create_commitment([g1, g2])
        self.assertIsNotNone(commitment)

        # Step 2: Verifier creates challenge
        challenge = verifier.create_challenge()
        self.assertIsNotNone(challenge)

        # Step 3: Prover creates response
        responses = prover.create_response(challenge)
        self.assertIsNotNone(responses)
        self.assertEqual(len(responses), 2)

        # Step 4: Verifier verifies
        result = verifier.verify([g1, g2], h, commitment, responses)
        self.assertTrue(result)

    def test_prove_and_verify_interactive_three_generators(self):
        """Test complete interactive proof cycle with three generators."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        g3 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        x3 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2) * (g3 ** x3)

        prover = RepresentationProof.Prover([x1, x2, x3], self.group)
        verifier = RepresentationProof.Verifier(self.group)

        commitment = prover.create_commitment([g1, g2, g3])
        challenge = verifier.create_challenge()
        responses = prover.create_response(challenge)

        self.assertEqual(len(responses), 3)
        result = verifier.verify([g1, g2, g3], h, commitment, responses)
        self.assertTrue(result)

    def test_invalid_proof_fails_interactive(self):
        """Test that wrong witnesses fail verification."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        # Use wrong witnesses
        wrong_x1 = self.group.random(ZR)
        wrong_x2 = self.group.random(ZR)
        prover = RepresentationProof.Prover([wrong_x1, wrong_x2], self.group)
        verifier = RepresentationProof.Verifier(self.group)

        commitment = prover.create_commitment([g1, g2])
        challenge = verifier.create_challenge()
        responses = prover.create_response(challenge)

        # Should fail because wrong witnesses
        result = verifier.verify([g1, g2], h, commitment, responses)
        self.assertFalse(result)

    def test_prover_commitment_before_response(self):
        """Test that prover must create commitment before response."""
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        prover = RepresentationProof.Prover([x1, x2], self.group)

        # Try to create response without commitment
        with self.assertRaises(ValueError):
            prover.create_response(self.group.random(ZR))


class TestRepresentationProofNonInteractive(unittest.TestCase):
    """Tests for non-interactive (Fiat-Shamir) Representation proof."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_non_interactive_proof_valid_two_generators(self):
        """Test Fiat-Shamir transformed proof with two generators."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [x1, x2]
        )

        self.assertIsNotNone(proof)
        self.assertIsNotNone(proof.commitment)
        self.assertIsNotNone(proof.challenge)
        self.assertIsNotNone(proof.responses)
        self.assertEqual(len(proof.responses), 2)

        result = RepresentationProof.verify_non_interactive(
            self.group, [g1, g2], h, proof
        )
        self.assertTrue(result)

    def test_non_interactive_proof_valid_three_generators(self):
        """Test Fiat-Shamir transformed proof with three generators."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        g3 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        x3 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2) * (g3 ** x3)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2, g3], h, [x1, x2, x3]
        )

        self.assertEqual(len(proof.responses), 3)
        result = RepresentationProof.verify_non_interactive(
            self.group, [g1, g2, g3], h, proof
        )
        self.assertTrue(result)

    def test_non_interactive_wrong_witness_fails(self):
        """Test that wrong witness fails non-interactive verification."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        # Create proof with wrong witnesses
        wrong_x1 = self.group.random(ZR)
        wrong_x2 = self.group.random(ZR)
        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [wrong_x1, wrong_x2]
        )

        result = RepresentationProof.verify_non_interactive(
            self.group, [g1, g2], h, proof
        )
        self.assertFalse(result)

    def test_non_interactive_tampered_proof_fails(self):
        """Test that tampered proof fails verification."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [x1, x2]
        )

        # Tamper with the first response
        tampered_responses = list(proof.responses)
        tampered_responses[0] = tampered_responses[0] + self.group.random(ZR)
        tampered = RepresentationProofData(
            commitment=proof.commitment,
            challenge=proof.challenge,
            responses=tampered_responses,
            proof_type=proof.proof_type
        )

        result = RepresentationProof.verify_non_interactive(
            self.group, [g1, g2], h, tampered
        )
        self.assertFalse(result)

    def test_proof_deterministic_verification(self):
        """Test that same proof verifies consistently."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [x1, x2]
        )

        # Verify multiple times
        for _ in range(5):
            result = RepresentationProof.verify_non_interactive(
                self.group, [g1, g2], h, proof
            )
            self.assertTrue(result)

    def test_single_generator_equivalent_to_schnorr(self):
        """Test that with 1 generator, representation proof works like Schnorr."""
        g = self.group.random(G1)
        x = self.group.random(ZR)
        h = g ** x

        # Create representation proof with single generator
        proof = RepresentationProof.prove_non_interactive(
            self.group, [g], h, [x]
        )

        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.responses), 1)

        result = RepresentationProof.verify_non_interactive(
            self.group, [g], h, proof
        )
        self.assertTrue(result)


class TestRepresentationProofSerialization(unittest.TestCase):
    """Tests for proof serialization and deserialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_serialization_roundtrip(self):
        """Test that proof can be serialized and deserialized."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [x1, x2]
        )

        # Serialize and deserialize
        serialized = RepresentationProof.serialize_proof(proof, self.group)
        self.assertIsInstance(serialized, bytes)

        deserialized = RepresentationProof.deserialize_proof(serialized, self.group)
        self.assertEqual(deserialized.commitment, proof.commitment)
        self.assertEqual(deserialized.challenge, proof.challenge)
        self.assertEqual(len(deserialized.responses), len(proof.responses))
        for i in range(len(proof.responses)):
            self.assertEqual(deserialized.responses[i], proof.responses[i])

    def test_serialized_proof_verifies(self):
        """Test that deserialized proof still verifies."""
        g1 = self.group.random(G1)
        g2 = self.group.random(G1)
        x1 = self.group.random(ZR)
        x2 = self.group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            self.group, [g1, g2], h, [x1, x2]
        )

        # Serialize, deserialize, then verify
        serialized = RepresentationProof.serialize_proof(proof, self.group)
        deserialized = RepresentationProof.deserialize_proof(serialized, self.group)

        result = RepresentationProof.verify_non_interactive(
            self.group, [g1, g2], h, deserialized
        )
        self.assertTrue(result)


class TestRepresentationProofWithDifferentGroups(unittest.TestCase):
    """Test Representation proofs with different pairing groups."""

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
        x1 = group.random(ZR)
        x2 = group.random(ZR)
        h = (g1 ** x1) * (g2 ** x2)

        proof = RepresentationProof.prove_non_interactive(
            group, [g1, g2], h, [x1, x2]
        )
        result = RepresentationProof.verify_non_interactive(
            group, [g1, g2], h, proof
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()