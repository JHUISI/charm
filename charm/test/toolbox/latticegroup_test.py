"""Tests for LatticeGroup wrapper and core lattice operations."""

import unittest

try:
    from charm.toolbox.latticegroup import LatticeGroup, POLY, ZQ, VEC, MAT
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


@unittest.skipUnless(LATTICE_AVAILABLE, "Lattice module not available (NTL not installed)")
class LatticeGroupTest(unittest.TestCase):
    """Test LatticeGroup construction and basic operations."""

    def setUp(self):
        self.group = LatticeGroup('RLWE-256-7681')

    def test_construction_named(self):
        g = LatticeGroup('RLWE-256-7681')
        self.assertEqual(g.degree(), 256)
        self.assertEqual(g.order(), 7681)
        self.assertEqual(g.groupSetting(), 'lattice')
        self.assertEqual(g.groupType(), 'RLWE-256-7681')

    def test_construction_custom(self):
        g = LatticeGroup(n=512, q=12289)
        self.assertEqual(g.degree(), 512)
        self.assertEqual(g.order(), 12289)

    def test_construction_bad_params(self):
        with self.assertRaises(ValueError):
            LatticeGroup('NONEXISTENT')
        with self.assertRaises(ValueError):
            LatticeGroup()  # no params
        with self.assertRaises(ValueError):
            LatticeGroup(n=7, q=7681)  # n not power of 2

    def test_random_poly(self):
        a = self.group.random(POLY)
        self.assertIsNotNone(a)
        self.assertTrue(self.group.ismember(a))

    def test_random_zq(self):
        s = self.group.random(ZQ)
        self.assertIsNotNone(s)
        self.assertTrue(self.group.ismember(s))

    def test_poly_addition_commutative(self):
        a = self.group.random(POLY)
        b = self.group.random(POLY)
        self.assertEqual(a + b, b + a)

    def test_poly_multiplication(self):
        a = self.group.random(POLY)
        b = self.group.random(POLY)
        c = a * b
        self.assertIsNotNone(c)
        self.assertTrue(self.group.ismember(c))

    def test_scalar_multiply(self):
        a = self.group.random(POLY)
        three_a = a + a + a
        self.assertEqual(a * 3, three_a)

    def test_negation(self):
        a = self.group.random(POLY)
        z = a + (-a)
        # All coefficients should be 0
        for i in range(self.group.degree()):
            self.assertEqual(self.group.get_coeff(z, i), 0)

    def test_equality(self):
        a = self.group.random(POLY)
        b = self.group.random(POLY)
        self.assertEqual(a, a)
        # Two random polynomials are overwhelmingly likely to differ
        self.assertNotEqual(a, b)

    def test_serialize_deserialize_poly(self):
        a = self.group.random(POLY)
        data = self.group.serialize(a)
        a2 = self.group.deserialize(data)
        self.assertEqual(a, a2)

    def test_serialize_deserialize_zq(self):
        s = self.group.random(ZQ)
        data = self.group.serialize(s)
        s2 = self.group.deserialize(data)
        self.assertEqual(s, s2)

    def test_serialize_deserialize_vec(self):
        v = self.group.random_vec(3)
        data = self.group.serialize(v)
        v2 = self.group.deserialize(data)
        self.assertEqual(v, v2)

    def test_serialize_deserialize_mat(self):
        A = self.group.random_mat(2, 3)
        data = self.group.serialize(A)
        A2 = self.group.deserialize(data)
        self.assertEqual(A, A2)

    def test_hash_deterministic(self):
        h1 = self.group.hash(b'test', POLY)
        h2 = self.group.hash(b'test', POLY)
        self.assertEqual(h1, h2)

    def test_hash_different_inputs(self):
        h1 = self.group.hash(b'hello', POLY)
        h2 = self.group.hash(b'world', POLY)
        self.assertNotEqual(h1, h2)

    def test_encode_decode_roundtrip(self):
        msg = b'Hello!'
        encoded = self.group.encode(msg)
        decoded = self.group.decode(encoded, num_bytes=len(msg))
        self.assertEqual(msg, decoded)

    def test_gaussian(self):
        g = self.group.gaussian(3.0)
        self.assertIsNotNone(g)
        self.assertTrue(self.group.ismember(g))

    def test_vec_operations(self):
        v1 = self.group.random_vec(3)
        v2 = self.group.random_vec(3)
        s = v1 + v2  # vector addition
        self.assertIsNotNone(s)
        ip = v1 * v2  # inner product -> POLY
        self.assertIsNotNone(ip)

    def test_mat_vec_multiply(self):
        A = self.group.random_mat(2, 3)
        v = self.group.random_vec(3)
        result = A * v
        self.assertIsNotNone(result)

    def test_mat_transpose(self):
        A = self.group.random_mat(2, 3)
        A_T = self.group.mat_transpose(A)
        self.assertIsNotNone(A_T)

    def test_kyber_params(self):
        g = LatticeGroup('KYBER-768')
        self.assertEqual(g.degree(), 256)
        self.assertEqual(g.order(), 3329)

    def test_dilithium_params(self):
        g = LatticeGroup('DILITHIUM-2')
        self.assertEqual(g.degree(), 256)
        self.assertEqual(g.order(), 8380417)


if __name__ == '__main__':
    unittest.main()
