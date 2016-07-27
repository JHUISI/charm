import unittest

from charm.schemes.chamhash_adm05 import ChamHash_Adm05
from charm.toolbox.integergroup import integer

debug = False


class ChamHash_Adm05Test(unittest.TestCase):
    def testChamHash_Adm05(self):
        # fixed params for unit tests
        p = integer(141660875619984104245410764464185421040193281776686085728248762539241852738181649330509191671665849071206347515263344232662465937366909502530516774705282764748558934610432918614104329009095808618770549804432868118610669336907161081169097403439689930233383598055540343198389409225338204714777812724565461351567)
        q = integer(70830437809992052122705382232092710520096640888343042864124381269620926369090824665254595835832924535603173757631672116331232968683454751265258387352641382374279467305216459307052164504547904309385274902216434059305334668453580540584548701719844965116691799027770171599194704612669102357388906362282730675783)
        chamHash = ChamHash_Adm05(p, q)
        #TODO: how long is paramgen supposed to take?
        (pk, sk) = chamHash.paramgen()
        if debug: print("pk => ", pk)
        if debug: print("sk => ", sk)

        msg = "Hello world this is the message!"
        (h, r, s) = chamHash.hash(pk, msg)
        if debug: print("Hash...")
        if debug: print("sig =>", h)

        (h1, r1, s1) = chamHash.hash(pk, msg, r, s)
        if debug: print("sig 2 =>", h1)

        assert h == h1, "Signature failed!!!"
        if debug: print("Signature generated correctly!!!")