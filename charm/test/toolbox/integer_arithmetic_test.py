"""
Comprehensive arithmetic tests for the integer module.

These tests validate integer module behavior with GCD operations and integer conversions,
specifically designed to catch Python 3.12+ compatibility issues like the Py_SIZE() vs lv_tag bug.

Tests cover:
1. Integer conversion correctness (Python int <-> integer)
2. GCD operations and isCoPrime() method
3. Modular arithmetic (modular inverse, modular operations)
4. Regression tests for Python 3.12+ compatibility
5. Integration tests that mirror real scheme usage
"""

import sys
import unittest
import pytest

from charm.core.math.integer import (
    integer, gcd, random, randomPrime, isPrime, bitsize, serialize, deserialize
)


class IntegerConversionTest(unittest.TestCase):
    """Test integer conversion correctness between Python int and integer objects."""

    def test_common_rsa_exponents(self):
        """Verify that common RSA exponents convert correctly."""
        common_exponents = [65537, 3, 5, 17, 257, 641, 6700417]
        for exp in common_exponents:
            with self.subTest(exponent=exp):
                result = integer(exp)
                self.assertEqual(int(result), exp, f"integer({exp}) should equal {exp}")
                self.assertEqual(str(result), str(exp), f"str(integer({exp})) should equal '{exp}'")

    def test_small_values(self):
        """Test edge cases with small values."""
        small_values = [0, 1, 2, 10, 100, 255, 256, 1000]
        for val in small_values:
            with self.subTest(value=val):
                result = integer(val)
                self.assertEqual(int(result), val, f"integer({val}) should equal {val}")

    def test_large_values(self):
        """Test large values that require multiple digits in PyLongObject."""
        # These values require multiple 30-bit digits in Python's internal representation
        large_values = [
            2**30,      # Just over one digit
            2**60,      # Two digits
            2**90,      # Three digits
            2**128,     # Common cryptographic size
            2**256,     # 256-bit value
            2**512,     # 512-bit value
            2**1024,    # 1024-bit value (RSA key size)
        ]
        for val in large_values:
            with self.subTest(bits=val.bit_length()):
                result = integer(val)
                self.assertEqual(int(result), val, f"integer(2^{val.bit_length()-1}) conversion failed")

    def test_negative_values(self):
        """Test negative integer conversion."""
        negative_values = [-1, -2, -10, -100, -65537, -2**30, -2**60, -2**128]
        for val in negative_values:
            with self.subTest(value=val):
                result = integer(val)
                self.assertEqual(int(result), val, f"integer({val}) should equal {val}")

    def test_round_trip_conversion(self):
        """Verify round-trip conversion: Python int -> integer -> Python int preserves value."""
        test_values = [
            0, 1, -1, 65537, -65537,
            2**30 - 1, 2**30, 2**30 + 1,  # Around digit boundary
            2**60 - 1, 2**60, 2**60 + 1,  # Two digit boundary
            2**256, -2**256,
            2**512 + 12345, -2**512 - 12345,
        ]
        for val in test_values:
            with self.subTest(value=val if abs(val) < 1000 else f"2^{val.bit_length()-1}"):
                result = int(integer(val))
                self.assertEqual(result, val, "Round-trip conversion failed")

    def test_integer_from_integer(self):
        """Test creating integer from another integer object."""
        original = integer(65537)
        copy = integer(original)
        self.assertEqual(int(copy), 65537)
        self.assertEqual(int(original), int(copy))


class GCDOperationsTest(unittest.TestCase):
    """Test GCD operations with various integer types."""

    def test_gcd_python_ints(self):
        """Test gcd() with Python integers."""
        test_cases = [
            (12, 8, 4),
            (17, 13, 1),  # Coprime
            (100, 25, 25),
            (65537, 65536, 1),  # Common RSA exponent vs power of 2
            (2**128, 2**64, 2**64),
        ]
        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                result = gcd(a, b)
                self.assertEqual(int(result), expected)

    def test_gcd_integer_objects(self):
        """Test gcd() with integer objects."""
        a = integer(48)
        b = integer(18)
        result = gcd(a, b)
        self.assertEqual(int(result), 6)

    def test_gcd_mixed_types(self):
        """Test gcd() with mixed Python int and integer objects."""
        a = integer(48)
        result1 = gcd(a, 18)
        result2 = gcd(48, integer(18))
        self.assertEqual(int(result1), 6)
        self.assertEqual(int(result2), 6)

    def test_gcd_edge_cases(self):
        """Test gcd edge cases."""
        # gcd(0, n) = n
        self.assertEqual(int(gcd(0, 5)), 5)
        self.assertEqual(int(gcd(5, 0)), 5)
        # gcd(1, n) = 1
        self.assertEqual(int(gcd(1, 12345)), 1)
        self.assertEqual(int(gcd(12345, 1)), 1)
        # gcd(n, n) = n
        self.assertEqual(int(gcd(42, 42)), 42)


class IsCoPrimeTest(unittest.TestCase):
    """Test isCoPrime() method for coprimality checking."""

    def test_coprime_common_exponents(self):
        """Test isCoPrime() with common RSA exponents vs typical phi_N values."""
        # Simulate phi_N = (p-1)(q-1) for small primes
        p, q = 61, 53
        phi_N = integer((p - 1) * (q - 1))  # 3120

        # 65537 should be coprime to 3120 (gcd = 1)
        self.assertTrue(phi_N.isCoPrime(65537))
        # 3 should be coprime to 3120 (gcd = 3, not coprime!)
        self.assertFalse(phi_N.isCoPrime(3))
        # 17 should be coprime to 3120
        self.assertTrue(phi_N.isCoPrime(17))

    def test_coprime_with_integer_objects(self):
        """Test isCoPrime() with integer objects as arguments."""
        a = integer(35)  # 5 * 7
        self.assertTrue(a.isCoPrime(12))   # gcd(35, 12) = 1
        self.assertFalse(a.isCoPrime(15))  # gcd(35, 15) = 5
        self.assertTrue(a.isCoPrime(integer(12)))

    def test_coprime_edge_cases(self):
        """Test isCoPrime() edge cases."""
        one = integer(1)
        self.assertTrue(one.isCoPrime(12345))  # 1 is coprime to everything

        # Any number is coprime to 1
        n = integer(12345)
        self.assertTrue(n.isCoPrime(1))


class ModularArithmeticTest(unittest.TestCase):
    """Test modular arithmetic operations."""

    def test_modular_inverse_basic(self):
        """Test basic modular inverse computation."""
        # e = 3, modulus = 11, inverse should be 4 (3*4 = 12 ≡ 1 mod 11)
        e = integer(3, 11)
        d = e ** -1
        self.assertEqual(int(d), 4)
        # Verify: e * d ≡ 1 (mod 11)
        product = integer(int(e) * int(d), 11)
        self.assertEqual(int(product), 1)

    def test_modular_inverse_rsa_exponent(self):
        """Test modular inverse with RSA-like parameters."""
        # Small RSA example: p=61, q=53, phi_N=3120, e=17
        phi_N = 3120
        e = integer(17, phi_N)
        d = e ** -1
        # Verify: e * d ≡ 1 (mod phi_N)
        product = (int(e) * int(d)) % phi_N
        self.assertEqual(product, 1)

    def test_modular_operations_respect_modulus(self):
        """Test that modular operations respect the modulus."""
        modulus = 17
        a = integer(20, modulus)  # 20 mod 17 = 3
        self.assertEqual(int(a), 3)

        b = integer(100, modulus)  # 100 mod 17 = 15
        self.assertEqual(int(b), 15)

    def test_modular_exponentiation(self):
        """Test modular exponentiation."""
        base = integer(2, 13)
        # 2^10 = 1024, 1024 mod 13 = 10
        result = base ** 10
        self.assertEqual(int(result), 1024 % 13)

    def test_integer_without_modulus(self):
        """Test integer behavior when modulus is not set."""
        a = integer(65537)
        b = integer(12345)
        # Without modulus, operations should work as regular integers
        product = a * b
        self.assertEqual(int(product), 65537 * 12345)


class Python312CompatibilityTest(unittest.TestCase):
    """Regression tests for Python 3.12+ compatibility.

    These tests specifically target the Py_SIZE() vs lv_tag bug that was fixed.
    The bug caused incorrect digit count extraction for multi-digit integers.
    """

    def test_65537_regression(self):
        """Test the specific value that exposed the Python 3.12+ bug.

        In the buggy version, integer(65537) returned a huge incorrect value
        like 12259964326940877255866161939725058870607969088809533441.
        """
        result = integer(65537)
        self.assertEqual(int(result), 65537)
        # Also verify string representation
        self.assertEqual(str(result), "65537")

    def test_multi_digit_integers(self):
        """Test integers that require multiple digits in PyLongObject.

        Python uses 30-bit digits internally. Values >= 2^30 require multiple digits.
        The bug was in extracting the digit count from lv_tag.
        """
        # Single digit (< 2^30)
        single_digit = 2**29
        self.assertEqual(int(integer(single_digit)), single_digit)

        # Two digits (2^30 to 2^60-1)
        two_digits = 2**45
        self.assertEqual(int(integer(two_digits)), two_digits)

        # Three digits (2^60 to 2^90-1)
        three_digits = 2**75
        self.assertEqual(int(integer(three_digits)), three_digits)

        # Many digits
        many_digits = 2**300
        self.assertEqual(int(integer(many_digits)), many_digits)

    def test_sign_handling(self):
        """Test sign handling for negative integers.

        In Python 3.12+, sign is stored in lv_tag bits 0-1:
        - 0 = positive
        - 1 = zero
        - 2 = negative
        """
        # Positive
        pos = integer(12345)
        self.assertEqual(int(pos), 12345)
        self.assertGreater(int(pos), 0)

        # Zero
        zero = integer(0)
        self.assertEqual(int(zero), 0)

        # Negative
        neg = integer(-12345)
        self.assertEqual(int(neg), -12345)
        self.assertLess(int(neg), 0)

        # Large negative
        large_neg = integer(-2**100)
        self.assertEqual(int(large_neg), -2**100)

    def test_digit_boundary_values(self):
        """Test values at digit boundaries (multiples of 2^30)."""
        boundaries = [
            2**30 - 1, 2**30, 2**30 + 1,
            2**60 - 1, 2**60, 2**60 + 1,
            2**90 - 1, 2**90, 2**90 + 1,
        ]
        for val in boundaries:
            with self.subTest(value=f"2^{val.bit_length()-1}"):
                self.assertEqual(int(integer(val)), val)
                self.assertEqual(int(integer(-val)), -val)

    def test_mpz_to_pylong_roundtrip(self):
        """Test that mpzToLongObj correctly creates Python integers.

        This tests the reverse direction: GMP mpz_t -> Python int.
        """
        # Create integer, perform operation, convert back
        a = integer(2**100)
        b = integer(2**50)
        product = a * b
        expected = 2**100 * 2**50
        self.assertEqual(int(product), expected)


class IntegrationSchemeTest(unittest.TestCase):
    """Integration tests that mirror real cryptographic scheme usage."""

    def test_rsa_coprime_search_pattern(self):
        """Test the RSA keygen coprime search pattern.

        This mirrors the pattern used in pkenc_rsa.py to find e coprime to phi_N.
        """
        # Simulate small RSA parameters
        p, q = 61, 53
        N = p * q  # 3233
        phi_N = integer((p - 1) * (q - 1))  # 3120

        # Common RSA exponents to try
        common_exponents = [65537, 3, 5, 17, 257, 641]
        e_value = None

        for candidate in common_exponents:
            if phi_N.isCoPrime(candidate):
                e_value = candidate
                break

        self.assertIsNotNone(e_value, "Should find a coprime exponent")
        # Verify it's actually coprime
        self.assertEqual(int(gcd(e_value, int(phi_N))), 1)

        # Compute modular inverse
        e = integer(e_value, int(phi_N))
        d = e ** -1

        # Verify: e * d ≡ 1 (mod phi_N)
        product = (e_value * int(d)) % int(phi_N)
        self.assertEqual(product, 1)

    def test_rsa_encryption_decryption_pattern(self):
        """Test RSA encryption/decryption with integer operations."""
        # Small RSA parameters for testing
        p, q = 61, 53
        N = p * q  # 3233
        phi_N = (p - 1) * (q - 1)  # 3120
        e = 17
        d = int(integer(e, phi_N) ** -1)  # 2753

        # Encrypt message m = 123
        m = 123
        c = pow(m, e, N)  # c = 123^17 mod 3233 = 855

        # Decrypt
        m_decrypted = pow(c, d, N)
        self.assertEqual(m_decrypted, m)

    def test_paillier_pattern(self):
        """Test Paillier-like integer encoding pattern."""
        # Paillier uses n^2 as modulus
        p, q = 17, 19
        n = p * q  # 323
        n_squared = n * n  # 104329

        # Encode a message
        m = 42
        r = 7  # Random value coprime to n

        # g = n + 1 is a common choice
        g = n + 1

        # Encrypt: c = g^m * r^n mod n^2
        c = (pow(g, m, n_squared) * pow(r, n, n_squared)) % n_squared

        # Verify the ciphertext is in the correct range
        self.assertGreater(c, 0)
        self.assertLess(c, n_squared)

    def test_serialization_roundtrip(self):
        """Test serialization and deserialization of integer objects."""
        test_values = [0, 1, 65537, 2**128, 2**256, -12345, -2**100]
        for val in test_values:
            with self.subTest(value=val if abs(val) < 1000 else f"2^{abs(val).bit_length()-1}"):
                original = integer(val)
                serialized = serialize(original)
                deserialized = deserialize(serialized)
                self.assertEqual(int(deserialized), val)


class ArithmeticOperationsTest(unittest.TestCase):
    """Test basic arithmetic operations on integer objects."""

    def test_addition(self):
        """Test integer addition."""
        a = integer(100)
        b = integer(200)
        self.assertEqual(int(a + b), 300)
        self.assertEqual(int(a + 50), 150)

    def test_subtraction(self):
        """Test integer subtraction."""
        a = integer(200)
        b = integer(100)
        self.assertEqual(int(a - b), 100)
        self.assertEqual(int(a - 50), 150)

    def test_multiplication(self):
        """Test integer multiplication."""
        a = integer(12)
        b = integer(34)
        self.assertEqual(int(a * b), 408)
        self.assertEqual(int(a * 10), 120)

    def test_division(self):
        """Test integer division."""
        a = integer(100)
        b = integer(25)
        self.assertEqual(int(a / b), 4)

    def test_exponentiation(self):
        """Test integer exponentiation."""
        a = integer(2)
        self.assertEqual(int(a ** 10), 1024)

    def test_comparison(self):
        """Test integer comparison operations."""
        a = integer(100)
        b = integer(200)
        c = integer(100)

        self.assertTrue(a < b)
        self.assertTrue(b > a)
        self.assertTrue(a <= c)
        self.assertTrue(a >= c)
        self.assertTrue(a == c)
        self.assertTrue(a != b)


if __name__ == "__main__":
    unittest.main()

