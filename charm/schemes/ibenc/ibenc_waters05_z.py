'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:			06/2011

:Improved by: Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date: 3/2013
:Notes:
1.e(g_1, g_2) is pre-calculated  as part of public parameters.
2.Previous implementation was trying to do: d1 = mk[`U'][i] ** v[i], we fixed the problem by having $\vec{\omega}$ as a vector in Z_q and u = g^{\vec{\omega}} as U. 
3. We stored \vec{\omega}  as part of msk. This will speed up the extract() a lot. The trick is that, instead of doing exponential operation and then multiply all together, we will compute the exponent first and then do one exponential operation
4 The code works perfectly under asymmetric groups now.
5.All elements in sk_id is now in G2 and ct_id in G1. Before that, we have one element in G1 and the other in G2 in both sk_id and ct_id.
''' 
from __future__ import print_function
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import IBEnc
from charm.toolbox.hash_module import Waters
import math, string, random

def randomStringGen(size=30, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

debug = False
class IBE_N04_z(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> from charm.toolbox.hash_module import Waters
    >>> group = PairingGroup('SS512')
    >>> waters_hash = Waters(group)
    >>> ibe = IBE_N04_z(group)
    >>> (master_public_key, master_key) = ibe.setup()
    >>> ID = "bob@mail.com"
    >>> kID = waters_hash.hash(ID)
    >>> secret_key = ibe.extract(master_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, ID, msg)
    >>> decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    
    """Implementation of David Naccahe Identity Based Encryption"""
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        #IBEnc.setProperty(self, secdef='IND_ID_CPA', assumption='DBDH', secmodel='Standard')
        #, other={'id':ZR}
        #message_space=[GT, 'KEM']
        global group
        group = groupObj
        global waters_hash
        waters_hash = Waters(group)

    def setup(self, l=32):
        '''l is the security parameter
        with l = 32, and the hash function at 160 bits = n * l with n = 5'''
        global waters
        g = group.random(G1)      # generator for group G of prime order p
        
        sha2_byte_len = 32
        hLen = sha2_byte_len * 8
        n = int(math.floor(hLen / l))
        waters = Waters(group, n, l, 'sha256')

        alpha = group.random(ZR)  #from Zp
        g1    = g ** alpha      # G1
        g2    = group.random(G2)    #G2
        u = group.random(ZR)
        uprime = g ** u
        U_z = [group.random(ZR) for x in range(n)]
        U = [g ** x  for x in U_z]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
            'n':n, 'l':l, 'eg1g2':pair(g1, g2)}

        mk = {'g1':g1, 'g2': g2, 'n':n, 'g2^alpha': g2 ** alpha, 'U_z':U_z, 'u':u} #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
        
    def extract(self, mk, ID):
        '''v = (v1, .., vn) is an identity'''

        v = waters_hash.hash(ID)
        r = group.random(ZR)
        
        u = mk['u']

        for i in range(mk['n']):
            u += mk['U_z'][i] * v[i]    
        d1 = mk['g2^alpha'] * (mk['g2'] ** (u * r) )
        d2 = mk['g2'] ** r
        
        if debug:
            print("D1    =>", d1)
            print("D2    =>", d2)
        return {'d1': d1, 'd2':d2}

    def encrypt(self, pk, ID, M): # M:GT

        v = waters_hash.hash(ID)
        t = group.random(ZR)
        c1 = (pk['eg1g2'] ** t) * M
        c2 = pk['g'] ** t
        c3 = pk['uPrime']

        for i in range(pk['n']):
            c3 *= pk['U'][i] ** v[i]
        c3 = c3 ** t
        
        if debug:
            print("Encrypting")
            print("C1    =>", c1)
            print("C2    =>", c2)
            print("C3    =>", c3)
        return {'c1':c1, 'c2': c2, 'c3':c3}

    def decrypt(self, pk, sID, ct):
        num = pair(ct['c3'], sID['d2'])
        dem = pair(ct['c2'], sID['d1'])
        if debug:
            print("Decrypting")    
            print("arg1    =>", sID['d2'].type)
            print("arg2    =>", ct['c3'].type)
            print("Num:    =>", num)
            print("Dem:    =>", dem)
            
        return ct['c1'] *  num / dem

def main():
    group = PairingGroup('MNT224')
    waters_hash = Waters(group)
    ibe = IBE_N04_z(group)
    (master_public_key, master_key) = ibe.setup()

    ID = "bob@mail.com"
    secret_key = ibe.extract(master_key, ID)
    msg = group.random(GT)
    cipher_text = ibe.encrypt(master_public_key, ID, msg)
    decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text)
    assert msg == decrypted_msg, "invalid decryption"
    if debug: print("Successful Decryption!")

if __name__ == "__main__":
    debug = True
    main()

