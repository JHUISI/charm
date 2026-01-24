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


class NumericAttributeTest(unittest.TestCase):
    """Tests for numeric attribute support using bag of bits encoding."""

    @classmethod
    def setUpClass(cls):
        cls.parser = PolicyParser()
        # Import here to avoid circular imports
        from charm.toolbox.ABEnumeric import NumericAttributeHelper
        cls.helper = NumericAttributeHelper(num_bits=8)

    def test_greater_than(self):
        """Test attr > value comparison."""
        expanded = self.helper.expand_policy('age > 10')
        tree = self.parser.parse(expanded)

        # age=15 should satisfy age > 10
        user_attrs = self.helper.user_attributes({'age': 15})
        result = self.parser.prune(tree, user_attrs)
        self.assertTrue(result)

        # age=10 should NOT satisfy age > 10
        user_attrs = self.helper.user_attributes({'age': 10})
        result = self.parser.prune(tree, user_attrs)
        self.assertFalse(result)

        # age=5 should NOT satisfy age > 10
        user_attrs = self.helper.user_attributes({'age': 5})
        result = self.parser.prune(tree, user_attrs)
        self.assertFalse(result)

    def test_greater_than_or_equal(self):
        """Test attr >= value comparison."""
        expanded = self.helper.expand_policy('age >= 18')
        tree = self.parser.parse(expanded)

        # age=25 should satisfy
        user_attrs = self.helper.user_attributes({'age': 25})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # age=18 should satisfy (boundary)
        user_attrs = self.helper.user_attributes({'age': 18})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # age=17 should NOT satisfy
        user_attrs = self.helper.user_attributes({'age': 17})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_less_than(self):
        """Test attr < value comparison."""
        expanded = self.helper.expand_policy('age < 18')
        tree = self.parser.parse(expanded)

        # age=17 should satisfy
        user_attrs = self.helper.user_attributes({'age': 17})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # age=18 should NOT satisfy
        user_attrs = self.helper.user_attributes({'age': 18})
        self.assertFalse(self.parser.prune(tree, user_attrs))

        # age=25 should NOT satisfy
        user_attrs = self.helper.user_attributes({'age': 25})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_less_than_or_equal(self):
        """Test attr <= value comparison."""
        expanded = self.helper.expand_policy('level <= 5')
        tree = self.parser.parse(expanded)

        # level=3 should satisfy
        user_attrs = self.helper.user_attributes({'level': 3})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # level=5 should satisfy (boundary)
        user_attrs = self.helper.user_attributes({'level': 5})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # level=6 should NOT satisfy
        user_attrs = self.helper.user_attributes({'level': 6})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_equality(self):
        """Test attr == value comparison."""
        expanded = self.helper.expand_policy('level == 5')
        tree = self.parser.parse(expanded)

        # level=5 should satisfy
        user_attrs = self.helper.user_attributes({'level': 5})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # level=4 should NOT satisfy
        user_attrs = self.helper.user_attributes({'level': 4})
        self.assertFalse(self.parser.prune(tree, user_attrs))

        # level=6 should NOT satisfy
        user_attrs = self.helper.user_attributes({'level': 6})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_compound_numeric_policy(self):
        """Test combined numeric comparisons."""
        expanded = self.helper.expand_policy('age >= 18 and level > 5')
        tree = self.parser.parse(expanded)

        # age=25, level=10 should satisfy both
        user_attrs = self.helper.user_attributes({'age': 25, 'level': 10})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # age=25, level=3 should fail (level > 5 fails)
        user_attrs = self.helper.user_attributes({'age': 25, 'level': 3})
        self.assertFalse(self.parser.prune(tree, user_attrs))

        # age=15, level=10 should fail (age >= 18 fails)
        user_attrs = self.helper.user_attributes({'age': 15, 'level': 10})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_mixed_numeric_and_string_policy(self):
        """Test policies mixing numeric comparisons and string attributes."""
        expanded = self.helper.expand_policy('(age >= 21 or admin) and level > 0')
        tree = self.parser.parse(expanded)

        # age=25, level=1 should satisfy (age >= 21 satisfies first clause)
        user_attrs = self.helper.user_attributes({'age': 25, 'level': 1})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # role=admin, level=1 should satisfy (admin satisfies first clause)
        user_attrs = self.helper.user_attributes({'level': 1, 'role': 'ADMIN'})
        result = self.parser.prune(tree, user_attrs)
        self.assertTrue(result)

    def test_bit_encoding_correctness(self):
        """Test that bit encoding is correct for various values."""
        from charm.toolbox.ABEnumeric import int_to_bits

        # Test specific values
        self.assertEqual(int_to_bits(0, 8), [0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(int_to_bits(1, 8), [1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(int_to_bits(5, 8), [1, 0, 1, 0, 0, 0, 0, 0])  # 101
        self.assertEqual(int_to_bits(255, 8), [1, 1, 1, 1, 1, 1, 1, 1])

    def test_boundary_values(self):
        """Test boundary conditions for numeric comparisons."""
        # Test at boundary of 8-bit range
        expanded = self.helper.expand_policy('val >= 255')
        tree = self.parser.parse(expanded)

        # val=255 should satisfy (exactly equal)
        user_attrs = self.helper.user_attributes({'val': 255})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # val=254 should NOT satisfy
        user_attrs = self.helper.user_attributes({'val': 254})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_zero_comparisons(self):
        """Test comparisons with zero."""
        # age > 0
        expanded = self.helper.expand_policy('age > 0')
        tree = self.parser.parse(expanded)

        user_attrs = self.helper.user_attributes({'age': 1})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        user_attrs = self.helper.user_attributes({'age': 0})
        self.assertFalse(self.parser.prune(tree, user_attrs))


class NumericAttributeEdgeCaseTest(unittest.TestCase):
    """Tests for edge cases in numeric attribute handling."""

    def setUp(self):
        from charm.toolbox.ABEnumeric import (
            NumericAttributeHelper, preprocess_numeric_policy,
            expand_numeric_comparison, int_to_bits, validate_num_bits,
            validate_attribute_name, BitOverflowError, InvalidBitWidthError,
            InvalidOperatorError, AttributeNameConflictError
        )
        self.helper = NumericAttributeHelper(num_bits=8)
        self.strict_helper = NumericAttributeHelper(num_bits=8, strict=True)
        self.preprocess = preprocess_numeric_policy
        self.expand = expand_numeric_comparison
        self.int_to_bits = int_to_bits
        self.validate_num_bits = validate_num_bits
        self.validate_attribute_name = validate_attribute_name
        self.BitOverflowError = BitOverflowError
        self.InvalidBitWidthError = InvalidBitWidthError
        self.InvalidOperatorError = InvalidOperatorError
        self.AttributeNameConflictError = AttributeNameConflictError

    # --- Bit Overflow Tests ---
    def test_bit_overflow_in_expand(self):
        """Test that values exceeding bit width raise BitOverflowError."""
        with self.assertRaises(self.BitOverflowError):
            self.expand('age', '==', 256, num_bits=8)  # Max for 8-bit is 255

    def test_bit_overflow_in_user_attributes(self):
        """Test that user_attributes raises error for overflow values."""
        with self.assertRaises(self.BitOverflowError):
            self.helper.user_attributes({'age': 256})

    def test_bit_overflow_error_in_int_to_bits(self):
        """Test that int_to_bits raises BitOverflowError on overflow."""
        with self.assertRaises(self.BitOverflowError):
            self.int_to_bits(256, 8)

    def test_boundary_value_at_max(self):
        """Test value exactly at maximum (255 for 8-bit)."""
        # Should work without error
        expanded = self.expand('age', '==', 255, num_bits=8)
        self.assertIsNotNone(expanded)

    def test_boundary_value_just_over_max(self):
        """Test value just over maximum."""
        with self.assertRaises(self.BitOverflowError):
            self.expand('age', '==', 256, num_bits=8)

    # --- Negative Value Tests ---
    def test_negative_value_in_expand(self):
        """Test that negative values raise ValueError."""
        with self.assertRaises(ValueError):
            self.expand('age', '>=', -1, num_bits=8)

    def test_negative_value_in_user_attributes(self):
        """Test that user_attributes raises error for negative values."""
        with self.assertRaises(ValueError):
            self.helper.user_attributes({'age': -5})

    def test_negative_value_message(self):
        """Test that error message mentions negative values."""
        try:
            self.expand('age', '>=', -10, num_bits=8)
        except ValueError as e:
            self.assertIn('Negative', str(e))

    # --- Invalid Operator Tests ---
    def test_invalid_operator_exclamation_equal(self):
        """Test that != operator is rejected."""
        with self.assertRaises(self.InvalidOperatorError):
            self.expand('age', '!=', 21, num_bits=8)

    def test_invalid_operator_not_equal_diamond(self):
        """Test that <> operator is rejected."""
        with self.assertRaises(self.InvalidOperatorError):
            self.expand('age', '<>', 21, num_bits=8)

    def test_invalid_operator_tilde(self):
        """Test that arbitrary operators are rejected."""
        with self.assertRaises(self.InvalidOperatorError):
            self.expand('age', '~', 21, num_bits=8)

    def test_valid_operators_all_work(self):
        """Test that all supported operators work."""
        for op in ['==', '>', '>=', '<', '<=']:
            result = self.expand('age', op, 10, num_bits=8)
            self.assertIsNotNone(result)

    # --- Invalid Bit Width Tests ---
    def test_zero_bit_width(self):
        """Test that num_bits=0 raises InvalidBitWidthError."""
        with self.assertRaises(self.InvalidBitWidthError):
            self.validate_num_bits(0)

    def test_negative_bit_width(self):
        """Test that negative num_bits raises InvalidBitWidthError."""
        with self.assertRaises(self.InvalidBitWidthError):
            self.validate_num_bits(-1)

    def test_excessive_bit_width(self):
        """Test that num_bits > 64 raises InvalidBitWidthError."""
        with self.assertRaises(self.InvalidBitWidthError):
            self.validate_num_bits(65)

    def test_non_integer_bit_width(self):
        """Test that non-integer num_bits raises InvalidBitWidthError."""
        with self.assertRaises(self.InvalidBitWidthError):
            self.validate_num_bits(8.5)

    def test_string_bit_width(self):
        """Test that string num_bits raises InvalidBitWidthError."""
        with self.assertRaises(self.InvalidBitWidthError):
            self.validate_num_bits("8")

    # --- Attribute Name Conflict Tests ---
    def test_attribute_name_with_encoding_pattern(self):
        """Test that attribute names with #b# pattern are rejected."""
        with self.assertRaises(self.AttributeNameConflictError):
            self.validate_attribute_name('age#b0#1')

    def test_attribute_name_with_partial_pattern(self):
        """Test attribute names with partial encoding pattern."""
        with self.assertRaises(self.AttributeNameConflictError):
            self.validate_attribute_name('test#b5#value')

    def test_valid_attribute_names(self):
        """Test that normal attribute names are accepted."""
        # These should not raise
        self.validate_attribute_name('age')
        self.validate_attribute_name('AGE')
        self.validate_attribute_name('user_level')
        self.validate_attribute_name('clearance123')

    # --- Empty/Malformed Policy Tests ---
    def test_none_policy(self):
        """Test that None policy raises ValueError."""
        with self.assertRaises(ValueError):
            self.preprocess(None, num_bits=8)

    def test_empty_policy(self):
        """Test that empty policy returns empty string."""
        result = self.preprocess('', num_bits=8)
        self.assertEqual(result, '')

    def test_whitespace_only_policy(self):
        """Test that whitespace-only policy returns empty string."""
        result = self.preprocess('   ', num_bits=8)
        self.assertEqual(result, '')

    def test_policy_without_numeric(self):
        """Test that policy without numeric comparisons is unchanged."""
        policy = 'admin and manager'
        result = self.preprocess(policy, num_bits=8)
        self.assertEqual(result, policy)

    # --- Regex Edge Cases ---
    def test_extra_spaces_around_operator(self):
        """Test numeric comparison with extra spaces."""
        policy = 'age   >=    21'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('#b', result)
        self.assertNotIn('>=', result)

    def test_no_spaces_around_operator(self):
        """Test numeric comparison without spaces."""
        policy = 'age>=21'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('#b', result)

    def test_mixed_spacing(self):
        """Test numeric comparison with mixed spacing."""
        policy = 'age>= 21 and level <5'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('#b', result)
        self.assertNotIn('>=', result)
        self.assertNotIn('<', result)

    def test_multiple_parentheses(self):
        """Test policy with multiple levels of parentheses."""
        policy = '((age >= 21) and (level > 5)) or admin'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('admin', result)
        self.assertIn('#b', result)

    def test_attr_name_all_caps(self):
        """Test attribute name in all caps."""
        policy = 'AGE >= 21'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('AGE#b', result)

    def test_attr_name_mixed_case(self):
        """Test attribute name in mixed case."""
        policy = 'Age >= 21'
        result = self.preprocess(policy, num_bits=8)
        self.assertIn('Age#b', result)

    # --- Strict Mode Tests ---
    def test_strict_mode_raises_on_overflow(self):
        """Test that strict mode raises exceptions."""
        from charm.toolbox.ABEnumeric import preprocess_numeric_policy
        with self.assertRaises(self.BitOverflowError):
            preprocess_numeric_policy('age >= 256', num_bits=8, strict=True)

    def test_non_strict_mode_continues_on_error(self):
        """Test that non-strict mode leaves problematic expression unchanged."""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.preprocess('age >= 256', num_bits=8, strict=False)
            # Should keep original expression and warn
            self.assertIn('age >= 256', result)
            self.assertGreater(len(w), 0)

    def test_strict_helper_raises_on_overflow(self):
        """Test that helper in strict mode raises exceptions."""
        with self.assertRaises((self.BitOverflowError, ValueError)):
            self.strict_helper.expand_policy('age >= 256')

    # --- Zero Comparison Tests ---
    def test_greater_than_zero(self):
        """Test attr > 0 works correctly."""
        result = self.expand('age', '>', 0, num_bits=8)
        self.assertIsNotNone(result)

    def test_greater_equal_zero_is_tautology(self):
        """Test attr >= 0 returns None (always true for non-negative)."""
        result = self.expand('age', '>=', 0, num_bits=8)
        # >= 0 is always true for non-negative, encode_greater_than_or_equal returns None
        self.assertIsNone(result)

    def test_less_than_zero_is_contradiction(self):
        """Test attr < 0 handling."""
        result = self.expand('age', '<', 0, num_bits=8)
        # < 0 is always false for non-negative, returns None
        self.assertIsNone(result)

    def test_equal_zero(self):
        """Test attr == 0 correctly encodes all zeros."""
        result = self.expand('age', '==', 0, num_bits=8)
        self.assertIsNotNone(result)
        # Should have all #0 (zero bits)
        self.assertIn('#0', result)

    # --- Max Value Property Test ---
    def test_helper_max_value_property(self):
        """Test that NumericAttributeHelper exposes max_value correctly."""
        from charm.toolbox.ABEnumeric import NumericAttributeHelper
        self.assertEqual(self.helper.max_value, 255)  # 2^8 - 1 = 255
        helper16 = NumericAttributeHelper(num_bits=16)
        self.assertEqual(helper16.max_value, 65535)  # 2^16 - 1


class NumericNegationTest(unittest.TestCase):
    """Tests for negation of numeric comparisons."""

    def setUp(self):
        from charm.toolbox.ABEnumeric import (
            NumericAttributeHelper, negate_comparison, negate_comparison_to_policy,
            InvalidOperatorError
        )
        from charm.toolbox.policytree import PolicyParser
        self.helper = NumericAttributeHelper(num_bits=8)
        self.negate = negate_comparison
        self.negate_to_policy = negate_comparison_to_policy
        self.parser = PolicyParser()
        self.InvalidOperatorError = InvalidOperatorError

    # --- Basic Negation Tests ---
    def test_negate_greater_equal(self):
        """Test NOT (age >= 21) becomes age < 21."""
        result = self.negate('age', '>=', 21)
        self.assertEqual(result, ('age', '<', 21))

    def test_negate_greater_than(self):
        """Test NOT (age > 21) becomes age <= 21."""
        result = self.negate('age', '>', 21)
        self.assertEqual(result, ('age', '<=', 21))

    def test_negate_less_equal(self):
        """Test NOT (age <= 21) becomes age > 21."""
        result = self.negate('age', '<=', 21)
        self.assertEqual(result, ('age', '>', 21))

    def test_negate_less_than(self):
        """Test NOT (age < 21) becomes age >= 21."""
        result = self.negate('age', '<', 21)
        self.assertEqual(result, ('age', '>=', 21))

    def test_negate_equality(self):
        """Test NOT (age == 21) becomes (age < 21) OR (age > 21)."""
        result = self.negate('age', '==', 21)
        self.assertEqual(result, (('age', '<', 21), ('age', '>', 21)))

    # --- Negation to Policy String Tests ---
    def test_negate_to_policy_simple(self):
        """Test negate_comparison_to_policy for simple operators."""
        self.assertEqual(self.negate_to_policy('age', '>=', 21), 'age < 21')
        self.assertEqual(self.negate_to_policy('age', '>', 21), 'age <= 21')
        self.assertEqual(self.negate_to_policy('age', '<=', 21), 'age > 21')
        self.assertEqual(self.negate_to_policy('age', '<', 21), 'age >= 21')

    def test_negate_to_policy_equality(self):
        """Test negate_comparison_to_policy for equality."""
        result = self.negate_to_policy('age', '==', 21)
        self.assertEqual(result, '(age < 21) or (age > 21)')

    # --- Invalid Operator Tests ---
    def test_negate_invalid_operator(self):
        """Test that negating invalid operators raises error."""
        with self.assertRaises(self.InvalidOperatorError):
            self.negate('age', '!=', 21)

    # --- Helper Method Tests ---
    def test_helper_negate_comparison(self):
        """Test NumericAttributeHelper.negate_comparison method."""
        result = self.helper.negate_comparison('age', '>=', 21)
        self.assertEqual(result, ('age', '<', 21))

    def test_helper_expand_negated_policy_simple(self):
        """Test expand_negated_policy for simple operators."""
        # NOT (age >= 21) should expand to bit encoding of age < 21
        result = self.helper.expand_negated_policy('age', '>=', 21)
        self.assertIsNotNone(result)
        self.assertIn('#b', result)

    def test_helper_expand_negated_policy_equality(self):
        """Test expand_negated_policy for equality."""
        # NOT (age == 21) should expand to (age < 21) OR (age > 21)
        result = self.helper.expand_negated_policy('age', '==', 21)
        self.assertIsNotNone(result)
        self.assertIn(' or ', result)
        self.assertIn('#b', result)

    # --- End-to-End Negation Tests ---
    def test_negated_policy_satisfaction(self):
        """Test that negated policies work correctly end-to-end."""
        # Original: age >= 21 (user with age 20 should NOT satisfy)
        # Negated: age < 21 (user with age 20 SHOULD satisfy)

        negated_policy = self.negate_to_policy('age', '>=', 21)
        expanded = self.helper.expand_policy(negated_policy)
        tree = self.parser.parse(expanded)

        # User with age 20 should satisfy "age < 21"
        user_attrs = self.helper.user_attributes({'age': 20})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # User with age 21 should NOT satisfy "age < 21"
        user_attrs = self.helper.user_attributes({'age': 21})
        self.assertFalse(self.parser.prune(tree, user_attrs))

        # User with age 25 should NOT satisfy "age < 21"
        user_attrs = self.helper.user_attributes({'age': 25})
        self.assertFalse(self.parser.prune(tree, user_attrs))

    def test_negated_equality_satisfaction(self):
        """Test that negated equality works correctly end-to-end."""
        # NOT (age == 21) means age != 21, i.e., (age < 21) OR (age > 21)

        negated_policy = self.negate_to_policy('age', '==', 21)
        expanded = self.helper.expand_policy(negated_policy)
        tree = self.parser.parse(expanded)

        # User with age 20 should satisfy "age != 21"
        user_attrs = self.helper.user_attributes({'age': 20})
        self.assertTrue(self.parser.prune(tree, user_attrs))

        # User with age 21 should NOT satisfy "age != 21"
        user_attrs = self.helper.user_attributes({'age': 21})
        self.assertFalse(self.parser.prune(tree, user_attrs))

        # User with age 22 should satisfy "age != 21"
        user_attrs = self.helper.user_attributes({'age': 22})
        self.assertTrue(self.parser.prune(tree, user_attrs))

    # --- Boundary Value Tests ---
    def test_negate_at_zero(self):
        """Test negation at zero boundary."""
        # NOT (age >= 0) = age < 0 (always false for non-negative)
        result = self.negate('age', '>=', 0)
        self.assertEqual(result, ('age', '<', 0))

        # NOT (age > 0) = age <= 0 (only true for 0)
        result = self.negate('age', '>', 0)
        self.assertEqual(result, ('age', '<=', 0))

    def test_negate_at_max(self):
        """Test negation at max value boundary."""
        # NOT (age <= 255) = age > 255 (always false for 8-bit)
        result = self.negate('age', '<=', 255)
        self.assertEqual(result, ('age', '>', 255))


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
    suite.addTests(loader.loadTestsFromTestCase(NumericAttributeTest))
    suite.addTests(loader.loadTestsFromTestCase(NumericAttributeEdgeCaseTest))
    suite.addTests(loader.loadTestsFromTestCase(NumericNegationTest))

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

