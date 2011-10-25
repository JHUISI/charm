""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod

debug = False

class CYH(PKSig):
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
        H1 = lambda x: group.H(('1', str(x)), G1)
        H2 = lambda a, b, c: group.H(('2', a, b, c), ZR)
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
 
        u = [group.init(G1) for i in range(num_signers)]
        h = [group.init(ZR, 1) for i in range(num_signers)]
        for i in range(num_signers):
            if IDs != L[i]:
               u[i] = group.random(G1)
               h[i] = H2(M, Lt, u[i])
            else:
               s = i
        
        r = group.random(ZR)
        pk = [ H1(i) for i in L] # get all signers pub keys
        u[s] = (IDpk ** r) * ~dotprod(group.init(G1), s, num_signers, lam_func, u, pk, h)
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
        result = dotprod(group.init(G1), -1, num_signers, lam_func, u, pk, h) 
        if pair(result, mpk['Pub']) == pair(S, mpk['g']):
            return True
        return False

if __name__ == "__main__":
   L = [ "alice", "bob", "carlos", "dexter", "eddie"] 
   ID = "bob"
   groupObj = pairing('../param/a.param')
   cyh = CYH(groupObj)
   (mpk, msk) = cyh.setup()

   (ID, Pk, Sk) = cyh.keygen(msk, ID)  
   sk = (ID, Pk, Sk)
   print("Keygen...")
   print("sk =>", sk)
  
   M = 'please sign this new message!'
   sig = cyh.sign(sk, L, M)
   print("Signature...")
   print("sig =>", sig)

   assert cyh.verify(mpk, L, M, sig), "invalid signature!"
   print("Verification successful!")
   
