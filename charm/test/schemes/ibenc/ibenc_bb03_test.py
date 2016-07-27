import unittest

from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.pairinggroup import ZR, GT

debug = False


class IBE_BB04Test(unittest.TestCase):
    def testIBE_BB04(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('MNT224')
        ibe = IBE_BB04(groupObj)
        (params, mk) = ibe.setup()

        # represents public identity
        kID = groupObj.random(ZR)
        key = ibe.extract(mk, kID)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(params, kID, M)
        m = ibe.decrypt(params, key, cipher)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!! M => '%s'" % m)
