import unittest 
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction,AuthenticatedCryptoAbstraction, MessageAuthenticator
from charm.toolbox.pairinggroup import PairingGroup,GT
from charm.core.math.pairing import hashPair as sha2
class SymmetricCryptoAbstractionTest(unittest.TestCase):
    
    def testAESCBC(self):
        self.MsgtestAESCBC(b"hello world")

    def testAESCBCLong(self):
        self.MsgtestAESCBC(b"Lots of people working in cryptography have no deep \
       concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")
        
    def testAESCBC_Seperate(self):
        self.MsgTestAESCBCSeperate(b"Lots of people working in cryptography have no deep \
        concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")

    def MsgtestAESCBC(self,msg):
        groupObj = PairingGroup('SS512')
        a =  SymmetricCryptoAbstraction(sha2(groupObj.random(GT)))
        ct = a.encrypt(msg)
        dmsg = a.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)
   
    def MsgTestAESCBCSeperate(self,msg):
        groupObj = PairingGroup('SS512')
        ran = groupObj.random(GT)
        a =  SymmetricCryptoAbstraction(sha2(ran))
        ct = a.encrypt(msg)        
        b =  SymmetricCryptoAbstraction(sha2(ran))
        dmsg = b.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)

class AuthenticatedCryptoAbstractionTest(unittest.TestCase):
    
    def testAESCBC(self):
       self.MsgtestAESCBC(b"hello world")

    def testAESCBCLong(self):
       self.MsgtestAESCBC(b"Lots of people working in cryptography have no deep \
       concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")
    def testAESCBC_Seperate(self):
        self.MsgTestAESCBCSeperate(b"Lots of people working in cryptography have no deep \
        concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")


    def MsgtestAESCBC(self,msg):
        groupObj = PairingGroup('SS512')
        a =  AuthenticatedCryptoAbstraction(sha2(groupObj.random(GT)))
        ct = a.encrypt(msg)
        dmsg = a.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)
   
    def MsgTestAESCBCSeperate(self,msg):
        groupObj = PairingGroup('SS512')
        ran = groupObj.random(GT)
        a =  AuthenticatedCryptoAbstraction(sha2(ran))
        ct = a.encrypt(msg)        
        b =  AuthenticatedCryptoAbstraction(sha2(ran))
        dmsg = b.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)

class MessageAuthenticatorTest(unittest.TestCase):
    def testSelfVerify(self):
        key = sha2(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        assert m.verify(a), "expected message to verify";

    def testSeperateVerify(self):
        key = sha2(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        assert m1.verify(a), "expected message to verify";
 
    def testTamperData(self):
        key = sha2(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["msg"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperMac(self):
        key = sha2(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["digest"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperAlg(self):
        key = sha2(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        m1._algorithm = "alg" # bypassing the algorithm check to verify the mac is over the alg + data 
        a["alg"]= "alg" 
        assert not m1.verify(a), "expected message to verify";

try:
    from charm.toolbox.symcrypto import AESGCMCryptoAbstraction
    GCM_AVAILABLE = True
except ImportError:
    GCM_AVAILABLE = False

@unittest.skipUnless(GCM_AVAILABLE, "AES-GCM requires 'cryptography' package")
class AESGCMCryptoAbstractionTest(unittest.TestCase):

    def _make_key(self, size=16):
        from hashlib import sha256
        return sha256(b'test-key').digest()[:size]

    def test_encrypt_decrypt(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        ct = cipher.encrypt(b"hello world")
        pt = cipher.decrypt(ct)
        self.assertEqual(pt, b"hello world")

    def test_encrypt_decrypt_long(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        msg = b"Lots of people working in cryptography have no deep " \
              b"concern with real application issues. -- Whitfield Diffie."
        ct = cipher.encrypt(msg)
        self.assertEqual(cipher.decrypt(ct), msg)

    def test_string_input(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        ct = cipher.encrypt("unicode string \u2603")
        self.assertEqual(cipher.decrypt(ct), "unicode string \u2603".encode('utf-8'))

    def test_associated_data(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        ad = b"authenticated header"
        ct = cipher.encrypt(b"payload", associatedData=ad)
        self.assertEqual(cipher.decrypt(ct, associatedData=ad), b"payload")

    def test_wrong_associated_data_fails(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        ct = cipher.encrypt(b"payload", associatedData=b"correct")
        with self.assertRaises(ValueError):
            cipher.decrypt(ct, associatedData=b"wrong")

    def test_wrong_key_fails(self):
        cipher1 = AESGCMCryptoAbstraction(self._make_key())
        ct = cipher1.encrypt(b"secret")
        cipher2 = AESGCMCryptoAbstraction(b'\x00' * 16)
        with self.assertRaises(ValueError):
            cipher2.decrypt(ct)

    def test_separate_instances(self):
        key = self._make_key()
        ct = AESGCMCryptoAbstraction(key).encrypt(b"shared key test")
        pt = AESGCMCryptoAbstraction(key).decrypt(ct)
        self.assertEqual(pt, b"shared key test")

    def test_aes256(self):
        key = self._make_key(32)
        cipher = AESGCMCryptoAbstraction(key)
        ct = cipher.encrypt(b"AES-256-GCM")
        self.assertEqual(cipher.decrypt(ct), b"AES-256-GCM")

    def test_bad_key_length(self):
        with self.assertRaises(ValueError):
            AESGCMCryptoAbstraction(b"short")

    def test_empty_message(self):
        cipher = AESGCMCryptoAbstraction(self._make_key())
        ct = cipher.encrypt(b"")
        self.assertEqual(cipher.decrypt(ct), b"")

if __name__ == "__main__":
    unittest.main()

