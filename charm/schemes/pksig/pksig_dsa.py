""" 
Digital Signature Algorithm (DSA)

| From: "NIST proposed in Aug 1991 for use in DSS."
| Published in: FIPS 186
| Available from: 
| Notes: 

* type:           signature
* setting:        integer groups

:Authors:    J. Ayo Akinyele
:Date:       5/2011
"""

from charm.toolbox.integergroup import IntegerGroupQ
from charm.toolbox.PKSig import PKSig

debug = False
class DSA(PKSig):
    """
    >>> from charm.core.math.integer import integer
    >>> p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
    >>> q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)    
    >>> dsa = DSA(p, q)
    >>> (public_key, secret_key) = dsa.keygen(1024)
    >>> msg = "hello world test message!!!"
    >>> signature = dsa.sign(public_key, secret_key, msg)
    >>> dsa.verify(public_key, signature, msg)
    True
    """
    def __init__(self, p=0, q=0):
        global group
        group = IntegerGroupQ()
        group.p, group.q, group.r = p, q, 2
        
    def keygen(self, bits):
        if group.p == 0 or group.q == 0:
            group.paramgen(bits)
        global p,q
        p,q = group.p, group.q 
        x = group.random()
        g = group.randomGen()
        y = (g ** x) % p
        return ({'g':g, 'y':y}, x)
    
    def sign(self, pk, x, M):
        while True:
            k = group.random()
            r = (pk['g'] ** k) % q
            s = (k ** -1) * ((group.hash(M) + x*r) % q)
            if (r == 0 or s == 0):
                print("unlikely error r = %s, s = %s" % (r,s))
                continue
            else:
                break
        return { 'r':r, 's':s }
        
    def verify(self, pk, sig, M):
        w = (sig['s'] ** -1) % q
        u1 = (group.hash(M) * w) % q
        u2 = (sig['r'] * w) % q
        v = ((pk['g'] ** u1) * (pk['y'] ** u2)) % p
        v %= q   
        if v == sig['r']:
            return True
        else:
            return False
        
