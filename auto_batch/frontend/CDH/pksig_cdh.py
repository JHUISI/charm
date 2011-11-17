#from toolbox.pairinggroup import *
from charm.pairing import *
from toolbox.PKSig import *
from math import *

class CDH(PKSig):
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
        print("S =>", S)
        M = group.H(msg, ZR)
        r, t = group.random(ZR), group.random(ZR)
        sigma1a = ((pk['u'] ** M) * (pk['v'] ** r) * pk['d']) ** sk['a']
        sigma1b = ((pk['w1'] ** self.ceilog(s)) * (pk['z1'] ** S) * pk['h1']) ** t
        sigma1 =  sigma1a * sigma1b
        sigma2 = pk['g1'] ** t
        
        return { 1:sigma1, 2:sigma2, 'r':r, 'i':s }
        
    def verify(self, pk, msg, sig):
        M = group.H(msg, ZR)
        sigma1, sigma2 = sig[1], sig[2]
        r, s = sig['r'], sig['i']
        S = group.init(ZR, s)        
        U, V, D = pk['U'], pk['V'], pk['D']
        rhs_pair = pair(sigma2, (pk['w2'] * self.ceilog(s)) * (pk['z2'] ** S) * pk['h2'])
        
        if( pair(sigma1, pk['g2']) == (U ** M) * (V ** r) * D * rhs_pair ):
            return True
        else:
            return False
        
if __name__ == "__main__":
    AES_SECURITY = 80
    # can this scheme be implemented in an asymmetric group?
#    groupObj = PairingGroup(AES_SECURITY)
    groupObj = pairing(AES_SECURITY)
    cdh = CDH(groupObj)
    
    (pk, sk) = cdh.setup()
    print("Public parameters")
    print("pk =>", pk)

    m = "please sign this message now please!"    
    sig = cdh.sign(pk, sk, pk['s'], m)
    print("Signature...")
    print("sig =>", sig)

    assert cdh.verify(pk, m, sig), "invalid signature"
    print("Verification Successful!!")
