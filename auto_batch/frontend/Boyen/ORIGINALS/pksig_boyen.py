from charm.pairing import *
from toolbox.PKSig import PKSig
#from toolbox.iterate import dotprod
#from toolbox.pairinggroup import *
#from charm.engine.util import *

N = 3
l = 3
numSigners = 3

debug = False

class Boyen(PKSig):
    def __init__(self):
        global group
        group = pairing('/Users/matt/Documents/charm/param/d224.param')
    
    def setup(self):
        global H
        H = lambda a: group.H(('1', str(a)), ZR)
        g1 = group.random(G1) 
        g2 = group.random(G2)
        a = [group.random(ZR) for i in range(3)]
        A = [] 
        At = []
        for i in range(3):
            A.append(g1 ** a[i])
            At.append(g2 ** a[i])
        mpk = {'g1':g1, 'g2':g2, 'A':A[0], 'B':A[1], 'C':A[2], 'At':At[0], 'Bt':At[1], 'Ct':At[2]}
        return mpk
    
    def keygen(self, mpk):
        a = group.random(ZR) 
        b = group.random(ZR) 
        c = group.random(ZR)
        A = mpk['g1'] ** a 
        B = mpk['g1'] ** b 
        C = mpk['g1'] ** c 
        At = mpk['g2'] ** a 
        Bt = mpk['g2'] ** b 
        Ct = mpk['g2'] ** c
        sk = {'a':a, 'b':b, 'c':c}
        pk = {'A':A, 'B':B, 'C':C, 'At':At, 'Bt':Bt, 'Ct':Ct}
        return (pk, sk)

    def sign(self, mpk, pk, sk, M):
        A_pk = {}
        B_pk = {}
        C_pk = {}
        A_pk[ 0 ] = mpk[ 'A' ]
        B_pk[ 0 ] = mpk[ 'B' ]
        C_pk[ 0 ] = mpk[ 'C' ]
        for i in pk.keys():
            A_pk[ i ] = pk[ i ][ 'A' ]
            B_pk[ i ] = pk[ i ][ 'B' ]
            C_pk[ i ] = pk[ i ][ 'C' ]        
        m = H(M)
        l = len(A_pk.keys())
        s = [group.random(ZR) for i in range(l-1)] # 0:l-1
        t = [group.random(ZR) for i in range(l)]
        S = {}
        for i in range(l-1):
            S[ i ] = mpk['g1'] ** s[i]
        A = A_pk[ 0 ] 
        B = B_pk[ 0 ] 
        C = C_pk[ 0 ]
        prod = (A * (B ** m) * (C ** t[0])) ** -s[0]
        
        for i in range(1, l-1):
            A = A_pk[i] 
            B = B_pk[i] 
            C = C_pk[i]
            prod *= ((A * (B ** m) * (C ** t[i])) ** -s[i])            

        final = l-1
        d = (sk['a'] + (sk['b'] * m) + (sk['c'] * t[final]))  # s[l]
        S[final] = (mpk['g1'] * prod) ** ~d # S[l]
        sig = { 'S':S, 't':t }
        return sig
    
    def verify(self, mpk, pk, M, sig):
        Atpk = {}
        Btpk = {}
        Ctpk = {}
        Atpk[ 0 ] = mpk[ 'At' ]
        Btpk[ 0 ] = mpk[ 'Bt' ]
        Ctpk[ 0 ] = mpk[ 'Ct' ]
        for i in pk.keys():
            Atpk[ i ] = pk[ i ][ 'At' ]
            Btpk[ i ] = pk[ i ][ 'Bt' ]
            Ctpk[ i ] = pk[ i ][ 'Ct' ]        
        l = len(Atpk.keys())
        D = pair(mpk['g1'], mpk['g2'])
        S = sig['S'] 
        t = sig['t']
        m = H(M)
        prod_result = group.init(GT, 1)
        for i in range(l):
            prod_result *= pair(S[i], Atpk[i] * (Btpk[i] ** m) * (Ctpk[i] ** t[i]))
        if prod_result == D:
           return True
        return False

if __name__ == "__main__":
   boyen = Boyen()
   mpk = boyen.setup()
   
   num_signers = 3
   L_keys = [ boyen.keygen(mpk) for i in range(num_signers)]     
   L_pk = {} 
   L_sk = {}
   for i in range(len(L_keys)):
       L_pk[ i+1 ] = L_keys[ i ][ 0 ] # pk
       L_sk[ i+1 ] = L_keys[ i ][ 1 ]

   signer = 3
   sk = L_sk[signer] 
   M = 'please sign this new message!'
   sig = boyen.sign(mpk, L_pk, sk, M)

   assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
  
