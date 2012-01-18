""" 
Hess and ChCh - Identity-based Signatures

| From: "Hess - Efficient identity based signature schemes based on pairings."
| Published in: Selected Areas in Cryptography
| Available from: Vol. 2595. LNCS, pages 310-324
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from toolbox.pairinggroup import PairingGroup,G1,G2,ZR,pair
from toolbox.PKSig import PKSig
from schemes.pksig_hess import Hess
from schemes.pksig_chch import CHCH

debug = False

class ComboScheme(PKSig):
    def __init__(self, groupObj):
        global H2, group, debug
        group = groupObj
        debug = False
        H2 = lambda x,y: group.hash((x,y), ZR)
            
    def verify(self, mpk, pk, M, sig):
        sig1, sig2 = sig['sig_hess'], sig['sig_chch']
        S1h, S2h = sig1['S1'], sig1['S2']
        S1c, S2c = sig2['S1'], sig2['S2']
        ah = H2(M, S1h)
        ac = H2(M, S1c)
        if pair(S2h, mpk['g2']) == (pair(pk, mpk['P']) ** ah) * S1h and pair(S2c, mpk['g2']) == pair(S1c * (pk ** ac), mpk['P']):                 
            return True
        return False
        
def main():
   
    groupObj = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
    hess = Hess(groupObj)
    chch = CHCH(groupObj)
    combo = ComboScheme(groupObj)
   
    (mpk, msk) = chch.setup()

    _id = "janedoe@email.com"
    (pk, sk) = chch.keygen(msk, _id)
    if debug:  
        print("Keygen...")
        print("pk =>", pk)
        print("sk =>", sk)
 
    M = "this is a message! twice!" 
    sig1 = hess.sign(mpk, sk, M)
    sig2 = chch.sign(pk, sk, M)
    sig = { 'sig_hess':sig1, 'sig_chch':sig2 }
    if debug:
        print("Signature...")
        print("sig1 =>", sig1)
        print("sig2 =>", sig2)
   
    assert combo.verify(mpk, pk, M, sig), "invalid signature!"
    if debug: print("Verification successful!")

if __name__ == "__main__":
    debug = False
    main()
