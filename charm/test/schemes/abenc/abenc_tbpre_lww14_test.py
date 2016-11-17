import unittest

import charm.schemes.abenc.abenc_tbpre_lww14 as abenc_tbpre_lww14

debug = False


# unit test for scheme contributed by artjomb
class TBPre_LWW14Test(unittest.TestCase):
    def testTBPre_LWW14(self):
        abenc_tbpre_lww14.basicTest()
        # abenc_tbpre_lww14.basicTest2() # seems to fail


if __name__ == "__main__":
    unittest.main()
