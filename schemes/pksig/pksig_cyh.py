""" 
Chow-Yiu-Hui - Identity-based ring signatures

| From: "S. Chow, S. Yiu and L. Hui - Efficient identity based ring signature."
| Published in: ACNS 2005
| Available from: Vol 3531 of LNCS, pages 499-512
| Notes: 

* type:           signature (ring-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair
from charm.toolbox.PKSig import PKSig
from charm.toolbox.iterate import dotprod

debug = False

class CYH(PKSig):
    """

    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> users = [ "alice", "bob", "carlos", "dexter", "eddie"] 
    >>> signer = "bob"
    >>> group = PairingGroup('SS512')
    >>> cyh = CYH(group)
    >>> (master_public_key, master_secret_key) = cyh.setup()
    >>> (signer, public_key, secret_key) = cyh.keygen(master_secret_key, signer)  
    >>> secret_key = (signer, public_key, secret_key)
    >>> msg = 'please sign this new message!'
    >>> signature = cyh.sign(secret_key, users, msg)
    >>> cyh.verify(master_public_key, users, msg, signature)
    True
    """
    def __init__(self, groupObj):
        global group
        group = groupObj
    
    def concat(self, L_id):
        result = ""
        for i in L_id:
            result += ":"+i 
        return result

    def setup(self):
        global H1,H2,lam_func
        H1 = lambda x: group.hash(('1', str(x)), G1)
        H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
        lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
        g, alpha = group.random(G2), group.random(ZR)
        P = g ** alpha
        msk = alpha
        mpk = {'Pub':P, 'g':g }
        return (mpk, msk) 
    
    def keygen(self, msk, ID):
        sk = H1(ID) ** msk
        pk = H1(ID)
        return (ID, pk, sk)
    
    def sign(self, sk, L, M):
        (IDs, IDpk, IDsk) = sk
        assert IDs in L, "signer should be an element in L"
        Lt = self.concat(L) 
        num_signers = len(L)
 
        u = [1 for i in range(num_signers)]
        h = [group.init(ZR, 1) for i in range(num_signers)]
        for i in range(num_signers):
            if IDs != L[i]:
               u[i] = group.random(G1)
               h[i] = H2(M, Lt, u[i])
            else:
               s = i
        
        r = group.random(ZR)
        pk = [ H1(i) for i in L] # get all signers pub keys
        u[s] = (IDpk ** r) * (dotprod(1, s, num_signers, lam_func, u, pk, h) ** -1)
        h[s] = H2(M, Lt, u[s])
        S = IDsk ** (h[s] + r)
        sig = { 'u':u, 'S':S }
        return sig
    
    def verify(self, mpk, L, M, sig):
        u, S = sig['u'], sig['S']
        Lt = self.concat(L) 
        num_signers = len(L)
        h = [group.init(ZR, 1) for i in range(num_signers)]
        for i in range(num_signers):
            h[i] = H2(M, Lt, u[i])

        pk = [ H1(i) for i in L] # get all signers pub keys
        result = dotprod(1, -1, num_signers, lam_func, u, pk, h) 
        if pair(result, mpk['Pub']) == pair(S, mpk['g']):
            return True
        return False


def main():
   L = [ "alice", "bob", "carlos", "dexter", "eddie"] 
   ID = "bob"
   groupObj = PairingGroup('SS512')
   cyh = CYH(groupObj)
   (mpk, msk) = cyh.setup()

   (ID, Pk, Sk) = cyh.keygen(msk, ID)  
   sk = (ID, Pk, Sk)
   if debug:
    print("Keygen...")
    print("sk =>", sk)
  
   M = 'please sign this new message!'
   sig = cyh.sign(sk, L, M)
   if debug:
    print("Signature...")
    print("sig =>", sig)

   assert cyh.verify(mpk, L, M, sig), "invalid signature!"
   if debug: print("Verification successful!")

if __name__ == "__main__":
    debug = True
    main()
