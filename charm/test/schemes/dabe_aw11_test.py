import unittest

from charm.schemes.abenc.dabe_aw11 import Dabe
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class DabeTest(unittest.TestCase):
    def testDabe(self):
        groupObj = PairingGroup('SS512')

        dabe = Dabe(groupObj)
        GP = dabe.setup()

        # Setup an authority
        auth_attrs = ['ONE', 'TWO', 'THREE', 'FOUR']
        (SK, PK) = dabe.authsetup(GP, auth_attrs)
        if debug: print("Authority SK")
        if debug: print(SK)

        # Setup a user and give him some keys
        gid, K = "bob", {}
        usr_attrs = ['THREE', 'ONE', 'TWO']
        for i in usr_attrs: dabe.keygen(GP, SK, i, gid, K)
        if debug: print('User credential list: %s' % usr_attrs)
        if debug: print("\nSecret key:")
        if debug: groupObj.debug(K)

        # Encrypt a random element in GT
        m = groupObj.random(GT)
        policy = '((one or three) and (TWO or FOUR))'
        if debug: print('Acces Policy: %s' % policy)
        CT = dabe.encrypt(GP, PK, m, policy)
        if debug: print("\nCiphertext...")
        if debug: groupObj.debug(CT)

        orig_m = dabe.decrypt(GP, K, CT)

        assert m == orig_m, 'FAILED Decryption!!!'
        if debug: print('Successful Decryption!')


if __name__ == "__main__":
    unittest.main()
