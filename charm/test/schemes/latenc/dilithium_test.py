"""Tests for Dilithium signature scheme."""

import unittest

try:
    from charm.toolbox.latticegroup import LatticeGroup
    from charm.schemes.latenc.dilithium_sig import DilithiumSig
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False


@unittest.skipUnless(LATTICE_AVAILABLE, "Lattice module not available (NTL not installed)")
class DilithiumSigTest(unittest.TestCase):
    """Test Dilithium sign/verify."""

    def setUp(self):
        self.group = LatticeGroup('DILITHIUM-2')
        self.sig = DilithiumSig(self.group, 'DILITHIUM-2')

    def test_keygen(self):
        pk, sk = self.sig.keygen()
        self.assertIn('A', pk)
        self.assertIn('t', pk)
        self.assertIn('s1', sk)
        self.assertIn('s2', sk)

    def test_sign_verify(self):
        pk, sk = self.sig.keygen()
        msg = b"Test message"
        signature = self.sig.sign(sk, msg)
        self.assertTrue(self.sig.verify(pk, msg, signature))

    def test_wrong_message_fails(self):
        pk, sk = self.sig.keygen()
        msg = b"Original message"
        signature = self.sig.sign(sk, msg)
        self.assertFalse(self.sig.verify(pk, b"Tampered message", signature))

    def test_multiple_roundtrips(self):
        """Test 10 sign/verify cycles with fresh keys."""
        for i in range(10):
            pk, sk = self.sig.keygen()
            msg = f"Message {i}".encode()
            signature = self.sig.sign(sk, msg)
            self.assertTrue(self.sig.verify(pk, msg, signature), f"Failed on trial {i}")

    def test_empty_message(self):
        pk, sk = self.sig.keygen()
        msg = b""
        signature = self.sig.sign(sk, msg)
        self.assertTrue(self.sig.verify(pk, msg, signature))

    def test_long_message(self):
        pk, sk = self.sig.keygen()
        msg = b"A" * 1000
        signature = self.sig.sign(sk, msg)
        self.assertTrue(self.sig.verify(pk, msg, signature))

    def test_string_message(self):
        pk, sk = self.sig.keygen()
        msg = "Unicode string 🔐"
        signature = self.sig.sign(sk, msg)
        self.assertTrue(self.sig.verify(pk, msg, signature))


if __name__ == '__main__':
    unittest.main()
