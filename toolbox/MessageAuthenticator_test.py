import unittest 
from toolbox.pairinggroup import PairingGroup,GT
from charm.pairing import hash as sha1
from MessageAuthenticator import MessageAuthenticator
class TestMessageAuthenticator(unittest.TestCase):
    def testSelfVerify(self):
        key = sha1(PairingGroup('../param/a.param').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        assert m.verify(a), "expected message to verify";

    def testSeperateVerify(self):
        key = sha1(PairingGroup('../param/a.param').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        assert m1.verify(a), "expected message to verify";
 
    def testTamperData(self):
        key = sha1(PairingGroup('../param/a.param').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["msg"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperMac(self):
        key = sha1(PairingGroup('../param/a.param').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        a["digest"]= "tampered" 
        assert not m1.verify(a), "expected message to verify";

    def testTamperAlg(self):
        key = sha1(PairingGroup('../param/a.param').random(GT))
        m = MessageAuthenticator(key)
        a = m.mac('hello world')
        m1 = MessageAuthenticator(key)
        m1._algorithm = "alg" # bypassing the algorithm check to verify the mac is over the alg + data 
        a["alg"]= "alg" 
        assert not m1.verify(a), "expected message to verify";

        
    
    
