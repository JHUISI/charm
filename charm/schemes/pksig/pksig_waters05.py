'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:		06/2011

:Improved by: Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date: 3/2013
:Notes:
1. e(g1,g2) is pre-calculated as part of public parameters.
2. g1 and g2 have been swapped. In the original scheme, signature happens in G2
but now, it happens in G1.
3. I stored U_z and u as part of mk. This will speed up the sign() a lot.
The trick is that, instead of doing exponential operation and then multiply
all together, I compute the exponent first and then do one exponential operation
''' 

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.PKSig import PKSig
from charm.toolbox.enum import Enum
from charm.toolbox.hash_module import Waters
import math

debug = False
class IBE_N04_Sig(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('SS512')
    >>> waters = Waters(group)
    >>> ibe = IBE_N04_Sig(group)
    >>> (public_key, secret_key) = ibe.keygen()
    >>> ID = "bob@example.com"
    >>> msg = waters.hash("This is a test.")    
    >>> signature = ibe.sign(public_key, secret_key, msg)
    >>> ibe.verify(public_key, msg, signature)
    True
    """
    """Implementation of David Naccahe Identity Based Encryption"""
    def __init__(self, groupObj):
        PKSig.__init__(self)
        #PKSig.setProperty(self, secdef='IND_ID_CPA', assumption='DBDH', secmodel='Standard')
        #, other={'id':ZR}
        #message_space=[GT, 'KEM']
        global group 
        group = groupObj        
        
    def keygen(self, l=32):
        """l is the security parameter
        with l = 32, and the hash function at 256 bits = n * l with n = 8"""
        global waters
        g = group.random(G2)      # generator for group G of prime order p
        
        #hLen = sha1_len * 8
        #int(math.floor(hLen / l))
        sha2_byte_len = 32
        hLen = sha2_byte_len * 8
        n = int(math.floor(hLen / l))
        waters = Waters(group, n, l, 'sha256')
        
        alpha = group.random(ZR)  #from Zp
        g2    = g ** alpha      
        g1    = group.random(G1)   
        u = group.random(ZR)
        uprime = g ** u
        U_z = [group.random(ZR) for x in range(n)]
        U = [g ** x  for x in U_z]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U,
              'n':n, 'l':l, 'egg': pair(g1, g2) }
        
        mk = {'g1^alpha':g1 ** alpha, 'U_z':U_z, 'u':u} #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
    
    def sign(self, pk, sk, m):
        """v = (v1, .., vn) is an identity"""
        r = group.random(ZR)
        u = sk['u']
        for i in range(pk['n']):
            u += sk['U_z'][i] * m[i]
            
        d1 = sk['g1^alpha'] * (pk['g1'] ** (u * r))
        d2 = pk['g1'] ** r
        return {'d1': d1, 'd2':d2}

    def verify(self, pk, msg, sig):
        c3 = pk['uPrime']
        for i in range(pk['n']):
            c3 *= pk['U'][i] ** msg[i]
        
        return pk['egg'] == (pair(sig['d1'], pk['g']) / pair(sig['d2'], c3))


def main():
    groupObj = PairingGroup('SS512')
    ibe = IBE_N04_Sig(groupObj)
    waters = Waters(group)
    (pk, sk) = ibe.keygen()

    # represents public identity
    M = "bob@example.com"
    msg = waters.hash("This is a test.")    
    sig = ibe.sign(pk, sk, msg)
    if debug:
        print("original msg => '%s'" % M)
        print("msg => '%s'" % msg)
        print("sig => '%s'" % sig)

    assert ibe.verify(pk, msg, sig), "Failed verification!"
    if debug: print("Successful Verification!!! msg => '%s'" % msg)

if __name__ == '__main__':
    debug = True
    main()
