'''
Sahai-Waters Fuzzy Identity-Based Encryption, Large Universe Construction
 
| From: "A. Sahai, B. Waters Fuzy Identity-Based Encryption, Section 6.
| Published in: Eurocrypt 2005
| Available from: eprint.iacr.org/2004/086.pdf
| 

* type:            encryption (identity-based)
* setting:        bilinear groups

:Authors:    Christina Garman
:Date:       10/2011
'''

from toolbox.pairinggroup import *
from charm.cryptobase import *
from toolbox.IBEnc import *
from charm.pairing import hash as sha1
import operator
from functools import reduce
import sys

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

    def eval_T(self, pk, n, x):
        N = [group.init(ZR,(x + 1)) for x in range(n + 1)]
        N_int = [(x + 1) for x in range(n + 1)]
        result = group.init(ZR,1)

        for i in N_int:
            result = result * (pk['t'][i-1] ** self.legrange_coeff(group.init(ZR,i),N,x))

        T = ((pk['g2'] ** x) ** group.init(ZR,n)) * result
        return T

    def intersection_subset(self, w, wPrime, d):
        S = []
        for i in range(len(w)):
            for j in range(len(wPrime)):
                if(w[i] == wPrime[j]):
                    S.append(w[i])

        if(len(S) < d):
            print("Cannot decrypt.  w and w' do not have enough attributes in common.")
            sys.exit()

        S_sub  = [S[k] for k in range(d)]
        return S_sub
    
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='sIND_ID_CPA', assumption='DBDH', 
                          message_space=[GT, 'KEM'], secmodel='SM', other={'id':ZR})
        global group
        group = groupObj
        
    def setup(self, n, d):
        '''
        :Parameters:
           - ``n``: the maximum number of attributes in the system.
                    OR the maximum length of an identity
           - ``d``: the set overlap required to decrypt
        '''
        g = group.random(G1)
        y = group.random(ZR)
        g1 = g ** y
        g2 = group.random(G1)
        t = [group.random(G1) for x in range(n + 1)]
       
        pk = { 'g':g, 'g1':g1, 'g2': g2, 't':t } 
        mk = { 'y':y }         # master secret
        return (pk, mk)
    
    def extract(self, mk, ID, pk, dOver, n):
        prefix = '0'
        w_hash = []
        for i in range(len(ID)):
            w_hash.append(group.hash((prefix,ID[i]), ZR))

        #a d-1 degree polynomial q is generated such that q(0) = y
        q = [group.random(ZR) for x in range(dOver)]
        q[0] = mk['y']

        r_i = group.random(ZR)

        D = []
        d = []
        q_i = group.init(ZR,0)
        for i in w_hash:
            #evaluate q(i)
            for x in range(dOver):
                j = group.init(ZR,x)
                q_i = q_i + (q[x] * (i ** j))

            D.append((pk['g2'] ** q_i) * (self.eval_T(pk,n,i) ** r_i))
            d.append(pk['g'] ** r_i)

        return (w_hash, { 'D':D, 'd':d })

    def encrypt(self, pk, Wprime, M, n):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        prefix = '0'
        wprime_hash = []
        for i in range(len(Wprime)):
            wprime_hash.append(group.hash((prefix,Wprime[i]), ZR))

        s = group.random(ZR)

        Eprime = M * (pair(pk['g1'],pk['g2']) ** s)

        Eprimeprime = pk['g'] ** s

        E = []
        for i in wprime_hash:
            E.append(self.eval_T(pk,n,i) ** s)

        return { 'wPrime':wprime_hash, 'Eprime':Eprime, 'Eprimeprime':Eprimeprime, 'E':E}

    def decrypt(self, pk, dID, CT, w, d):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        S = self.intersection_subset(w, CT['wPrime'], d)

        prod = 1
        for i in S:
            j = w.index(i)
            k = CT['wPrime'].index(i)

            prod = prod * ((pair(dID['d'][j],CT['E'][k])/pair(dID['D'][j],CT['Eprimeprime'])) ** (self.legrange_coeff(i,S,group.init(ZR,0))))

        M = CT['Eprime'] * prod

        return M

def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('../param/a.param')
    n = 5; d = 3
    ibe = IBE_SW05(groupObj)
    (pk, mk) = ibe.setup(n, d)
    print("Parameter Setup...")
    print("pk =>", pk)
    print("mk =>", mk)

    #w = [group.init(ZR,1), group.init(ZR,3), group.init(ZR,5), group.init(ZR,7), group.init(ZR,9)] #private identity
    #wPrime = [group.init(ZR,1), group.init(ZR,2), group.init(ZR,3), group.init(ZR,7), group.init(ZR,9)] #public identity

    w = ["doctor","nurse","JHU","oncology","id=12345"] #private identity
    wPrime = ["id=12345","insurance","oncology","JHU","misc"] #public identity

    (w, key) = ibe.extract(mk, w, pk, d, n)

    M = groupObj.random(G2)
    cipher = ibe.encrypt(pk, wPrime, M, n)
    m = ibe.decrypt(pk, key, cipher, w, d)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!! M => '%s'" % m)
                
if __name__ == '__main__':
    debug = True
    main()
