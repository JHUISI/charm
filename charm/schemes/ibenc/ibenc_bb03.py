'''
Boneh-Boyen Identity Based Encryption
 
| From: "D. Boneh, X. Boyen.  Efficient Selective Identity-Based Encryption Without Random Oracles", Section 5.1.
| Published in: Eurocrypt 2004
| Available from: http://crypto.stanford.edu/~dabo/pubs/papers/bbibe.pdf
| Notes: This is the IBE (1-level HIBE) implementation of the HIBE scheme BB_2.

* type:     encryption (identity-based)
* setting:  bilinear groups (asymmetric)

:Authors:   J Ayo Akinyele
:Date:      11/2010
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import *
from charm.core.math.pairing import hashPair as sha2

debug = False
class IBE_BB04(IBEnc):
    """
    >>> group = PairingGroup('MNT224')
    >>> ibe = IBE_BB04(group)
    >>> (master_public_key, master_key) = ibe.setup()
    >>> master_public_key_ID = group.random(ZR)
    >>> key = ibe.extract(master_key, master_public_key_ID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, master_public_key_ID, msg)
    >>> decrypted_msg = ibe.decrypt(master_public_key, key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secDef=IND_sID_CPA, assumption=DBDH, 
                          messageSpace=[GT, 'KEM'], secModel=ROM, id=ZR)
        global group
        group = groupObj
        
    def setup(self, secparam=None):
        #StartBenchmark(bID1, [CpuTime, NativeTime])
        g, h = group.random(G1), group.random(G2)
        v = pair(g, h)
        x, y = group.random(), group.random()

        X = g ** x
        Y = g ** y 
        pk = { 'g':g, 'X':X, 'Y':Y, 'v':v } # public params
        mk = { 'x':x, 'y':y, 'h':h }         # master secret
        return (pk, mk)
    
    # Note: ID is in Zp* and is the public key ID for the user
    def extract(self, mk, ID):
        r = group.random()
        # compute K
        K = mk['h'] ** ~(ID + mk['x'] + r*mk['y'])
        return { 'id':ID, 'r':r, 'K':K }

    # assume that M is in GT
    def encrypt(self, params, ID, M):
        s = group.random()

        A = (params['v'] ** s) * M 
        B = params['Y'] ** s
        C = (params['X'] ** s) * (params['g'] ** (s * ID))
        return { 'A':A, 'B':B, 'C':C }

    def keyenc(self, params, ID, msg):
        s = group.random()
        A = sha2(params['v'] ** s) # session key
        B = params['Y'] ** s
        C = (params['X'] ** s) * (params['g'] ** (s * ID))
        # use prf here?
        ciph = { 'B': B, 'C': C }
        return (A, ciph) # user must destroy A since it protects the msg

    def decrypt(self, pk, dID, CT):
        A, B, C = CT['A'], CT['B'], CT['C']
        v_s = pair(((B ** dID['r']) * C), dID['K'])
        return A / v_s
    
    def keydec(self, pk, dID, CT):
        A, B, C = CT['A'], CT['B'], CT['C']
        v_s = pair(((B ** dID['r']) * C), dID['K'])
        return sha2(v_s)

