""" 
Digital Signature Algorithm (DSA)

| From: "NIST proposed in Aug 1991 for use in DSS."
| Published in: FIPS 186
| Available from: 
| Notes: 

* type:           signature
* setting:        elliptic curve groups

:Authors:    J. Ayo Akinyele
:Date:       5/2011
"""
from charm.toolbox.ecgroup import ECGroup,ZR,G
from charm.toolbox.PKSig import PKSig

debug = False
class ECDSA(PKSig):
    """
    >>> from charm.toolbox.eccurve import prime192v2
    >>> group = ECGroup(prime192v2)
    >>> ecdsa = ECDSA(group)
    >>> (public_key, secret_key) = ecdsa.keygen(0)
    >>> msg = "hello world! this is a test message."
    >>> signature = ecdsa.sign(public_key, secret_key, msg)
    >>> ecdsa.verify(public_key, signature, msg)
    True
    """
    def __init__(self, groupObj):
        PKSig.__init__(self)
        global group
        group = groupObj
        
    def keygen(self, bits):
        group.paramgen(bits)
        x, g = group.random(), group.random(G)
        y = (g ** x)
        return ({'g':g, 'y':y}, x)
    
    def sign(self, pk, x, M):
        while True:
            k = group.random()
            r = group.zr(pk['g'] ** k)
            e = group.hash(M)
            s = (k ** -1) * (e + x * r)
            if (r == 0 or s == 0):
                print ("unlikely error r = %s, s = %s" % (r,s))
                continue
            else:
                break
        return { 'r':r, 's':s }
        
    def verify(self, pk, sig, M):
        w = sig['s'] ** -1
        u1 = group.hash(M) * w
        u2 = sig['r'] * w
        v = (pk['g'] ** u1) * (pk['y'] ** u2)
    
        if group.zr(v) == sig['r']:
            return True
        else:
            return False

