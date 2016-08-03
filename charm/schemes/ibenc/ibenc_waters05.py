'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:			06/2011
''' 

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import *
from charm.toolbox.bitstring import Bytes
from charm.toolbox.hash_module import Waters
import hashlib, math

debug = False
class IBE_N04(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> from charm.toolbox.hash_module import Waters
    >>> group = PairingGroup('SS512')
    >>> waters_hash = Waters(group)
    >>> ibe = IBE_N04(group)
    >>> (master_public_key, master_key) = ibe.setup()
    >>> ID = "bob@mail.com"
    >>> kID = waters_hash.hash(ID)
    >>> secret_key = ibe.extract(master_key, kID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, kID, msg)
    >>> decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    
    """Implementation of David Naccahe Identity Based Encryption"""
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secDef=IND_ID_CPA, assumption=DBDH, secModel=SM, id=ZR, messageSpace=[GT, 'KEM'])
        global group
        group = groupObj

    def setup(self, l=32):
        """l is the security parameter
        with l = 32, and the hash function at 256 bits = n * l with n = 8"""
        global waters
        g = group.random(G1)      # generator for group G of prime order p

        sha2_byte_len = 32
        hLen = sha2_byte_len * 8
        n = int(math.floor(hLen / l))
        waters = Waters(group, n, l, 'sha256')
                
        alpha = group.random()  #from Zp
        g1    = g ** alpha      # G1
        g2    = group.random(G2)    #G2
        uprime = group.random(G2)
        U = [group.random() for x in range(n)]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l}
        
        mk = pk.copy()
        mk['g2^alpha'] = g2 ** alpha #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
        
    def extract(self, mk, v):
        '''v = (v1, .., vn) is an identity'''
        r = group.random()
        
        d1 = mk['uPrime']
        for i in range(mk['n']):
            d1 *= mk['U'][i] ** v[i]
            
        d1 = mk['g2^alpha'] * (d1 ** r)
        d2 = mk['g'] ** r
        
        if debug:
            print("D1    =>", d1)
            print("D2    =>", d2)
        return {'d1': d1, 'd2':d2}

    def encrypt(self, pk, ID, M): # M:GT
        t = group.random()
        c1 = (pair(pk['g1'], pk['g2']) ** t) * M
        c2 = pk['g'] ** t
        c3 = pk['uPrime']
        for i in range(pk['n']):
            c3 *= pk['U'][i] ** ID[i]
        c3 = c3 ** t
        
        if debug:
            print("Encrypting")
            print("C1    =>", c1)
            print("C2    =>", c2)
            print("C3    =>", c3)
        return {'c1':c1, 'c2': c2, 'c3':c3}

    def decrypt(self, pk, sID, ct):
        num = pair(sID['d2'], ct['c3'])
        dem = pair(ct['c2'], sID['d1'])
        if debug:
            print("Decrypting")    
            print("arg1    =>", sID['d2'].type)
            print("arg2    =>", ct['c3'].type)
            print("Num:    =>", num)
            print("Dem:    =>", dem)
            
        return ct['c1'] *  num / dem

def main():
    group = PairingGroup('SS512')
    waters_hash = Waters(group)
    ibe = IBE_N04(group)
    (master_public_key, master_key) = ibe.setup()

    ID = "bob@mail.com"
    kID = waters_hash.hash(ID)
    secret_key = ibe.extract(master_key, kID)
    msg = group.random(GT)
    cipher_text = ibe.encrypt(master_public_key, kID, msg)
    decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text)
    assert msg == decrypted_msg, "invalid decryption"
    if debug: print("Successful Decryption!")

if __name__ == "__main__":
    debug = True
    main()

