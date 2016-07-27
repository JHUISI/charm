import unittest

from charm.adapters.kpabenc_adapt_hybrid import HybridABEnc as HybridKPABEnc
from charm.schemes.abenc.abenc_lsw08 import KPabe
from charm.toolbox.pairinggroup import PairingGroup

debug = False


class HybridKPABEncTest(unittest.TestCase):
    def testHybridKPABEnc(self):
        groupObj = PairingGroup('SS512')
        kpabe = KPabe(groupObj)
        hyb_abe = HybridKPABEnc(kpabe, groupObj)
        access_key = '((ONE or TWO) and THREE)'
        access_policy = ['ONE', 'TWO', 'THREE']
        message = b"hello world this is an important message."
        (pk, mk) = hyb_abe.setup()
        if debug: print("pk => ", pk)
        if debug: print("mk => ", mk)
        sk = hyb_abe.keygen(pk, mk, access_key)
        if debug: print("sk => ", sk)
        ct = hyb_abe.encrypt(pk, message, access_policy)
        mdec = hyb_abe.decrypt(ct, sk)
        assert mdec == message, "Failed Decryption!!!"
        if debug: print("Successful Decryption!!!")


if __name__ == "__main__":
    unittest.main()
