""" TODO: Description of Scheme here.
"""

from toolbox.pairinggroup import *
from charm.engine.util import *
from toolbox.PKSig import *

debug = False
class CHP(PKSig):
    def __init__(self, groupObj):
        global group, H1, H2, H3
        group = groupObj
        
    def setup(self):
        H1 = lambda x: group.hash(('0', str(x)), G1)
        H2 = lambda y: group.hash(('1', str(y)), G1)
        H3 = lambda a,b: group.hash(('2', str(a), str(b)), ZR)
    
    def keygen(self):
        g2, alpha = group.random(G2), group.random(ZR)
        sk = alpha
        pk = {'g2':g2, 'g2^a':g2 ** alpha}
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H1(M['t1'])
        h = H2(M['t2'])
        b = H3(M['t3'], M['str'])
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, pk, M, sig):
        a = H1(M['t1'])
        h = H2(M['t2'])
        b = H3(M['t3'], M['str'])
        if pair(sig, pk['g2']) == (pair(a, pk['g2^a']) * pair(h, pk['g2^a'])):
            return True
        return False