'''
BBS Proxy Re-Encryption
| From: Blaze, M., Bleumer, G., & Strauss, M. (1998). Divertible protocols and atomic proxy cryptography.
| Published in: Advances in Cryptology-EUROCRYPT'98 (pp. 127-144). Springer Berlin Heidelberg.
| Available from: http://link.springer.com/chapter/10.1007/BFb0054122
* type:           proxy encryption
* properties:     CPA-secure, bidirectional, multihop, not collusion-resistant, interactive, transitive
* setting:        DDH-hard EC groups of prime order (F_p) or Integer Groups
* assumption:     DDH
:Authors:    D. Nuñez (dnunez@lcc.uma.es)
:Date:       04/2016
'''

from charm.toolbox.ecgroup import G
from charm.toolbox.PREnc import PREnc

debug = False
class BBS98(PREnc):
    """
    Testing BBS98 implementation

    >>> from charm.toolbox.eccurve import prime192v1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> groupObj = ECGroup(prime192v1)
    >>> bbs = BBS98(groupObj)
    >>> params = bbs.setup()
    >>> (pk_a, sk_a) = bbs.keygen(params)
    >>> (pk_b, sk_b) = bbs.keygen(params)
    >>> msg = b"hello world!!!123456"
    >>> c_a = bbs.encrypt(params, pk_a, msg)
    >>> assert msg == bbs.decrypt(params, sk_a, c_a), 'Decryption of original ciphertext was incorrect'
    >>> rk = bbs.rekeygen(params, pk_a, sk_a, pk_b, sk_b)
    >>> c_b = bbs.re_encrypt(params, rk, c_a)
    >>> assert msg == bbs.decrypt(params, sk_b, c_b), 'Decryption of re-encrypted ciphertext was incorrect'
    """

    def __init__(self, groupObj, p=0, q=0):
        global group
        group = groupObj
        if group.groupSetting() == 'integer':
            group.p, group.q, group.r = p, q, 2

    def setup(self, secparam=0):
        global g
        if group.groupSetting() == 'integer':
            if group.p == 0 or group.q == 0:
                group.paramgen(secparam)
            g = group.randomGen()
        elif group.groupSetting() == 'elliptic_curve':
            group.paramgen(secparam)
            g = group.random(G)

        params = {'g': g}
        if(debug):
            print("Setup: Public parameters...")
            group.debug(params)
        return params

    def keygen(self, params):
        x = group.random()
        g_x = params['g'] ** x

        sk = x      # { 'sk' : x }
        pk = g_x    # { 'pk' : g_x }

        if(debug):
            print('\nKeygen...')
            print("pk => '%s'" % pk)
            print("sk => '%s'" % sk)
        return (pk, sk)

    def rekeygen(self, params, pk_a, sk_a, pk_b, sk_b):
        rk = sk_b * (~sk_a)
        if(debug):
            print('\nReKeyGen...')
            print("rk => '%s'" % rk)
        return rk

    def encrypt(self, params, pk, M):
        m = group.encode(M)
        r = group.random()
        c1 = pk ** r
        c2 = (params['g'] ** r) * m

        c = {'c1': c1, 'c2': c2}

        if(debug):
            print('\nEncrypt...')
            print('m => %s' % m)
            print('r => %s' % r)
            group.debug(c)
        return c

    def decrypt(self, params, sk, c):
        c1 = c['c1']
        c2 = c['c2']
        m = c2 / (c1 ** (~sk))

        if(debug):
            print('\nDecrypt...')
            print('m => %s' % m)

        return group.decode(m)

    def re_encrypt(self, params, rk, c_a):
        c1 = c_a['c1']
        c2 = c_a['c2']

        c_b = {'c1': (c1 ** rk), 'c2': c2}

        if(debug):
            print('\nRe-encrypt...')
            group.debug(c_b)
        return c_b
