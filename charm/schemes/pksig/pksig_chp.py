""" 
Camenisch-Hohenberger-Pedersen - Identity-based Signatures

| From: "Camenisch, S. Hohenberger, M. Pedersen - Batch Verification of short signatures."
| Published in: EUROCRYPT 2007
| Available from: http://epring.iacr.org/2007/172.pdf
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import G1,G2,ZR,pair
from charm.toolbox.PKSig import PKSig

debug = False

class CHP(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup   
    >>> group = PairingGroup('SS512')
    >>> chp = CHP(group)
    >>> master_public_key = chp.setup()
    >>> (public_key, secret_key) = chp.keygen(master_public_key) 
    >>> msg = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message'}
    >>> signature = chp.sign(public_key, secret_key, msg)
    >>> chp.verify(master_public_key, public_key, msg, signature)
    True
    """
    def __init__(self, groupObj):
        global group, H
        group = groupObj
        
    def setup(self):
        global H,H3
        H = lambda prefix,x: group.hash((str(prefix), str(x)), G1)
        H3 = lambda a,b: group.hash(('3', str(a), str(b)), ZR)
        g = group.random(G2) 
        return { 'g' : g }
    
    def keygen(self, mpk):
        alpha = group.random(ZR)
        sk = alpha
        pk = mpk['g'] ** alpha
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, mpk, pk, M, sig):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        if pair(sig, mpk['g']) == (pair(a, pk) * (pair(h, pk) ** b)):
            return True
        return False

