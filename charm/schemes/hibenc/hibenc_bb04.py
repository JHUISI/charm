'''
Boneh-Boyen Hierarchical Identity Based Encryption
 
| From: "D. Boneh, X. Boyen.  Efficient Selective Identity-Based Encryption Without Random Oracles", Section 4.1.
| Published in: Eurocrypt 2004
| Available from: http://crypto.stanford.edu/~dabo/pubs/papers/bbibe.pdf
| Notes: Core HIBE implementation

* type:            encryption (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J Ayo Akinyele
:Date:       3/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.iterate import dotprod2
from charm.toolbox.hash_module import Waters

debug = False
class HIBE_BB04:
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup, GT
    >>> group = PairingGroup('SS512')
    >>> hibe = HIBE_BB04(group)
    >>> (master_public_key, master_key) = hibe.setup()
    >>> ID = "bob@mail.com"
    >>> (public_key, secret_key) = hibe.extract(3, master_public_key, master_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = hibe.encrypt(master_public_key, public_key, msg)
    >>> decrypted_msg = hibe.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg 
    True

    """
    def __init__(self, groupObj):
        global group, hash_func
        group = groupObj
        hash_func = lambda k,w,x,y,z: ((w ** x[k]) * y[k]) ** z[k]
    
    def setup(self, l=5, z=32):
        """ j represents maximum depth of HIBE system, 
            z represents the bit size of each integer_j of identity.
        """
        assert l > 0, "invalid number of levels (need more than 0)"
        alpha, beta = group.random(ZR, 2)
        g = group.random(G1)
        gb = group.random(G2)
        g1 = g ** alpha
        g1b = gb ** alpha
        delta = [group.random(ZR) for i in range(l)]
        h = [g ** delta[i] for i in range(l)]
        hb = [gb ** delta[i] for i in range(l)]
        g0b = gb ** (alpha * beta)
        v = pair(g, g0b)
    
        mpk = { 'g': g, 'g1':g1, 'h':h, 'gb':gb, 'g1b':g1b, 'hb':hb, 'v':v, 'l':l, 'z':z }
        mk = { 'g0b':g0b }
        return (mpk, mk)
    
    def extract(self, level, mpk, mk, ID):
        j = level
        assert j >= 1 and j <= mpk['l'], "invalid level: 1 - %d" % mpk['l']
        I = Waters(group, j, mpk['z']).hash(ID)
        r = [group.random(ZR) for i in range(j)]
        g_b = [mpk['gb'] ** r[i] for i in range(j)]
        hashID = mk['g0b'] * dotprod2(range(j), hash_func, mpk['g1b'], I, mpk['hb'], r)
        return { 'ID':ID, 'j':j }, { 'd0':hashID, 'dn':g_b }
    
    # TODO: come back to this
    def derive(self, mpk, pk):
        j = pk['j'] # pk[j-1] 
        assert pk['j'] + 1 <= mpk['l'], "invalid level: 1 - %d" % mpk['l']
        I = Waters(group, j, mpk['z']).hash(pk['ID'])

        r = [group.random(ZR) for i in range(j)]
        g_b = [pk['dn'][i] * (mpk['gb'] ** r[i]) for i in range(j)] # j-1
        g_b.append( pk['gb'] ** r[j] ) # represents j
        hashID = dID['d0'] * dotprod2(range(j+1), hash_func, mpk['g1b'], I, mpk['hb'], r)        
        return { 'ID':ID, 'j':j }, { 'd0':hashID, 'dn':g_b}
        
    def encrypt(self, mpk, pk, M):
        I = Waters(group, pk['j'], mpk['z']).hash(pk['ID'])
        s = group.random(ZR)
        A = M * (mpk['v'] ** s)
        B = mpk['g'] ** s
        C = {}
        for i in range(pk['j']):
            C[i] = ((mpk['g1'] ** I[i]) * mpk['h'][i]) ** s
            
        return {'A':A, 'B':B, 'C':C, 'j':pk['j'] }
    
    def decrypt(self, pk, sk, ct):
        prod_result = 1
        for i in range(ct['j']):
            prod_result *= pair(ct['C'][i], sk['dn'][i])
        M = ct['A'] * (prod_result / pair(ct['B'], sk['d0']))
        return M

