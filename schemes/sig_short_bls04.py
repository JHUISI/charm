# Boneh-Lynn-Shacham Identity Based Signature
# 
# From: "D. Boneh, B. Lynn, H. Shacham Short Signatures from the Weil Pairing"
# Published in: Journal of Cryptology 2004
# Available from: http://
# Notes: This is the IBE (2-level HIBE) implementation of the HIBE scheme BB_2.
#
# type:           signature (identity-based)
# setting:        bilinear groups (asymmetric)
#
# Implementer:    Joseph Ayo Akinyele
# Date:            1/2011
from toolbox.pairinggroup import *
from charm.engine.util import *

debug = False
class IBSig():
    def __init__(self, groupObj):
        global group
        group = groupObj
        
    def dump(self, obj):
        ser_a = serializeDict(obj, group)
        return str(pickleObject(ser_a))
            
    def keygen(self, secparam=None):
        g, x = group.random(G2), group.random()
        g_x = g ** x
        pk = { 'g^x':g_x, 'g':g, 'identity':str(g_x), 'secparam':secparam }
        sk = { 'x':x }
        return (pk, sk)
        
    def sign(self, x, message):
        M = self.dump(message)
        if debug: print("Message => '%s'" % M)
        return group.hash(M, G1) ** x
        
    def verify(self, pk, sig, message):
        M = self.dump(message)
        h = group.hash(M, G1)
        if pair(sig, pk['g']) == pair(h, pk['g^x']):
            return True  
        return False 

def main():
    groupObj = PairingGroup('d224.param')
    
    m = { 'a':"hello world!!!" , 'b':"test message" }
    bls = IBSig(groupObj)
    
    (pk, sk) = bls.keygen(0)
    
    sig = bls.sign(sk['x'], m)
    
    if debug: print("Message: '%s'" % m)
    if debug: print("Signature: '%s'" % sig)     
    assert bls.verify(pk, sig, m)
    if debug: print('SUCCESS!!!')
    
if __name__ == "__main__":
    main()
    
