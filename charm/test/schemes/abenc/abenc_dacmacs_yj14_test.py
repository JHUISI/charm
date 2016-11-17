import unittest

import charm.schemes.abenc.abenc_dacmacs_yj14 as abenc_dacmacs_yj14

debug = False


# unit test for scheme contributed by artjomb
class DacMacs_YJ14Test(unittest.TestCase):
    def testDacmacs_YJ14(self):
        abenc_dacmacs_yj14.basicTest()
        abenc_dacmacs_yj14.revokedTest()


if __name__ == "__main__":
    unittest.main()
