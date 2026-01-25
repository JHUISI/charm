r'''
**Chen-Lim-Ling-Wang-Wee Shorter IBE (CLLWW12)**

*Authors:* Jie Chen, Hoon Wei Lim, San Ling, Huaxiong Wang, Hoeteck Wee

| **Title:** "Shorter IBE and Signatures via Asymmetric Pairings"
| **Published in:** Pairing 2012
| **Available from:** http://eprint.iacr.org/2012/224
| **Notes:** Section 4 - Shorter IBE construction based on SXDH assumption

.. rubric:: Scheme Properties

* **Type:** encryption (identity-based)
* **Setting:** bilinear groups (asymmetric)
* **Assumption:** SXDH (Symmetric External Diffie-Hellman)

.. rubric:: Implementation

:Authors: Fan Zhang (zfwise@gwu.edu), supported by GWU computer science department
:Date: 3/2013
:Notes: Optimized implementation stores msk = {alpha, d_1*, d_2*} instead of
    pre-computed group elements. Computes (alpha + r*ID)*d_1* - r*d_2* before
    exponentiation, reducing G2 exponentials from 8 to 4.
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.matrixops import *
from charm.core.crypto.cryptobase import *
from charm.toolbox.IBEnc import IBEnc

debug = False
class IBE_Chen12_z(IBEnc):
    """
    >>> group = PairingGroup('MNT224', secparam=1024)    
    >>> ibe = IBE_Chen12_z(group)
    >>> (master_public_key, master_secret_key) = ibe.setup()
    >>> ID = 'user@email.com'
    >>> private_key = ibe.extract(master_secret_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, ID, msg)
    >>> decryptedMSG = ibe.decrypt(master_public_key, private_key, cipher_text)
    >>> print (decryptedMSG==msg)
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group
        group = groupObj
        
    def setup(self):
        g1 = group.random(G1)
        g2 = group.random(G2)
        alpha = group.random(ZR)
        #generate the 4*4 dual pairing vector spaces.
        d11, d12, d13, d14, d21, d22, d23, d24 = group.random(ZR, 8)
        d31, d32, d33, d34, d41, d42, d43, d44 = group.random(ZR, 8)
        D11, D12, D13, D14 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D21, D22, D23, D24 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D31, D32, D33, D34 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D41, D42, D43, D44 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)

        one = group.random(ZR)
        
        [D11, D12, D13, D14] = GaussEliminationinGroups([[d11, d12, d13, d14, one],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D21, D22, D23, D24] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, one],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D31, D32, D33, D34] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, one],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D41, D42, D43, D44] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, one]])        
        

        #generate public parameters.
        PP2 = (pair(g1, g2))**(alpha*one)
        gd11 = g1**d11
        gd12 = g1**d12
        gd13 = g1**d13
        gd14 = g1**d14
        gd21 = g1**d21
        gd22 = g1**d22
        gd23 = g1**d23
        gd24 = g1**d24
        pk = { 'PP2':PP2,
               'gd11':gd11, 'gd12':gd12,'gd13':gd13, 'gd14':gd14,
               'gd21':gd21, 'gd22':gd22, 'gd23':gd23, 'gd24':gd24 }
        #generate private parameters
##        gD11 = g2**D11
##        gD12 = g2**D12
##        gD13 = g2**D13
##        gD14 = g2**D14
##        gD21 = g2**D21
##        gD22 = g2**D22
##        gD23 = g2**D23
##        gD24 = g2**D24
##        msk = { 'alpha':alpha, 'gD11':gD11, 'gD12':gD12, 'gD13':gD13, 'gD14':gD14,
##               'gD21':gD21, 'gD22':gD22, 'gD23':gD23, 'gD24':gD24 }
        msk = {'alpha': alpha, 'g2':g2,
               'D11':D11, 'D12':D12, 'D13':D13, 'D14':D14,
               'D21':D21, 'D22':D22, 'D23':D23, 'D24':D24}
        if(debug):
            print("Public parameters...")
            group.debug(pk)
            print("Secret parameters...")
            group.debug(msk)
        return (pk, msk)
    
    def extract(self, msk, ID):
        _ID = group.hash(ID)
        r = group.random(ZR)
        sk_id1 = msk['g2']**((msk['alpha']+ r * _ID) * msk['D11'] - r * msk['D21'])
        sk_id2 = msk['g2']**((msk['alpha']+ r * _ID) * msk['D12'] - r * msk['D22'])
        sk_id3 = msk['g2']**((msk['alpha']+ r * _ID) * msk['D13'] - r * msk['D23'])
        sk_id4 = msk['g2']**((msk['alpha']+ r * _ID) * msk['D14'] - r * msk['D24'])
        
        k = { 'sk_id1':sk_id1, 'sk_id2':sk_id2, 'sk_id3':sk_id3,
              'sk_id4':sk_id4 }
        
        if(debug):
            print("Generate User SK...")
            group.debug(k)
        return k
        
    
    def encrypt(self, pk, ID, M):
        s = group.random(ZR)
        _ID = group.hash(ID)
        #M is an element in GT
        C0 = (pk['PP2']**s)*M
        C11 = (pk['gd11']**s)*(pk['gd21']**(s*_ID))
        C12 = (pk['gd12']**s)*(pk['gd22']**(s*_ID))
        C13 = (pk['gd13']**s)*(pk['gd23']**(s*_ID))
        C14 = (pk['gd14']**s)*(pk['gd24']**(s*_ID))

        CT = { 'C0':C0, 'C11':C11, 'C12':C12, 'C13':C13, 'C14':C14 }
        
        if(debug):
            print('\nEncrypt...')
            group.debug(CT)
        return CT
    
    def decrypt(self, pk, sk, ct):
        Mprime = ct['C0']/(pair(ct['C11'],sk['sk_id1'])*pair(ct['C12'],sk['sk_id2'])*
                           pair(ct['C13'],sk['sk_id3'])*pair(ct['C14'],sk['sk_id4']))

        if(debug):
            print('\nDecrypt....')
        return Mprime

def main():

    group = PairingGroup('MNT224', secparam=1024)    
    ibe = IBE_Chen12_z(group)
    (master_public_key, master_secret_key) = ibe.setup()
    ID = 'user@email.com'
    private_key = ibe.extract(master_secret_key, ID)
    msg = group.random(GT)
    cipher_text = ibe.encrypt(master_public_key, ID, msg)
    decryptedMSG = ibe.decrypt(master_public_key, private_key, cipher_text)
    print (decryptedMSG==msg)
    
if __name__ == '__main__':
    debug = True
    main()   

