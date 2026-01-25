"""
Unit tests for Schnorr ZK proof implementation.

Tests cover:
- Interactive proof protocol
- Non-interactive (Fiat-Shamir) proof
- Different pairing groups
- Edge cases and error handling
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof


class TestSchnorrProofInteractive(unittest.TestCase):
    """Tests for interactive Schnorr protocol."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h = self.g ** self.x
    
    def test_prove_and_verify_interactive(self):
        """Test complete interactive proof cycle."""
        # Create prover and verifier
        prover = SchnorrProof.Prover(self.x, self.group)
        verifier = SchnorrProof.Verifier(self.group)
        
        # Step 1: Prover creates commitment
        commitment = prover.create_commitment(self.g)
        self.assertIsNotNone(commitment)
        
        # Step 2: Verifier creates challenge
        challenge = verifier.create_challenge()
        self.assertIsNotNone(challenge)
        
        # Step 3: Prover creates response
        response = prover.create_response(challenge)
        self.assertIsNotNone(response)
        
        # Step 4: Verifier verifies
        result = verifier.verify(self.g, self.h, commitment, response)
        self.assertTrue(result)
    
    def test_invalid_proof_fails_interactive(self):
        """Test that wrong secret fails verification."""
        wrong_x = self.group.random(ZR)
        prover = SchnorrProof.Prover(wrong_x, self.group)
        verifier = SchnorrProof.Verifier(self.group)
        
        commitment = prover.create_commitment(self.g)
        challenge = verifier.create_challenge()
        response = prover.create_response(challenge)
        
        # Should fail because wrong secret
        result = verifier.verify(self.g, self.h, commitment, response)
        self.assertFalse(result)
    
    def test_prover_commitment_before_response(self):
        """Test that prover must create commitment before response."""
        prover = SchnorrProof.Prover(self.x, self.group)
        
        # Try to create response without commitment
        with self.assertRaises(Exception):
            prover.create_response(self.group.random(ZR))


class TestSchnorrProofNonInteractive(unittest.TestCase):
    """Tests for non-interactive (Fiat-Shamir) Schnorr proof."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h = self.g ** self.x
    
    def test_non_interactive_proof_valid(self):
        """Test Fiat-Shamir transformed proof."""
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        self.assertIsNotNone(proof)
        self.assertIsNotNone(proof.commitment)
        self.assertIsNotNone(proof.challenge)
        self.assertIsNotNone(proof.response)
        
        result = SchnorrProof.verify_non_interactive(
            self.group, self.g, self.h, proof
        )
        self.assertTrue(result)
    
    def test_non_interactive_wrong_secret_fails(self):
        """Test that wrong secret fails non-interactive verification."""
        wrong_x = self.group.random(ZR)
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, wrong_x
        )
        
        result = SchnorrProof.verify_non_interactive(
            self.group, self.g, self.h, proof
        )
        self.assertFalse(result)
    
    def test_non_interactive_tampered_proof_fails(self):
        """Test that tampered proof fails verification."""
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        # Tamper with the response
        tampered = Proof(
            commitment=proof.commitment,
            challenge=proof.challenge,
            response=proof.response + self.group.random(ZR),
            proof_type=proof.proof_type
        )
        
        result = SchnorrProof.verify_non_interactive(
            self.group, self.g, self.h, tampered
        )
        self.assertFalse(result)
    
    def test_proof_deterministic_verification(self):
        """Test that same proof verifies consistently."""
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        # Verify multiple times
        for _ in range(5):
            result = SchnorrProof.verify_non_interactive(
                self.group, self.g, self.h, proof
            )
            self.assertTrue(result)


class TestSchnorrProofWithDifferentGroups(unittest.TestCase):
    """Test Schnorr proofs with different pairing groups."""

    def test_with_bn254_group(self):
        """Test with BN254 pairing group."""
        self._test_with_group('BN254')

    def test_with_mnt224_group(self):
        """Test with MNT224 pairing group."""
        self._test_with_group('MNT224')

    def _test_with_group(self, curve_name):
        """Helper to test with a specific group."""
        group = PairingGroup(curve_name)
        g = group.random(G1)
        x = group.random(ZR)
        h = g ** x

        proof = SchnorrProof.prove_non_interactive(group, g, h, x)
        result = SchnorrProof.verify_non_interactive(group, g, h, proof)
        self.assertTrue(result)


class TestSchnorrProofSecurity(unittest.TestCase):
    """Security-focused tests for Schnorr proofs."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h = self.g ** self.x

    def test_invalid_proof_structure_rejected(self):
        """Test that proofs with missing attributes are rejected."""
        # Create a fake proof object without required attributes
        class FakeProof:
            pass

        fake_proof = FakeProof()
        result = SchnorrProof.verify_non_interactive(self.group, self.g, self.h, fake_proof)
        self.assertFalse(result)

    def test_identity_commitment_rejected(self):
        """Test that proofs with identity element commitment are rejected."""
        # Create a valid proof first
        proof = SchnorrProof.prove_non_interactive(self.group, self.g, self.h, self.x)

        # Replace commitment with identity element
        identity = self.group.init(G1, 1)
        tampered_proof = Proof(
            commitment=identity,
            challenge=proof.challenge,
            response=proof.response,
            proof_type='schnorr'
        )

        result = SchnorrProof.verify_non_interactive(self.group, self.g, self.h, tampered_proof)
        self.assertFalse(result)

    def test_challenge_mismatch_rejected(self):
        """Test that proofs with wrong challenge are rejected."""
        proof = SchnorrProof.prove_non_interactive(self.group, self.g, self.h, self.x)

        # Tamper with the challenge
        wrong_challenge = self.group.random(ZR)
        tampered_proof = Proof(
            commitment=proof.commitment,
            challenge=wrong_challenge,
            response=proof.response,
            proof_type='schnorr'
        )

        result = SchnorrProof.verify_non_interactive(self.group, self.g, self.h, tampered_proof)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

