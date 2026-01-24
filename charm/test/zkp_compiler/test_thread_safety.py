"""
Thread safety tests for ZKP proof implementations.

Tests verify that:
1. Non-interactive proof methods are thread-safe
2. Thread-safe wrappers work correctly for interactive proofs
3. Concurrent proof generation/verification works correctly
"""

import unittest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof
from charm.zkp_compiler.dleq_proof import DLEQProof
from charm.zkp_compiler.representation_proof import RepresentationProof
from charm.zkp_compiler.thread_safe import ThreadSafeProver, ThreadSafeVerifier


class TestNonInteractiveThreadSafety(unittest.TestCase):
    """Test that non-interactive proof methods are thread-safe."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
        self.num_threads = 10
        self.proofs_per_thread = 5
    
    def test_schnorr_concurrent_prove_verify(self):
        """Test concurrent Schnorr proof generation and verification."""
        results = []
        errors = []
        
        def prove_and_verify():
            try:
                g = self.group.random(G1)
                x = self.group.random(ZR)
                h = g ** x
                
                for _ in range(self.proofs_per_thread):
                    proof = SchnorrProof.prove_non_interactive(self.group, g, h, x)
                    valid = SchnorrProof.verify_non_interactive(self.group, g, h, proof)
                    results.append(valid)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=prove_and_verify) for _ in range(self.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), self.num_threads * self.proofs_per_thread)
        self.assertTrue(all(results), "All proofs should verify")
    
    def test_dleq_concurrent_prove_verify(self):
        """Test concurrent DLEQ proof generation and verification."""
        results = []
        errors = []
        
        def prove_and_verify():
            try:
                g1 = self.group.random(G1)
                g2 = self.group.random(G1)
                x = self.group.random(ZR)
                h1 = g1 ** x
                h2 = g2 ** x
                
                for _ in range(self.proofs_per_thread):
                    proof = DLEQProof.prove_non_interactive(self.group, g1, h1, g2, h2, x)
                    valid = DLEQProof.verify_non_interactive(self.group, g1, h1, g2, h2, proof)
                    results.append(valid)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=prove_and_verify) for _ in range(self.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), self.num_threads * self.proofs_per_thread)
        self.assertTrue(all(results), "All proofs should verify")
    
    def test_representation_concurrent_prove_verify(self):
        """Test concurrent Representation proof generation and verification."""
        results = []
        errors = []
        
        def prove_and_verify():
            try:
                g1 = self.group.random(G1)
                g2 = self.group.random(G1)
                x1 = self.group.random(ZR)
                x2 = self.group.random(ZR)
                h = (g1 ** x1) * (g2 ** x2)
                
                for _ in range(self.proofs_per_thread):
                    proof = RepresentationProof.prove_non_interactive(
                        self.group, [g1, g2], h, [x1, x2]
                    )
                    valid = RepresentationProof.verify_non_interactive(
                        self.group, [g1, g2], h, proof
                    )
                    results.append(valid)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=prove_and_verify) for _ in range(self.num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), self.num_threads * self.proofs_per_thread)
        self.assertTrue(all(results), "All proofs should verify")


class TestThreadSafeWrappers(unittest.TestCase):
    """Test thread-safe wrappers for interactive proofs."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.group = PairingGroup('BN254')
    
    def test_thread_safe_prover_context_manager(self):
        """Test ThreadSafeProver as context manager."""
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x
        
        prover = ThreadSafeProver(SchnorrProof.Prover(x, self.group))
        verifier = SchnorrProof.Verifier(self.group)
        
        with prover:
            commitment = prover.create_commitment(g)
            challenge = verifier.create_challenge()
            response = prover.create_response(challenge)
        
        result = verifier.verify(g, h, commitment, response)
        self.assertTrue(result)
    
    def test_thread_safe_verifier_context_manager(self):
        """Test ThreadSafeVerifier as context manager."""
        x = self.group.random(ZR)
        g = self.group.random(G1)
        h = g ** x
        
        prover = SchnorrProof.Prover(x, self.group)
        verifier = ThreadSafeVerifier(SchnorrProof.Verifier(self.group))
        
        commitment = prover.create_commitment(g)
        
        with verifier:
            challenge = verifier.create_challenge()
            response = prover.create_response(challenge)
            result = verifier.verify(g, h, commitment, response)
        
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

