from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *

N = 3
numSigners = 5
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
        lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
        g = group.random(G2) 
        alpha = group.random(ZR)
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
        Lt = ""
        for i in L:
            Lt += ":"+i 
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
        u = sig['u'] 
        S = sig['S']
        Lt = ""
        for i in L:
            Lt = Lt + ":"+i
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

   L1 = [ "alice", "bob", "carlos", "dexter", "eddie"] 
   L2 = [ "adfas", "asd", "asdfas", "asdfdf", "asdfd"]
   L3 = [ "asdfd", "ase", "kdkdkd", "dkdkdk", "dkdkd"]

   ID1 = "bob"
   ID2 = "asd"
   ID3 = "ase"

   cyh1 = CYH()
   cyh2 = CYH()
   cyh3 = CYH()

   (mpk1, msk1) = cyh1.setup()
   (mpk2, msk2) = cyh2.setup()
   (mpk3, msk3) = cyh3.setup()

   (ID1, Pk1, Sk1) = cyh1.keygen(msk1, ID1)
   (ID2, Pk2, Sk2) = cyh2.keygen(msk2, ID2)
   (ID3, Pk3, Sk3) = cyh3.keygen(msk3, ID3)
  
   sk1 = (ID1, Pk1, Sk1)
   sk2 = (ID2, Pk2, Sk2)
   sk3 = (ID3, Pk3, Sk3)
  
   m1 = 'please sign this new message!'
   m2 = 'asdfk k asdfasdf kasdf'
   m3 = ' asdf kafl  asdfk '

   sig1 = cyh1.sign(sk1, L1, m1)
   sig2 = cyh2.sign(sk2, L2, m2)
   sig3 = cyh3.sign(sk3, L3, m3)

   #print(cyh1.verify(mpk1, L1, m1, sig1))
   #print(cyh2.verify(mpk2, L2, m2, sig2))
   #print(cyh3.verify(mpk3, L3, m3, sig3))


   f_mpk1 = open('mpk1.charmPickle', 'wb')
   f_mpk2 = open('mpk2.charmPickle', 'wb')
   f_mpk3 = open('mpk3.charmPickle', 'wb')

   f_L1 = open('L1.pythonPickle', 'wb')
   f_L2 = open('L2.pythonPickle', 'wb')
   f_L3 = open('L3.pythonPickle', 'wb')

   f_m1 = open('m1.pythonPickle', 'wb')
   f_m2 = open('m2.pythonPickle', 'wb')
   f_m3 = open('m3.pythonPickle', 'wb')

   f_sig1 = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')
   f_sig3 = open('sig3.charmPickle', 'wb')



   pick_mpk1 = pickleObject( serializeDict( mpk1, group ) )


   pick_mpk2 = pickleObject( serializeDict( mpk2, group ) )
   pick_mpk3 = pickleObject( serializeDict( mpk3, group ) )

   pickle.dump(L1, f_L1)



   pickle.dump(L2, f_L2)
   pickle.dump(L3, f_L3)

   pickle.dump(m1, f_m1)
   pickle.dump(m2, f_m2)
   pickle.dump(m3, f_m3)

   pick_sig1 = pickleObject( serializeDict( sig1, group ) )
   pick_sig2 = pickleObject( serializeDict( sig2, group ) )
   pick_sig3 = pickleObject( serializeDict( sig3, group ) )

   f_mpk1.write(pick_mpk1)



   f_mpk2.write(pick_mpk2)
   f_mpk3.write(pick_mpk3)

   f_sig1.write(pick_sig1)
   f_sig2.write(pick_sig2)
   f_sig3.write(pick_sig3)

   f_mpk1.close()

 

   f_mpk2.close()
   f_mpk3.close()

   f_L1.close()
   f_L2.close()
   f_L3.close()

   f_m1.close()
   f_m2.close()
   f_m3.close()

   f_sig1.close()
   f_sig2.close()
   f_sig3.close()

