from toolbox.pairinggroup import *
from charm.engine.util import *

N = 100
num_signers = 1

debug = False

class IBSig():
    def __init__(self):
        global group
        group = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
  
    def dump(self, obj):
        ser_a = serializeDict(obj, group)
        return str(pickleObject(ser_a))
            
    def keygen(self, secparam=None):
        g = group.random(G2)
        x = group.random()
        g_x = g ** x
        pk = { 'g^x':g_x, 'g':g, 'identity':str(g_x), 'secparam':secparam }
        sk = { 'x':x }
        return (pk, sk)
        
    def sign(self, x, message):
        M = self.dump(message)
        sig = group.hash(M, G1) ** x
        return sig
        
    def verify(self, pk, sig, message):
        M = self.dump(message)
        h = group.hash(M, G1)
        if pair(sig, pk['g']) == pair(h, pk['g^x']):
            return True  
        return False 

def main():    
    m1 = "hello"
    m2 = "bye"
    m3 = "goodbye"

    bls1 = IBSig()
    bls2 = IBSig()
    bls3 = IBSig()
    
    (pk1, sk1) = bls1.keygen(0)
    (pk2, sk2) = bls2.keygen(0)
    (pk3, sk3) = bls3.keygen(0)
    
    sig1 = bls1.sign(sk1['x'], m1)

    print(sig1)

    sig2 = bls2.sign(sk2['x'], m2)
    sig3 = bls3.sign(sk3['x'], m3)

    f_pk1 = open('pk1.pickle', 'wb')
    f_pk2 = open('pk2.pickle', 'wb')
    f_pk3 = open('pk3.pickle', 'wb')

    f_m1 = open('m1.pickle', 'wb')
    f_m2 = open('m2.pickle', 'wb')
    f_m3 = open('m3.pickle', 'wb')

    f_sig1 = open('sig1.pickle', 'wb')
    f_sig2 = open('sig2.pickle', 'wb')
    f_sig3 = open('sig3.pickle', 'wb')

    pick_pk1 = pickleObject( serializeDict( pk1, group ) )
    pick_pk2 = pickleObject( serializeDict( pk2, group ) )
    pick_pk3 = pickleObject( serializeDict( pk3, group ) )

    pick_m1 = pickleObject( serializeDict( m1, group ) )
    pick_m2 = pickleObject( serializeDict( m2, group ) )
    pick_m3 = pickleObject( serializeDict( m3, group ) )

    pick_sig1 = pickleObject( serializeDict( sig1, group ) )

    print(pick_sig1)

    pick_sig2 = pickleObject( serializeDict( sig2, group ) )
    pick_sig3 = pickleObject( serializeDict( sig3, group ) )

    f_pk1.write(pick_pk1)
    f_pk2.write(pick_pk2)
    f_pk3.write(pick_pk3)

    f_m1.write(pick_m1)
    f_m2.write(pick_m2)
    f_m3.write(pick_m3)

    f_sig1.write(pick_sig1)
    f_sig2.write(pick_sig2)
    f_sig3.write(pick_sig3)

    f_pk1.close()
    f_pk2.close()
    f_pk3.close()

    f_m1.close()
    f_m2.close()
    f_m3.close()

    f_sig1.close()
    f_sig2.close()
    f_sig3.close()

if __name__ == "__main__":
    debug = True
    main()
    
