"""Tests for Kyber KEM scheme."""

import unittest

try:
    from charm.toolbox.latticegroup import LatticeGroup
    from charm.schemes.latenc.kyber_kem import KyberKEM
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


@unittest.skipUnless(LATTICE_AVAILABLE, "Lattice module not available (NTL not installed)")
class KyberKEMTest(unittest.TestCase):
    """Test Kyber KEM encapsulate/decapsulate."""

    def setUp(self):
        self.group = LatticeGroup('KYBER-768')
        self.kem = KyberKEM(self.group, 'KYBER-768')

    def test_keygen(self):
        pk, sk = self.kem.keygen()
        self.assertIn('A', pk)
        self.assertIn('t', pk)
        self.assertIn('s', sk)

    def test_encapsulate_decapsulate(self):
        pk, sk = self.kem.keygen()
        ct, ss_enc = self.kem.encapsulate(pk)
        ss_dec = self.kem.decapsulate(sk, ct)
        self.assertEqual(ss_enc, ss_dec)
        self.assertEqual(len(ss_enc), 32)  # SHA-256 output

    def test_multiple_roundtrips(self):
        """Test 10 encap/decap cycles with fresh keys."""
        for i in range(10):
            pk, sk = self.kem.keygen()
            ct, ss1 = self.kem.encapsulate(pk)
            ss2 = self.kem.decapsulate(sk, ct)
            self.assertEqual(ss1, ss2, f"Failed on trial {i}")

    def test_wrong_key_fails(self):
        """Decapsulating with wrong key should produce different shared secret."""
        pk1, sk1 = self.kem.keygen()
        pk2, sk2 = self.kem.keygen()
        ct, ss_enc = self.kem.encapsulate(pk1)
        ss_dec = self.kem.decapsulate(sk2, ct)
        self.assertNotEqual(ss_enc, ss_dec)

    def test_kyber_512(self):
        group = LatticeGroup('KYBER-512')
        kem = KyberKEM(group, 'KYBER-512')
        pk, sk = kem.keygen()
        ct, ss1 = kem.encapsulate(pk)
        ss2 = kem.decapsulate(sk, ct)
        self.assertEqual(ss1, ss2)

    def test_kyber_1024(self):
        group = LatticeGroup('KYBER-1024')
        kem = KyberKEM(group, 'KYBER-1024')
        pk, sk = kem.keygen()
        ct, ss1 = kem.encapsulate(pk)
        ss2 = kem.decapsulate(sk, ct)
        self.assertEqual(ss1, ss2)


if __name__ == '__main__':
    unittest.main()
