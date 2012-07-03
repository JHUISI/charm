""" 
Jae Choon Cha and Jung Hee Cheon - Identity-based Signatures

| From: "J. Cha and J. Choen - An identity-based signature from gap Diffie-Hellman groups."
| Published in: PKC 2003
| Available from: Vol. 2567. LNCS, pages 18-30
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.PKSig import PKSig

debug = False
class CHCH(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('SS512')
    >>> chch = CHCH(group)
    >>> (master_public_key, master_secret_key) = chch.setup()
    >>> ID = "janedoe@email.com"
    >>> (public_key, secret_key) = chch.keygen(master_secret_key, ID)  
    >>> msg = "this is a message!" 
    >>> signature = chch.sign(public_key, secret_key, msg)
    >>> chch.verify(master_public_key, public_key, msg, signature)
    True
    """
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
        s = group.random(ZR)
        S1 = pk ** s
        a = H2(M, S1)
        S2 = sk ** (s + a)
        return {'S1':S1, 'S2':S2}
    
    def verify(self, mpk, pk, M, sig):
        if debug: print("verify...")
        (S1, S2) = sig['S1'], sig['S2']
        a = H2(M, S1)
        if pair(S2, mpk['g2']) == pair(S1 * (pk ** a), mpk['P']): 
            return True
        return False

def main():
   groupObj = PairingGroup('SS512')
   chch = CHCH(groupObj)
   (mpk, msk) = chch.setup()

   _id = "janedoe@email.com"
   (pk, sk) = chch.keygen(msk, _id)  
   if debug:
    print("Keygen...")
    print("pk =>", pk)
    print("sk =>", sk)
 
   M = "this is a message!" 
   sig = chch.sign(pk, sk, M)
   if debug:
    print("Signature...")
    print("sig =>", sig)

   assert chch.verify(mpk, pk, M, sig), "invalid signature!"
   if debug: print("Verification successful!")

if __name__ == "__main__":
    debug = True
    main()
