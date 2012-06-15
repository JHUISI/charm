'''
Brent Waters (Pairing-based)
 
| From: "Dual System Encryption: Realizing Fully Secure IBE and HIBE under Simple Assumptions"
| Published in: CRYPTO 2009
| Available from: http://eprint.iacr.org/2009/385.pdf
| Notes: fully secure IBE Construction 

* type:           identity-based encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       03/2012
'''
from charm.toolbox.pairinggroup import ZR,G1,pair
from charm.toolbox.IBEnc import *

debug = False
class DSE09(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup, GT
    >>> group = PairingGroup('SS512')
    >>> ibe = DSE09(group)
    >>> ID = "user2@email.com"
    >>> (master_public_key, master_secret_key) = ibe.setup()
    >>> secret_key = ibe.keygen(master_public_key, master_secret_key, ID)
    >>> msg = group.random(GT)    
    >>> cipher_text = ibe.encrypt(master_public_key, msg, ID)
    >>> decrypted_msg = ibe.decrypt(cipher_text, secret_key)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group, util
        group = groupObj

    def setup(self):
        g, w, u, h, v, v1, v2 = group.random(G1, 7)
        a1, a2, b, alpha = group.random(ZR, 4)
        
        tau1 = v * (v1 ** a1)
        tau2 = v * (v2 ** a2)        
        mpk = { 'g':g, 'g^b':g ** b, 'g^a1':g ** a1, 'g^a2':g ** a2, 
              'g^ba1':g ** (b * a1), 'g^ba2':g ** (b * a2), 'tau1':tau1, 'tau2':tau2, 
              'tau1^b':tau1 ** b, 'tau2^b':tau2 ** b, 'w':w, 'u':u,'h':h,
              'egg_alpha': pair(g, g) ** (alpha * a1 * b) }
        msk = { 'g^alph':g ** alpha, 'g^alph_a1':g ** (alpha * a1),
              'v':v, 'v1':v1, 'v2':v2, 'alpha':alpha }
        return (mpk, msk)
    
    def keygen(self, mpk, msk, ID):
        r1, r2, z1, z2, tag_k = group.random(ZR, 5)
        r = r1 + r2
        _ID = group.hash(ID)
        D = {}
        D[1] = msk['g^alph_a1'] * (msk['v'] ** r)
        D[2] = (mpk['g'] ** -msk['alpha']) * (msk['v1'] ** r) * (mpk['g'] ** z1)
        D[3] = mpk['g^b'] ** -z1
        D[4] = (msk['v2'] ** r) * (mpk['g'] ** z2)
        D[5] = mpk['g^b'] ** -z2
        D[6] = mpk['g^b'] ** r2
        D[7] = mpk['g'] ** r1
        K = ((mpk['u'] ** _ID) * (mpk['w'] ** tag_k) * mpk['h']) ** r1
        
        sk = { 'ID':_ID, 'D':D, 'K':K, 'tag_k':tag_k }
        return sk

    def encrypt(self, mpk, M, ID):
        s1, s2, t, tag_c = group.random(ZR, 4)
        s = s1 + s2
        _ID = group.hash(ID)
        
        C = {}
        C[0] = M * (mpk['egg_alpha'] ** s2)
        C[1] = mpk['g^b'] ** s
        C[2] = mpk['g^ba1'] ** s1
        C[3] = mpk['g^a1'] ** s1
        C[4] = mpk['g^ba2'] ** s2
        C[5] = mpk['g^a2'] ** s2
        C[6] = (mpk['tau1'] ** s1) * (mpk['tau2'] ** s2)
        C[7] = (mpk['tau1^b'] ** s1) * (mpk['tau2^b'] ** s2) * (mpk['w'] ** -t)

        C['E1'] = ((mpk['u'] ** _ID) * (mpk['w'] ** tag_c) * mpk['h']) ** t
        C['E2'] = mpk['g'] ** t
        C['tag_c'] = tag_c
        return C

    def decrypt(self, ct, sk):
        tag = (1 / (ct['tag_c'] - sk['tag_k']))
        E1, E2 = ct['E1'], ct['E2']
        C, D, K = ct, sk['D'], sk['K']
        _ID = sk['ID']
        # hash IDs
        A1 = pair(C[1], D[1]) * pair(C[2], D[2]) * pair(C[3], D[3]) * pair(C[4], D[4]) * pair(C[5], D[5])
        A2 = pair(C[6], D[6]) * pair(C[7], D[7])
        A3 = A1 / A2
        A4 = (pair(E1, D[7]) / pair(E2, K)) ** tag
        return C[0] / (A3 / A4) 

