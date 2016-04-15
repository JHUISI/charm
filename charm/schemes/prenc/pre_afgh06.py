'''
AFGH Proxy Re-Encryption
| From: Ateniese, G., Fu, K., Green, M., & Hohenberger, S. (2006). Improved proxy re-encryption schemes with applications to secure distributed storage. 
| Published in: ACM Transactions on Information and System Security (TISSEC), 9(1), 1-30.
| Available from: http://dl.acm.org/citation.cfm?id=1127346
* type:           proxy encryption
* properties:     CPA-secure, unidirectional, single-hop, non-interactive, collusion-resistant
* setting:        Pairing groups (Type 1 "symmetric")
* assumption:     eDBDH (Extended Decisional Bilinear DH)
* to-do:          first-level encryption & second-level decryption
:Authors:    D. Nuñez
:Date:       04/2016
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.PREnc import PREnc

debug = False
class AFGH06(PREnc):
    """
    Testing AFGH06 implementation 

    >>> from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
    >>> groupObj = PairingGroup('SS512')
    >>> pre = AFGH06(groupObj)
    >>> params = pre.setup()
    >>> (pk_a, sk_a) = pre.keygen(params)
    >>> (pk_b, sk_b) = pre.keygen(params)
    >>> msg = groupObj.random(GT)
    >>> c_a = pre.encrypt(params, pk_a, msg)
    >>> rk = pre.rekeygen(params, pk_a, sk_a, pk_b, sk_b)
    >>> c_b = pre.re_encrypt(params, rk, c_a)
    >>> assert msg == pre.decrypt(params, sk_b, c_b), 'Decryption of re-encrypted ciphertext was incorrect'
    """

    def __init__(self, groupObj):
        global group
        group = groupObj
        
    def setup(self):
        g = group.random(G1)
        Z = pair(g,g)

        params = { 'g': g, 'Z' : Z }
        if(debug):
            print("Setup: Public parameters...")
            group.debug(params)
        return params

    def keygen(self, params):
        x1, x2 = group.random(ZR), group.random(ZR)
        Z_x1 = params['Z'] ** x1
        g_x2 = params['g'] ** x2

        sk = { 'sk1' : x1, 'sk2' : x2 }
        pk = { 'pk1' : Z_x1, 'pk2' : g_x2 }
        
        if(debug):
            print('\nKeygen...')
            print("pk => '%s'" % pk)
            print("sk => '%s'" % sk)
        return (pk, sk)

    def rekeygen(self, params, pk_a, sk_a, pk_b, sk_b):
        pk_b2 = pk_b['pk2']
        sk_a1 = sk_a['sk1']
        rk = pk_b2 ** sk_a1
        if(debug):
            print('\nReKeyGen...')
            print("rk => '%s'" % rk)
        return rk

    def encrypt(self, params, pk, m):
        #m = group.encode(M, GT)
        r = group.random(ZR)
        
        Z_a1 = pk['pk1']

        c1 = params['g'] ** r
        c2 = m * (Z_a1 ** r)

        c = { 'c1' : c1, 'c2' : c2 }
               
        if(debug):
            print('\nEncrypt...')
            print('m => %s' % m)
            print('r => %s' % r)
            group.debug(c)
        return c  
        
    def decrypt(self, params, sk, c):
        c1 = c['c1'] 
        c2 = c['c2']
        m = c2 / (c1 ** (~sk['sk2']))
        
        if(debug):
            print('\nDecrypt...')
            print('m => %s' % m)

        #return group.decode(m)
        return m
        
    def re_encrypt(self, params, rk, c_a):
        c1 = c_a['c1'] 
        c2 = c_a['c2']

        c1_prime = pair(c1, rk)

        c_b = { 'c1' : c1_prime, 'c2' : c2 }
        if(debug):
            print('\nRe-encrypt...')
            group.debug(c_b)
        return c_b



    