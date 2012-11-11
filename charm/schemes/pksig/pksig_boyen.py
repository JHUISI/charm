""" 
Xavier Boyen - Anonymous Ring Signatures

| From: "X. Boyen. Mesh Signatures: How to Leak a Secret with Unwitting and Unwilling Participants"
| Published in: EUROCRYPT 2007
| Available from: http://eprint.iacr.org/2007/094.pdf
| Notes: 

* type:           signature (ring-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011

"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.PKSig import PKSig

debug = False

# need RingSig
class Boyen(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('MNT224')
    >>> boyen = Boyen(group)
    >>> master_public_key = boyen.setup()
    >>> num_signers = 3
    >>> keys = [ boyen.keygen(master_public_key) for i in range(num_signers)]     
    >>> public_keys, secret_keys = {},{}
    >>> for i in range(len(keys)):
    ...     public_keys[ i+1 ] = keys[ i ][ 0 ]
    ...     secret_keys[ i+1 ] = keys[ i ][ 1 ]
    >>> signer = 3
    >>> secret_key = secret_keys[signer] 
    >>> msg = 'please sign this new message!'
    >>> signature = boyen.sign(signer, master_public_key, public_keys, secret_key, msg) 
    >>> boyen.verify(master_public_key, public_keys, msg, signature) 
    True
    """
    def __init__(self, groupObj):
        global group
        group = groupObj
    
    def setup(self):
        global H
        H = lambda a: group.hash(('1', str(a)), ZR)
        g1, g2 = group.random(G1), group.random(G2)
        a = [group.random(ZR) for i in range(3)]
        A = []; At = [];
        for i in range(3):
            A.append(g1 ** a[i])
            At.append(g2 ** a[i])
        # public verification key "in the sky" for all users
        return {'g1':g1, 'g2':g2, 'A':A[0],    'B':A[1],   'C':A[2], 
                                  'At':At[0], 'Bt':At[1], 'Ct':At[2]}
    
    def keygen(self, mpk):
        a, b, c = group.random(ZR), group.random(ZR), group.random(ZR)
        A = mpk['g1'] ** a; B = mpk['g1'] ** b; C = mpk['g1'] ** c 
        At = mpk['g2'] ** a; Bt = mpk['g2'] ** b; Ct = mpk['g2'] ** c
        sk = {'a':a, 'b':b, 'c':c}
        pk = {'A':A, 'B':B, 'C':C, 'At':At, 'Bt':Bt, 'Ct':Ct}
        return (pk, sk)

    def getPKdict(self, mpk, pk, k):
        A_pk, B_pk, C_pk = {}, {}, {}
        A_pk[ 0 ] = mpk[ k[0] ]
        B_pk[ 0 ] = mpk[ k[1] ]
        C_pk[ 0 ] = mpk[ k[2] ]
        for i in pk.keys():
            A_pk[ i ] = pk[ i ][ k[0] ]
            B_pk[ i ] = pk[ i ][ k[1] ]
            C_pk[ i ] = pk[ i ][ k[2] ]        
        return A_pk, B_pk, C_pk
    
    def sign(self, index, mpk, pk, sk, M):
        if debug: print("pk =>", pk.keys())
        (A_pk, B_pk, C_pk) = self.getPKdict(mpk, pk, ['A', 'B', 'C'])
        m = H(M)
        l = len(A_pk.keys())
        assert index >= 0 and index < l, "invalid index"
        if debug: print("l defined as =>", l)        
        s = {}
        S = {}
        for i in range(0, l):
            if i != index:
               s[i] = group.random(ZR)	
               S[i] = mpk['g1'] ** s[i]   
        t = [group.random(ZR) for i in range(l)]
        # index=0
        (A, B, C) = A_pk[ 0 ], B_pk[ 0 ], C_pk[ 0 ]
        prod = (A * (B ** m) * (C ** t[0])) ** -s[0]
        
        # 1 -> l
        for i in range(1, l):
            if i != index:
               (A, B, C) = A_pk[i], B_pk[i], C_pk[i]
               prod *= ((A * (B ** m) * (C ** t[i])) ** -s[i])            

        d = (sk['a'] + (sk['b'] * m) + (sk['c'] * t[index]))  # s[l]
        S[index] = (mpk['g1'] * prod) ** (1 / d) # S[l]
        if debug: print("S[", index, "] :=", S[index])
        sig = { 'S':S, 't':t }
        return sig
    
    def verify(self, mpk, pk, M, sig):
        if debug: print("Verifying...")
        At, Bt, Ct = self.getPKdict(mpk, pk, ['At', 'Bt', 'Ct'])
        l = len(At.keys())
        D = pair(mpk['g1'], mpk['g2'])
        S, t = sig['S'], sig['t']
        m = H(M)
        dotProd0 = 1
        for i in range(l):
            dotProd0 *= pair(S[i], At[i] * (Bt[i] ** m) * (Ct[i] ** t[i]))
        if dotProd0 == D:
           return True
        return False

def main():
   groupObj = PairingGroup('MNT224')
   boyen = Boyen(groupObj)
   mpk = boyen.setup()
   if debug: print("Pub parameters")
   if debug: print(mpk, "\n\n")
   
   num_signers = 3
   L_keys = [ boyen.keygen(mpk) for i in range(num_signers)]     
   L_pk = {}; L_sk = {}
   for i in range(len(L_keys)):
       L_pk[ i+1 ] = L_keys[ i ][ 0 ] # pk
       L_sk[ i+1 ] = L_keys[ i ][ 1 ]

   if debug: print("Keygen...")
   if debug: print("sec keys =>", L_sk.keys(),"\n", L_sk) 

   signer = 3
   sk = L_sk[signer] 
   M = 'please sign this new message!'
   sig = boyen.sign(signer, mpk, L_pk, sk, M)
   if debug: print("\nSignature...")
   if debug: print("sig =>", sig)

   assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
   if debug: print("Verification successful!")

if __name__ == "__main__":
    debug = True
    main()
