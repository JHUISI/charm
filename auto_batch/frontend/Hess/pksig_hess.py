""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig

from toolbox.iterate import dotprod
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
        #print("sign...")
        h = group.random(G1) 
        s = group.random(ZR)
        S1 = pair(h,pk['g2']) ** s 
        a = H2(M, S1)
        S2 = (sk ** a) * (h ** s)
        sig = {'S1':S1, 'S2':S2}
        return sig
    
    def verify(self, mpk, pk, M, sig):
        #print("verify...")
        S1 = sig['S1']
        S2 = sig['S2']
        a = H2(M, S1)
        if pair(S2, mpk['g2']) == (pair(pk, mpk['P']) ** a) * S1: 
            return True
        return False

if __name__ == "__main__":
   
   #groupObj = pairing('../param/a.param')
   chch = CHCH()
   (mpk, msk) = chch.setup()

   _id = "janedoe@email.com"
   (pk, sk) = chch.keygen(msk, _id)  
   #print("Keygen...")
   #print("pk =>", pk)
   #print("sk =>", sk)
 
   m1 = "m1"
   m2 = "m2"
   m3 = "m3"
 
   sig1 = chch.sign(mpk, sk, m1)
   sig2 = chch.sign(mpk, sk, m2)
   sig3 = chch.sign(mpk, sk, m3)

   assert chch.verify(mpk, pk, m1, sig1), "invalid signature!"
   assert chch.verify(mpk, pk, m2, sig2), "invalid signature!"
   assert chch.verify(mpk, pk, m3, sig3), "invalid signature!"
   


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

