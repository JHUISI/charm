'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:			06/2011
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
    >>> ID = "bob@mail.com"
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
        '''l is the security parameter
        with l = 32, and the hash function at 160 bits = n * l with n = 5'''
        global waters
        sha1_func, sha1_len = 'sha1', 20
        g = group.random(G1)      # generator for group G of prime order p
        
        hLen = sha1_len * 8
        n = int(math.floor(hLen / l))
        waters = Waters(group, n, l, sha1_func)
        
        alpha = group.random()  #from Zp
        g1    = g ** alpha      # G1
        g2    = group.random(G2)    #G2
        uprime = group.random(G2)
        U = [group.random() for x in range(n)]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l, 'egg': pair(g, g2) ** alpha }
        
        # mk = pk.copy()
        mk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l, 'egg': pair(g, g2) ** alpha }
        mk['g2^alpha'] = g2 ** alpha #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
    
    def sign(self, pk, sk, m):
        '''v = (v1, .., vn) is an identity'''
        r = group.random()
        
        d1 = sk['uPrime']
        for i in range(sk['n']):
            d1 *= sk['U'][i] ** m[i]
            
        d1 = sk['g2^alpha'] * (d1 ** r)
        d2 = sk['g'] ** r
        return {'d1': d1, 'd2':d2}

    def verify(self, pk, msg, sig):
        c3 = pk['uPrime']
        for i in range(pk['n']):
            c3 *= pk['U'][i] ** msg[i]
        
        num = pair(pk['g'], sig['d1'])
        dem = pair(sig['d2'], c3)
        return pk['egg'] == num / dem


def main():
    groupObj = PairingGroup('SS512')
    ibe = IBE_N04_Sig(groupObj)
    waters = Waters(group)
    (pk, sk) = ibe.keygen()

    # represents public identity
    M = "bob@mail.com"
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
    
