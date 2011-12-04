import unittest 
from SymmetricCryptoAbstraction import SymmetricCryptoAbstraction
from toolbox.pairinggroup import PairingGroup,GT
from charm.pairing import hash as sha1
class TesSymmetricCryptoAbstraction(unittest.TestCase):
    
    def testAESCBC(self):
       self.MsgtestAESCBC("hello world")

    def testAESCBCLong(self):
       self.MsgtestAESCBC("Lots of people working in cryptography have no deep \
       concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")
    def testAESCBC_Seperate(self):
        self.MsgTestAESCBCSeperate("Lots of people working in cryptography have no deep \
        concern with real application issues. They are trying to discover things \
        clever enough to write papers about -- Whitfield Diffie.")


    def MsgtestAESCBC(sef,msg):
        groupObj = PairingGroup('../param/a.param')
        a =  SymmetricCryptoAbstraction(sha1(groupObj.random(GT)))
        ct = a.encrypt(msg)
        dmsg = a.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)
   
    def MsgTestAESCBCSeperate(self,msg):
        groupObj = PairingGroup('../param/a.param')
        ran = groupObj.random(GT)
        a =  SymmetricCryptoAbstraction(sha1(ran))
        ct = a.encrypt(msg)        
        b =  SymmetricCryptoAbstraction(sha1(ran))
        dmsg = b.decrypt(ct);
        assert msg == dmsg , 'o: =>%s\nm: =>%s' % (msg, dmsg)

               





