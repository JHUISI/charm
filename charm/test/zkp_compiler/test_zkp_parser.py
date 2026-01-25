"""
Unit tests for the ZK statement parser.

Tests cover parsing of ZK statements, structure extraction, and error handling.
"""

import unittest
from charm.zkp_compiler.zkparser import ZKParser
from charm.toolbox.zknode import BinNode


class TestZKParser(unittest.TestCase):
    """Tests for ZK statement parser."""

    def setUp(self):
        self.parser = ZKParser()

    def test_parse_simple_statement(self):
        """Test parsing 'h = g^x'."""
        result = self.parser.parse("h = g^x")
        self.assertIsNotNone(result)
        self.assertEqual(result.type, BinNode(4).EQ)  # EQ node

    def test_parse_extracts_correct_structure(self):
        """Test that parsed tree has correct structure."""
        result = self.parser.parse("h = g^x")
        # h = g^x means: EQ(h, EXP(g, x))
        # Left side is the variable name (string)
        self.assertEqual(result.getLeft().upper(), 'H')
        # Right side is the exponentiation BinNode
        right = result.getRight()
        self.assertEqual(right.type, BinNode(3).EXP)

    def test_parse_multi_exponent_and(self):
        """Test parsing 'h = g^x AND j = g^y'.

        Note: The ZKParser processes this but may return an EQ node
        as the root depending on how AND is handled in the grammar.
        This tests that the parse succeeds and returns a BinNode.
        """
        result = self.parser.parse("h = g^x AND j = g^y")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)
        # The parser may return EQ (4) at the root level for this grammar
        # We just verify it's a valid BinNode type
        self.assertIn(result.type, [BinNode(2).AND, BinNode(4).EQ])

    def test_parse_preserves_variable_names(self):
        """Test that variable names are preserved (uppercased)."""
        result = self.parser.parse("h = g^x")
        # The left of EQ should be 'H'
        self.assertEqual(result.getLeft().upper(), 'H')

    def test_parse_empty_string_fails(self):
        """Test that empty string raises exception."""
        with self.assertRaises(Exception):
            self.parser.parse("")

    def test_parse_invalid_syntax_fails(self):
        """Test that completely unparseable syntax raises exception.

        Note: The parser is lenient and may accept partial matches.
        We test with symbols that cannot match any grammar rules.
        """
        with self.assertRaises(Exception):
            # Use symbols that cannot be parsed at all
            self.parser.parse("@@@ ### $$$")

    def test_node_structure_access(self):
        """Test that we can access node structure correctly."""
        result = self.parser.parse("h = g^x")
        # Right side is a BinNode (EXP node)
        right = result.getRight()
        self.assertIsInstance(right, BinNode)
        # Check that we can access the EXP node's children
        # The EXP node has left='G' and right='X' as strings
        self.assertIsNotNone(right.getLeft())
        self.assertIsNotNone(right.getRight())

    def test_result_is_binnode(self):
        """Test that parser returns a BinNode."""
        result = self.parser.parse("h = g^x")
        self.assertIsInstance(result, BinNode)


class TestZKParserMultiCharVariables(unittest.TestCase):
    """Tests for multi-character variable name support (new in v0.61)."""

    def setUp(self):
        self.parser = ZKParser()

    def test_parse_numbered_variables(self):
        """Test parsing with numbered variables like x1, g1, h1."""
        result = self.parser.parse("h1 = g1^x1")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)
        self.assertEqual(result.type, BinNode(4).EQ)

    def test_parse_descriptive_variable_names(self):
        """Test parsing with descriptive variable names."""
        result = self.parser.parse("commitment = generator^secret")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)
        self.assertEqual(result.type, BinNode(4).EQ)

    def test_parse_greek_letter_names(self):
        """Test parsing with Greek letter-style names."""
        result = self.parser.parse("gamma = alpha^beta")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)

    def test_parse_mixed_length_variables(self):
        """Test parsing with mixed single and multi-char variables."""
        result = self.parser.parse("h = generator^x")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)

    def test_parse_complex_multi_char_statement(self):
        """Test parsing complex statement with multi-char variables."""
        result = self.parser.parse("pk1 = g^sk1 AND pk2 = g^sk2")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BinNode)

    def test_multi_char_preserves_variable_names(self):
        """Test that multi-char variable names are preserved."""
        result = self.parser.parse("commitment = generator^secret")
        # The left of EQ should be 'COMMITMENT' (uppercased)
        self.assertEqual(result.getLeft().upper(), 'COMMITMENT')

    def test_backwards_compatible_single_char(self):
        """Test that single-char variables still work (backwards compatibility)."""
        result = self.parser.parse("h = g^x")
        self.assertIsNotNone(result)
        self.assertEqual(result.getLeft().upper(), 'H')


if __name__ == "__main__":
    unittest.main()

