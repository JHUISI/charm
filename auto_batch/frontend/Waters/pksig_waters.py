from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hashlib
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *

N = 3
l = 5
numSigners = 5

debug = False

class WatersSig:
    def __init__(self):
        global group,lam_func,hashObj
        #group = pairing('/Users/matt/Documents/charm/param/a.param')
        group = PairingGroup(80)
        lam_func = lambda i,a,b: a[i] ** b[i]
        hashObj = hashlib.new('sha1')

    def sha1(self, message):
        h = hashObj.copy()
        h.update(bytes(message, 'utf-8'))
        return Bytes(h.digest())    

    def setup(self, x, l=32):
        alpha = group.random(ZR)
        h = group.random(G1)
        g1 = group.random(G1) 
        g2 = group.random(G2)
        A = pair(h, g2) ** alpha
        y = [group.random(ZR) for i in range(x)]
        y1t = group.random(ZR) 
        y2t = group.random(ZR)

        u1t = g1 ** y1t
        u2t = g1 ** y2t
        u = [g1 ** y[i] for i in range(x)]

        u1b = g2 ** y1t
        u2b = g2 ** y2t
        ub =[g2 ** y[i] for i in range(x)]

        msk = h ** alpha
        mpk = {'g1':g1, 'g2':g2, 'A':A, 'u1t':u1t, 'u2t':u2t, 'u':u, 'u1b':u1b, 'u2b':u2b, 'ub':ub, 'x':x, 'l':l } 
        return (mpk, msk) 

    def strToId(self, pk, strID):
        h = hashObj.copy()
        h.update(bytes(strID, 'utf-8'))
        hash = Bytes(h.digest())
        val = Conversion.OS2IP(hash)
        bstr = bin(val)[2:]
        v=[]
        for i in range(pk['x']):
            binsubstr = bstr[pk['l']*i : pk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        return v
    
    def keygen(self, mpk, msk, ID):
        h = hashObj.copy()
        h.update(bytes(ID, 'utf-8'))
        hash = Bytes(h.digest())
        val = Conversion.OS2IP(hash)
        bstr = bin(val)[2:]
        v=[]
        for i in range(mpk['x']):
            binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        k = v
        r = group.random(ZR)
        k1 = msk * ((mpk['u1t'] * dotprod(group.init(G1), -1, mpk['x'], lam_func, mpk['u'], k)) ** r)  
        k2 = mpk['g1'] ** -r
        sk = (k1, k2)
        return sk
    
    def sign(self, mpk, sk, M):
        h = hashObj.copy()
        h.update(bytes(M, 'utf-8'))
        hash = Bytes(h.digest())
        val = Conversion.OS2IP(hash)
        bstr = bin(val)[2:]
        v=[]
        for i in range(mpk['x']):
            binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        m = v
        (k1, k2) = sk
        s  = group.random(ZR)
        S1 = k1 * ((mpk['u2t'] * dotprod(group.init(G1), -1, mpk['x'], lam_func, mpk['u'], m)) ** s)
        S2 = k2
        S3 = mpk['g1'] ** -s
        sig = {'S1':S1, 'S2':S2, 'S3':S3}
        return sig
    
    def verify(self, mpk, ID, M, sig):
        h = hashObj.copy()
        h.update(bytes(ID, 'utf-8'))
        hash = Bytes(h.digest())
        val = Conversion.OS2IP(hash)
        bstr = bin(val)[2:]
        v=[]
        for i in range(mpk['x']):
            binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        k = v
        h = hashObj.copy()
        h.update(bytes(M, 'utf-8'))
        hash = Bytes(h.digest())
        val = Conversion.OS2IP(hash)
        bstr = bin(val)[2:]
        v=[]
        for i in range(mpk['x']):
            binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        m = v
        S1 = sig['S1'] 
        S2 = sig['S2'] 
        S3 = sig['S3']
        A = mpk['A'] 
        g2 = mpk['g2']
        comp1 = dotprod(group.init(G2), -1, mpk['x'], lam_func, mpk['ub'], k)
        comp2 = dotprod(group.init(G2), -1, mpk['x'], lam_func, mpk['ub'], m)
        if (pair(S1, g2) * pair(S2, mpk['u1b'] * comp1) * pair(S3, mpk['u2b'] * comp2)) == A: 
            return True
        return False

if __name__ == "__main__":
   x = 5
   waters = WatersSig()
   (mpk, msk) = waters.setup(x)

   ID = 'janedoe@email.com'
   sk = waters.keygen(mpk, msk, ID)  
   m1 = 'm1'
   m2 = 'm2'
   m3 = 'm3'

   sig1 = waters.sign(mpk, sk, m1)
   sig2 = waters.sign(mpk, sk, m2)
   sig3 = waters.sign(mpk, sk, m3)

   assert waters.verify(mpk, ID, m1, sig1), "invalid signature!"
   assert waters.verify(mpk, ID, m2, sig2), "invalid signature!"
   assert waters.verify(mpk, ID, m3, sig3), "invalid signature!"


   f_mpk = open('mpk.charmPickle', 'wb')
   f_id = open('id.pythonPickle', 'wb')

   f_m1 = open('m1.pythonPickle', 'wb')
   f_m2 = open('m2.pythonPickle', 'wb')
   f_m3 = open('m3.pythonPickle', 'wb')

   f_sig1 = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')
   f_sig3 = open('sig3.charmPickle', 'wb')

   pick_mpk = pickleObject( serializeDict( mpk, group ) )
   pickle.dump(ID, f_id)

   pickle.dump(m1, f_m1)
   pickle.dump(m2, f_m2)
   pickle.dump(m3, f_m3)

   pick_sig1 = pickleObject( serializeDict( sig1, group ) )
   pick_sig2 = pickleObject( serializeDict( sig2, group ) )
   pick_sig3 = pickleObject( serializeDict( sig3, group ) )

   f_mpk.write(pick_mpk)

   f_sig1.write(pick_sig1)
   f_sig2.write(pick_sig2)
   f_sig3.write(pick_sig3)

   f_mpk.close()
   f_id.close()

   f_m1.close()
   f_m2.close()
   f_m3.close()

   f_sig1.close()
   f_sig2.close()
   f_sig3.close()


'''

   delta = group.init(ZR, randomBits(80))

   h = hashObj.copy()
   h.update(bytes(ID, 'utf-8'))
   hash = Bytes(h.digest())
   val = Conversion.OS2IP(hash)
   bstr = bin(val)[2:]
   v=[]
   for i in range(mpk['x']):
      binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
      intval = int(binsubstr, 2)
      intelement = group.init(ZR, intval)
      v.append(intelement)

   k = v
   h = hashObj.copy()
   h.update(bytes(m1, 'utf-8'))
   hash = Bytes(h.digest())
   val = Conversion.OS2IP(hash)
   bstr = bin(val)[2:]
   v=[]
   for i in range(mpk['x']):
      binsubstr = bstr[mpk['l']*i : mpk['l']*(i+1)]
      intval = int(binsubstr, 2)
      intelement = group.init(ZR, intval)
      v.append(intelement)

   m = v
   S1 = sig1['S1'] 
   S2 = sig1['S2'] 
   S3 = sig1['S3']
   A = mpk['A'] 
   g2 = mpk['g2']

   comp1 = dotprod(group.init(G2), -1, mpk['x'], lam_func, mpk['ub'], k)
   comp2 = dotprod(group.init(G2), -1, mpk['x'], lam_func, mpk['ub'], m)
   if (pair(S1, g2) * pair(S2, mpk['u1b'] * comp1) * pair(S3, mpk['u2b'] * comp2)) == A: 
      print("individual works")
   else:
      print("individual doesn't work")

   A2 = pair ( ( S1 ** delta ) , g2 )

   B2 = pair ( ( S2 ** delta ) , mpk['u1b'] )

   C2 = pair ( ( S3 ** delta ) , mpk['u2b'] )

   dotprod = group.init(GT, 1)


   for index in range(0, mpk['x']):
      D1 = ( (S2 ** k[index]) * (S3 ** m[index]) ) ** delta
      D2 = pair ( D1, mpk['ub'][index] )
      dotprod = dotprod * D2
      print(dotprod)

   leftSide = A2 * B2 * C2 * dotprod

   rightSide = A ** delta

   if (leftSide == rightSide):
      print("success")
   else:
      print("failure")
'''
