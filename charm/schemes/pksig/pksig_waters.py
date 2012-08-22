""" 
Waters - Identity-based signatures

| From: "B. Waters - Efficient identity-based encryption without random oracles"
| Published in: EUROCRYPT 2005
| Available from: Vol 3494 of LNCS, pages 320-329
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair
from charm.toolbox.iterate import dotprod
from charm.toolbox.hash_module import Waters

debug = False
class WatersSig:
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('SS512')
    >>> water = WatersSig(group)
    >>> (master_public_key, master_secret_key) = water.setup(5)
    >>> ID = 'janedoe@email.com'
    >>> secret_key = water.keygen(master_public_key, master_secret_key, ID)  
    >>> msg = 'please sign this new message!'
    >>> signature = water.sign(master_public_key, secret_key, msg)
    >>> water.verify(master_public_key, ID, msg, signature)
    True
    """
    def __init__(self, groupObj):
        global group,lam_func
        group = groupObj
        lam_func = lambda i,a,b: a[i] ** b[i]

    def setup(self, z, l=32):
        global waters
        waters = Waters(group, z, l)
        alpha, h = group.random(ZR), group.random(G1)
        g1, g2 = group.random(G1), group.random(G2)
        A = pair(h, g2) ** alpha
        y = [group.random(ZR) for i in range(z)]
        y1t,y2t = group.random(ZR), group.random(ZR)

        u1t = g1 ** y1t; u2t = g1 ** y2t
        u = [g1 ** y[i] for i in range(z)]

        u1b = g2 ** y1t; u2b = g2 ** y2t
        ub =[g2 ** y[i] for i in range(z)]

        msk = h ** alpha
        mpk = {'g1':g1, 'g2':g2, 'A':A, 'u1t':u1t, 'u2t':u2t, 'u':u, 'u1b':u1b, 'u2b':u2b, 'ub':ub, 'z':z, 'l':l } 
        return (mpk, msk) 

    def keygen(self, mpk, msk, ID):
        if debug: print("Keygen alg...")
        k = waters.hash(ID) # return list from k1,...,kz
        if debug: print("k =>", k)
        r = group.random(ZR)
        k1 = msk * ((mpk['u1t'] * dotprod(1, -1, mpk['z'], lam_func, mpk['u'], k)) ** r)  
        k2 = mpk['g1'] ** -r
        return (k1, k2)
    
    def sign(self, mpk, sk, M):
        if debug: print("Sign alg...")
        m = waters.hash(M) # return list from m1,...,mz
        if debug: print("m =>", m)
        (k1, k2) = sk
        s  = group.random(ZR)
        S1 = k1 * ((mpk['u2t'] * dotprod(1, -1, mpk['z'], lam_func, mpk['u'], m)) ** s)
        S2 = k2
        S3 = mpk['g1'] ** -s
        return {'S1':S1, 'S2':S2, 'S3':S3}
    
    def verify(self, mpk, ID, M, sig):
        if debug: print("Verify...")
        k = waters.hash(ID)
        m = waters.hash(M)
        (S1, S2, S3) = sig['S1'], sig['S2'], sig['S3']
        A, g2 = mpk['A'], mpk['g2']
        comp1 = dotprod(1, -1, mpk['z'], lam_func, mpk['ub'], k)
        comp2 = dotprod(1, -1, mpk['z'], lam_func, mpk['ub'], m)
        lhs = (pair(S1, g2) * pair(S2, mpk['u1b'] * comp1) * pair(S3, mpk['u2b'] * comp2)) 
        #if ((pair(S1, g2) * pair(S2, mpk['u1b'] * comp1) * pair(S3, mpk['u2b'] * comp2)) == A): 
        if lhs == A:
            return True
        return False

def main():
    groupObj = PairingGroup('SS512')
    wat = WatersSig(groupObj)
    (master_public_key, master_secret_key) = wat.setup(5)
    ID = 'janedoe@email.com'
    secret_key = wat.keygen(master_public_key, master_secret_key, ID)  
    msg = 'please sign this new message!'

    sig = wat.sign(master_public_key, secret_key, msg)

    assert wat.verify(master_public_key, ID, msg, sig), "invalid signature"
    if debug: print("Successful Verification!")

if __name__ == "__main__":
    debug = True
    main()

   
