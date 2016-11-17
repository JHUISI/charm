import unittest

from charm.schemes.abenc.abenc_waters09 import CPabe09
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class CPabe09Test(unittest.TestCase):
    def testCPabe(self):
        # Get the eliptic curve with the bilinear mapping feature needed.
        groupObj = PairingGroup('SS512')

        cpabe = CPabe09(groupObj)
        (msk, pk) = cpabe.setup()
        pol = '((ONE or THREE) and (TWO or FOUR))'
        attr_list = ['THREE', 'ONE', 'TWO']

        if debug: print('Acces Policy: %s' % pol)
        if debug: print('User credential list: %s' % attr_list)
        m = groupObj.random(GT)

        cpkey = cpabe.keygen(pk, msk, attr_list)
        if debug: print("\nSecret key: %s" % attr_list)
        if debug: groupObj.debug(cpkey)
        cipher = cpabe.encrypt(pk, m, pol)

        if debug: print("\nCiphertext...")
        if debug: groupObj.debug(cipher)
        orig_m = cpabe.decrypt(pk, cpkey, cipher)

        assert m == orig_m, 'FAILED Decryption!!!'
        if debug: print('Successful Decryption!')
        del groupObj


if __name__ == "__main__":
    unittest.main()
