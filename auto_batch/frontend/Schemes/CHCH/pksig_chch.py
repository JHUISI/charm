from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *

N = 3
debug = False

class CHCH(PKSig):
    def __init__(self):
        global group
        group = pairing('/Users/matt/Documents/charm/param/a.param')
        
    def setup(self):
        global H1,H2
        H1 = lambda x: group.H(x, G1)
        H2 = lambda x,y: group.H((x,y), ZR)
        g2 = group.random(G2) 
        alpha = group.random(ZR)
        msk = alpha
        P = g2 ** alpha 
        mpk = {'P':P, 'g2':g2}
        return (mpk, msk)

    def keygen(self, msk, ID):
        alpha = msk
        sk = H1(ID) ** alpha
        pk = H1(ID)
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        s = group.random(ZR)
        S1 = pk ** s
        a = H2(M, S1)
        S2 = sk ** (s + a)
        sig = {'S1':S1, 'S2':S2}
        return sig
    
    def verify(self, mpk, pk, M, sig):
        S1 = sig['S1']
        S2 = sig['S2']
        a = H2(M, sig['S1'])
	# END_PRECOMPUTE
        if pair(sig['S2'], mpk['g2']) == pair(sig['S1'] * (pk ** a), mpk['P']): 
            return True
        return False

if __name__ == "__main__":
   
   chch = CHCH()
   (mpk, msk) = chch.setup()

   #print("mpk")
   #print(mpk)
   #print("\n")

   _id = "janedoe@email.com"
   (pk, sk) = chch.keygen(msk, _id)  

   #print("pk")
   #print(pk)
   #print("\n")
 
   m1 = "m1" 
   m2 = "m2"
   m3 = "m3"

   sig1 = chch.sign(pk, sk, m1)
   sig2 = chch.sign(pk, sk, m2)
   sig3 = chch.sign(pk, sk, m3)

   #print("sig1")
   #print(sig1)
   #print("\n")

   #print("sig2")
   #print(sig2)
   #print("\n")

   #print("sig3")
   #print(sig3)
   #print("\n")

   assert chch.verify(mpk, pk, m1, sig1), "invalid signature!"
   assert chch.verify(mpk, pk, m2, sig2), "invalid signature!"
   assert chch.verify(mpk, pk, m3, sig3), "invalid signature!"

   delta = group.init(ZR, randomBits(80))

   dotA = sig1['S2'] ** delta

   a = H2(m1, sig1['S1'])

   dotB = sig1['S1'] * (pk ** a )

   if (pair(dotA, mpk['g2'])) == (pair(dotB, mpk['P'])):
      print("success")
   else:
      print("failure")

   f_mpk = open('mpk.charmPickle', 'wb')
   f_pk  = open('pk.charmPickle', 'wb')   

   f_m1 = open('m1.pythonPickle', 'wb')
   f_m2 = open('m2.pythonPickle', 'wb')
   f_m3 = open('m3.pythonPickle', 'wb')

   f_sig1 = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')
   f_sig3 = open('sig3.charmPickle', 'wb')

   pick_mpk = pickleObject( serializeDict( mpk, group))
   pick_pk = pickleObject( serializeDict(pk, group))

   pickle.dump(m1, f_m1)
   pickle.dump(m2, f_m2)
   pickle.dump(m3, f_m3)

   pick_sig1 = pickleObject( serializeDict( sig1, group ) )
   pick_sig2 = pickleObject( serializeDict( sig2, group ) )
   pick_sig3 = pickleObject( serializeDict( sig3, group ) )

   f_mpk.write(pick_mpk)
   f_pk.write(pick_pk)

   f_sig1.write(pick_sig1)
   f_sig2.write(pick_sig2)
   f_sig3.write(pick_sig3)

   f_mpk.close()
   f_pk.close()
 
   f_m1.close()
   f_m2.close()
   f_m3.close()

   f_sig1.close()
   f_sig2.close()
   f_sig3.close()

