import unittest

from charm.schemes.commit.commit_pedersen92 import CM_Ped92
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.pairinggroup import ZR

debug = False


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
