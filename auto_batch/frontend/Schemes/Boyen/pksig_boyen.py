from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *

N = 1
l = 3
debug = False

class Boyen(PKSig):
    def __init__(self):
        global group
        #group = pairing('../../../param/d224.param')
        group = pairing(80)
    
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
        mpk = {'g1':g1, 'g2':g2, 'A':A[0],    'B':A[1],   'C':A[2], 'At':At[0], 'Bt':At[1], 'Ct':At[2]}
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

    def getPKdict(self, mpk, pk, k):
        A_pk, B_pk, C_pk = {}, {}, {}
        A_pk[ 0 ] = mpk[ k[0] ]
        B_pk[ 0 ] = mpk[ k[1] ]
        C_pk[ 0 ] = mpk[ k[2] ]
        for i in pk.keys():
            A_pk[ i ] = pk[ i ][ k[0] ]
            B_pk[ i ] = pk[ i ][ k[1] ]
            C_pk[ i ] = pk[ i ][ k[2] ]        
        return A_pk, B_pk, C_pk
    
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
        (A, B, C) = A_pk[ 0 ], B_pk[ 0 ], C_pk[ 0 ]
        prod = (A * (B ** m) * (C ** t[0])) ** -s[0]
        
        for i in range(1, l-1):
            (A, B, C) = A_pk[i], B_pk[i], C_pk[i]
            prod *= ((A * (B ** m) * (C ** t[i])) ** -s[i])            

        final = l-1
        d = (sk['a'] + (sk['b'] * m) + (sk['c'] * t[final]))
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
       L_pk[ i+1 ] = L_keys[ i ][ 0 ]
       L_sk[ i+1 ] = L_keys[ i ][ 1 ]

   signer = 3
   sk = L_sk[signer] 
   M = 'please sign this new message!'
   M2 = 'testing'
   sig = boyen.sign(mpk, L_pk, sk, M)
   sig2 = boyen.sign(mpk, L_pk, sk, M2)

   assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
   assert boyen.verify(mpk, L_pk, M2, sig2), "invalid signature!"

   f_mpk = open('mpk.charmPickle', 'wb')
   f_pk = open('pk.charmPickle', 'wb')
   f_sig = open('sig1.charmPickle', 'wb')
   f_sig2 = open('sig2.charmPickle', 'wb')

   f_mess = open('mess.pythonPickle', 'wb')
   f_mess2 = open('mess2.pythonPickle', 'wb')

   pick_mpk = pickleObject( serializeDict( mpk, group ) )
   pick_pk = pickleObject( serializeDict(L_pk, group))
   pick_sig = pickleObject( serializeDict(sig, group))
   pick_sig2 = pickleObject(serializeDict(sig2, group))

   pickle.dump(M, f_mess)
   pickle.dump(M2, f_mess2)

   f_mpk.write(pick_mpk)
   f_pk.write(pick_pk)
   f_sig.write(pick_sig)
   f_sig2.write(pick_sig2)

    
   f_mpk.close()
   f_pk.close()
   f_mess.close()
   f_mess2.close()
   f_sig.close()
   f_sig2.close()




   #print("Verification successful!")
   
   delta = group.init(ZR, randomBits(80))

   D = pair(mpk['g1'],mpk['g2'])

   dotE = group.init(GT, 1)

   Atpk = {}
   Btpk = {} 
   Ctpk = {}
   Atpk[ 0 ] = mpk[ 'At' ]
   Btpk[ 0 ] = mpk[ 'Bt' ]
   Ctpk[ 0 ] = mpk[ 'Ct' ]
   for i in L_pk.keys():
      Atpk[ i ] = L_pk[ i ][ 'At' ]
      Btpk[ i ] = L_pk[ i ][ 'Bt' ]
      Ctpk[ i ] = L_pk[ i ][ 'Ct' ]

   for index in range(0, num_signers):
      S = sig['S'][index]
      preA = S ** delta
      dotA = preA
      dotB = preA ** (H(M)) #is this correct?
      t = sig['t'][index]
      dotC = preA ** t
      dotEpair1 = pair(dotA, Atpk[index])
      dotEpair2 = pair(dotB, Btpk[index])
      dotEpair3 = pair(dotC, Ctpk[index])
      newDotE = dotEpair1 * dotEpair2 * dotEpair3
      dotE = dotE * newDotE


   if (dotE) == (D ** delta):
      print("look here:  success")
   else:
      print("look here:  failure")


   dotE = group.init(GT, 1)

   for index in range(0, 3):
      S = sig['S'][index]
      t = sig['t'][index]
      dotA = pair( (S ** delta), Atpk[index])
      dotB = pair( (S ** (delta * (H(M)))), Btpk[index])
      dotC = pair( (S ** (delta *  t)), Ctpk[index])
      dotE = dotE * (dotA * dotB * dotC) 

   if (dotE) == (D ** delta):
      print("look here:  success")
   else:
      print("look here:  failure")


   dotE = group.init(GT, 1)

   for index in range(0, 3):
      S = sig['S'][index]
      t = sig['t'][index]
      partA = Atpk[index]
      partB = Btpk[index] ** (H(M2))
      partC = Ctpk[index] ** t
      rightSide = partA * partB * partC
      leftSide = S ** delta
      pairResult = pair(leftSide, rightSide)
      dotE = dotE * pairResult

 
   if (dotE) == (D ** delta):
      print("success")
   else:
      print("failure")
 

   S = sig['S'][0]
   t = sig['t'][0]
   partA = Atpk[0]
   partB = Btpk[0]
   partC = Ctpk[0]


   leftSide = pair( S ** delta, partA * (partB ** H(M)) * (partC ** t) )
   rightSide = pair(S ** delta, partA) * pair(S ** (delta * H(M)), partB) * pair(S ** (delta * t), partC)
   if (leftSide == rightSide):
      print("equality holds")
   else:
      print("equality doesn't hold")

