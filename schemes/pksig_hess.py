""" 
Hess - Identity-based Signatures

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
#import gc
#gc.disable()
#gc.set_debug(gc.DEBUG_LEAK)

debug = False

class Hess(PKSig):
    def __init__(self, groupObj):
        global group,H1,H2
        group = groupObj
        H1 = lambda x: group.hash(x, G1)
        H2 = lambda x,y: group.hash((x,y), ZR)
        
    def setup(self):
        g2, alpha = group.random(G2), group.random(ZR)
        msk = alpha
        P = g2 ** alpha 
        mpk = {'P':P, 'g2':g2}
        return (mpk, msk)

    def keygen(self, msk, ID):
        alpha = msk
        sk = H1(ID) ** alpha
        pk = H1(ID)
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        if debug: print("sign...")
        h, s = group.random(G1), group.random(ZR)
        S1 = pair(h,pk['g2']) ** s 
        a = H2(M, S1)
        S2 = (sk ** a) * (h ** s)
        #return {'S1':S1, 'S2':S2}
        return (S1, S2)

    
    def verify(self, mpk, pk, M, sig):
        if debug: print("verify...")
        (S1, S2) = sig
        a = H2(M, S1)
        if pair(S2, mpk['g2']) == (pair(pk, mpk['P']) ** a) * S1: 
            return True
        return False

def main():
   
   groupObj = PairingGroup('../param/a.param')
   chch = Hess(groupObj)
   (mpk, msk) = chch.setup()

   _id = "janedoe@email.com"
   (pk, sk) = chch.keygen(msk, _id)
   if debug:  
    print("Keygen...")
    print("pk =>", pk)
    print("sk =>", sk)
 
   M = "this is a message!" 
   sig = chch.sign(mpk, sk, M)
   if debug:
    print("Signature...")
    print("sig =>", sig)

   assert chch.verify(mpk, pk, M, sig), "invalid signature!"
   if debug: print("Verification successful!")

if __name__ == "__main__":
    debug = True
    main()
