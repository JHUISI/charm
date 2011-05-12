from toolbox.integergroup import *
from toolbox.PKSig import *

class SchnorrSig(PKSig):
    def __init__(self):
        PKSig.__init__(self)
        
    def params(self, bits=160):
        global group
        group = IntegerGroupQ(0)
        group.paramgen(bits)
    
    def keygen(self):
        p = group.p
        x, g = group.random(), group.randomGen()
        y = (g ** x)
        return ({'y':y, 'g':g}, x)
    
    def sign(self, pk, x, M):
        p,q = group.p, group.q
        k = group.random()
        r = (pk['g'] ** k) % p
        e = group.hash(M, r)
        s = (k - x*e) % q

        return {'e':e, 's':s }
    
    def verify(self, pk, sig, M):
        p = group.p
        r = ((pk['g'] ** sig['s']) * (pk['y'] ** sig['e'])) % p
        print("Verifying...")
        e = group.hash(M, r)
        print("e => %s" % e)
        print("r => %s" % r)
        if e == sig['e']:
            return True
        else:
            return False
        return None
    
if __name__ == "__main__":
    pksig = SchnorrSig()
    
    pksig.params()
    
    (pk, sk) = pksig.keygen()
    
    M = "hello world."
    sig = pksig.sign(pk, sk, M)
    
    if pksig.verify(pk, sig, M):
        print("Signature verified!!!!")
    else:
        print("Signature FAILED!!!")
    
