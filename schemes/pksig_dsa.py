from toolbox.integergroup import *
from toolbox.PKSig import *

debug = False
class DSA():
    def __init__(self):
        global group
        group = IntegerGroupQ()
        
    def keygen(self, bits):
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
        
def main():
    dsa = DSA()

    (pk, sk) = dsa.keygen(1024)
    m = "hello world test message!!!"
    sig = dsa.sign(pk, sk, m)

    assert dsa.verify(pk, sig, m)
    if debug: print("Signature Verified!!!")

if __name__ == "__main__":
    debug = True
    main()
    
