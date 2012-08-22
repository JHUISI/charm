''' 
Hohenberger-Waters Chameleon Hash (RSA-based)
based on the scheme of Ateneise and de Medeiros
 
 | From: "S. Hohenberger, B. Waters. Realizing Hash-and-Sign Signatures under Standard Assumptions", Appendix A.
 | Published in: Eurocrypt 2009
 | Available from: http://eprint.iacr.org/2009/028.pdf
 | Notes: 

 * type:       hash function (chameleon)
 * setting:      RSA
 * assumption:   RSA

:Author:    J. Ayo Akinyele
:Date:      1/2011
'''

from charm.toolbox.Hash import ChamHash,Hash
from charm.toolbox.integergroup import IntegerGroupQ,gcd
from charm.toolbox.conversion import Conversion

debug=False
class ChamHash_HW09(ChamHash):
    """
    >>> from charm.core.math.integer import integer
    >>> p = integer(164960892556379843852747960442703555069442262500242170785496141408191025653791149960117681934982863436763270287998062485836533436731979391762052869620652382502450810563192532079839617163226459506619269739544815249458016088505187490329968102214003929285843634017082702266003694786919671197914296386150563930299)
    >>> q = integer(82480446278189921926373980221351777534721131250121085392748070704095512826895574980058840967491431718381635143999031242918266718365989695881026434810326191251225405281596266039919808581613229753309634869772407624729008044252593745164984051107001964642921817008541351133001847393459835598957148193075281965149) 
    >>> chamHash = ChamHash_HW09()
    >>> (public_key, secret_key) = chamHash.paramgen(1024, p, q)
    >>> msg = "Hello world this is the message!"
    >>> (hash1, r) = chamHash.hash(public_key, msg)
    >>> (hash2, r) = chamHash.hash(public_key, msg, r)
    >>> hash1 == hash2
    True
    """
    def __init__(self):
        global group
        group = IntegerGroupQ(0)
    
    def paramgen(self, secparam, p = 0, q = 0):
        # If we're given p, q, compute N = p*q.  Otherwise select random p, q
        if not (p == 0 or q == 0):
            N = p * q
            if debug: print("p :=", p)
            if debug: print("q :=", q)
        else:
            group.paramgen(secparam)
            p, q = group.p, group.q
            N = p * q
        
        phi_N = (p-1)*(q-1)
        J = group.random(N)
        e = group.random(phi_N)
        while (not gcd(e, phi_N) == 1):
            e = group.random(phi_N)
        pk = { 'secparam': secparam, 'N': N, 'J': J, 'e': e }
        sk = { 'p': p, 'q': q }
        return (pk, sk)
          
    def hash(self, pk, message, r = 0):
        N, J, e = pk['N'], pk['J'], pk['e']
        if r == 0:
           r = group.random(N)
        M = Conversion.bytes2integer(message)
        h = ((J ** M) * (r ** e)) % N
        return (h, r)

