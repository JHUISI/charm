from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.pk_vrf import VRF10
import unittest

debug = False
class VRF10Test(unittest.TestCase):
    def testVRF10(self):
        grp = PairingGroup('MNT224')
        
        # bits
        x1 = [0, 1, 1, 0, 1, 0, 1, 0]
    #    x2 = [1, 1, 1, 0, 1, 0, 1, 0]
        # block of bits
        n = 8 
        
        vrf = VRF10(grp)
        
        # setup the VRF to accept input blocks of 8-bits 
        (pk, sk) = vrf.setup(n)
        
        # generate proof over block x (using sk)
        st = vrf.prove(sk, x1)
        
        # verify bits using pk and proof
        assert vrf.verify(pk, x1, st), "VRF failed verification"
#    assert vrf.verify(pk, x2, st), "VRF should FAIL verification!!!"

if __name__ == "__main__":
    unittest.main()
