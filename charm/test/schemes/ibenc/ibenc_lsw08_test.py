import unittest

from charm.schemes.ibenc.ibenc_lsw08 import IBE_Revoke
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class IBE_RevokeTest(unittest.TestCase):
    def testIBE_Revoke(self):
        # scheme designed for symmetric billinear groups
        grp = PairingGroup('SS512')
        n = 5  # total # of users

        ibe = IBE_Revoke(grp)

        ID = "user2@email.com"
        S = ["user1@email.com", "user3@email.com", "user4@email.com"]
        (mpk, msk) = ibe.setup(n)

        sk = ibe.keygen(mpk, msk, ID)
        if debug: print("Keygen...\nsk :=", sk)

        M = grp.random(GT)

        ct = ibe.encrypt(mpk, M, S)
        if debug: print("Ciphertext...\nct :=", ct)

        m = ibe.decrypt(S, ct, sk)
        assert M == m, "Decryption FAILED!"
        if debug: print("Successful Decryption!!!")
