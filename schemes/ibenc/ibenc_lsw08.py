'''
Allison Lewko, Amit Sahai and Brent Waters (Pairing-based)
 
| From: "Revocation Systems with Very Small Private Keys"
| Published in: IEEE S&P 2010
| Available from: http://eprint.iacr.org/2008/309.pdf
| Notes: fully secure IBE Construction with revocable keys.

* type:           identity-based encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       1/2012
'''
from charm.toolbox.pairinggroup import ZR,G1,pair
from charm.toolbox.IBEnc import *

debug = False
class IBE_Revoke(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup, GT, G2
    >>> group = PairingGroup('SS512')
    >>> num_users = 5 # total # of users
    >>> ibe = IBE_Revoke(group)
    >>> ID = "user2@email.com"
    >>> S = ["user1@email.com", "user3@email.com", "user4@email.com"]
    >>> (master_public_key, master_secret_key) = ibe.setup(num_users)
    >>> secret_key = ibe.keygen(master_public_key, master_secret_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, msg, S)
    >>> decrypted_msg = ibe.decrypt(S, cipher_text, secret_key)
    >>> decrypted_msg == msg
    True
    """

    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group, util
        group = groupObj

    def setup(self, n):
        g, w, h, v, v1, v2 = group.random(G1, 6)
        a1, a2, b, alpha = group.random(ZR, 4)
        
        tau1 = v * (v1 ** a1)
        tau2 = v * (v2 ** a2)        
        pk = {'n':n, 'g':g, 'g^b':g ** b, 'g^a1':g ** a1, 'g^a2':g ** a2, 
              'g^ba1':g ** (b * a1), 'g^ba2':g ** (b * a2), 'tau1':tau1, 'tau2':tau2, 
              'tau1^b':tau1 ** b, 'tau2^b':tau2 ** b, 'w':w, 'h':h,
              'egg_alpha': pair(g, g) ** (alpha * a1 * b)}
        sk = {'g^alph':g ** alpha, 'g^alph_a1':g ** (alpha * a1),
              'g^b':g ** b,'v':v, 'v1':v1, 'v2':v2, 'alpha':alpha }
        return (pk, sk)
    
    def keygen(self, mpk, msk, ID):
        d1, d2, z1, z2 = group.random(ZR, 4)
        d = d1 + d2
        _ID = group.hash(ID.upper())
        D = {}
        D[1] = msk['g^alph_a1'] * (msk['v'] ** d)
        D[2] = (mpk['g'] ** -msk['alpha']) * (msk['v1'] ** d) * (mpk['g'] ** z1)
        D[3] = mpk['g^b'] ** -z1
        D[4] = (msk['v2'] ** d) * (mpk['g'] ** z2)
        D[5] = mpk['g^b'] ** -z2
        D[6] = mpk['g^b'] ** d2
        D[7] = mpk['g'] ** d1
        K = ((mpk['w'] ** _ID) * mpk['h']) ** d1
        
        sk = { 'ID':_ID, 'D':D, 'K':K }
        return sk

    def encrypt(self, mpk, M, S):
        s1, s2 = group.random(ZR, 2)
        s = s1 + s2
        # number of revoked users
        r = len(S); t_r = group.random(ZR, r)
        t = 0
        for i in t_r: t += i 
        
        C = {}
        C[0] = M * (mpk['egg_alpha'] ** s2)
        C[1] = mpk['g^b'] ** s
        C[2] = mpk['g^ba1'] ** s1
        C[3] = mpk['g^a1'] ** s1
        C[4] = mpk['g^ba2'] ** s2
        C[5] = mpk['g^a2'] ** s2
        C[6] = (mpk['tau1'] ** s1) * (mpk['tau2'] ** s2)
        C[7] = (mpk['tau1^b'] ** s1) * (mpk['tau2^b'] ** s2) * (mpk['w'] ** -t)
        
        c1 = [i for i in range(r)]; c2 = [i for i in range(r)]
        for i in range(len(t_r)):
            c1[i] = mpk['g'] ** t_r[i]
            S_hash = group.hash(S[i].upper())
            c2[i] = ((mpk['w'] ** S_hash) * mpk['h']) ** t_r[i]
        C['i1'] = c1
        C['i2'] = c2
        return C

    def decrypt(self, S, ct, sk):
        C, D, K = ct, sk['D'], sk['K']
        _ID = sk['ID']
        # hash IDs
        S_id = [group.hash(i.upper()) for i in S]
        if debug: print("hashed IDs: ", S_id)
        if _ID in S_id: print("Your ID:", _ID, "is in revoked list!"); return
        A1 = pair(C[1], D[1]) * pair(C[2], D[2]) * pair(C[3], D[3]) * pair(C[4], D[4]) * pair(C[5], D[5])
        A2 = pair(C[6], D[6]) * pair(C[7], D[7])
        A3 = A1 / A2
        A4 = 1
        for i in range(len(S_id)):
            A4 *= (pair(C['i1'][i], K) / pair(C['i2'][i], D[7])) ** (1 / (_ID - S_id[i]))
        return C[0] / (A3 / A4) 

