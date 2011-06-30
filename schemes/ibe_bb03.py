# Boneh-Boyen Identity Based Encryption
# 
# From: "D. Boneh, X. Boyen.  Efficient Selective Identity-Based Encryption Without Random Oracles", Section 5.1.
# Published in: Eurocrypt 2004
# Available from: http://crypto.stanford.edu/~dabo/pubs/papers/bbibe.pdf
# Notes: This is the IBE (1-level HIBE) implementation of the HIBE scheme BB_2.
#
# type:			encryption (identity-based)
# setting:		bilinear groups (asymmetric)
#
# Implementer:	J Ayo Akinyele
# Date:			11/2010

from toolbox.pairinggroup import *
from charm.cryptobase import *
from toolbox.IBEnc import *
from charm.pairing import hash as sha1


class IBE_BB04(IBEnc):
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='IND_sID_CPA', assumption='DBDH', 
                          message_space=[GT, 'KEM'], secmodel='ROM', other={'id':ZR})
        global group, debug
        group = groupObj
        debug = True
        
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
        A = sha1(params['v'] ** s) # session key
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
        return sha1(v_s)

def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('d224.param')
    ibe = IBE_BB04(groupObj)
    print("Running through IBE setup...")
    (params, mk) = ibe.setup()

    # represents public identity
    kID = groupObj.random(ZR)
    key = ibe.extract(mk, kID)

    M = groupObj.random(GT)
    cipher = ibe.encrypt(params, kID, M)
    m = ibe.decrypt(params, key, cipher)

    assert m == M, "FAILED Decryption!"
    print("Successful Decryption!!! M => '%s'" % m)
                
if __name__ == '__main__':
    main()
