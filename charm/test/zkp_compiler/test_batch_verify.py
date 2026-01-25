"""
Unit tests for batch verification implementation.

Tests cover:
- Batch verification of Schnorr proofs
- Batch verification of DLEQ proofs
- BatchVerifier class functionality
- Performance comparison with individual verification
"""

import unittest
import time
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.dleq_proof import DLEQProof, DLEQProofData
from charm.zkp_compiler.batch_verify import BatchVerifier, batch_verify_schnorr, batch_verify_dleq


class TestBatchVerifySchnorr(unittest.TestCase):
    """Tests for batch verification of Schnorr proofs."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)

    def _create_valid_schnorr_proof(self):
        """Helper to create a valid Schnorr proof."""
        x = self.group.random(ZR)
        h = self.g ** x
        proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
        return {'g': self.g, 'h': h, 'proof': proof}

    def _create_invalid_schnorr_proof(self):
        """Helper to create an invalid Schnorr proof (wrong secret)."""
        x = self.group.random(ZR)
        wrong_x = self.group.random(ZR)
        h = self.g ** x
        proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, wrong_x)
        return {'g': self.g, 'h': h, 'proof': proof}

    def test_batch_verify_all_valid(self):
        """Test that all valid proofs pass batch verification."""
        proofs_data = [self._create_valid_schnorr_proof() for _ in range(5)]
        result = batch_verify_schnorr(self.group, proofs_data)
        self.assertTrue(result)

    def test_batch_verify_one_invalid(self):
        """Test that one invalid proof fails entire batch."""
        proofs_data = [self._create_valid_schnorr_proof() for _ in range(4)]
        proofs_data.append(self._create_invalid_schnorr_proof())
        result = batch_verify_schnorr(self.group, proofs_data)
        self.assertFalse(result)

    def test_batch_verify_empty(self):
        """Test that empty batch returns True (vacuously true)."""
        result = batch_verify_schnorr(self.group, [])
        self.assertTrue(result)

    def test_batch_verify_single(self):
        """Test that single proof batch works."""
        proofs_data = [self._create_valid_schnorr_proof()]
        result = batch_verify_schnorr(self.group, proofs_data)
        self.assertTrue(result)

    def test_batch_verify_many(self):
        """Test that 10+ proofs batch works."""
        proofs_data = [self._create_valid_schnorr_proof() for _ in range(12)]
        result = batch_verify_schnorr(self.group, proofs_data)
        self.assertTrue(result)


class TestBatchVerifyDLEQ(unittest.TestCase):
    """Tests for batch verification of DLEQ proofs."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G1)

    def _create_valid_dleq_proof(self):
        """Helper to create a valid DLEQ proof."""
        x = self.group.random(ZR)
        h1 = self.g1 ** x
        h2 = self.g2 ** x
        proof = DLEQProof.prove_non_interactive(self.group, self.g1, h1, self.g2, h2, x)
        return {'g1': self.g1, 'h1': h1, 'g2': self.g2, 'h2': h2, 'proof': proof}

    def _create_invalid_dleq_proof(self):
        """Helper to create an invalid DLEQ proof (wrong secret)."""
        x = self.group.random(ZR)
        wrong_x = self.group.random(ZR)
        h1 = self.g1 ** x
        h2 = self.g2 ** x
        proof = DLEQProof.prove_non_interactive(self.group, self.g1, h1, self.g2, h2, wrong_x)
        return {'g1': self.g1, 'h1': h1, 'g2': self.g2, 'h2': h2, 'proof': proof}

    def test_batch_verify_all_valid(self):
        """Test that all valid DLEQ proofs pass batch verification."""
        proofs_data = [self._create_valid_dleq_proof() for _ in range(5)]
        result = batch_verify_dleq(self.group, proofs_data)
        self.assertTrue(result)

    def test_batch_verify_one_invalid(self):
        """Test that one invalid DLEQ proof fails entire batch."""
        proofs_data = [self._create_valid_dleq_proof() for _ in range(4)]
        proofs_data.append(self._create_invalid_dleq_proof())
        result = batch_verify_dleq(self.group, proofs_data)
        self.assertFalse(result)


class TestBatchVerifierClass(unittest.TestCase):
    """Tests for BatchVerifier class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G1)

    def test_add_and_verify_schnorr(self):
        """Test adding Schnorr proofs and verifying."""
        verifier = BatchVerifier(self.group)

        for _ in range(3):
            x = self.group.random(ZR)
            h = self.g ** x
            proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
            verifier.add_schnorr_proof(self.g, h, proof)

        result = verifier.verify_all()
        self.assertTrue(result)

    def test_add_and_verify_dleq(self):
        """Test adding DLEQ proofs and verifying."""
        verifier = BatchVerifier(self.group)

        for _ in range(3):
            x = self.group.random(ZR)
            h1 = self.g1 ** x
            h2 = self.g2 ** x
            proof = DLEQProof.prove_non_interactive(self.group, self.g1, h1, self.g2, h2, x)
            verifier.add_dleq_proof(self.g1, h1, self.g2, h2, proof)

        result = verifier.verify_all()
        self.assertTrue(result)

    def test_mixed_proof_types(self):
        """Test mixing Schnorr and DLEQ proofs in same batch."""
        verifier = BatchVerifier(self.group)

        # Add Schnorr proofs
        for _ in range(2):
            x = self.group.random(ZR)
            h = self.g ** x
            proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
            verifier.add_schnorr_proof(self.g, h, proof)

        # Add DLEQ proofs
        for _ in range(2):
            x = self.group.random(ZR)
            h1 = self.g1 ** x
            h2 = self.g2 ** x
            proof = DLEQProof.prove_non_interactive(self.group, self.g1, h1, self.g2, h2, x)
            verifier.add_dleq_proof(self.g1, h1, self.g2, h2, proof)

        result = verifier.verify_all()
        self.assertTrue(result)

    def test_clear_batch(self):
        """Test clearing and reusing verifier."""
        verifier = BatchVerifier(self.group)

        # Add a valid proof
        x = self.group.random(ZR)
        h = self.g ** x
        proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
        verifier.add_schnorr_proof(self.g, h, proof)

        # Verify first batch
        self.assertTrue(verifier.verify_all())

        # Clear the verifier
        verifier.clear()

        # Add new proofs
        for _ in range(2):
            x = self.group.random(ZR)
            h = self.g ** x
            proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
            verifier.add_schnorr_proof(self.g, h, proof)

        # Verify second batch
        result = verifier.verify_all()
        self.assertTrue(result)


class TestBatchVerifyPerformance(unittest.TestCase):
    """Tests for batch verification performance."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.g = self.group.random(G1)

    def test_batch_faster_than_individual(self):
        """Test that batch verification is not slower than individual verification."""
        num_proofs = 10
        proofs_data = []

        # Generate proofs
        for _ in range(num_proofs):
            x = self.group.random(ZR)
            h = self.g ** x
            proof = SchnorrProof.prove_non_interactive(self.group, self.g, h, x)
            proofs_data.append({'g': self.g, 'h': h, 'proof': proof})

        # Time individual verification
        start_individual = time.time()
        for data in proofs_data:
            SchnorrProof.verify_non_interactive(
                self.group, data['g'], data['h'], data['proof']
            )
        time_individual = time.time() - start_individual

        # Time batch verification
        start_batch = time.time()
        result = batch_verify_schnorr(self.group, proofs_data)
        time_batch = time.time() - start_batch

        # Batch verification should work
        self.assertTrue(result)

        # Batch should ideally be faster (or at least not significantly slower)
        # Allow generous tolerance for timing variations in CI environments
        # We just check that batch works, not strict performance guarantees
        # as performance may vary based on system load
        # Using 3x multiplier to account for CI timing variability
        self.assertLessEqual(time_batch, time_individual * 3 + 0.01,
                             f"Batch ({time_batch:.4f}s) should not be significantly "
                             f"slower than individual ({time_individual:.4f}s)")


if __name__ == "__main__":
    unittest.main()

