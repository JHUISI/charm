from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *

N = 3
l = 5
debug = False

class CYH(PKSig):
    def __init__(self):
        global group
        #group = pairing('/Users/matt/Documents/charm/param/a.param')
        group = PairingGroup(80)
    
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

   L0 = [ "alice", "bob", "carlos", "dexter", "eddie"] 
   #L1 = [ "adfas", "asd", "asdfas", "asdfdf", "asdfd"]
   #L2 = [ "asdfd", "ase", "kdkdkd", "dkdkdk", "dkdkd"]

   ID0 = "bob"
   #ID1 = "alice"
   #ID2 = "carlos"

   cyh0 = CYH()
   #cyh1 = CYH()
   #cyh2 = CYH()

   (mpk0, msk0) = cyh0.setup()
   #(mpk1, msk1) = cyh1.setup()
   #(mpk2, msk2) = cyh2.setup()

   (ID0, Pk0, Sk0) = cyh0.keygen(msk0, ID0)
   #(ID1, Pk1, Sk1) = cyh1.keygen(msk1, ID1)
   #(ID2, Pk2, Sk2) = cyh2.keygen(msk2, ID2)
  
   sk0 = (ID0, Pk0, Sk0)
   #sk1 = (ID1, Pk1, Sk1)
   #sk2 = (ID2, Pk2, Sk2)
  
   m0 = 'please sign this new message!'
   m1 = 'asdfk k asdfasdf kasdf'
   m2 = ' asdf kafl  asdfk '

   sig0 = cyh0.sign(sk0, L0, m0)
   sig1 = cyh0.sign(sk0, L0, m1)
   sig2 = cyh0.sign(sk0, L0, m2)

   #print(cyh0.verify(mpk0, L0, m0, sig0))
   #print(cyh0.verify(mpk0, L0, m1, sig1))
   #print(cyh0.verify(mpk0, L0, m2, sig2))


   f_mpk0 = open('mpk0.charmPickle', 'wb')
   #f_mpk1 = open('mpk1.charmPickle', 'wb')
   #f_mpk2 = open('mpk2.charmPickle', 'wb')

   f_L0 = open('L0.pythonPickle', 'wb')
   #f_L1 = open('L1.pythonPickle', 'wb')
   #f_L2 = open('L2.pythonPickle', 'wb')

   f_m0 = open('m0.pythonPickle', 'wb')
   f_m1 = open('m1.pythonPickle', 'wb')
   f_m2 = open('m2.pythonPickle', 'wb')

   f_sig0 = open('sig0.charmPickle', 'wb')
   f_sig1 = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')



   pick_mpk0 = pickleObject( serializeDict( mpk0, group ) )
   #pick_mpk1 = pickleObject( serializeDict( mpk1, group ) )
   #pick_mpk2 = pickleObject( serializeDict( mpk2, group ) )

   pickle.dump(L0, f_L0)
   #pickle.dump(L1, f_L1)
   #pickle.dump(L2, f_L2)

   pickle.dump(m0, f_m0)
   pickle.dump(m1, f_m1)
   pickle.dump(m2, f_m2)

   pick_sig0 = pickleObject( serializeDict( sig0, group ) )
   pick_sig1 = pickleObject( serializeDict( sig1, group ) )
   pick_sig2 = pickleObject( serializeDict( sig2, group ) )

   f_mpk0.write(pick_mpk0)
   #f_mpk1.write(pick_mpk1)
   #f_mpk2.write(pick_mpk2)

   f_sig0.write(pick_sig0)
   f_sig1.write(pick_sig1)
   f_sig2.write(pick_sig2)

   f_mpk0.close()
   #f_mpk1.close()
   #f_mpk2.close()

   f_L0.close()
   #f_L1.close()
   #f_L2.close()

   f_m0.close()
   f_m1.close()
   f_m2.close()

   f_sig0.close()
   f_sig1.close()
   f_sig2.close()

