import unittest

from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.toolbox.pairinggroup import PairingGroup, GT

debug = False


class HashIDAdapterTest(unittest.TestCase):
    def testHashIDAdapter(self):
        group = PairingGroup('SS512')

        ibe = IBE_BB04(group)

        hashID = HashIDAdapter(ibe, group)

        (pk, mk) = hashID.setup()

        kID = 'waldoayo@email.com'
        sk = hashID.extract(mk, kID)
        if debug: print("Keygen for %s" % kID)
        if debug: print(sk)

        m = group.random(GT)
        ct = hashID.encrypt(pk, kID, m)

        orig_m = hashID.decrypt(pk, sk, ct)

        assert m == orig_m
        if debug: print("Successful Decryption!!!")
        if debug: print("Result =>", orig_m)
