"""
Unit tests for Range Proof implementation.

Tests cover:
- Basic range proofs with boundary values
- Different bit sizes for ranges
- Pedersen commitment creation and properties
- Proof serialization and deserialization
"""

import unittest
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.range_proof import RangeProof, RangeProofData


class TestRangeProofBasic(unittest.TestCase):
    """Tests for basic range proof functionality with 8-bit range."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.h = self.group.random(G1)
        self.num_bits = 8  # Range [0, 256)

    def test_value_zero(self):
        """Prove 0 is in range [0, 2^8)."""
        value = 0
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_value_one(self):
        """Prove 1 is in range [0, 2^8)."""
        value = 1
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_value_max(self):
        """Prove 255 (max value) is in range [0, 2^8)."""
        value = 255  # 2^8 - 1
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_value_middle(self):
        """Prove 42 is in range [0, 2^8)."""
        value = 42
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_value_out_of_range_fails(self):
        """Value >= 2^n should fail."""
        value = 256  # 2^8, out of range
        randomness = self.group.random(ZR)
        with self.assertRaises(ValueError):
            RangeProof.prove(
                self.group, self.g, self.h, value, randomness, self.num_bits
            )


class TestRangeProofDifferentBitSizes(unittest.TestCase):
    """Tests for range proofs with different bit sizes."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.h = self.group.random(G1)

    def test_4_bit_range(self):
        """Test range [0, 16) with 4-bit proof."""
        num_bits = 4
        value = 15  # Max value in range
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, num_bits
        )
        self.assertEqual(proof.num_bits, 4)
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_8_bit_range(self):
        """Test range [0, 256) with 8-bit proof."""
        num_bits = 8
        value = 200
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, num_bits
        )
        self.assertEqual(proof.num_bits, 8)
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)

    def test_16_bit_range(self):
        """Test range [0, 65536) with 16-bit proof."""
        num_bits = 16
        value = 50000
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, num_bits
        )
        self.assertEqual(proof.num_bits, 16)
        result = RangeProof.verify(self.group, self.g, self.h, commitment, proof)
        self.assertTrue(result)


class TestRangeProofPedersenCommitment(unittest.TestCase):
    """Tests for Pedersen commitment creation and properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.h = self.group.random(G1)

    def test_create_commitment(self):
        """Test commitment creation helper."""
        value = 42
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        # Verify commitment is C = g^v * h^r
        v = self.group.init(ZR, value)
        expected = (self.g ** v) * (self.h ** randomness)
        self.assertEqual(commitment, expected)

    def test_commitment_hiding(self):
        """Same value, different randomness = different commitment."""
        value = 42
        r1 = self.group.random(ZR)
        r2 = self.group.random(ZR)
        c1 = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, r1
        )
        c2 = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, r2
        )
        # Different randomness should produce different commitments
        self.assertNotEqual(c1, c2)

    def test_commitment_binding(self):
        """Commitment is binding - different values produce different commitments."""
        r = self.group.random(ZR)
        c1 = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, 42, r
        )
        c2 = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, 43, r
        )
        # Different values with same randomness should produce different commitments
        self.assertNotEqual(c1, c2)


class TestRangeProofSerialization(unittest.TestCase):
    """Tests for proof serialization and deserialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.h = self.group.random(G1)
        self.num_bits = 4  # Use small bit size for fast tests

    def test_serialization_roundtrip(self):
        """Serialize and deserialize proof."""
        value = 10
        randomness = self.group.random(ZR)
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        # Serialize
        serialized = RangeProof.serialize_proof(proof, self.group)
        self.assertIsInstance(serialized, bytes)
        # Deserialize
        deserialized = RangeProof.deserialize_proof(serialized, self.group)
        # Check structure is preserved
        self.assertEqual(deserialized.num_bits, proof.num_bits)
        self.assertEqual(deserialized.proof_type, proof.proof_type)
        self.assertEqual(len(deserialized.bit_commitments), len(proof.bit_commitments))
        self.assertEqual(len(deserialized.bit_proofs), len(proof.bit_proofs))

    def test_serialized_proof_verifies(self):
        """Deserialized proof still verifies."""
        value = 12
        randomness = self.group.random(ZR)
        commitment = RangeProof.create_pedersen_commitment(
            self.group, self.g, self.h, value, randomness
        )
        proof = RangeProof.prove(
            self.group, self.g, self.h, value, randomness, self.num_bits
        )
        # Serialize and deserialize
        serialized = RangeProof.serialize_proof(proof, self.group)
        deserialized = RangeProof.deserialize_proof(serialized, self.group)
        # Verify deserialized proof
        result = RangeProof.verify(
            self.group, self.g, self.h, commitment, deserialized
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

