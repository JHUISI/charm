#!/usr/bin/env python
"""
Comprehensive stress test for the ABE policy parser.

This script tests the PolicyParser and MSP classes for expressiveness,
correctness, and robustness. It can be run independently to verify
the policy parser functionality.

Usage:
    python -m charm.test.toolbox.policy_parser_stress_test
    
    # Or with pytest:
    pytest charm/test/toolbox/policy_parser_stress_test.py -v
"""

import sys
import time
import random
import string
import unittest
from typing import List, Tuple, Optional

from charm.toolbox.policytree import PolicyParser
from charm.toolbox.node import OpType, BinNode
from charm.toolbox.msp import MSP
from charm.toolbox.pairinggroup import PairingGroup


class PolicyParserStressTest(unittest.TestCase):
    """Comprehensive stress tests for the ABE policy parser."""
    
    @classmethod
    def setUpClass(cls):
        cls.parser = PolicyParser()
        cls.group = PairingGroup('SS512')
        cls.msp = MSP(cls.group)
    
    # =========================================================================
    # Basic Parsing Tests
    # =========================================================================
    
    def test_single_attribute(self):
        """Test parsing single attributes."""
        # Note: underscore followed by digits is treated as duplicate index
        # e.g., ATTR_123 becomes ATTR with index 123
        test_cases = [
            ('A', 'A'),
            ('attribute', 'ATTRIBUTE'),
            ('role-admin', 'ROLE-ADMIN'),
            ('user.name', 'USER.NAME'),
        ]
        for attr, expected in test_cases:
            tree = self.parser.parse(attr)
            self.assertEqual(tree.getNodeType(), OpType.ATTR)
            self.assertEqual(tree.getAttribute(), expected)

    def test_attribute_with_index(self):
        """Test attributes with numeric index suffix (used for duplicates)."""
        # ATTR_123 is parsed as attribute ATTR with index 123
        tree = self.parser.parse('ATTR_123')
        self.assertEqual(tree.getNodeType(), OpType.ATTR)
        self.assertEqual(tree.getAttribute(), 'ATTR')
        self.assertEqual(tree.index, 123)
    
    def test_basic_and(self):
        """Test basic AND operations."""
        for op in ['and', 'AND']:
            tree = self.parser.parse(f'A {op} B')
            self.assertEqual(tree.getNodeType(), OpType.AND)
    
    def test_basic_or(self):
        """Test basic OR operations."""
        for op in ['or', 'OR']:
            tree = self.parser.parse(f'A {op} B')
            self.assertEqual(tree.getNodeType(), OpType.OR)
    
    def test_nested_expressions(self):
        """Test nested policy expressions."""
        test_cases = [
            ('(A and B) or C', OpType.OR),
            ('A and (B or C)', OpType.AND),
            ('((A and B) or C) and D', OpType.AND),
            ('(A or B) and (C or D)', OpType.AND),
        ]
        for policy, expected_root_type in test_cases:
            tree = self.parser.parse(policy)
            self.assertEqual(tree.getNodeType(), expected_root_type,
                           f"Failed for policy: {policy}")
    
    def test_negated_attributes(self):
        """Test negated attribute parsing."""
        tree = self.parser.parse('!A and B')
        left = tree.getLeft()
        self.assertTrue(left.negated)
        self.assertEqual(left.getAttribute(), '!A')
    
    # =========================================================================
    # Stress Tests
    # =========================================================================
    
    def test_deep_nesting(self):
        """Test deeply nested expressions (20 levels)."""
        policy = 'A'
        for i in range(20):
            policy = f'({policy} and B{i})'
        tree = self.parser.parse(policy)
        self.assertIsNotNone(tree)
    
    def test_many_attributes(self):
        """Test policy with 100 attributes."""
        attrs = ' and '.join([f'ATTR{i}' for i in range(100)])
        tree = self.parser.parse(attrs)
        self.assertIsNotNone(tree)
        
        # Verify all attributes are present
        attr_list = self.msp.getAttributeList(tree)
        self.assertEqual(len(attr_list), 100)
    
    def test_wide_or_tree(self):
        """Test wide OR tree with 50 branches."""
        attrs = ' or '.join([f'ATTR{i}' for i in range(50)])
        tree = self.parser.parse(attrs)
        self.assertIsNotNone(tree)
    
    def test_balanced_tree(self):
        """Test balanced binary tree structure."""
        # Create: ((A and B) or (C and D)) and ((E and F) or (G and H))
        policy = '((A and B) or (C and D)) and ((E and F) or (G and H))'
        tree = self.parser.parse(policy)
        self.assertEqual(tree.getNodeType(), OpType.AND)
    
    def test_random_policies(self):
        """Generate and parse 100 random valid policies."""
        for _ in range(100):
            policy = self._generate_random_policy(depth=5, max_attrs=10)
            try:
                tree = self.parser.parse(policy)
                self.assertIsNotNone(tree)
            except Exception as e:
                self.fail(f"Failed to parse random policy: {policy}\nError: {e}")
    
    # =========================================================================
    # Policy Satisfaction Tests
    # =========================================================================
    
    def test_prune_and_policy(self):
        """Test policy satisfaction for AND policies."""
        tree = self.parser.parse('A and B and C')
        
        # All attributes present - should satisfy
        result = self.parser.prune(tree, ['A', 'B', 'C'])
        self.assertIsNotNone(result)
        self.assertNotEqual(result, False)
        
        # Missing one attribute - should not satisfy
        result = self.parser.prune(tree, ['A', 'B'])
        self.assertFalse(result)
    
    def test_prune_or_policy(self):
        """Test policy satisfaction for OR policies."""
        tree = self.parser.parse('A or B or C')
        
        # Any single attribute should satisfy
        for attr in ['A', 'B', 'C']:
            result = self.parser.prune(tree, [attr])
            self.assertIsNotNone(result)
            self.assertNotEqual(result, False)
        
        # No attributes - should not satisfy
        result = self.parser.prune(tree, [])
        self.assertFalse(result)
    
    def test_prune_complex_policy(self):
        """Test policy satisfaction for complex policies."""
        tree = self.parser.parse('(A and B) or (C and D)')

        # Left branch satisfied
        result = self.parser.prune(tree, ['A', 'B'])
        self.assertIsNotNone(result)

        # Right branch satisfied
        result = self.parser.prune(tree, ['C', 'D'])
        self.assertIsNotNone(result)

        # Neither branch satisfied
        result = self.parser.prune(tree, ['A', 'C'])
        self.assertFalse(result)

    # =========================================================================
    # MSP Conversion Tests
    # =========================================================================

    def test_msp_simple_and(self):
        """Test MSP conversion for AND policy."""
        tree = self.msp.createPolicy('A and B')
        matrix = self.msp.convert_policy_to_msp(tree)

        self.assertIn('A', matrix)
        self.assertIn('B', matrix)
        # AND gate: first child gets [1, 1], second gets [0, -1]
        self.assertEqual(matrix['A'], [1, 1])
        self.assertEqual(matrix['B'], [0, -1])

    def test_msp_simple_or(self):
        """Test MSP conversion for OR policy."""
        tree = self.msp.createPolicy('A or B')
        matrix = self.msp.convert_policy_to_msp(tree)

        self.assertIn('A', matrix)
        self.assertIn('B', matrix)
        # OR gate: both children get same vector
        self.assertEqual(matrix['A'], [1])
        self.assertEqual(matrix['B'], [1])

    def test_msp_complex_policy(self):
        """Test MSP conversion for complex policy."""
        policy = '((A and B) or C) and D'
        tree = self.msp.createPolicy(policy)
        matrix = self.msp.convert_policy_to_msp(tree)

        # All attributes should be in the matrix
        for attr in ['A', 'B', 'C', 'D']:
            self.assertIn(attr, matrix)

    def test_msp_coefficient_recovery(self):
        """Test coefficient recovery from MSP."""
        tree = self.msp.createPolicy('A and B')
        coeffs = self.msp.getCoefficients(tree)

        self.assertIn('A', coeffs)
        self.assertIn('B', coeffs)

    # =========================================================================
    # Duplicate Attribute Tests
    # =========================================================================

    def test_duplicate_attributes(self):
        """Test handling of duplicate attributes."""
        tree = self.parser.parse('A and B and A')

        _dictCount = {}
        self.parser.findDuplicates(tree, _dictCount)

        self.assertEqual(_dictCount['A'], 2)
        self.assertEqual(_dictCount['B'], 1)

    def test_duplicate_labeling(self):
        """Test that duplicate attributes get unique labels."""
        tree = self.msp.createPolicy('A and B and A')
        attr_list = self.msp.getAttributeList(tree)

        # Should have 3 attributes with unique labels
        self.assertEqual(len(attr_list), 3)
        # Check that duplicates are labeled (A_0, A_1)
        a_attrs = [a for a in attr_list if a.startswith('A')]
        self.assertEqual(len(a_attrs), 2)

    # =========================================================================
    # Special Character Tests
    # =========================================================================

    def test_special_characters_in_attributes(self):
        """Test attributes with special characters."""
        # Note: underscore followed by non-digits works, but underscore + digits
        # is treated as duplicate index notation (e.g., ATTR_0, ATTR_1)
        special_attrs = [
            'attr-name',      # hyphen
            'attr.name',      # dot
            'attr@domain',    # at sign
            'attr#123',       # hash
            'attr$var',       # dollar
            'role/admin',     # slash
        ]
        for attr in special_attrs:
            try:
                tree = self.parser.parse(attr)
                self.assertEqual(tree.getNodeType(), OpType.ATTR)
            except Exception as e:
                self.fail(f"Failed to parse attribute: {attr}\nError: {e}")

    def test_underscore_limitation(self):
        """Test that underscore + non-digits fails (known limitation)."""
        # This is a known limitation: attr_name fails because the parser
        # expects digits after underscore for duplicate indexing
        with self.assertRaises(Exception):
            self.parser.parse('attr_name')

    # =========================================================================
    # Performance Tests
    # =========================================================================

    def test_parsing_performance(self):
        """Test parsing performance with 1000 iterations."""
        policy = '(A and B) or (C and D) or (E and F)'

        start = time.time()
        for _ in range(1000):
            self.parser.parse(policy)
        elapsed = time.time() - start

        # Should complete in under 5 seconds
        self.assertLess(elapsed, 5.0,
                       f"Parsing 1000 policies took {elapsed:.2f}s (expected < 5s)")

    def test_msp_conversion_performance(self):
        """Test MSP conversion performance."""
        policy = ' and '.join([f'ATTR{i}' for i in range(20)])
        tree = self.msp.createPolicy(policy)

        start = time.time()
        for _ in range(100):
            self.msp.convert_policy_to_msp(tree)
        elapsed = time.time() - start

        # Should complete in under 2 seconds
        self.assertLess(elapsed, 2.0,
                       f"MSP conversion took {elapsed:.2f}s (expected < 2s)")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _generate_random_policy(self, depth: int, max_attrs: int) -> str:
        """Generate a random valid policy expression."""
        if depth <= 0 or random.random() < 0.3:
            # Generate leaf node (attribute)
            return f'ATTR{random.randint(0, max_attrs)}'

        # Generate internal node
        left = self._generate_random_policy(depth - 1, max_attrs)
        right = self._generate_random_policy(depth - 1, max_attrs)
        op = random.choice(['and', 'or'])
        return f'({left} {op} {right})'


class PolicyParserEdgeCaseTest(unittest.TestCase):
    """Edge case tests for the policy parser."""

    @classmethod
    def setUpClass(cls):
        cls.parser = PolicyParser()

    def test_case_insensitive_operators(self):
        """Test that AND/OR operators are case-insensitive."""
        # These should all parse correctly
        for policy in ['A AND B', 'A and B', 'A OR B', 'A or B']:
            tree = self.parser.parse(policy)
            self.assertIsNotNone(tree)

    def test_whitespace_handling(self):
        """Test handling of extra whitespace."""
        policies = [
            'A  and  B',      # extra spaces
            ' A and B ',      # leading/trailing spaces
            'A and  B',       # mixed spacing
        ]
        for policy in policies:
            tree = self.parser.parse(policy)
            self.assertIsNotNone(tree)

    def test_parentheses_variations(self):
        """Test various parentheses patterns."""
        policies = [
            '(A)',
            '((A))',
            '(A and B)',
            '((A and B))',
            '(A) and (B)',
        ]
        for policy in policies:
            tree = self.parser.parse(policy)
            self.assertIsNotNone(tree)


def run_stress_test():
    """Run the stress test suite and print results."""
    print("=" * 70)
    print("ABE Policy Parser Stress Test")
    print("=" * 70)
    print()

    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(PolicyParserStressTest))
    suite.addTests(loader.loadTestsFromTestCase(PolicyParserEdgeCaseTest))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_stress_test()
    sys.exit(0 if success else 1)

