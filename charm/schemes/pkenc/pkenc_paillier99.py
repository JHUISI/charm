'''
Pascal Paillier (Public-Key)
 
| From: "Public-Key Cryptosystems Based on Composite Degree Residuosity Classes" 
| Published in: EUROCRYPT 1999
| Available from: http://eprint.iacr.org/2009/309.pdf
| Notes: 

* type:           public-key encryption (public key)
* setting:        Integer

:Authors:    J Ayo Akinyele
:Date:            4/2011
'''
from __future__ import print_function
from charm.toolbox.integergroup import lcm,integer
from charm.toolbox.PKEnc import PKEnc
from charm.core.engine.util import *

debug = False
"""A ciphertext class with homomorphic properties"""
class Ciphertext(dict):
    """
    This tests the additively holomorphic properties of 
    the Paillier encryption scheme.

    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = RSAGroup()
    >>> pai = Pai99(group)
    >>> (public_key, secret_key) = pai.keygen()

    >>> msg_1=12345678987654321
    >>> msg_2=12345761234123409
    >>> msg_3 = msg_1 + msg_2
    
    >>> msg_1 = pai.encode(public_key['n'], msg_1)
    >>> msg_2 = pai.encode(public_key['n'], msg_2)
    >>> msg_3 = pai.encode(public_key['n'], msg_3) 
    
    >>> cipher_1 = pai.encrypt(public_key, msg_1)
    >>> cipher_2 = pai.encrypt(public_key, msg_2)
    >>> cipher_3 = cipher_1 + cipher_2
    
    >>> decrypted_msg_3 = pai.decrypt(public_key, secret_key, cipher_3)
    >>> decrypted_msg_3 == msg_3
    True
    """
    def __init__(self, ct, pk, key):
        dict.__init__(self, ct)
        self.pk, self.key = pk, key
    
    def __add__(self, other):
        if type(other) == int: # rhs must be Cipher
           lhs = dict.__getitem__(self, self.key)
           return Ciphertext({self.key:lhs * ((self.pk['g'] ** other) % self.pk['n2']) }, 
                             self.pk, self.key)        
        else: # neither are plain ints
           lhs = dict.__getitem__(self, self.key)
           rhs = dict.__getitem__(other, self.key)
        return Ciphertext({self.key:(lhs * rhs) % self.pk['n2']}, 
                          self.pk, self.key) 
        
    def __mul__(self, other):
        if type(other) == int:
            lhs = dict.__getitem__(self, self.key)
            return Ciphertext({self.key:(lhs ** other)}, self.pk, self.key)
    
    def randomize(self, r): # need to provide random value
        lhs = dict.__getitem__(self, self.key)
        rhs = (integer(r) ** self.pk['n']) % self.pk['n2']
        return Ciphertext({self.key:(lhs * rhs) % self.pk['n2']})
    
    def __str__(self):
        value = dict.__str__(self)
        return value # + ", pk =" + str(pk)
    
class Pai99(PKEnc):
    def __init__(self, groupObj):
        PKEnc.__init__(self)
        global group
        group = groupObj
    
    def L(self, u, n):
        return integer(int(u - 1)) / n
                
    def keygen(self, secparam=1024):
        (p, q, n) = group.paramgen(secparam)
        g = n + 1
        lam = lcm(p - 1, q - 1)
        n2 = n ** 2
        u = (self.L(((g % n2) ** lam), n) % n) ** -1
        pk, sk = {'n':n, 'g':g, 'n2':n2}, {'lamda':lam, 'u':u}
        return (pk, sk)

    def encrypt(self, pk, m):
        g, n, n2 = pk['g'], pk['n'], pk['n2']
        r = group.random(pk['n'])
        c = ((g % n2) ** m) * ((r % n2) ** n)
        return Ciphertext({'c':c}, pk, 'c')
    
    def decrypt(self, pk, sk, ct):
        n, n2 = pk['n'], pk['n2']
        return ((self.L(ct['c'] ** sk['lamda'], n) % n) * sk['u']) % n
    
    def encode(self, modulus, message):
        # takes a string and represents as a bytes object
        elem = integer(message)
        return elem % modulus
        
    def decode(self, pk, element):
        pass

