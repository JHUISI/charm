""" 
Hohenberger-Waters - Realizing hash-and-sign signatures

| From: "S. Hohenberger and B. Waters - Realizing hash-and-sign signatures under standard assumptions."
| Published in: EUROCRYPT 2009
| Available from: pages 333-350
| Notes: CDH construction

* type:           signature
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair
from charm.toolbox.PKSig import PKSig
from math import ceil, log 

debug=False
class HW(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup, GT
    >>> group = PairingGroup('SS512')
    >>> hw = HW(group)
    >>> (public_key, secret_key) = hw.setup()
    >>> msg = "please sign this message now please!"    
    >>> signature = hw.sign(public_key, secret_key, public_key['s'], msg)
    >>> hw.verify(public_key, msg, signature)
    True
    """
    def __init__(self, groupObj):
        global group
        group = groupObj

    def ceilog(self, value):
        return group.init(ZR, ceil(log(value, 2)))
        
    def setup(self):
        s = 0
        g1, a = group.random(G1), group.random(ZR)
        g2 = group.random(G2)
        A = g2 ** a
        u, v, d = group.random(G1), group.random(G1), group.random(G1)
        U = pair(u, A)
        V = pair(v, A)
        D = pair(d, A)
        w, z, h = group.random(ZR), group.random(ZR), group.random(ZR)
        w1, w2 = g1 ** w, g2 ** w
        z1, z2 = g1 ** z, g2 ** z
        h1, h2 = g1 ** h, g2 ** h
        pk = {'U':U, 'V':V, 'D':D, 'g1':g1, 'g2':g2, 'A':A,  
              'w1':w1, 'w2':w2, 'z1':z1, 'z2':z2, 
              'h1':h1, 'h2':h2, 'u':u, 'v':v, 'd':d, 's':s }
        sk = {'a':a }
        return (pk, sk)
    
    def sign(self, pk, sk, s, msg):
        s += 1
        S = group.init(ZR, s)
        if debug: print("S =>", S)
        M = group.hash(msg, ZR)
        r, t = group.random(ZR), group.random(ZR)
        sigma1a = ((pk['u'] ** M) * (pk['v'] ** r) * pk['d']) ** sk['a']
        sigma1b = ((pk['w1'] ** self.ceilog(s)) * (pk['z1'] ** S) * pk['h1']) ** t
        sigma1 =  sigma1a * sigma1b
        sigma2 = pk['g1'] ** t
        
        return { 1:sigma1, 2:sigma2, 'r':r, 'i':s }
        
    def verify(self, pk, msg, sig):
        M = group.hash(msg, ZR)
        sigma1, sigma2 = sig[1], sig[2]
        r, s = sig['r'], sig['i']
        S = group.init(ZR, s)        
        U, V, D = pk['U'], pk['V'], pk['D']
        rhs_pair = pair(sigma2, (pk['w2'] * self.ceilog(s)) * (pk['z2'] ** S) * pk['h2'])
        
        if( pair(sigma1, pk['g2']) == (U ** M) * (V ** r) * D * rhs_pair ):
            return True
        else:
            return False
        
def main():
    groupObj = PairingGroup('SS512')
    hw = HW(groupObj)
    
    (pk, sk) = hw.setup()
    if debug:
        print("Public parameters")
        print("pk =>", pk)

    m = "please sign this message now please!"    
    sig = hw.sign(pk, sk, pk['s'], m)
    if debug:
        print("Signature...")
        print("sig =>", sig)

    assert hw.verify(pk, m, sig), "invalid signature"
    if debug: print("Verification Successful!!")

if __name__ == "__main__":
    debug = True
    main()
