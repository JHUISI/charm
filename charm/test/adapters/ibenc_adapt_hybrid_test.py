import unittest

from charm.adapters.ibenc_adapt_hybrid import HybridIBEnc
from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.toolbox.pairinggroup import PairingGroup

debug = False


class HybridIBEncTest(unittest.TestCase):
    def testHybridIBEnc(self):
        groupObj = PairingGroup('SS512')
        ibe = IBE_BB04(groupObj)

        hashID = HashIDAdapter(ibe, groupObj)

        hyb_ibe = HybridIBEnc(hashID, groupObj)

        (pk, mk) = hyb_ibe.setup()

        kID = 'waldoayo@gmail.com'
        sk = hyb_ibe.extract(mk, kID)

        msg = b"This is a test message."

        ct = hyb_ibe.encrypt(pk, kID, msg)
        if debug:
            print("Ciphertext")
            print("c1 =>", ct['c1'])
            print("c2 =>", ct['c2'])

        decrypted_msg = hyb_ibe.decrypt(pk, sk, ct)
        if debug: print("Result =>", decrypted_msg)
        assert decrypted_msg == msg
        del groupObj
