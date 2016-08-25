import unittest

from charm.schemes.ibenc.ibenc_waters05 import IBE_N04
from charm.toolbox.hash_module import Waters
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class IBE_N04Test(unittest.TestCase):
    def testIBE_N04(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('SS512')
        waters = Waters(groupObj)
        ibe = IBE_N04(groupObj)
        (pk, mk) = ibe.setup()

        # represents public identity
        ID = "bob@mail.com"
        kID = waters.hash(ID)
        # if debug: print("Bob's key  =>", kID)
        key = ibe.extract(mk, kID)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(pk, kID, M)
        m = ibe.decrypt(pk, key, cipher)
        # print('m    =>', m)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!!! m => '%s'" % m)
        del groupObj
