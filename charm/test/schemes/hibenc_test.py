from charm.schemes.hibenc.hibenc_bb04 import HIBE_BB04
from charm.toolbox.pairinggroup import PairingGroup, GT
import unittest

debug = False

class HIBE_BB04Test(unittest.TestCase):
    def testHIBE_BB04(self):
        groupObj = PairingGroup('SS512')
        hibe = HIBE_BB04(groupObj)
        (mpk, mk) = hibe.setup()

        # represents public identity
        ID = "bob@mail.com"
        (pk, sk) = hibe.extract(3, mpk, mk, ID)
        # dID => pk, sk
        if debug: print("ID:%s , sk:%s" % (pk, sk))
        
        M = groupObj.random(GT)
        if debug: print("M :=", M)
        ct = hibe.encrypt(mpk, pk, M)
        
        orig_M = hibe.decrypt(pk, sk, ct)
        assert orig_M == M, "invalid decryption!!!!"
        if debug: print("Successful DECRYPTION!!!")

if __name__ == "__main__":
    unittest.main()
