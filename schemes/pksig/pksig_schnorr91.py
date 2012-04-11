from toolbox.integergroup import *
from toolbox.PKSig import *

debug = False
class SchnorrSig(PKSig):
    def __init__(self):
        PKSig.__init__(self)
        
    def params(self, p=0, q=0, bits=1024):
        global group
        group = IntegerGroupQ(0)
        if p == 0 or q == 0:
            group.paramgen(bits)
        else:
            group.p, group.q, group.r = p, q, 2
    
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
        if debug: print("Verifying...")
        e = group.hash(M, r)
        if debug: print("e => %s" % e)
        if debug: print("r => %s" % r)
        if e == sig['e']:
            return True
        else:
            return False
        return None
    
def main():
    # test only parameters for p,q
    p = integer(156816585111264668689583680968857341596876961491501655859473581156994765485015490912709775771877391134974110808285244016265856659644360836326566918061490651852930016078015163968109160397122004869749553669499102243382571334855815358562585736488447912605222780091120196023676916968821094827532746274593222577067)
    q = integer(78408292555632334344791840484428670798438480745750827929736790578497382742507745456354887885938695567487055404142622008132928329822180418163283459030745325926465008039007581984054580198561002434874776834749551121691285667427907679281292868244223956302611390045560098011838458484410547413766373137296611288533)    
    pksig = SchnorrSig()
    
    pksig.params(p, q)
    
    (pk, sk) = pksig.keygen()
    
    M = "hello world."
    sig = pksig.sign(pk, sk, M)
    
    assert pksig.verify(pk, sig, M), "Failed verification!"
    if debug: print("Signature verified!!!!")
    
if __name__ == "__main__":
    debug = True
    main()
    
