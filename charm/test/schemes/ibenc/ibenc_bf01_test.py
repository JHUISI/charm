import unittest

from charm.schemes.ibenc.ibenc_bf01 import IBE_BonehFranklin
from charm.toolbox.pairinggroup import PairingGroup

debug = False


class IBE_BonehFranklinTest(unittest.TestCase):
    def testIBE_BonehFranklin(self):
        groupObj = PairingGroup('MNT224', secparam=1024)
        ibe = IBE_BonehFranklin(groupObj)

        (pk, sk) = ibe.setup()

        id = 'user@email.com'
        key = ibe.extract(sk, id)

        m = b"hello world!!!!!"
        ciphertext = ibe.encrypt(pk, id, m)

        msg = ibe.decrypt(pk, key, ciphertext)
        assert msg == m, "failed decrypt: \n%s\n%s" % (msg, m)
        if debug: print("Successful Decryption!!!")
