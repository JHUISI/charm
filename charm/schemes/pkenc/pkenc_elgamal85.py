'''
El Gamal Public Key Encryption Scheme (Decisional Diffie-Hellman Assumption in groups of prime order)

| Available from: http://en.wikipedia.org/wiki/ElGamal_encryption
| Notes: 

* type:          encryption (public key)
* setting:       DDH-hard prime order group
* assumption:    DDH

:Authors: J Ayo Akinyele
:Date:           3/2011
'''

from charm.toolbox.PKEnc import PKEnc
from charm.toolbox.ecgroup import G

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
    """
    >>> from charm.toolbox.eccurve import prime192v2
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> groupObj = ECGroup(prime192v2)
    >>> el = ElGamal(groupObj)    
    >>> (public_key, secret_key) = el.keygen()
    >>> msg = b"hello world!12345678"
    >>> cipher_text = el.encrypt(public_key, msg)
    >>> decrypted_msg = el.decrypt(public_key, secret_key, cipher_text)    
    >>> decrypted_msg == msg
    True
    >>> from charm.toolbox.integergroup import IntegerGroupQ, integer
    >>> p = integer(148829018183496626261556856344710600327516732500226144177322012998064772051982752493460332138204351040296264880017943408846937646702376203733370973197019636813306480144595809796154634625021213611577190781215296823124523899584781302512549499802030946698512327294159881907114777803654670044046376468983244647367)
    >>> q = integer(74414509091748313130778428172355300163758366250113072088661006499032386025991376246730166069102175520148132440008971704423468823351188101866685486598509818406653240072297904898077317312510606805788595390607648411562261949792390651256274749901015473349256163647079940953557388901827335022023188234491622323683)
    >>> groupObj = IntegerGroupQ()
    >>> el = ElGamal(groupObj, p, q)    
    >>> (public_key, secret_key) = el.keygen()
    >>> msg = b"hello world!"
    >>> cipher_text = el.encrypt(public_key, msg)
    >>> decrypted_msg = el.decrypt(public_key, secret_key, cipher_text)    
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, groupObj, p=0, q=0):
        PKEnc.__init__(self)
        global group
        group = groupObj
        if group.groupSetting() == 'integer':
            group.p, group.q, group.r = p, q, 2

    def keygen(self, secparam=1024):
        if group.groupSetting() == 'integer':
            if group.p == 0 or group.q == 0:
                group.paramgen(secparam)
            g = group.randomGen()
        elif group.groupSetting() == 'elliptic_curve':
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
        m = c['c2'] * (s ** -1)
        if group.groupSetting() == 'integer':
            M = group.decode(m % group.p)
        elif group.groupSetting() == 'elliptic_curve':
            M = group.decode(m)
        if debug: print('m => %s' % m)
        if debug: print('dec M => %s' % M)
        return M
