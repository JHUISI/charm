import unittest

from charm.adapters.abenc_adapt_hybrid import HybridABEnc as HybridABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup

debug = False


class HybridABEncTest(unittest.TestCase):
    def testHybridABEnc(self):
        groupObj = PairingGroup('SS512')
        cpabe = CPabe_BSW07(groupObj)
        hyb_abe = HybridABEnc(cpabe, groupObj)
        access_policy = '((four or three) and (two or one))'
        message = b"hello world this is an important message."
        (pk, mk) = hyb_abe.setup()
        if debug: print("pk => ", pk)
        if debug: print("mk => ", mk)
        sk = hyb_abe.keygen(pk, mk, ['ONE', 'TWO', 'THREE'])
        if debug: print("sk => ", sk)
        ct = hyb_abe.encrypt(pk, message, access_policy)
        mdec = hyb_abe.decrypt(pk, sk, ct)
        assert mdec == message, "Failed Decryption!!!"
        if debug: print("Successful Decryption!!!")


if __name__ == "__main__":
    unittest.main()
