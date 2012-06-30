'''
 Identity Based Signature
 
| From: "J. Camenisch, A. Lysyanskaya. Signature Schemes and Anonymous Credentials from Bilinear Maps"
| Published in: 2004
| Available from: http://www.cs.brown.edu/~anna/papers/cl04.pdf
| Notes: Scheme A on page 5 section 3.1.

* type:           signature (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       1/2012
 '''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair
from charm.toolbox.PKSig import PKSig

debug = False
class CL04(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('MNT224')
    >>> cl = CL04(group)
    >>> master_public_key = cl.setup()
    >>> (public_key, secret_key) = cl.keygen(master_public_key)
    >>> msg = "Please sign this stupid message!"
    >>> signature = cl.sign(public_key, secret_key, msg)
    >>> cl.verify(public_key, msg, signature)
    True
    """
    def __init__(self, groupObj):
        global group
        group = groupObj
        
    def setup(self):
        g = group.random(G1)
        return { 'g': g }
        
    def keygen(self, mpk):
        x, y = group.random(ZR), group.random(ZR)
        sk = { 'x':x, 'y':y }
        pk = { 'X':mpk['g'] ** x, 'Y': mpk['g'] ** y, 'g':mpk['g'] }        
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = group.random(G2)
        m = group.hash(M, ZR)
        sig = {'a':a, 'a_y':a ** sk['y'], 'a_xy':a ** (sk['x'] + (m * sk['x'] * sk['y'])) }
        return sig
    
    def verify(self, pk, M, sig):
        (a, b, c) = sig['a'], sig['a_y'], sig['a_xy']
        m = group.hash(M, ZR)
        if pair(pk['Y'], a) == pair(pk['g'], b) and (pair(pk['X'], a) * (pair(pk['X'], b) ** m)) == pair(pk['g'], c):
            return True
        return False
    
def main():
    grp = PairingGroup('MNT224')
    cl = CL04(grp)
    
    mpk = cl.setup()
    
    (pk, sk) = cl.keygen(mpk)
    if debug:
        print("Keygen...")
        print("pk :=", pk)
        print("sk :=", sk)
    
    M = "Please sign this stupid message!"
    sig = cl.sign(pk, sk, M)
    if debug: print("Signature: ", sig)
    
    result = cl.verify(pk, M, sig)
    assert result, "INVALID signature!"
    if debug: print("Successful Verification!!!")
    
if __name__ == "__main__":
    debug = True
    main()
