# Boneh-Boyen Identity Based Encryption
# 
# From: "D. Boneh, X. Boyen.  Efficient Selective Identity-Based Encryption Without Random Oracles", Section 5.1.
# Published in: Eurocrypt 2004
# Available from: http://crypto.stanford.edu/~dabo/pubs/papers/bbibe.pdf
# Notes: This is the IBE (2-level HIBE) implementation of the HIBE scheme BB_2.
#
# type:			encryption (identity-based)
# setting:		bilinear groups (asymmetric)
#
# Implementer:	Joseph Ayo Akinyele
# Date:			11/2010

from toolbox.pairinggroup import *
from charm.pairing import pair,hash as sha1
from charm.cryptobase import *
from toolbox.IBEnc import *

class IBE_BB04(IBEnc):
    def __init__(self, groupObj, key_size=16, alg=AES):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='IND_sID_CPA', assumption='DBDH', 
                          message_space=[GT, 'KEM'], secmodel='ROM', other={'id':ZR})
        global group, prf
        group = groupObj
        #global bID1
        #bID1 = InitBenchmark()
        
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
        # verify we have an appropriate 'r' value for ID
        if type(ID) == pairing: id = ID
        else:
            assert False, "ID has invalid type!"
        # compute K
        K = mk['h'] ** ~(id + mk['x'] + r*mk['y'])
        return { 'id':id, 'r':r, 'K':K }

    # assume that M is in GT
    def encrypt(self, params, ID, M):
        s = group.random()

        A = (params['v'] ** s) * M 
        B = params['Y'] ** s
        C = (params['X'] ** s) * (params['g'] ** (s * ID))
        return { 'A':A, 'B':B, 'C':C }

    def keyenc(self, params, ID, msg):
        s = group.random()
        A = sha1(params['v'] ** s) # session key
        B = params['Y'] ** s
        C = (params['X'] ** s) * (params['g'] ** (s * ID))
        # use prf here?
        ciph = { 'B': B, 'C': C }
        return (A, ciph) # user must destory A since it protects the msg

    def decrypt(self, pk, dID, CT):
        A, B, C = CT['A'], CT['B'], CT['C']
        v_s = pair(((B ** dID['r']) * C), dID['K'])
        return A / v_s
    
    def keydec(self, pk, dID, CT):
        A, B, C = CT['A'], CT['B'], CT['C']
        v_s = pair(((B ** dID['r']) * C), dID['K'])
        return sha1(v_s)
                
if __name__ == '__main__':
    # initialize the element object so that object references have global scope
    #elem = pairing('library/d224.param')
    groupObj = PairingGroup('library/d224.param')
    ibe = IBE_BB04(groupObj)
    print("Running through IBE setup...")
    (params, mk) = ibe.setup()

    kID = 'ayo@email.com'
    key = ibe.extract(mk, kID)

    #kID2 = 'adversary@email.com'
    #key2 = ibe.extract(mk, kID2)

    M = groupObj.random(GT)
    cipher = ibe.encrypt(params, key['id'], M)
    m = ibe.decrypt(params, key, cipher)

    if m == M:
        print("Successful Decryption!!! M => '%s'" % m)
    else:
        print("FAILED Decryption!")

