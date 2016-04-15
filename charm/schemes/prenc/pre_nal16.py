'''
NAL16 Proxy Re-Encryption
| From: Nunez, D., Agudo, I., & Lopez, J. (2016). On the application of generic CCA-secure transformations to proxy re-encryption
| Published in: Security and Communication Networks
| Available from: http://onlinelibrary.wiley.com/doi/10.1002/sec.1434/full
* type:           proxy encryption
* properties:     CCA_21-secure, unidirectional, single-hop, non-interactive, collusion-resistant
* setting:        Pairing groups (Type 1 "symmetric")
* assumption:     3-wDBDHI (3-weak Decisional Bilinear DH Inversion)
* to-do:          first-level encryption, type annotations
:Authors:    D. Nuñez
:Date:       04/2016
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.PREnc import PREnc

debug = False
class NAL16(PREnc):
    """
    Testing NAL16 implementation 

    >>> from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
    >>> groupObj = PairingGroup('SS512')
    >>> pre = NAL16(groupObj)
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
        
    def F(self, params, t):
        return (params['u'] ** t) * params['v']

    def H(self, params, x, s):
        h1 = group.hash(x, s, 1, ZR)
        h2 = group.hash(x, s, 2, ZR)
        if(debug):
            print('\nKeygen...')
            print("x => '%s'" % x)
            print("s => '%s'" % s)
            print("h1 => '%s'" % h1)
            print("h2 => '%s'" % h2)
        return (h1, h2)

    def setup(self):
        g, u, v = group.random(G1), group.random(G1), group.random(G1)
        Z = pair(g,g)

        params = {'g': g, 'u': u, 'v': v, 'Z': Z} 
        if(debug):
            print("Setup: Public parameters...")
            group.debug(params)
        return params

    def keygen(self, params):
        x = group.random(ZR)
        g_x = params['g'] ** x

        sk = x      # { 'sk' : x }
        pk = g_x    # { 'pk' : g_x }

        if(debug):
            print('\nKeygen...')
            print("pk => '%s'" % pk)
            print("sk => '%s'" % sk)
        return (pk, sk)

    def rekeygen(self, params, pk_a, sk_a, pk_b, sk_b):
        rk = pk_b ** (~sk_a)
        if(debug):
            print('\nReKeyGen...')
            print("rk => '%s'" % rk)
        return rk

    def encrypt(self, params, pk, m):
        #m = group.encode(M, GT)
        r1, r2 = group.random(ZR), group.random(ZR)
        
        c0 = self.F(params, r1) ** r2
        c1 = m * (params['Z'] ** r2)
        c2 = pk ** r2

        c = {'c0': c0, 'c1': c1, 'c2': c2}
               
        if(debug):
            print('\nEncrypt...')
            print('m => %s' % m)
            print('r1 => %s' % r1)
            print('r2 => %s' % r2)
            print('c => %s' % c)
            group.debug(c)
        return c  
        
    def decrypt(self, params, sk, c):
    
        c1 = c['c1'] 
        c2 = c['c2']

        m = c1 / (c2 ** (~sk))
        
        if(debug):
            print('\nDecrypt...')
            print('m => %s' % m)

        #return group.decode(m)
        return m
        
    def re_encrypt(self, params, rk, c_a):

        c2 = c_a['c2']

        c_b = c_a
        c_b['c2'] = pair(c2, rk)
        
        if(debug):
            print('\nRe-encrypt...')
            group.debug(c_b)
        return c_b


# groupObj = PairingGroup('SS512')
# pre = NAL16(groupObj)
# params = pre.setup()

# (pk_a, sk_a) = pre.keygen(params)
# (pk_b, sk_b) = pre.keygen(params)
# msg = groupObj.random(GT)
# c_a = pre.encrypt(params, pk_a, msg)
# rk = pre.rekeygen(params, pk_a, sk_a, pk_b, sk_b)
# c_b = pre.re_encrypt(params, rk, c_a)
# pre.decrypt(params, sk_b, c_b) 