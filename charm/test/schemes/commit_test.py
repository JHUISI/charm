from charm.schemes.commit.commit_gs08 import Commitment_GS08
from charm.schemes.commit.commit_pedersen92 import CM_Ped92
from charm.toolbox.pairinggroup import PairingGroup, G1
from charm.toolbox.ecgroup import ECGroup, ZR
import unittest

debug = False

class Commitment_GS08Test(unittest.TestCase):
    def testCommitment_GS08(self):
        groupObj = PairingGroup('SS512')
        cm = Commitment_GS08(groupObj)
       
        pk = cm.setup()
        if debug: 
            print("Public parameters...")
            print("pk =>", pk)
        
        m = groupObj.random(G1)
        if debug: print("Committing to =>", m)
        (c, d) = cm.commit(pk, m)
        
        assert cm.decommit(pk, c, d, m), "FAILED to decommit"
        if debug: print("Successful and Verified decommitment!!!")

class CM_Ped92Test(unittest.TestCase):
    def testCM_Ped92(self):
        groupObj = ECGroup(410)    
        cm = CM_Ped92(groupObj)
       
        pk = cm.setup()
        if debug: 
            print("Public parameters...")
            print("pk =>", pk)
        
        m = groupObj.random(ZR)
        if debug: print("Commiting to =>", m)
        (c, d) = cm.commit(pk, m)
        
        assert cm.decommit(pk, c, d, m), "FAILED to decommit"
        if debug: print("Successful and Verified decommitment!!!")
        del groupObj

if __name__ == "__main__":
    unittest.main()
