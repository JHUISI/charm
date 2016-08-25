import unittest

from charm.schemes.abenc.abenc_lsw08 import KPabe
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class KPabeTest(unittest.TestCase):
    def testKPabe(self):
        groupObj = PairingGroup('MNT224')
        kpabe = KPabe(groupObj)

        (pk, mk) = kpabe.setup()

        policy = '(ONE or THREE) and (THREE or TWO)'
        attributes = ['ONE', 'TWO', 'THREE', 'FOUR']
        msg = groupObj.random(GT)

        mykey = kpabe.keygen(pk, mk, policy)

        if debug: print("Encrypt under these attributes: ", attributes)
        ciphertext = kpabe.encrypt(pk, msg, attributes)
        if debug: print(ciphertext)

        rec_msg = kpabe.decrypt(ciphertext, mykey)

        assert msg == rec_msg
        if debug: print("Successful Decryption!")


if __name__ == "__main__":
    unittest.main()
