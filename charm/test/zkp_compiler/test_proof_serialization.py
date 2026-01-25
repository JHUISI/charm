"""
Unit tests for ZK proof serialization.

Tests cover:
- Serializing proofs to bytes
- Deserializing bytes back to proofs
- Roundtrip preservation
- Error handling for invalid data
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof


class TestProofSerialization(unittest.TestCase):
    """Tests for proof serialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.x = self.group.random(ZR)
        self.h = self.g ** self.x
    
    def test_serialize_deserialize_roundtrip(self):
        """Test that proof survives serialization roundtrip."""
        # Generate proof
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        # Serialize
        data = SchnorrProof.serialize_proof(proof, self.group)
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 0)
        
        # Deserialize
        recovered = SchnorrProof.deserialize_proof(data, self.group)
        self.assertIsNotNone(recovered)
        
        # Verify recovered proof still works
        result = SchnorrProof.verify_non_interactive(
            self.group, self.g, self.h, recovered
        )
        self.assertTrue(result)
    
    def test_serialized_proof_is_bytes(self):
        """Test that serialization produces bytes."""
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        data = SchnorrProof.serialize_proof(proof, self.group)
        self.assertIsInstance(data, bytes)
    
    def test_different_proofs_different_serialization(self):
        """Test that different proofs produce different serialized data."""
        proof1 = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        proof2 = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        data1 = SchnorrProof.serialize_proof(proof1, self.group)
        data2 = SchnorrProof.serialize_proof(proof2, self.group)
        
        # Different proofs should have different serializations
        # (due to different random commitments)
        self.assertNotEqual(data1, data2)
    
    def test_deserialize_preserves_proof_type(self):
        """Test that proof_type is preserved through serialization."""
        proof = SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self.x
        )
        
        data = SchnorrProof.serialize_proof(proof, self.group)
        recovered = SchnorrProof.deserialize_proof(data, self.group)
        
        self.assertEqual(recovered.proof_type, proof.proof_type)
    
    def test_serialization_with_different_groups(self):
        """Test serialization works with different pairing groups."""
        for curve in ['BN254', 'MNT224']:
            with self.subTest(curve=curve):
                group = PairingGroup(curve)
                g = group.random(G1)
                x = group.random(ZR)
                h = g ** x
                
                proof = SchnorrProof.prove_non_interactive(group, g, h, x)
                data = SchnorrProof.serialize_proof(proof, group)
                recovered = SchnorrProof.deserialize_proof(data, group)
                
                result = SchnorrProof.verify_non_interactive(
                    group, g, h, recovered
                )
                self.assertTrue(result)


class TestProofSerializationErrors(unittest.TestCase):
    """Tests for serialization error handling."""
    
    def setUp(self):
        self.group = PairingGroup('BN254')
    
    def test_deserialize_invalid_data_fails(self):
        """Test that invalid data raises an exception."""
        with self.assertRaises(Exception):
            SchnorrProof.deserialize_proof(b"not valid data", self.group)
    
    def test_deserialize_empty_data_fails(self):
        """Test that empty data raises an exception."""
        with self.assertRaises(Exception):
            SchnorrProof.deserialize_proof(b"", self.group)


if __name__ == "__main__":
    unittest.main()

