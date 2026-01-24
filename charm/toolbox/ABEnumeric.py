#!/usr/bin/env python
"""
Numeric Attribute Encoding for CP-ABE

This module implements the "bag of bits" technique from the Bethencourt-Sahai-Waters
CP-ABE paper (IEEE S&P 2007) for representing numeric attributes and comparisons.

The technique converts numeric comparisons (e.g., age >= 21) into boolean attribute
expressions that can be evaluated using standard ABE schemes.

For an n-bit integer k, we create the following attributes:
- attr_bit_i:0  (bit i is 0)
- attr_bit_i:1  (bit i is 1)

Comparisons are then encoded as boolean expressions over these bit attributes.
"""

from charm.toolbox.node import BinNode, OpType


def int_to_bits(value, num_bits=32):
    """Convert an integer to a list of bits (LSB first)."""
    if value < 0:
        raise ValueError("Negative values not supported")
    bits = []
    for i in range(num_bits):
        bits.append((value >> i) & 1)
    return bits


def bits_to_attributes(attr_name, value, num_bits=32):
    """
    Convert a numeric value to a set of bit-level attributes.

    For example, if attr_name='age' and value=5 (binary: 101), with num_bits=8:
    Returns: {'age#b0#1', 'age#b1#0', 'age#b2#1', ...}

    Uses '#' delimiter instead of '_' because '_' is reserved for attribute indexing
    in the PolicyParser.

    This is used when generating user attribute sets.
    """
    bits = int_to_bits(value, num_bits)
    attributes = set()
    for i, bit in enumerate(bits):
        attributes.add(f"{attr_name}#b{i}#{bit}")
    return attributes


def encode_equality(attr_name, value, num_bits=32):
    """
    Encode 'attr == value' as a conjunction of bit attributes.

    Returns the policy string representation.
    For example: age == 5 (binary: 101) becomes:
    (age#b0#1 and age#b1#0 and age#b2#1 and ...)
    """
    bits = int_to_bits(value, num_bits)
    clauses = [f"{attr_name}#b{i}#{bit}" for i, bit in enumerate(bits)]
    return " and ".join(clauses)


def encode_greater_than(attr_name, value, num_bits=32):
    """
    Encode 'attr > value' using bag of bits.

    The encoding works by finding positions where the attribute can be strictly greater.
    For each bit position i from high to low:
      - If all higher bits match AND bit i of value is 0 AND bit i of attr is 1
        OR a higher bit already made attr > value
    """
    bits = int_to_bits(value, num_bits)

    # Build clauses for each bit position where attr can exceed value
    or_clauses = []

    for i in range(num_bits - 1, -1, -1):  # high bit to low bit
        if bits[i] == 0:
            # If value's bit i is 0, attr > value if:
            # - attr's bit i is 1 AND all higher bits are equal
            higher_bits_match = [f"{attr_name}#b{j}#{bits[j]}"
                                 for j in range(i + 1, num_bits)]
            this_bit_greater = f"{attr_name}#b{i}#1"

            if higher_bits_match:
                clause = "(" + " and ".join(higher_bits_match + [this_bit_greater]) + ")"
            else:
                clause = this_bit_greater
            or_clauses.append(clause)

    if not or_clauses:
        # value is all 1s, nothing can be greater (within num_bits)
        return None

    return " or ".join(or_clauses)


def encode_greater_than_or_equal(attr_name, value, num_bits=32):
    """Encode 'attr >= value' as (attr > value - 1) or handle edge cases."""
    if value == 0:
        return None  # Always true for non-negative
    
    return encode_greater_than(attr_name, value - 1, num_bits)


def encode_less_than(attr_name, value, num_bits=32):
    """
    Encode 'attr < value' using bag of bits.

    Similar to greater_than, but looking for positions where attr can be less.
    """
    if value == 0:
        return None  # Nothing is less than 0 for non-negative

    bits = int_to_bits(value, num_bits)
    or_clauses = []

    for i in range(num_bits - 1, -1, -1):
        if bits[i] == 1:
            # If value's bit i is 1, attr < value if:
            # - attr's bit i is 0 AND all higher bits are equal
            higher_bits_match = [f"{attr_name}#b{j}#{bits[j]}"
                                 for j in range(i + 1, num_bits)]
            this_bit_less = f"{attr_name}#b{i}#0"

            if higher_bits_match:
                clause = "(" + " and ".join(higher_bits_match + [this_bit_less]) + ")"
            else:
                clause = this_bit_less
            or_clauses.append(clause)

    if not or_clauses:
        return None

    return " or ".join(or_clauses)


def encode_less_than_or_equal(attr_name, value, num_bits=32):
    """Encode 'attr <= value' as (attr < value + 1)."""
    return encode_less_than(attr_name, value + 1, num_bits)


def expand_numeric_comparison(attr_name, operator, value, num_bits=32):
    """
    Expand a numeric comparison into a boolean policy expression.
    
    Args:
        attr_name: The attribute name (e.g., 'age', 'level')
        operator: One of '==', '>', '>=', '<', '<='
        value: The numeric value to compare against
        num_bits: Number of bits for the representation (default 32)
    
    Returns:
        A string policy expression using bit-level attributes
    """
    value = int(value)
    
    if operator == '==':
        return encode_equality(attr_name, value, num_bits)
    elif operator == '>':
        return encode_greater_than(attr_name, value, num_bits)
    elif operator == '>=':
        return encode_greater_than_or_equal(attr_name, value, num_bits)
    elif operator == '<':
        return encode_less_than(attr_name, value, num_bits)
    elif operator == '<=':
        return encode_less_than_or_equal(attr_name, value, num_bits)
    else:
        raise ValueError(f"Unknown operator: {operator}")


# Regex pattern to match numeric comparisons in policies
import re
NUMERIC_PATTERN = re.compile(
    r'(\w+)\s*(==|>=|<=|>|<)\s*(\d+)',
    re.IGNORECASE
)


def preprocess_numeric_policy(policy_str, num_bits=32):
    """
    Preprocess a policy string to expand numeric comparisons.

    Takes a policy like:
        '(age >= 21 and clearance > 3) or admin'

    And expands numeric comparisons into bit-level attributes:
        '((age_bit_4:1 or ...) and (clearance_bit_...)) or admin'

    Args:
        policy_str: Original policy string with numeric comparisons
        num_bits: Number of bits for numeric representation

    Returns:
        Expanded policy string with bit-level attributes
    """
    def replace_match(match):
        attr_name = match.group(1)
        operator = match.group(2)
        value = int(match.group(3))

        expanded = expand_numeric_comparison(attr_name, operator, value, num_bits)
        if expanded is None:
            # Return a tautology or contradiction as appropriate
            if operator in ['>=', '<='] and value == 0:
                # >= 0 is always true for non-negative, use placeholder
                return f"{attr_name}#b0#0 or {attr_name}#b0#1"
            return "FALSE"  # placeholder for impossible conditions

        # Wrap in parentheses to preserve operator precedence
        return f"({expanded})"

    return NUMERIC_PATTERN.sub(replace_match, policy_str)


def numeric_attributes_from_value(attr_name, value, num_bits=32):
    """
    Generate the attribute dictionary for a numeric attribute value.

    This should be called when preparing user attributes for key generation.

    Args:
        attr_name: The attribute name (e.g., 'age')
        value: The numeric value (e.g., 25)
        num_bits: Number of bits for representation

    Returns:
        List of attribute strings like ['age#b0#1', 'age#b1#0', ...]
    """
    bits = int_to_bits(value, num_bits)
    return [f"{attr_name}#b{i}#{bit}" for i, bit in enumerate(bits)]


class NumericAttributeHelper:
    """
    Helper class for working with numeric attributes in CP-ABE.

    This class provides a high-level interface for:
    - Expanding policies with numeric comparisons
    - Converting numeric attribute values to bit representations

    Usage:
        helper = NumericAttributeHelper(num_bits=16)  # 16-bit integers

        # For encryption: expand the policy
        policy = helper.expand_policy("age >= 21 and level > 5")

        # For key generation: get user attributes
        user_attrs = helper.user_attributes({'age': 25, 'level': 7, 'role': 'manager'})
        # Returns: ['age_bit_0:1', 'age_bit_1:0', ..., 'level_bit_0:1', ..., 'ROLE']
    """

    def __init__(self, num_bits=32):
        """
        Initialize the helper with a specific bit width.

        Args:
            num_bits: Number of bits for numeric representation (default 32)
                     Use smaller values (e.g., 8, 16) for better performance
                     if your numeric ranges are limited.
        """
        self.num_bits = num_bits

    def expand_policy(self, policy_str):
        """
        Expand numeric comparisons in a policy string.

        Args:
            policy_str: Policy with numeric comparisons like "age >= 21"

        Returns:
            Expanded policy with bit-level attributes
        """
        return preprocess_numeric_policy(policy_str, self.num_bits)

    def user_attributes(self, attr_dict):
        """
        Convert a dictionary of user attributes to a list suitable for ABE.

        Numeric values are converted to bit representations.
        String values are uppercased as per standard attribute handling.

        Args:
            attr_dict: Dictionary mapping attribute names to values
                      e.g., {'age': 25, 'role': 'admin', 'level': 5}

        Returns:
            List of attribute strings for key generation
        """
        result = []

        for name, value in attr_dict.items():
            if isinstance(value, int):
                # Numeric attribute - convert to bits (uppercase to match parser)
                attrs = numeric_attributes_from_value(name, value, self.num_bits)
                result.extend([a.upper() for a in attrs])
            elif isinstance(value, str):
                # String attribute - uppercase
                result.append(value.upper())
            else:
                # Convert to string and uppercase
                result.append(str(value).upper())

        return result

    def check_satisfaction(self, user_attrs, required_comparison, attr_name, operator, value):
        """
        Check if a user's numeric attribute satisfies a comparison.

        This is a utility for testing/debugging.

        Args:
            user_attrs: Dict with user's attribute values
            attr_name: Name of the numeric attribute
            operator: Comparison operator
            value: Comparison value

        Returns:
            True if the comparison is satisfied
        """
        if attr_name not in user_attrs:
            return False

        user_value = user_attrs[attr_name]

        if operator == '==':
            return user_value == value
        elif operator == '>':
            return user_value > value
        elif operator == '>=':
            return user_value >= value
        elif operator == '<':
            return user_value < value
        elif operator == '<=':
            return user_value <= value

        return False

