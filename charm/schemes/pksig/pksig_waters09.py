'''
Brent Waters (Pairing-based)
 
| From: "Dual System ENcryption: Realizing Fully Secure IBE and HIBE under Simple Assumptions"
| Published in: CRYPTO 2009
| Available from: http://eprint.iacr.org/2009/385.pdf
| Notes: 

* type:           identity-based encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       2/2012

:Improved by: Fan Zhang, 3/2013
:Notes: Only minor changes has been made. Deleted the alpha from msk and added g2^-alpha into it.
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import IBEnc

debug = False
class IBEWaters09(IBEnc):
    """
    >>> group = PairingGroup('MNT224')
    >>> ibe = IBEWaters09(group)
    >>> (master_public_key, master_secret_key) = ibe.keygen()
    >>> msg = "plese sign this message!!!!"
    >>> signature = ibe.sign(master_public_key, master_secret_key, msg)
    >>> ibe.verify(master_public_key, signature, msg)
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group, util
        group = groupObj

    def keygen(self):
        g1 = group.random(G1)
        g2 = group.random(G2)
        a1, a2, b, alpha = group.random(ZR, 4)
        _w, _h, _v, _v1, _v2, _u = group.random(ZR, 6)
        
        v = g1 ** _v 
        v1 = g1 ** _v1 
        v2 = g1 ** _v2
        
        v_2 = g2 ** _v
        v1_2 = g2 ** _v1
        v2_2 = g2 ** _v2
        w1, h1 = g1 ** _w, g1 ** _h
        w2, h2 = g2 ** _w, g2 ** _h
        u2 = g2 ** _u
        u1 = g1 ** _u
        
        tau1 = v * (v1 ** a1)
        tau2 = v * (v2 ** a2)
        pk = { 'g1':g1, 'g2':g2, 'g1^b':g1 ** b, 'g^a1':g1 ** a1, 'g^a2':g1 ** a2, 
              'g^ba1':g1 ** (b * a1), 'g^ba2':g1 ** (b * a2), 'tau1':tau1, 'tau2':tau2, 
              'tau1^b':tau1 ** b, 'tau2^b':tau2 ** b, 'u':u1, 'u2':u2,'w1':w1, 'h1':h1, 'w2':w2, 'h2':h2,
              'egg_alpha': pair(g1, g2) ** (alpha * a1 * b) }
        sk = {'g^alph_a1':g2 ** (alpha * a1),
              'g2^b':g2 ** b,'v':v_2, 'v1':v1_2, 'v2':v2_2, 'g2^-alpha':g2 ** -alpha }
        return (pk, sk)
    
    def sign(self, mpk, msk, m):
        r1, r2, z1, z2, tagk = group.random(ZR, 5)
        r = r1 + r2
        M = group.hash(m)

        S = {}
        S[1] = msk['g^alph_a1'] * (msk['v'] ** r)
        S[2] = msk['g2^-alpha'] * (msk['v1'] ** r) * (mpk['g2'] ** z1)
        S[3] = msk['g2^b'] ** -z1
        S[4] = (msk['v2'] ** r) * (mpk['g2'] ** z2)
        S[5] = msk['g2^b'] ** -z2
        S[6] = msk['g2^b'] ** r2
        S[7] = mpk['g2'] ** r1
        SK = ((mpk['u2'] ** M) * (mpk['w2'] ** tagk) * mpk['h2']) ** r1
        
        sigma = { 'sig':S, 'K':SK, 'tagk':tagk }
        return sigma

    def verify(self, mpk, sigma, m):
        s1, s2, t, tagc = group.random(ZR, 4)
        s = s1 + s2
        M = group.hash(m)
        
        sig1, sig2, sig3, sig4, sig5, sig6, sig7, sigK, tagk = sigma['sig'][1],sigma['sig'][2],sigma['sig'][3],sigma['sig'][4],sigma['sig'][5],sigma['sig'][6],sigma['sig'][7],sigma['K'],sigma['tagk']
        E1 = ((mpk['u'] ** M) * (mpk['w1'] ** tagc) * mpk['h1']) ** t
        E2 = mpk['g1'] ** t
        A = (mpk['egg_alpha'] ** s2)
        theta =  ~(tagc - tagk)
        
        lhs_pair = pair(mpk['g1^b'] ** s, sig1) * pair(mpk['g^ba1'] ** s1, sig2) * pair(mpk['g^a1'] ** s1, sig3) * pair(mpk['g^ba2'] ** s2, sig4) * pair(mpk['g^a2'] ** s2, sig5)        
        rhs_pair = pair((mpk['tau1'] ** s1) * (mpk['tau2'] ** s2), sig6) * pair((mpk['tau1^b'] ** s1) * (mpk['tau2^b'] ** s2) * (mpk['w1'] ** -t), sig7) * (( pair(E1, sig7) / pair(E2, sigK) ) ** theta) * A
        if lhs_pair == rhs_pair:
            return True
        return False

def main():
    # scheme designed for symmetric billinear groups
    grp = PairingGroup('MNT224')

    ibe = IBEWaters09(grp)

    (mpk, msk) = ibe.keygen()

    m = "plese sign this message!!!!"
    sigma = ibe.sign(mpk, msk, m)
    if debug: print("Signature :=", sigma)

    assert ibe.verify(mpk, sigma, m), "Invalid Verification!!!!"
    if debug: print("Successful Individual Verification!")

if __name__ == "__main__":
    debug = True
    main()
