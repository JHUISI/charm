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

debug = False
class ElGamalCipher(dict):
    def __init__(self, ct):
        if type(ct) != dict: assert False, "Not a dictionary!"
        if not set(ct).issubset(['c1', 'c2']): assert False, "'c1','c2' keys not present."
        dict.__init__(self, ct)

    def __add__(self, other):
        if type(other) == int:
           lhs_c1 = dict.__getitem__(self, 'c1')
           lhs_c2 = dict.__getitem__(self, 'c2')
           return ElGamalCipher({'c1':lhs_c1, 'c2':lhs_c2 + other})
        else:
           pass 

    def __mul__(self, other):
        if type(other) == int:
           lhs_c1 = dict.__getitem__(self, 'c1')
           lhs_c2 = dict.__getitem__(self, 'c2')
           return ElGamalCipher({'c1':lhs_c1, 'c2':lhs_c2 * other})
        else:
           lhs_c1 = dict.__getitem__(self, 'c1') 
           rhs_c1 = dict.__getitem__(other, 'c1')

           lhs_c2 = dict.__getitem__(self, 'c2') 
           rhs_c2 = dict.__getitem__(other, 'c2')
           return ElGamalCipher({'c1':lhs_c1 * rhs_c1, 'c2':lhs_c2 * rhs_c2})
        return None

class ElGamal(PKEnc):
    def __init__(self, group_type=int, builtin_cv=410):
        PKEnc.__init__(self)
        global _type
        _type = group_type
        self.paramgen(_type, builtin_cv)

    def paramgen(self, _type, _cv):
        global group
        if _type == int:
            group = IntegerGroupQ()
        elif _type == ecc:
            group = ECGroup(_cv)
        else:
            assert False, "Invalid Type Exception!"

    def keygen(self, secparam=1024):
        if _type == int:
            group.paramgen(secparam)
            g = group.randomGen()
        elif _type == ecc:
            g = group.random(G)
        # x is private, g is public param
        x = group.random(); h = g ** x
        if debug:
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
        return ElGamalCipher({'c1':c1, 'c2':c2})
    
    def decrypt(self, pk, sk, c):
        s = c['c1'] ** sk['x']
        m = c['c2'] * ~s
        M = group.decode(m)
        if debug: print('m => %s' % m)
        if debug: print('dec M => %s' % M)
        return M

def main():
    el = ElGamal(ecc, 410)    
    (pk, sk) = el.keygen()
    msg = "hello world!"
    size = len(msg)
    cipher1 = el.encrypt(pk, msg)
    
    m = el.decrypt(pk, sk, cipher1)    
    assert m[0:size] == msg[0:size]
    if debug: print("SUCCESSFULLY DECRYPTED!!!")
        
if __name__ == "__main__":
    debug = True
    main()
