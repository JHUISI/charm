import unittest

from charm.schemes.ibenc.ibenc_waters09 import DSE09
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class DSE09Test(unittest.TestCase):
    def testDSE09(self):
        grp = PairingGroup('SS512')

        ibe = DSE09(grp)

        ID = "user2@email.com"
        (mpk, msk) = ibe.setup()

        sk = ibe.keygen(mpk, msk, ID)
        if debug: print("Keygen...\nsk :=", sk)

        M = grp.random(GT)
        ct = ibe.encrypt(mpk, M, ID)
        if debug: print("Ciphertext...\nct :=", ct)

        m = ibe.decrypt(ct, sk)
        assert M == m, "Decryption FAILED!"
        if debug: print("Successful Decryption!!!")
