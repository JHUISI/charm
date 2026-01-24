#!/usr/bin/env python
"""
Numeric Attribute Encoding for CP-ABE

This module implements the "bag of bits" technique from the Bethencourt-Sahai-Waters
CP-ABE paper (IEEE S&P 2007) for representing numeric attributes and comparisons.

The technique converts numeric comparisons (e.g., age >= 21) into boolean attribute
expressions that can be evaluated using standard ABE schemes.

For an n-bit integer k, we create the following attributes:
- attr#bi#0  (bit i is 0)
- attr#bi#1  (bit i is 1)

Comparisons are then encoded as boolean expressions over these bit attributes.

Note: Uses '#' as delimiter instead of '_' because '_' is reserved for attribute
indexing in the PolicyParser.
"""

import re
import warnings


# Constants for validation
MIN_BITS = 1
MAX_BITS = 64  # Reasonable upper bound for bit width
RESERVED_PATTERN = re.compile(r'#b\d+#')  # Pattern used in bit encoding


class NumericAttributeError(Exception):
    """Base exception for numeric attribute encoding errors."""
    pass


class BitOverflowError(NumericAttributeError):
    """Raised when a value exceeds the representable range for the given bit width."""
    pass


class InvalidBitWidthError(NumericAttributeError):
    """Raised when an invalid bit width is specified."""
    pass


class InvalidOperatorError(NumericAttributeError):
    """Raised when an unsupported comparison operator is used."""
    pass


class AttributeNameConflictError(NumericAttributeError):
    """Raised when an attribute name conflicts with the bit encoding format."""
    pass


def validate_num_bits(num_bits):
    """
    Validate the num_bits parameter.

    Args:
        num_bits: Number of bits for representation

    Raises:
        InvalidBitWidthError: If num_bits is invalid
    """
    if not isinstance(num_bits, int):
        raise InvalidBitWidthError(f"num_bits must be an integer, got {type(num_bits).__name__}")
    if num_bits < MIN_BITS:
        raise InvalidBitWidthError(f"num_bits must be at least {MIN_BITS}, got {num_bits}")
    if num_bits > MAX_BITS:
        raise InvalidBitWidthError(f"num_bits must be at most {MAX_BITS}, got {num_bits}")


def validate_value(value, num_bits, context="value"):
    """
    Validate a numeric value for the given bit width.

    Args:
        value: The numeric value to validate
        num_bits: Number of bits for representation
        context: Description of the value for error messages

    Raises:
        ValueError: If value is negative
        BitOverflowError: If value exceeds the bit width
    """
    if value < 0:
        raise ValueError(f"Negative values not supported for {context}: {value}")

    max_value = (1 << num_bits) - 1
    if value > max_value:
        raise BitOverflowError(
            f"{context} {value} exceeds maximum representable value {max_value} "
            f"for {num_bits}-bit encoding. Consider increasing num_bits."
        )


def validate_attribute_name(attr_name):
    """
    Validate that an attribute name doesn't conflict with bit encoding format.

    Args:
        attr_name: The attribute name to validate

    Raises:
        AttributeNameConflictError: If the name conflicts with encoding format
    """
    if RESERVED_PATTERN.search(attr_name):
        raise AttributeNameConflictError(
            f"Attribute name '{attr_name}' contains reserved pattern '#b<digit>#' "
            f"which conflicts with bit encoding format. Please rename the attribute."
        )


def int_to_bits(value, num_bits=32):
    """
    Convert an integer to a list of bits (LSB first).

    Args:
        value: Non-negative integer to convert
        num_bits: Number of bits in the representation

    Returns:
        List of bits (0 or 1), LSB first

    Raises:
        ValueError: If value is negative
        BitOverflowError: If value exceeds bit width
        InvalidBitWidthError: If num_bits is invalid
    """
    validate_num_bits(num_bits)
    validate_value(value, num_bits, "value")

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

    Raises:
        AttributeNameConflictError: If attr_name conflicts with encoding format
        ValueError: If value is negative
        BitOverflowError: If value exceeds bit width
    """
    validate_attribute_name(attr_name)
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


# Supported comparison operators
SUPPORTED_OPERATORS = {'==', '>', '>=', '<', '<='}


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

    Raises:
        InvalidOperatorError: If operator is not supported
        AttributeNameConflictError: If attr_name conflicts with encoding format
        ValueError: If value is negative
        BitOverflowError: If value exceeds bit width
        InvalidBitWidthError: If num_bits is invalid
    """
    # Validate operator
    if operator not in SUPPORTED_OPERATORS:
        raise InvalidOperatorError(
            f"Unsupported operator '{operator}'. "
            f"Supported operators are: {', '.join(sorted(SUPPORTED_OPERATORS))}"
        )

    # Validate attribute name
    validate_attribute_name(attr_name)

    # Validate num_bits
    validate_num_bits(num_bits)

    # Convert and validate value
    try:
        value = int(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert value to integer: {value}") from e

    if value < 0:
        raise ValueError(f"Negative values not supported: {value}")

    # Check for potential overflow in <= comparison (value + 1)
    max_value = (1 << num_bits) - 1
    if operator == '<=' and value >= max_value:
        # value + 1 would overflow, but <= max_value is always true for valid values
        warnings.warn(
            f"Comparison '{attr_name} <= {value}' with {num_bits}-bit encoding: "
            f"value equals or exceeds max ({max_value}), result is always true for valid inputs.",
            UserWarning
        )
        # Return a tautology
        return f"{attr_name}#b0#0 or {attr_name}#b0#1"

    # Check for overflow in the value itself (for other operators)
    if value > max_value:
        raise BitOverflowError(
            f"Value {value} exceeds maximum representable value {max_value} "
            f"for {num_bits}-bit encoding. Consider increasing num_bits."
        )

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


# Regex pattern to match numeric comparisons in policies
# Matches: attr_name operator value (e.g., "age >= 21", "level>5")
# Note: Uses word boundary to avoid matching partial words
NUMERIC_PATTERN = re.compile(
    r'\b([a-zA-Z][a-zA-Z0-9]*)\s*(==|>=|<=|>|<)\s*(\d+)\b'
)


def preprocess_numeric_policy(policy_str, num_bits=32, strict=False):
    """
    Preprocess a policy string to expand numeric comparisons.

    Takes a policy like:
        '(age >= 21 and clearance > 3) or admin'

    And expands numeric comparisons into bit-level attributes:
        '((age#b4#1 or ...) and (clearance#b...)) or admin'

    Args:
        policy_str: Original policy string with numeric comparisons
        num_bits: Number of bits for numeric representation
        strict: If True, raise exceptions on errors; if False, return original
                expression on error (default: False)

    Returns:
        Expanded policy string with bit-level attributes

    Raises:
        ValueError: If policy_str is None
        InvalidBitWidthError: If num_bits is invalid

    Note:
        - Empty strings or whitespace-only strings return empty string
        - Malformed expressions that don't match the pattern are left unchanged
        - In non-strict mode, errors during expansion leave the original expression
    """
    # Validate inputs
    if policy_str is None:
        raise ValueError("policy_str cannot be None")

    validate_num_bits(num_bits)

    # Handle empty or whitespace-only strings
    if not policy_str or policy_str.isspace():
        return ""

    errors = []

    def replace_match(match):
        attr_name = match.group(1)
        operator = match.group(2)
        value_str = match.group(3)
        original = match.group(0)

        try:
            value = int(value_str)

            # Check for attribute name conflicts
            validate_attribute_name(attr_name)

            expanded = expand_numeric_comparison(attr_name, operator, value, num_bits)
            if expanded is None:
                # Return a tautology or contradiction as appropriate
                if operator == '>=' and value == 0:
                    # >= 0 is always true for non-negative
                    return f"({attr_name}#b0#0 or {attr_name}#b0#1)"
                elif operator == '<' and value == 0:
                    # < 0 is always false for non-negative
                    # Return a contradiction (attribute AND its negation can't both be true)
                    # But since we can't use negation easily, we use a placeholder
                    warnings.warn(
                        f"Comparison '{attr_name} < 0' is always false for non-negative values",
                        UserWarning
                    )
                    return "FALSE"
                elif operator == '>' and value == (1 << num_bits) - 1:
                    # > max_value is always false
                    warnings.warn(
                        f"Comparison '{attr_name} > {value}' is always false for {num_bits}-bit values",
                        UserWarning
                    )
                    return "FALSE"
                return "FALSE"  # placeholder for impossible conditions

            # Wrap in parentheses to preserve operator precedence
            return f"({expanded})"

        except (NumericAttributeError, ValueError) as e:
            errors.append((original, str(e)))
            if strict:
                raise
            # In non-strict mode, leave the original expression unchanged
            return original

    result = NUMERIC_PATTERN.sub(replace_match, policy_str)

    # Warn about any errors that occurred in non-strict mode
    if errors and not strict:
        for original, error in errors:
            warnings.warn(
                f"Failed to expand numeric comparison '{original}': {error}",
                UserWarning
            )

    return result


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
        # Returns: ['AGE#B0#1', 'AGE#B1#0', ..., 'LEVEL#B0#1', ..., 'MANAGER']

    Attributes:
        num_bits: Number of bits for numeric representation
        max_value: Maximum representable value for the configured bit width
    """

    def __init__(self, num_bits=32, strict=False):
        """
        Initialize the helper with a specific bit width.

        Args:
            num_bits: Number of bits for numeric representation (default 32)
                     Use smaller values (e.g., 8, 16) for better performance
                     if your numeric ranges are limited.
            strict: If True, raise exceptions on errors during policy expansion;
                   if False, leave problematic expressions unchanged (default: False)

        Raises:
            InvalidBitWidthError: If num_bits is invalid
        """
        validate_num_bits(num_bits)
        self.num_bits = num_bits
        self.max_value = (1 << num_bits) - 1
        self.strict = strict

    def expand_policy(self, policy_str):
        """
        Expand numeric comparisons in a policy string.

        Args:
            policy_str: Policy with numeric comparisons like "age >= 21"

        Returns:
            Expanded policy with bit-level attributes

        Raises:
            ValueError: If policy_str is None
            NumericAttributeError: In strict mode, if expansion fails
        """
        return preprocess_numeric_policy(policy_str, self.num_bits, self.strict)

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

        Raises:
            ValueError: If a numeric value is negative
            BitOverflowError: If a numeric value exceeds the bit width
            AttributeNameConflictError: If an attribute name conflicts with encoding
        """
        if attr_dict is None:
            raise ValueError("attr_dict cannot be None")

        result = []

        for name, value in attr_dict.items():
            if isinstance(value, int):
                # Validate the value
                if value < 0:
                    raise ValueError(f"Negative value not supported for attribute '{name}': {value}")
                if value > self.max_value:
                    raise BitOverflowError(
                        f"Value {value} for attribute '{name}' exceeds maximum {self.max_value} "
                        f"for {self.num_bits}-bit encoding"
                    )
                # Validate attribute name
                validate_attribute_name(name)
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

