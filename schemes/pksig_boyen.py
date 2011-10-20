""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod

debug = False

class Boyen(PKSig):
    def __init__(self, groupObj):
        global group
        group = groupObj
    
    def setup(self):
        global H
        H = lambda a: group.H(('1', str(a)), ZR)
        g1 = group.random(G1)
        g2 = group.random(G2)
        return {'g1':g1, 'g2':g2}
    
    def keygen(self, mpk):
        a = group.random(ZR)
        b = group.random(ZR)
        c = group.random(ZR)
        A = mpk['g1'] ** a; B = mpk['g1'] ** b; C = mpk['g1'] ** c 
        At = mpk['g2'] ** a; Bt = mpk['g2'] ** b; Ct = mpk['g2'] ** c
        sk = {'a':a, 'b':b, 'c':c}
        pk = {'A':A, 'B':B, 'C':C, 'At':At, 'Bt':Bt, 'Ct':Ct}
        return (pk, sk)
    
    def sign(self, mpk, pk, sk, M):
        A = [ i['A'] for i in pk ]
        B = [ i['B'] for i in pk ]
        C = [ i['C'] for i in pk ]
        m = H(M)
        num_signers = len(pk)
        l = len(pk) - 1
        s = [group.random(ZR) for i in range(l)]
        t = [group.random(ZR) for i in range(num_signers)]
        S = [i for i in range(num_signers)]
        lam_func = lambda i,a,b,c: (a[i] * (b[i] * m) * (c[i] * t[i])) ** ~s[i] 

        for i in range(l):
            S[i] = mpk['g1'] ** s[i]
 
        d = ~(sk['a'] + (sk['b'] * m) + (sk['c'] * t[l]))
        S[l] = (mpk['g1'] * dotprod(group.init(G1), -1, l, lam_func, A, B, C)) ** d

        sig = { 'S':S, 't':t }
        return sig
    
    def verify(self, mpk, pk, M, sig):
        num_signers = len(pk)
        At = [ i['At'] for i in pk ]
        Bt = [ i['Bt'] for i in pk ]
        Ct = [ i['Ct'] for i in pk ]
        D = pair(mpk['g1'], mpk['g2'])
        S, t = sig['S'], sig['t']
        m = H(M)
        lam_func2 = lambda i,a,b,c,d: pair(S[i], a[i] * (b[i] * m) * (c[i] * t[i]))
        result = dotprod(group.init(GT), -1, num_signers, lam_func2, S, At, Bt, Ct)
        if result == D:
           return True
        return False

if __name__ == "__main__":
   groupObj = pairing('../param/a.param')
   boyen = Boyen(groupObj)
   mpk = boyen.setup()
   print("Pub parameters")
   print(mpk)
   
   num_signers = 5
   L_keys = [ boyen.keygen(mpk) for i in range(num_signers)]  
   L_pk = [ x for x,y in L_keys ]
   L_sk = [ y for x,y in L_keys ]
   print("Keygen...")
   print("pub keys =>", L_pk) 
   print("sec keys =>", L_sk)

   signer = 4
   sk = L_sk[signer] 
   M = 'please sign this new message!'
   sig = boyen.sign(mpk, L_pk, sk, M)
   print("\nSignature...")
   print("sig =>", sig)

   assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
   print("Verification successful!")
   
