import unittest

from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class CPabe_BSW07Test(unittest.TestCase):
    def testCPabe_BSW07(self):
        groupObj = PairingGroup('SS512')

        cpabe = CPabe_BSW07(groupObj)
        attrs = ['ONE', 'TWO', 'THREE']
        access_policy = '((four or three) and (three or one))'
        if debug:
            print("Attributes =>", attrs);
            print("Policy =>", access_policy)

        (pk, mk) = cpabe.setup()

        sk = cpabe.keygen(pk, mk, attrs)

        rand_msg = groupObj.random(GT)
        if debug: print("msg =>", rand_msg)
        ct = cpabe.encrypt(pk, rand_msg, access_policy)
        if debug: print("\n\nCiphertext...\n")
        groupObj.debug(ct)

        rec_msg = cpabe.decrypt(pk, sk, ct)
        if debug: print("\n\nDecrypt...\n")
        if debug: print("Rec msg =>", rec_msg)

        assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
        if debug: print("Successful Decryption!!!")


if __name__ == "__main__":
    unittest.main()
