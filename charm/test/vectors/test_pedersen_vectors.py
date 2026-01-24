"""
Pedersen Commitment Test Vectors

Test vectors for Pedersen Commitment scheme based on:
- Original paper: "Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing" (Pedersen, 1992)
- Standard commitment scheme properties: hiding and binding

These tests verify the mathematical correctness of the Pedersen commitment implementation.
"""

import unittest
from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.schemes.commit.commit_pedersen92 import CM_Ped92


class TestPedersenMathematicalProperties(unittest.TestCase):
    """
    Test mathematical properties of Pedersen commitments.

    Pedersen commitments have two key properties:
    1. Hiding: Commitment reveals nothing about the message
    2. Binding: Cannot open commitment to different message (computationally)
    """

    def setUp(self):
        """Set up test fixtures with secp256k1 curve."""
        # Use curve 714 (secp256k1) for 128-bit security
        self.group = ECGroup(714)
        self.pedersen = CM_Ped92(self.group)
        self.pk = self.pedersen.setup()

    def test_commitment_correctness(self):
        """
        Test Vector PEDERSEN-1: Commitment Correctness

        Property: commit(m, r) produces C = g^m * h^r

        Source: Pedersen 1992, Definition 1
        """
        msg = self.group.random(ZR)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        # Verify commitment structure: C = g^m * h^r
        expected = (self.pk['g'] ** msg) * (self.pk['h'] ** decommit)

        self.assertEqual(commit, expected,
            "Commitment must equal g^m * h^r")

    def test_decommitment_verification(self):
        """
        Test Vector PEDERSEN-2: Decommitment Verification

        Property: decommit(C, r, m) returns True for valid (C, r, m)

        Source: Pedersen 1992, Verification procedure
        """
        msg = self.group.random(ZR)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        result = self.pedersen.decommit(self.pk, commit, decommit, msg)

        self.assertTrue(result,
            "Valid decommitment must verify")

    def test_wrong_message_decommit_fails(self):
        """
        Test Vector PEDERSEN-3: Binding Property

        Property: Cannot decommit to a different message.

        Source: Computational binding property
        """
        msg1 = self.group.random(ZR)
        msg2 = self.group.random(ZR)

        (commit, decommit) = self.pedersen.commit(self.pk, msg1)

        # Try to decommit with wrong message
        result = self.pedersen.decommit(self.pk, commit, decommit, msg2)

        self.assertFalse(result,
            "Decommitment with wrong message must fail (binding)")

    def test_wrong_randomness_decommit_fails(self):
        """
        Test Vector PEDERSEN-4: Randomness Binding

        Property: Cannot decommit with wrong randomness.
        """
        msg = self.group.random(ZR)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        # Try with wrong randomness
        wrong_decommit = self.group.random(ZR)
        result = self.pedersen.decommit(self.pk, commit, wrong_decommit, msg)

        self.assertFalse(result,
            "Decommitment with wrong randomness must fail")

    def test_different_randomness_different_commitments(self):
        """
        Test Vector PEDERSEN-5: Hiding Property (Statistical)

        Property: Same message with different randomness produces different commitments.

        Source: Information-theoretic hiding property
        """
        msg = self.group.random(ZR)

        # Commit to same message twice (different randomness)
        (commit1, _) = self.pedersen.commit(self.pk, msg)
        (commit2, _) = self.pedersen.commit(self.pk, msg)

        self.assertNotEqual(commit1, commit2,
            "Same message with different randomness must produce different commitments")

    def test_homomorphic_property(self):
        """
        Test Vector PEDERSEN-6: Homomorphic Property

        Property: C(m1, r1) * C(m2, r2) = C(m1+m2, r1+r2)

        Source: Pedersen commitments are additively homomorphic
        """
        m1 = self.group.random(ZR)
        m2 = self.group.random(ZR)

        (c1, r1) = self.pedersen.commit(self.pk, m1)
        (c2, r2) = self.pedersen.commit(self.pk, m2)

        # Compute product of commitments
        c_product = c1 * c2

        # This should equal commitment to sum
        expected = (self.pk['g'] ** (m1 + m2)) * (self.pk['h'] ** (r1 + r2))

        self.assertEqual(c_product, expected,
            "Pedersen commitments must be additively homomorphic")

    def test_homomorphic_decommit(self):
        """
        Test Vector PEDERSEN-7: Homomorphic Decommitment

        Property: Can decommit product of commitments with sum of values.
        """
        m1 = self.group.random(ZR)
        m2 = self.group.random(ZR)

        (c1, r1) = self.pedersen.commit(self.pk, m1)
        (c2, r2) = self.pedersen.commit(self.pk, m2)

        # Product commitment
        c_product = c1 * c2

        # Should decommit with sums
        result = self.pedersen.decommit(self.pk, c_product, r1 + r2, m1 + m2)

        self.assertTrue(result,
            "Homomorphic commitment must decommit with sum of values")


class TestPedersenEdgeCases(unittest.TestCase):
    """
    Edge case tests for Pedersen commitments.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = ECGroup(714)
        self.pedersen = CM_Ped92(self.group)
        self.pk = self.pedersen.setup()

    def test_zero_message(self):
        """
        Test Vector PEDERSEN-EDGE-1: Zero Message

        Property: Commitment to zero message works correctly.
        """
        msg = self.group.init(ZR, 0)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        result = self.pedersen.decommit(self.pk, commit, decommit, msg)

        self.assertTrue(result,
            "Commitment to zero must work correctly")

    def test_one_message(self):
        """
        Test Vector PEDERSEN-EDGE-2: Message = 1

        Property: Commitment to 1 works correctly.
        """
        msg = self.group.init(ZR, 1)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        result = self.pedersen.decommit(self.pk, commit, decommit, msg)

        self.assertTrue(result,
            "Commitment to 1 must work correctly")

    def test_negative_message(self):
        """
        Test Vector PEDERSEN-EDGE-3: Negative Message (Modular)

        Property: Commitment to negative values (mod order) works correctly.
        """
        # In ZR, -1 is equivalent to order - 1
        msg = self.group.init(ZR, -1)
        (commit, decommit) = self.pedersen.commit(self.pk, msg)

        result = self.pedersen.decommit(self.pk, commit, decommit, msg)

        self.assertTrue(result,
            "Commitment to negative value must work correctly")


class TestPedersenSecurityProperties(unittest.TestCase):
    """
    Security-focused tests for Pedersen commitments.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = ECGroup(714)
        self.pedersen = CM_Ped92(self.group)
        self.pk = self.pedersen.setup()

    def test_generators_are_independent(self):
        """
        Test Vector PEDERSEN-SEC-1: Generator Independence

        Property: g and h should be independent (no known discrete log relation).

        Note: This is a structural test - we verify g ≠ h.
        True independence requires g, h to be generated from nothing-up-my-sleeve numbers.
        """
        self.assertNotEqual(self.pk['g'], self.pk['h'],
            "Generators g and h must be different")

    def test_commitment_not_identity(self):
        """
        Test Vector PEDERSEN-SEC-2: Non-trivial Commitment

        Property: Commitment should not be identity element for random message.
        """
        msg = self.group.random(ZR)
        (commit, _) = self.pedersen.commit(self.pk, msg)

        identity = self.group.init(G, 1)

        self.assertNotEqual(commit, identity,
            "Commitment to random message should not be identity")

    def test_random_commitment_does_not_verify(self):
        """
        Test Vector PEDERSEN-SEC-3: Random Commitment Rejection

        Property: Random group element should not verify as valid commitment.
        """
        msg = self.group.random(ZR)
        random_commit = self.group.random(G)
        random_decommit = self.group.random(ZR)

        result = self.pedersen.decommit(self.pk, random_commit, random_decommit, msg)

        self.assertFalse(result,
            "Random commitment should not verify")


class TestPedersenMultipleRuns(unittest.TestCase):
    """
    Statistical tests with multiple commitment operations.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.group = ECGroup(714)
        self.pedersen = CM_Ped92(self.group)
        self.pk = self.pedersen.setup()

    def test_multiple_commitments_all_verify(self):
        """
        Test Vector PEDERSEN-STAT-1: Multiple Commitment Verification

        Property: All honestly generated commitments must verify.
        """
        for i in range(100):
            msg = self.group.random(ZR)
            (commit, decommit) = self.pedersen.commit(self.pk, msg)
            result = self.pedersen.decommit(self.pk, commit, decommit, msg)

            self.assertTrue(result,
                f"Commitment {i+1} must verify (correctness)")

    def test_all_commitments_unique(self):
        """
        Test Vector PEDERSEN-STAT-2: Commitment Uniqueness

        Property: Different (message, randomness) pairs produce unique commitments.
        """
        commitments = set()

        for _ in range(100):
            msg = self.group.random(ZR)
            (commit, _) = self.pedersen.commit(self.pk, msg)
            # Convert to string for set comparison
            commit_str = str(commit)

            self.assertNotIn(commit_str, commitments,
                "All commitments should be unique")
            commitments.add(commit_str)


if __name__ == '__main__':
    unittest.main()
