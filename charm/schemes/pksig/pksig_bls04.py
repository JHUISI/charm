'''
:Boneh-Lynn-Shacham Identity Based Signature
 
| From: "D. Boneh, B. Lynn, H. Shacham Short Signatures from the Weil Pairing"
| Published in: Journal of Cryptology 2004
| Available from: http://
| Notes: This is the IBE (2-level HIBE) implementation of the HIBE scheme BB_2.

* type:           signature (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       1/2011
 '''
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair
from charm.core.engine.util import objectToBytes
from charm.toolbox.IBSig import *


debug = False


class BLS01(IBSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('MNT224')
    >>> messages = { 'a':"hello world!!!" , 'b':"test message" }
    >>> ib = BLS01(group)
    >>> (public_key, secret_key) = ib.keygen()
    >>> signature = ib.sign(secret_key['x'], messages)
    >>> ib.verify(public_key, signature, messages) 
    True
    """
    def __init__(self, groupObj):
        IBSig.__init__(self)
        global group
        group = groupObj
        
    def dump(self, obj):
        return objectToBytes(obj, group)
            
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
    groupObj = PairingGroup('MNT224')
    
    m = { 'a':"hello world!!!" , 'b':"test message" }
    bls = BLS01(groupObj)
    
    (pk, sk) = bls.keygen()
    
    sig = bls.sign(sk['x'], m)
    
    if debug: print("Message: '%s'" % m)
    if debug: print("Signature: '%s'" % sig)     
    assert bls.verify(pk, sig, m), "Failure!!!"
    if debug: print('SUCCESS!!!')


if __name__ == "__main__":
    debug = True
    main()
