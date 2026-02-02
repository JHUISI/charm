import unittest

from charm.schemes.chamhash_rsa_hw09 import ChamHash_HW09
from charm.toolbox.integergroup import integer

debug = False


class ChamHash_HW09Test(unittest.TestCase):
    def testChamHash_HW09(self):
        # Test p and q primes for unit tests only
        # These primes are mathematically suitable - phi_N = (p-1)*(q-1) is coprime with 65537
        # This ensures the deterministic coprime algorithm finds a solution quickly
        p = integer(95969491500266197744623842643163713790605329484264579952704690252128663957034885038057265490969414900858594119440280815406458877960454430736966405387849574204717896425412057524927419980472986383200765875162149934175300724788379539851438576829444747397186724447127392785957485487971933719848100802790176324337)
        q = integer(165685596906806363133681673469906489437474476163789251744214878002662496954723502283532073376723817149461444040314419947626958411649072129703545884779008062578922350877123596086401947242893563534827734633284461244941306661332124200807263458137608535445118169374047964965396160553232687802551488935469282118877)

        chamHash = ChamHash_HW09()
        (pk, sk) = chamHash.paramgen(1024, p, q)

        msg = "Hello world this is the message!"
        (h, r) = chamHash.hash(pk, msg)
        if debug: print("Hash...")
        if debug: print("sig =>", h)

        (h1, r1) = chamHash.hash(pk, msg, r)
        if debug: print("sig 2 =>", h1)

        assert h == h1, "Signature failed!!!"
        if debug: print("Signature generated correctly!!!")
