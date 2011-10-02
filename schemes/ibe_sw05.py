'''
Sahai-Waters Fuzzy Identity-Based Encryption
 
| From: "A. Sahai, B. Waters Fuzy Identity-Based Encryption, Section 4.
| Published in: Eurocrypt 2005
| Available from: eprint.iacr.org/2004/086.pdf
| 

* type:            encryption (identity-based)
* setting:        bilinear groups

:Authors:    Gary Belvin & Christina Garman
:Date:       10/2011
:Status:     Broken
'''

from toolbox.pairinggroup import *
from charm.cryptobase import *
from toolbox.IBEnc import *
from charm.pairing import hash as sha1
import operator
from functools import reduce

debug = False
class IBE_SW05(IBEnc):
    def legrange_coeff(self, i, S, x):
        '''
        Legrange Coefficient
        :Parameters:
           - ``i`` in Zp
           - ``S`` a set of elements in Zp
        '''
        result = group.init(ZR,1)
        for j in S:
            if not(j == i):
                result = result * ((x - j) / (i - j))
        return result

    def intersection_subset(self, w, wPrime, d):
        S = []
        for i in range(len(w)):
            for j in range(len(wPrime)):
                if(w[i] == wPrime[j]):
                    S.append(w[i])

        S_sub  = [S[k] for k in range(d)]
        return S_sub
    
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='sIND_ID_CPA', assumption='DBDH', 
                          message_space=[GT, 'KEM'], secmodel='SM', other={'id':ZR})
        global group
        group = groupObj
        
    def setup(self, u):
        g = group.random(G1)
        y = group.random(ZR)
        Y = pair(g,g) ** y
        t = [group.random(ZR) for x in range(u)]
        
        T = [g ** t[x] for x in range(u)]
         
        pk = { 'g':g, 'T':T, 'Y':Y } 
        mk = { 't':t, 'y':y }         # master secret

        return (pk, mk)
    
    def extract(self, mk, ID, pk, d):
        q = [group.random(ZR) for x in range(d)]
        q[0] = mk['y']

        D=[]
        q_i = group.init(ZR,0)
        for i in ID:
            #evaluate q(i)
            for x in range(d):
                j = group.init(ZR,x)
                q_i = q_i + (q[x] * (i ** j))
            D.append(pk['g'] ** (q_i/mk['t'][int(i)]))

        return D
        

    def encrypt(self, pk, Wprime, M):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        s = group.random(ZR)
        Eprime = M * (pk['Y'] ** s);

        E = []
        for i in Wprime:
            E.append(pk['T'][int(i)] ** s)

        return { 'wPrime':Wprime, 'Eprime':Eprime, 'E':E}

    def decrypt(self, pk, dID, CT, w, d):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        S = self.intersection_subset(w, CT['wPrime'], d)

        prod = 1
        for i in S:
            j = w.index(i)
            k = CT['wPrime'].index(i)
            prod = prod * pair(dID[j], CT['E'][k]) ** self.legrange_coeff(i, S, group.init(ZR,0))

        M = CT['Eprime']/prod

        return M

def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('../param/a.param')
    ibe = IBE_SW05(groupObj)

    u = 10 #universe
    d = 3 #overlap

    (pk, mk) = ibe.setup(u)

    w = [group.init(ZR,1), group.init(ZR,3), group.init(ZR,5), group.init(ZR,7), group.init(ZR,9)] #private identity
    key = ibe.extract(mk, w, pk, d)
    wPrime = [group.init(ZR,1), group.init(ZR,2), group.init(ZR,3), group.init(ZR,4), group.init(ZR,7), group.init(ZR,9)]

    M = groupObj.random(G2)

    cipher = ibe.encrypt(pk, wPrime, M)
    m = ibe.decrypt(pk, key, cipher, w, d)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!! M => '%s'" % m)
                
if __name__ == '__main__':
    debug = True
    main()
