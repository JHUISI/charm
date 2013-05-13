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

:Improved by: Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date: 3/2013
:Notes:
1. It works under MNT curve now. However, the size of pk and msk are larger since I need
have some duplicate elements in G2.
2. u,w, and h has two copies now. One in G1, the other one in G2. They all stored as public params
3. pre-calculated g2^-alpha, g2^b and stored in msk. This makes the keygen() faster.
4. The size of public param and msk should be minimal now.
5. The extract() takes one more params now, which is the mpk. We don't want to
increse the size of msk by store redundant elements.
'''
from charm.toolbox.pairinggroup import ZR,G1,G2,pair
from charm.toolbox.IBEnc import *

debug = False
class DSE09_z(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup, GT
    >>> group = PairingGroup('SS512')
    >>> ibe = DSE09_z(group)
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
        g1 = group.random(G1)
        g2 = group.random(G2)
        w_z, u_z, h_z, v_z, v1_z, v2_z = group.random(ZR, 6)
        a1, a2, b, alpha = group.random(ZR, 4)

        v_G1 = g1 ** v_z
        v1_G1 = g1 ** v1_z
        v2_G1 = g1 ** v2_z
        v_G2 = g2 ** v_z
        v1_G2 = g2 ** v1_z
        v2_G2 = g2 ** v2_z
        w_G1 = g1 ** w_z
        w_G2 = g2 ** w_z
        h_G1 = g1 ** h_z
        h_G2 = g2 ** h_z
        u_G1 = g1 ** u_z
        u_G2 = g2 ** u_z
        
        tau1_G1 = v_G1 * (v1_G1 ** a1)
        tau2_G1 = v_G1 * (v2_G1 ** a2)        
        mpk = { 'g1':g1, 'g2':g2, 'g1^b':g1 ** b, 'g1^a1':g1 ** a1, 'g1^a2':g1 ** a2, 
              'g1^ba1':g1 ** (b * a1), 'g1^ba2':g1 ** (b * a2), 'tau1_G1':tau1_G1,
              'tau2_G1':tau2_G1,'tau1_G1^b':tau1_G1 ** b, 'tau2_G1^b':tau2_G1 ** b,
              'w_G1':w_G1, 'w_G2':w_G2, 'u_G1':u_G1, 'u_G2':u_G2,'h_G1':h_G1, 'h_G2':h_G2,
              'egg_alpha': pair(g1, g2) ** (alpha * a1 * b) }
        msk = { 'g2^alph_a1':g2 ** (alpha * a1), 'g2^b':g2 ** b,
              'v_G2':v_G2, 'v1_G2':v1_G2, 'v2_G2':v2_G2, 'g2^-alpha':g2 ** (-alpha) }
        return (mpk, msk)
    
    def keygen(self, mpk, msk, ID):
        r1, r2, z1, z2, tag_k = group.random(ZR, 5)
        r = r1 + r2
        _ID = group.hash(ID)
        D = {}
        D[1] = msk['g2^alph_a1'] * (msk['v_G2'] ** r)
        D[2] = msk['g2^-alpha'] * (msk['v1_G2'] ** r) * (mpk['g2'] ** z1)
        D[3] = msk['g2^b'] ** -z1
        D[4] = (msk['v2_G2'] ** r) * (mpk['g2'] ** z2)
        D[5] = msk['g2^b'] ** -z2
        D[6] = msk['g2^b'] ** r2
        D[7] = mpk['g2'] ** r1
        K = ((mpk['u_G2'] ** _ID) * (mpk['w_G2'] ** tag_k) * mpk['h_G2']) ** r1
        
        sk = { 'ID':_ID, 'D':D, 'K':K, 'tag_k':tag_k }
        return sk

    def encrypt(self, mpk, M, ID):
        s1, s2, t, tag_c = group.random(ZR, 4)
        s = s1 + s2
        _ID = group.hash(ID)
        
        C = {}
        C[0] = M * (mpk['egg_alpha'] ** s2)
        C[1] = mpk['g1^b'] ** s
        C[2] = mpk['g1^ba1'] ** s1
        C[3] = mpk['g1^a1'] ** s1
        C[4] = mpk['g1^ba2'] ** s2
        C[5] = mpk['g1^a2'] ** s2
        C[6] = (mpk['tau1_G1'] ** s1) * (mpk['tau2_G1'] ** s2)
        C[7] = (mpk['tau1_G1^b'] ** s1) * (mpk['tau2_G1^b'] ** s2) * (mpk['w_G1'] ** -t)

        C['E1'] = ((mpk['u_G1'] ** _ID) * (mpk['w_G1'] ** tag_c) * mpk['h_G1']) ** t
        C['E2'] = mpk['g1'] ** t
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

def main():
    group = PairingGroup('MNT224')
    ibe = DSE09_z(group)
    ID = "user2@email.com"
    (master_public_key, master_secret_key) = ibe.setup()
    secret_key = ibe.keygen(master_public_key, master_secret_key, ID)
    msg = group.random(GT)    
    cipher_text = ibe.encrypt(master_public_key, msg, ID)
    decrypted_msg = ibe.decrypt(cipher_text, secret_key)
    print(decrypted_msg == msg)

if __name__ == "__main__":
    debug = True
    main()

