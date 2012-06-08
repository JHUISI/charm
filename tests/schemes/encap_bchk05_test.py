from charm.schemes.encap_bchk05 import EncapBCHK
import unittest

debug = False
class EncapBCHKTest(unittest.TestCase):
    def testEncapBCHK(self):
        encap = EncapBCHK()

        hout = encap.setup()

        (r, com, dec) = encap.S(hout)

        rout = encap.R(hout, com, dec)
        
        if debug: print("recovered m =>", rout)

        assert r == rout, "Failed Decryption"
        if debug: print("Successful Decryption!!!")

if __name__ == "__main__":
    unittest.main()
