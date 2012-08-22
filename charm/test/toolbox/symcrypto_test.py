import unittest 
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction,AuthenticatedCryptoAbstraction, MessageAuthenticator
from charm.toolbox.pairinggroup import PairingGroup,GT
from charm.core.math.pairing import hashPair as sha1
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
        a =  SymmetricCryptoAbstraction(sha1(groupObj.random(GT)))
        ct = a.encrypt(msg)
        dmsg = a.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)
   
    def MsgTestAESCBCSeperate(self,msg):
        groupObj = PairingGroup('SS512')
        ran = groupObj.random(GT)
        a =  SymmetricCryptoAbstraction(sha1(ran))
        ct = a.encrypt(msg)        
        b =  SymmetricCryptoAbstraction(sha1(ran))
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
        a =  AuthenticatedCryptoAbstraction(sha1(groupObj.random(GT)))
        ct = a.encrypt(msg)
        dmsg = a.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)
   
    def MsgTestAESCBCSeperate(self,msg):
        groupObj = PairingGroup('SS512')
        ran = groupObj.random(GT)
        a =  AuthenticatedCryptoAbstraction(sha1(ran))
        ct = a.encrypt(msg)        
        b =  AuthenticatedCryptoAbstraction(sha1(ran))
        dmsg = b.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)

class MessageAuthenticatorTest(unittest.TestCase):
    def testSelfVerify(self):
        key = sha1(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        assert m.verify(a), "expected message to verify";

    def testSeperateVerify(self):
        key = sha1(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        assert m1.verify(a), "expected message to verify";
 
    def testTamperData(self):
        key = sha1(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["msg"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperMac(self):
        key = sha1(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["digest"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperAlg(self):
        key = sha1(PairingGroup('SS512').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        m1._algorithm = "alg" # bypassing the algorithm check to verify the mac is over the alg + data 
        a["alg"]= "alg" 
        assert not m1.verify(a), "expected message to verify";

if __name__ == "__main__":
    unittest.main()

