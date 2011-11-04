from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod

N = 10
num_signers = 5
debug = False

class CYH(PKSig):
    def __init__(self):
        global group
        group = pairing('/Users/matt/Documents/charm/param/a.param')
    
    def concat(self, L_id):
        result = ""
        for i in L_id:
            result += ":"+i 
        return result

    def setup(self):
        global H1,H2,lam_func
        H1 = lambda x: group.H(('1', str(x)), G1)
        H2 = lambda a, b, c: group.H(('2', a, b, c), ZR)
        lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i])
        g = group.random(G2)
        alpha = group.random(ZR)
        P = g ** alpha
        msk = alpha
        mpk = {'Pub':P, 'g':g }
        return (mpk, msk) 
    
    def keygen(self, msk, ID):
        sk = H1(ID) ** msk
        pk = H1(ID)
        sk_tuple = (ID, pk, sk)
        return sk_tuple
    
    def sign(self, sk_tuple, L, M):
        (IDs, IDpk, IDsk) = sk_tuple
        assert IDs in L, "signer should be an element in L"
        Lt = self.concat(L)
 
        u = [group.init(G1) for i in range(num_signers)]
        h = [group.init(ZR, 1) for i in range(num_signers)]
        for i in range(num_signers):
            if IDs != L[i]:
               u[i] = group.random(G1)
               h[i] = H2(M, Lt, u[i])
            else:
               s = i
        
        r = group.random(ZR)
        pk_sign = [ H1(i) for i in L] # get all signers pub keys
        u[s] = (IDpk ** r) * ~dotprod(group.init(G1), s, num_signers, lam_func, u, pk_sign, h)
        h[s] = H2(M, Lt, u[s])
        S = IDsk ** (h[s] + r)
        sig = { 'u_in_dict':u, 'S_in_dict':S }
        return sig
    
    def verify(self, mpk, L, M, sig):
        uverify = sig['u_in_dict']
        A = uverify 
        Sverify = sig['S_in_dict']
        if (1 == 1):
            pass
            sig = 4
            pass
            Sverify = 5
            A = 4
        Lt = self.concat(L) 
        B = uverify * Sverify * A
        
        if 1 == 1:
            d = 4
            e = d *28
        
        hverify = [group.init(ZR, 1) for i in range(num_signers)]
        for i in range(num_signers):
            hverify[i] = H2(M, Lt, uverify[i])
            pass

	# END_PRECOMPUTE
            b = 18
            pass
            c = 24
        pkverify = [ H1(i) for i in L] # get all signers pub keys
            #test
        result = dotprod(group.init(G1), -1, num_signers, lam_func, uverify, pkverify, hverify) 
        if pair(result, mpk['Pub']) == pair(Sverify, mpk['g']):
            return True
        return False

if __name__ == "__main__":
   L = [ "alice", "bob", "carlos", "dexter", "eddie"] 
   ID = "bob"
   cyh = CYH()
   (mpk, msk) = cyh.setup()

   (ID, Pk, Sk) = cyh.keygen(msk, ID)  
   sk_main = (ID, Pk, Sk)
   print("Keygen...")
   print("sk =>", sk_main)
  
   M = 'please sign this new message!'
   sig = cyh.sign(sk_main, L, M)
   print("Signature...")
   print("sig =>", sig)

   assert cyh.verify(mpk, L, M, sig), "invalid signature!"
   print("Verification successful!")
   
