import unittest

from charm.schemes.commit.commit_gs08 import Commitment_GS08
from charm.toolbox.pairinggroup import PairingGroup, G1

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