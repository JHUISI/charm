'''
:Date: Aug 26, 2016
:Authors: J. Ayo Akinyele
'''
from charm.toolbox.ecgroup import ECGroup,G
from charm.toolbox.eccurve import prime192v1,prime192v2
from charm.toolbox.securerandom import OpenSSLRand
import unittest

runs = 10

class ECGroupEncodeAndDecode(unittest.TestCase):
    def testRandomGroupDecode(self):
        group = ECGroup(prime192v1)

        for i in range(runs):
            r = group.random(G)
            m = group.decode(r, True)
            n = group.encode(m, True)
            assert r == n, "Failed to encode/decode properly including counter"

    def testRandomMessageDecode(self):
        group = ECGroup(prime192v2)
        for i in range(runs):
            msg_len = group.bitsize()
            s = OpenSSLRand().getRandomBytes(msg_len)
            g = group.encode(s)
            t = group.decode(g)
            assert s == t, "Failed to encode/decode %d properly" % i

    def testBadMessage1Decode(self):
        group = ECGroup(prime192v1)
        s = b'\x00\x9d\xaa2\xfa\xf2;\xd5\xe56,\xe8\x1c\x17[k4\xa4\x8b\xad'
        g = group.encode(s)
        t = group.decode(g)
        assert s == t, "Failed to encode/decode properly"

    def testBadMessage2Decode(self):
        group = ECGroup(prime192v2)
        s = b'~3\xfcN\x00\x8eF\xfaq\xdc\x8d\x14\x8d\xde\xebC^1`\x99'
        g = group.encode(s)
        t = group.decode(g)
        assert s == t, "Failed to encode/decode properly"

    def testBadMessage3Decode(self):
        group = ECGroup(prime192v2)
        s = b'\x8a$\x1b@5xm\x00f\xa5\x98{OJ\xd9,\x17`\xb7\xcf\xd2\x1e\xb3\x99'
        g = group.encode(s, True)
        t = group.decode(g, True)
        assert s == t, "Failed to encode/decode properly"

if __name__ == "__main__":
    unittest.main()
