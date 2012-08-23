from charm.schemes.chamhash_adm05 import ChamHash_Adm05
from charm.schemes.chamhash_rsa_hw09 import ChamHash_HW09
from charm.toolbox.integergroup import integer
import unittest

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

class ChamHash_HW09Test(unittest.TestCase):
    def testChamHash_HW09(self):    
        # test p and q primes for unit tests only
        p = integer(164960892556379843852747960442703555069442262500242170785496141408191025653791149960117681934982863436763270287998062485836533436731979391762052869620652382502450810563192532079839617163226459506619269739544815249458016088505187490329968102214003929285843634017082702266003694786919671197914296386150563930299)
        q = integer(82480446278189921926373980221351777534721131250121085392748070704095512826895574980058840967491431718381635143999031242918266718365989695881026434810326191251225405281596266039919808581613229753309634869772407624729008044252593745164984051107001964642921817008541351133001847393459835598957148193075281965149) 

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

if __name__ == "__main__":
    unittest.main()
