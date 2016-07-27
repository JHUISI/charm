import unittest

from charm.schemes.ibenc.ibenc_sw05 import IBE_SW05_LUC
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class IBE_SW05_LUCTest(unittest.TestCase):
    def testIBE_SW05_LUC(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('SS512')
        n = 6;
        d = 4
        ibe = IBE_SW05_LUC(groupObj)
        (pk, mk) = ibe.setup(n, d)
        if debug:
            print("Parameter Setup...")
            print("pk =>", pk)
            print("mk =>", mk)

        w = ['insurance', 'id=2345', 'oncology', 'doctor', 'nurse', 'JHU']  # private identity
        wPrime = ['insurance', 'id=2345', 'doctor', 'oncology', 'JHU', 'billing', 'misc']  # public identity for encrypt

        (w_hashed, sk) = ibe.extract(mk, w, pk, d, n)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(pk, wPrime, M, n)
        m = ibe.decrypt(pk, sk, cipher, w_hashed, d)

        assert m == M, "FAILED Decryption: \nrecovered m = %s and original m = %s" % (m, M)
        if debug: print("Successful Decryption!! M => '%s'" % m)
