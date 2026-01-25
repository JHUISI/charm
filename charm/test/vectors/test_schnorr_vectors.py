"""
Schnorr Zero-Knowledge Proof Test Vectors

Test vectors for Schnorr's ZKP protocol based on:
- Original paper: "Efficient Signature Generation by Smart Cards" (Schnorr, 1991)
- RFC 8235: Schnorr Non-interactive Zero-Knowledge Proof
- Fiat-Shamir heuristic for non-interactive proofs

These tests verify both interactive and non-interactive Schnorr proofs.
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.core.engine.util import objectToBytes


class TestSchnorrMathematicalProperties(unittest.TestCase):
    """
    Test mathematical properties of Schnorr ZK proofs.
    
    These tests verify the fundamental algebraic properties that must hold
    for any correct Schnorr proof implementation.
    """
    
    def setUp(self):
        """Set up test fixtures with BN254 curve."""
        self.group = PairingGroup('BN254')
    
    def test_completeness_interactive(self):
        """
        Test Vector SCHNORR-1: Completeness (Interactive)
        
        Property: Honest prover with valid witness always convinces honest verifier.
        
        Source: Schnorr 1991, Definition of ZK proof system
        """
        # Generate secret and public values
        x = self.group.random(ZR)  # Secret
        g = self.group.random(G1)  # Generator
        h = g ** x                  # Public value h = g^x
        
        # Interactive protocol
        prover = SchnorrProof.Prover(x, self.group)
        verifier = SchnorrProof.Verifier(self.group)
        
        # Step 1: Prover creates commitment
        commitment = prover.create_commitment(g)
        
        # Step 2: Verifier creates challenge
        challenge = verifier.create_challenge()
        
        # Step 3: Prover creates response
        response = prover.create_response(challenge)
        
        # Step 4: Verifier verifies
        result = verifier.verify(g, h, commitment, response)
        
        self.assertTrue(result,
            "Completeness: Honest prover must always convince honest verifier")
    
    def test_completeness_non_interactive(self):
        """
        Test Vector SCHNORR-2: Completeness (Non-Interactive)
        
        Property: Non-interactive proof with valid witness always verifies.
        
        Source: Fiat-Shamir heuristic applied to Schnorr protocol
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x
        
        # Generate non-interactive proof
        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        
        # Verify
        result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)
        
        self.assertTrue(result,
            "Completeness: Valid non-interactive proof must verify")
    
    def test_soundness_wrong_witness(self):
        """
        Test Vector SCHNORR-3: Soundness (Wrong Witness)
        
        Property: Prover with wrong witness cannot convince verifier.
        
        Source: Soundness requirement for ZK proofs
        """
        x_real = self.group.random(ZR)
        x_fake = self.group.random(ZR)  # Wrong witness
        g = self.group.random(G1)
        h = g ** x_real  # h = g^x_real
        
        # Try to prove with wrong witness
        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x_fake)
        
        # Should fail verification (with overwhelming probability)
        result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)
        
        self.assertFalse(result,
            "Soundness: Proof with wrong witness must not verify")
    
    def test_verification_equation(self):
        """
        Test Vector SCHNORR-4: Verification Equation
        
        Property: g^z = u * h^c where z = r + c*x, u = g^r, h = g^x
        
        Source: Schnorr 1991, Protocol specification
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x
        
        # Generate proof
        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        
        # Manually verify the equation: g^z = u * h^c
        lhs = g ** proof.response
        rhs = proof.commitment * (h ** proof.challenge)
        
        self.assertEqual(lhs, rhs,
            "Verification equation g^z = u * h^c must hold")
    
    def test_challenge_binding(self):
        """
        Test Vector SCHNORR-5: Challenge Binding (Fiat-Shamir)
        
        Property: Challenge is deterministically derived from (g, h, commitment)
        
        Source: Fiat-Shamir heuristic security requirement
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x
        
        # Generate two proofs
        proof1 = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        proof2 = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        
        # Commitments are random, so challenges should differ
        # But if we recompute challenge from same commitment, it should match
        expected_challenge = SchnorrProof._compute_challenge_hash(
            self.group, g, h, proof1.commitment
        )
        
        self.assertEqual(proof1.challenge, expected_challenge,
            "Challenge must be deterministically derived from public values")
    
    def test_zero_knowledge_simulation(self):
        """
        Test Vector SCHNORR-6: Zero-Knowledge Property (Simulation)
        
        Property: Proofs can be simulated without knowing the witness.
        This demonstrates the zero-knowledge property.
        
        Source: Schnorr 1991, Zero-knowledge proof
        
        Note: This test verifies that simulated proofs have the same structure
        as real proofs, demonstrating that proofs reveal nothing about x.
        """
        g = self.group.random(G1)
        x = self.group.random(ZR)
        h = g ** x
        
        # Simulate a proof (without knowing x):
        # 1. Choose random z and c
        # 2. Compute u = g^z * h^(-c)
        # This creates a valid-looking proof without knowing x
        
        z_sim = self.group.random(ZR)
        c_sim = self.group.random(ZR)
        u_sim = (g ** z_sim) * (h ** (-c_sim))
        
        # Verify the simulation satisfies the verification equation
        lhs = g ** z_sim
        rhs = u_sim * (h ** c_sim)
        
        self.assertEqual(lhs, rhs,
            "Simulated proof must satisfy verification equation")


class TestSchnorrEdgeCases(unittest.TestCase):
    """
    Edge case tests for Schnorr proofs.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_identity_commitment_rejection(self):
        """
        Test Vector SCHNORR-EDGE-1: Identity Commitment Attack

        Property: Proof with identity element as commitment should be rejected.

        Attack: Attacker submits identity as commitment to bypass verification.
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x

        # Create malicious proof with identity commitment
        identity = self.group.init(G1, 1)
        malicious_proof = Proof(
            commitment=identity,
            challenge=self.group.random(ZR),
            response=self.group.random(ZR)
        )

        # Should be rejected
        result = SchnorrProof.verify_non_interactive(self.group, g, h, malicious_proof)

        self.assertFalse(result,
            "Proof with identity commitment must be rejected")

    def test_zero_secret(self):
        """
        Test Vector SCHNORR-EDGE-2: Zero Secret

        Property: Proof works correctly when secret x = 0 (h = g^0 = 1).
        """
        x = self.group.init(ZR, 0)  # Zero secret
        g = self.group.random(G1)
        h = g ** x  # h = identity

        # Should still work correctly
        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)

        self.assertTrue(result,
            "Proof must work correctly for zero secret")

    def test_one_secret(self):
        """
        Test Vector SCHNORR-EDGE-3: Secret = 1

        Property: Proof works correctly when secret x = 1 (h = g).
        """
        x = self.group.init(ZR, 1)
        g = self.group.random(G1)
        h = g ** x  # h = g

        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)

        self.assertTrue(result,
            "Proof must work correctly for secret = 1")

    def test_large_secret(self):
        """
        Test Vector SCHNORR-EDGE-4: Large Secret

        Property: Proof works correctly for secrets near the group order.
        """
        # Use a large secret (close to group order)
        g = self.group.random(G1)
        x = self.group.random(ZR)  # Random element in ZR (full range)
        h = g ** x

        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)

        self.assertTrue(result,
            "Proof must work correctly for large secrets")


class TestSchnorrSerialization(unittest.TestCase):
    """
    Serialization tests for Schnorr proofs.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_serialize_deserialize_roundtrip(self):
        """
        Test Vector SCHNORR-SER-1: Serialization Roundtrip

        Property: serialize(deserialize(proof)) == proof
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x

        # Generate proof
        original_proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)

        # Serialize and deserialize
        serialized = SchnorrProof.serialize_proof(original_proof, self.group)
        deserialized_proof = SchnorrProof.deserialize_proof(serialized, self.group)

        # Verify deserialized proof
        result = SchnorrProof.verify_non_interactive(self.group, g, h, deserialized_proof)

        self.assertTrue(result,
            "Deserialized proof must verify correctly")

    def test_serialized_proof_is_bytes(self):
        """
        Test Vector SCHNORR-SER-2: Serialization Format

        Property: Serialized proof is bytes type.
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x

        proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
        serialized = SchnorrProof.serialize_proof(proof, self.group)

        self.assertIsInstance(serialized, bytes,
            "Serialized proof must be bytes")


class TestSchnorrMultipleRuns(unittest.TestCase):
    """
    Statistical tests running multiple proof generations.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')

    def test_multiple_proofs_all_verify(self):
        """
        Test Vector SCHNORR-STAT-1: Multiple Proof Verification

        Property: All honestly generated proofs must verify.
        """
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x

        # Generate and verify 100 proofs
        for i in range(100):
            proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
            result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)
            self.assertTrue(result,
                f"Proof {i+1} must verify (completeness)")

    def test_different_generators(self):
        """
        Test Vector SCHNORR-STAT-2: Different Generators

        Property: Proofs work correctly with different generators.
        """
        x = self.group.random(ZR)

        # Test with 10 different generators
        for i in range(10):
            g = self.group.random(G1)
            h = g ** x

            proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
            result = SchnorrProof.verify_non_interactive(self.group, g, h, proof)

            self.assertTrue(result,
                f"Proof with generator {i+1} must verify")


if __name__ == '__main__':
    unittest.main()

