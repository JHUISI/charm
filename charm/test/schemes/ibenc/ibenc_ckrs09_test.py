import unittest

from charm.schemes.ibenc.ibenc_ckrs09 import IBE_CKRS
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class IBE_CKRSTest(unittest.TestCase):
    def testIBE_CKRS(self):
        groupObj = PairingGroup('SS512')
        ibe = IBE_CKRS(groupObj)
        (mpk, msk) = ibe.setup()

        # represents public identity
        ID = "bob@mail.com"
        sk = ibe.extract(mpk, msk, ID)

        M = groupObj.random(GT)
        ct = ibe.encrypt(mpk, ID, M)
        m = ibe.decrypt(mpk, sk, ct)
        if debug: print('m    =>', m)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!!! m => '%s'" % m)
