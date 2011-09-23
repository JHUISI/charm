""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig

debug = False

class CHP(PKSig):
    def __init__(self, groupObj):
        global group, H
        group = groupObj
        
    def setup(self):
        global H,H3
        H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
        H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)
    
    def keygen(self):
        g2, alpha = group.random(G2), group.random(ZR)
        sk = alpha
        pk = {'g2':g2, 'g2a':g2 ** alpha}
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, pk, M, sig):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        if pair(sig, pk['g2']) == (pair(a, pk['g2a']) * (pair(h, pk['g2a']) ** b)):
            return True
        return False

if __name__ == "__main__":
   
   groupObj = pairing('../param/a.param')
   chp = CHP(groupObj)
   chp.setup()

   (pk, sk) = chp.keygen()  
   print("Keygen...")
   print("pk =>", pk)
   print("sk =>", sk)
  
   M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message'}
   sig = chp.sign(pk, sk, M)
   print("Signature...")
   print("sig =>", sig)

   assert chp.verify(pk, M, sig), "invalid signature!"
   print("Verification successful!")
   
