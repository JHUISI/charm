# El Gamal Public Key Encryption Scheme (Decisional Diffie-Hellman Assumption in groups of prime order)
# Available from: http://en.wikipedia.org/wiki/ElGamal_encryption
# Notes: 
#
# type:          encryption (public key)
# setting:       DDH-hard prime order group
# assumption:    DDH
#
# Implementer:    J Ayo Akinyele
# Date:           3/2011

from toolbox.integergroup import *
from toolbox.ecgroup import *
from toolbox.PKEnc import *

class ElGamal(PKEnc):
    def __init__(self, group_type='int', builtin_cv=410):
        PKEnc.__init__(self)
        global _type
        _type = group_type
        self.paramgen(_type, builtin_cv)

    def paramgen(self, _type, _cv):
        global group
        if _type == 'int':
            group = IntegerGroupQ()
        elif _type == 'ecc':
            group = ECGroup(_cv)
        else:
            raise InvalidTypeException

    def keygen(self, secparam=1024):
        if _type == 'int':
            group.paramgen(secparam)
            g = group.randomGen()
        elif _type == 'ecc':
            g = group.random(G)
        # x is private, g is public param
        x = group.random(); h = g ** x
        print('Public parameters...')
        print('h => %s' % h)
        print('g => %s' % g)
        print('Secret key...')
        print('x => %s' % x)
        pk = {'g':g, 'h':h }
        sk = {'x':x}
        return (pk, sk)
    
    def encrypt(self, pk, M):    
        y = group.random()
        c1 = pk['g'] ** y 
        s = pk['h'] ** y
        # check M and make sure it's right size
        c2 = group.encode(M) * s
        return {'c1':c1, 'c2':c2}
    
    def decrypt(self, pk, sk, c):
        s = c['c1'] ** sk['x']
        m = c['c2'] * ~s
        M = group.decode(m)
        print('m => %s' % m)
        print('dec M => %s' % M)
        return M
        
if __name__ == "__main__":
    el = ElGamal('ecc', 410)    
    (pk, sk) = el.keygen()
    msg = "hello world!"
    size = len(msg)
    ciphertext = el.encrypt(pk, msg)
    
    m = el.decrypt(pk, sk, ciphertext)    
    if m[0:size] == msg[0:size]:
        print("SUCCESSFULLY DECRYPTED!!!")
    else:
        print("FAILED TO DECRYPT :(")
        
    
