''' Ateneise-Medeiros (Schnorr group-based)
 
 | From: "Ateneise-Breno de Medeiros On the Key Exposure Problem in Chameleon Hashes", Section 4.
 | Published in: SCN 2004
 | Available from:
 | Notes: 

 * type:         hash function (chameleon)
 * setting:      Schnorr groups
 * assumption:   DL-Hard

:Authors: J Ayo Akinyele
:Date:    4/2011
'''
from charm.toolbox.Hash import ChamHash
from charm.toolbox.integergroup import IntegerGroupQ
from charm.core.math.integer import integer


debug = False
class ChamHash_Adm05(ChamHash):
    """
    >>> from charm.core.math.integer import integer
    >>> p = integer(141660875619984104245410764464185421040193281776686085728248762539241852738181649330509191671665849071206347515263344232662465937366909502530516774705282764748558934610432918614104329009095808618770549804432868118610669336907161081169097403439689930233383598055540343198389409225338204714777812724565461351567)
    >>> q = integer(70830437809992052122705382232092710520096640888343042864124381269620926369090824665254595835832924535603173757631672116331232968683454751265258387352641382374279467305216459307052164504547904309385274902216434059305334668453580540584548701719844965116691799027770171599194704612669102357388906362282730675783)
    >>> chamHash = ChamHash_Adm05(p, q)
    >>> (public_key, secret_key) = chamHash.paramgen()
    >>> msg = "hello world this is the message"
    >>> c = chamHash.hash(public_key, msg)
    >>> c == chamHash.hash(public_key, msg, c[1], c[2])
    True
    """

    def __init__(self, p=0, q=0):
        ChamHash.__init__(self)
        global group
        group = IntegerGroupQ(0)
        # if p and q parameters have already been selected
        group.p, group.q, group.r = p, q, 2
        self.group = group        
    
    def paramgen(self, secparam=1024):
        if group.p == 0 or group.q == 0:
            group.paramgen(secparam)
        g, x = group.randomGen(), group.random()    # g, [1,q-1]
        y = g ** x
        
        if debug:
            print("Public params")
            print("g =>", g); print("y =>", y)
        
        pk = {'g': g, 'y': y}
        sk = {'x': x}
        return pk, sk
    
    def hash(self, pk, m, r=0, s=0):
        p, q = group.p, group.q
        if r == 0:
            r = group.random()
        if s == 0:
            s = group.random()
        e = group.hash(m, r)
        
        C = r - (((pk['y'] ** e) * (pk['g'] ** s)) % p) % q
        return C, r, s

    @staticmethod
    def find_collision(pk, sk, C, new_message):
        p, q = group.p, group.q
        k_prime = group.random()
        r_prime = C + ((pk['g'] ** k_prime) % p) % q
        e_prime = group.hash(new_message, r_prime)
        s_prime = (k_prime - (e_prime * sk['x'])) % q
        C_prime = r_prime - (((pk['y'] ** e_prime) * (pk['g'] ** s_prime)) % p) % q
        return C_prime, r_prime, s_prime


def main():
    p = integer(141660875619984104245410764464185421040193281776686085728248762539241852738181649330509191671665849071206347515263344232662465937366909502530516774705282764748558934610432918614104329009095808618770549804432868118610669336907161081169097403439689930233383598055540343198389409225338204714777812724565461351567)
    q = integer(70830437809992052122705382232092710520096640888343042864124381269620926369090824665254595835832924535603173757631672116331232968683454751265258387352641382374279467305216459307052164504547904309385274902216434059305334668453580540584548701719844965116691799027770171599194704612669102357388906362282730675783)
    cham_hash = ChamHash_Adm05(p, q)
    pk, sk = cham_hash.paramgen()
    if debug:
        print("Paramgen...")
        print("pk :=", pk)
        print("sk :=", sk)

    msg = 'Some message to hash'
    c, r, s = cham_hash.hash(pk, msg)
    if debug:
        print('Hashing: ', msg)
        print('Hash is: ', c)

    other_msg = 'Some other message to hash, different from previous message'
    assert msg != other_msg
    new_c, new_r, new_s = cham_hash.find_collision(pk, sk, c, other_msg)
    if debug:
        print('Hashing: ', other_msg)
        print('Hash is: ', new_c)

    assert new_c == c, 'Could not generate collision'
    if debug:
        print('Generated hash collision')


if __name__ == "__main__":
    debug = True
    main()


