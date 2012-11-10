'''
Susan Hohenberger and Brent Waters (Pairing-based)
 
| From: "Constructing Verifiable Random Functions with Large Input Spaces"
| Published in: ePrint
| Available from: http://eprint.iacr.org/2010/102.pdf
| Notes: applications to resetable ZK proofs, micropayment schemes, updatable ZK DBs
         and verifiable transaction escrow schemes to name a few

* type:           verifiable random functions (family of pseudo random functions)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       1/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair
from charm.toolbox.iterate import dotprod 

debug = False
class VRF10:
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('MNT224')
    >>> vrf = VRF10(group)
    >>> statement = [0, 1, 1, 0, 1, 0, 1, 0]
    >>> n = len(statement) 
    >>> (public_key, secret_key) = vrf.setup(n)
    >>> witness = vrf.prove(secret_key, statement)
    >>> vrf.verify(public_key, statement, witness)
    True
    """
    """Definition in paper: behave as Pseudo Random Functions (PRFs) with an additional property that party
    holding the seed will publish a commitment to the function and is able to non-interactively convince
    a verifier that a given evaluation is correct (matches pub commitment) without sacrificing pseudo-
    randomness property on other inputs."""
    def __init__(self, groupObj):
        global group, lam_func
        group = groupObj
        lam_func = lambda i,a,b: a[i] ** b[i]
        
    def setup(self, n):
        """n = bit length of inputs"""
        g1 = group.random(G1)
        g2, h = group.random(G2), group.random(G2)
        u_t = group.random(ZR)
        u = [group.random(ZR) for i in range(n+1)]
        U_t = g2 ** u_t
        U1 = [g1 ** u[i] for i in range(0, n)]
        U2 = [g2 ** u[i] for i in range(0, n)]
        
        pk = { 'U1':U1, 'U2':U2,'U_t':U_t, 'g1':g1, 'g2':g2, 'h':h,'n':n   }
        sk = { 'u':u, 'u_t':u_t, 'g1':g1, 'h':h,'n':n }
        return (pk, sk)
    
    def F(self, sk, x):
        result = dotprod(1, -1, sk['n'], lam_func, sk['u'], x) 
        return pair(sk['g1'] ** (sk['u_t'] * sk['u'][0] * result), sk['h'])
    
    def prove(self, sk, x):
        pi = {} # [i for i in range(sk['n'])]
        for i in range(0, sk['n']):
            dotProd0 = dotprod(1, -1, i+1, lam_func, sk['u'], x) 
            pi[i+1] = sk['g1'] ** (sk['u_t'] * dotProd0)
        
        dotProd1 = dotprod(1, -1, sk['n'], lam_func, sk['u'], x)
        pi[0] = sk['g1'] ** (sk['u_t'] * sk['u'][0] * dotProd1)
        y = self.F(sk, x)
        return { 'y':y, 'pi':pi } #, 'pi0':pi_0 }
                
    def verify(self, pk, x, st):
        n, y, pi = pk['n'], st['y'], st['pi']
        # check first index 
        check1 = pair(pi[1], pk['g2'])
        if x[0] == 0 and check1 == pair(pk['g1'], pk['U_t']):
            if debug: print("Verify: check 0 successful!\t\tcase:", x[0])
        elif x[0] == 1 and check1 == pair(pk['U1'][0], pk['U_t']):
            if debug: print("Verify: check 0 successful!\t\tcase:", x[0])            
        else: 
            if debug: print("Verify: check 0 FAILURE!\t\t failed case:", x[0])            
            return False
        
        for i in range(2, n+1):
            check2 = pair(pi[i], pk['g2'])
            if x[i-1] == 0 and check2 == pair(pi[i-1], pk['g2']):
                if debug: print("Verify: check", i-1 ,"successful!\t\tcase:", x[i-1])
            elif x[i-1] == 1 and check2 == pair(pi[i-1], pk['U2'][i-1]):
                if debug: print("Verify: check", i-1 ,"successful!\t\tcase:", x[i-1])
            else:
                if debug: print("Verify: check", i-1 ,"FAILURE!\t\tcase:", x[i-1])
                return False
        
        if pair(pi[0], pk['g2'] * pk['h']) == (pair(pi[n], pk['U2'][0]) * y): #and pair(pi_0, pk['h']) == y:
            if debug: print("Verify: all and final check successful!!!")
            return True
        else:
            return False
        
def main():
    grp = PairingGroup('MNT224')
    
    # bits
    x1 = [0, 1, 1, 0, 1, 0, 1, 0]
    #x2 = [1, 1, 1, 0, 1, 0, 1, 0]
    # block of bits
    n = 8 
    
    vrf = VRF10(grp)
    
    # setup the VRF to accept input blocks of 8-bits 
    (pk, sk) = vrf.setup(n)
    
    # generate proof over block x (using sk)
    st = vrf.prove(sk, x1)
    
    # verify bits using pk and proof
    assert vrf.verify(pk, x1, st), "VRF failed verification"
    #assert vrf.verify(pk, x2, st), "VRF should FAIL verification!!!"
    
if __name__ == "__main__":
    debug = True
    main()
