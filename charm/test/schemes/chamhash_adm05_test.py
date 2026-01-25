import unittest
import sys

from charm.schemes.chamhash_adm05 import ChamHash_Adm05
from charm.toolbox.integergroup import integer

debug = False


class ChamHash_Adm05Test(unittest.TestCase):
    def testChamHash_Adm05(self):
        # fixed params for unit tests
        p = integer(141660875619984104245410764464185421040193281776686085728248762539241852738181649330509191671665849071206347515263344232662465937366909502530516774705282764748558934610432918614104329009095808618770549804432868118610669336907161081169097403439689930233383598055540343198389409225338204714777812724565461351567)
        q = integer(70830437809992052122705382232092710520096640888343042864124381269620926369090824665254595835832924535603173757631672116331232968683454751265258387352641382374279467305216459307052164504547904309385274902216434059305334668453580540584548701719844965116691799027770171599194704612669102357388906362282730675783)
        chamHash = ChamHash_Adm05(p, q)

        # Debug: verify group params are set correctly
        print(f"\nDEBUG: Platform: {sys.platform}", flush=True)
        print(f"DEBUG: group.p == p: {chamHash.group.p == p}", flush=True)
        print(f"DEBUG: group.q == q: {chamHash.group.q == q}", flush=True)

        #TODO: how long is paramgen supposed to take?
        (pk, sk) = chamHash.paramgen()
        if debug: print("pk => ", pk)
        if debug: print("sk => ", sk)

        msg = "Hello world this is the message!"
        (h, r, s) = chamHash.hash(pk, msg)
        print(f"DEBUG: First hash h = {h}", flush=True)
        print(f"DEBUG: r = {r}", flush=True)
        print(f"DEBUG: s = {s}", flush=True)
        if debug: print("Hash...")
        if debug: print("sig =>", h)

        (h1, r1, s1) = chamHash.hash(pk, msg, r, s)
        print(f"DEBUG: Second hash h1 = {h1}", flush=True)
        print(f"DEBUG: r1 = {r1}", flush=True)
        print(f"DEBUG: s1 = {s1}", flush=True)
        print(f"DEBUG: r == r1: {r == r1}", flush=True)
        print(f"DEBUG: s == s1: {s == s1}", flush=True)
        print(f"DEBUG: h == h1: {h == h1}", flush=True)
        if debug: print("sig 2 =>", h1)

        if h != h1:
            print(f"FAILURE: h != h1", flush=True)
            print(f"  h  = {h}", flush=True)
            print(f"  h1 = {h1}", flush=True)
        assert h == h1, f"Signature failed!!! h={h}, h1={h1}"
        if debug: print("Signature generated correctly!!!")