import unittest

import charm.schemes.abenc.abenc_maabe_yj14 as abenc_maabe_yj14

debug = False


# unit test for scheme contributed by artjomb
class MAabe_YJ14Test(unittest.TestCase):
    def testMAabe_YJ14(self):
        abenc_maabe_yj14.basicTest()
        abenc_maabe_yj14.revokedTest()


if __name__ == "__main__":
    unittest.main()
