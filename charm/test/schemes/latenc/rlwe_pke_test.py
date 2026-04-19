"""Tests for RLWE Public Key Encryption scheme."""

import unittest

try:
    from charm.toolbox.latticegroup import LatticeGroup
    from charm.schemes.latenc.rlwe_pke import RLWE_PKE
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


@unittest.skipUnless(LATTICE_AVAILABLE, "Lattice module not available (NTL not installed)")
class RLWE_PKETest(unittest.TestCase):
    """Test Ring-LWE PKE encrypt/decrypt roundtrip."""

    def setUp(self):
        self.group = LatticeGroup('RLWE-256-7681')
        self.rlwe = RLWE_PKE(self.group, sigma=3.0)

    def test_keygen(self):
        pk, sk = self.rlwe.keygen()
        self.assertIn('a', pk)
        self.assertIn('b', pk)
        self.assertIn('s', sk)

    def test_encrypt_decrypt_roundtrip(self):
        pk, sk = self.rlwe.keygen()
        msg = b"Hello, lattice world!"
        ct = self.rlwe.encrypt(pk, msg)
        dec = self.rlwe.decrypt(sk, ct)[:len(msg)]
        self.assertEqual(msg, dec)

    def test_short_message(self):
        pk, sk = self.rlwe.keygen()
        msg = b"A"
        ct = self.rlwe.encrypt(pk, msg)
        dec = self.rlwe.decrypt(sk, ct)[:len(msg)]
        self.assertEqual(msg, dec)

    def test_max_length_message(self):
        pk, sk = self.rlwe.keygen()
        msg = b'\xAA' * 32  # n/8 = 32 bytes max
        ct = self.rlwe.encrypt(pk, msg)
        dec = self.rlwe.decrypt(sk, ct)[:len(msg)]
        self.assertEqual(msg, dec)

    def test_message_too_long(self):
        pk, sk = self.rlwe.keygen()
        msg = b'X' * 33  # exceeds 32 bytes
        with self.assertRaises(ValueError):
            self.rlwe.encrypt(pk, msg)

    def test_multiple_roundtrips(self):
        """Test 10 encrypt/decrypt cycles with fresh keys."""
        for i in range(10):
            pk, sk = self.rlwe.keygen()
            msg = f"Message {i}".encode()
            ct = self.rlwe.encrypt(pk, msg)
            dec = self.rlwe.decrypt(sk, ct)[:len(msg)]
            self.assertEqual(msg, dec, f"Failed on trial {i}")

    def test_wrong_key_fails(self):
        """Decrypting with wrong key should produce garbage."""
        pk1, sk1 = self.rlwe.keygen()
        pk2, sk2 = self.rlwe.keygen()
        msg = b"Secret message"
        ct = self.rlwe.encrypt(pk1, msg)
        dec = self.rlwe.decrypt(sk2, ct)[:len(msg)]
        # With overwhelming probability, wrong key produces wrong result
        self.assertNotEqual(msg, dec)

    def test_different_params(self):
        """Test with different parameter set."""
        group2 = LatticeGroup('RLWE-512-12289')
        rlwe2 = RLWE_PKE(group2, sigma=3.0)
        pk, sk = rlwe2.keygen()
        msg = b"Different ring"
        ct = rlwe2.encrypt(pk, msg)
        dec = rlwe2.decrypt(sk, ct)[:len(msg)]
        self.assertEqual(msg, dec)


if __name__ == '__main__':
    unittest.main()
