""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig

from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *



N = 3

debug = False

class CHP(PKSig):
    def __init__(self):
        global group, H
        group = pairing('/Users/matt/Documents/charm/param/a.param')
        
    def setup(self):
        global H,H3
        H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
        H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)
        g = group.random(G2) 
        mpk = { 'g' : g }
        return mpk
    
    def keygen(self, mpk):
        alpha = group.random(ZR)
        sk = alpha
        pk = mpk['g'] ** alpha
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, mpk, pk, M, sig):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        if pair(sig, mpk['g']) == (pair(a, pk) * pair(h, pk ** b)):
            return True
        return False

if __name__ == "__main__":
   
   #groupObj = pairing('../param/a.param')
   chp = CHP()
   mpk = chp.setup()

   #print(mpk)
   #print("\n")
   (pk, sk) = chp.keygen(mpk)  
   #print("Keygen...")
   #print("pk =>", pk)
   #print("sk =>", sk)

   #print(pk)
   #print("\n")  
   M1 = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message1'}
   M2 = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message2'}
   M3 = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message3'}

   sig1 = chp.sign(pk, sk, M1)
   sig2 = chp.sign(pk, sk, M2)
   sig3 = chp.sign(pk, sk, M3)


   #print(sig1)
   #print("\n")
   #print(sig2)
   #print("\n")
   #print(sig3)
   #print("\n")

   #print("Signature...")
   #print("sig =>", sig)

   assert chp.verify(mpk, pk, M1, sig1), "invalid signature!"
   assert chp.verify(mpk, pk, M2, sig2), "invalid signature!"
   assert chp.verify(mpk, pk, M3, sig3), "invalid signature!"
   #print("Verification successful!")
   


   delta1 = group.init(ZR, randomBits(80))
   delta2 = group.init(ZR, randomBits(80))
   delta3 = group.init(ZR, randomBits(80))
   
   A1 = sig1 ** delta1
   #print(A1)
   #print("\n")
   A2 = sig2 ** delta2
   #print(A2)
   #print("\n")
   A3 = sig3 ** delta3
   #print(A3)
   #print("\n")
   
   B1 = pk ** delta1
   #print(B1)
   #print("\n")
   B2 = pk ** delta2
   #print(B2)
   #print("\n")
   B3 = pk ** delta3
   #print(B3)
   #print("\n")
   
   C1 = B1 ** H3(M1['str'], M1['t3'])
   #print(C1)
   #print("\n")
   C2 = B2 ** H3(M2['str'], M2['t3'])
   #print(C2)
   #print("\n")
   C3 = B3 ** H3(M3['str'], M3['t3'])
   #print(C3)
   #print("\n")
   
   dotA = A1 * A2 * A3
   #print(dotA)
   #print("\n")
   dotB = B1 * B2 * B3
   #print(dotB)
   #print("\n")
   dotC = C1 * C2 * C3
   #print(dotC)
   #print("\n")

   littleA = H(1, M1['t1'])
   #print(littleA)
   #print("\n")
   littleH = H(2, M1['t2'])
   #print(littleH)
   #print("\n")
   
   print(H3(M1['str'], M1['t3']))

   if pair(dotA,mpk['g']) == (pair(littleA,dotB) * pair(littleH,dotC)):
       print("pass")
   else:
       print("fail")



   f_mpk = open('mpk.charmPickle', 'wb')

   f_pk = open('pk.charmPickle', 'wb')



   f_m0 = open('m0.pythonPickle', 'wb')
   f_m1 = open('m1.pythonPickle', 'wb')
   f_m2 = open('m2.pythonPickle', 'wb')

   f_sig0 = open('sig0.charmPickle', 'wb')
   f_sig1 = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')



   pick_mpk = pickleObject( serializeDict( mpk, group ) )
   pick_pk = pickleObject( serializeDict( pk, group))   


   pickle.dump(M1, f_m0)
   pickle.dump(M2, f_m1)
   pickle.dump(M3, f_m2)

   pick_sig0 = pickleObject( serializeDict( sig1, group ) )
   pick_sig1 = pickleObject( serializeDict( sig2, group ) )
   pick_sig2 = pickleObject( serializeDict( sig3, group ) )

   f_mpk.write(pick_mpk)
   f_pk.write(pick_pk)

   f_sig0.write(pick_sig0)
   f_sig1.write(pick_sig1)
   f_sig2.write(pick_sig2)

   f_mpk.close()
   f_pk.close()


   f_m0.close()
   f_m1.close()
   f_m2.close()

   f_sig0.close()
   f_sig1.close()
   f_sig2.close()

