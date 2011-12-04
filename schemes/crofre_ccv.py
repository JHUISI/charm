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
class CROFRE_CCV(IBEnc):
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group
        group = groupObj
    
    def setup(self):
        g = group.random(G1)
        h = group.random(G2)
        return (g,h)

    def Igen(self, g, d):
        '''
        :Parameters:
           - ``n``: the maximum number of attributes in the system.
                    OR the maximum length of an identity
           - ``d``: the set overlap required to decrypt
        '''
        #why do a's of length 1 not work??? -> but all others do
        a = [[group.random(ZR), group.random(ZR), group.random(ZR)] for x in range(d)]
        print("a => ", a, type(a[0][0]), range(d))
        ga = [[g ** aij for aij in ai] for ai in a]

        pk = { 'g':g, 'ga':ga }
        sk = { 'a':a }

        return (pk, sk)
    
    def Iencrypt(self, pk, i, m):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        r = group.random(ZR)
        print("r => ", r)
        rprime = group.random(ZR)
        print("r' => ", rprime, 1/rprime)

        ai = pk['ga'][i-1]

        C = [gai ** r for gai in ai]
        #C = pk['ga'][i] ** r
        D = (pk['g'] ** r) * m

        Cprime = [gai ** rprime for gai in ai]
        #Cprime = pk['ga'][i] ** rprime
        Dprime = pk['g'] ** rprime

        E = { 'C':C, 'D':D }
        Eprime = { 'Cprime':Cprime, 'Dprime':Dprime }

        return { 'E':E, 'Eprime':Eprime }

    def Idecrypt(self, d, sk, pk, c):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        E = c['E']
        print("E => ", E)
        C = E['C']
        print("C => ", C)
        D = E['D']
        print("D => ", D)

        for i in range(d):
            print("i => ", i)
            ai = sk['a'][i]
            #aij = ai[0]
            #print("ai => ", ai, len(ai), aij, type(aij), 1/aij, 1/ai[0])
            #Cvec = [(C[j] ** (1/ai[j])) ** -1 for j in range(len(ai))]
            Cvec = [print(C[j], ai[j], type(C[j]), type(ai[j]), 1/ai[j], 1/C[j]) for j in range(len(ai))]
            Cvec = [1/(C[j] ** (1/ai[j])) for j in range(len(ai))]
            print("Cvec => ", Cvec)
            #Cvec = [(C[i] ** (1/sk['a'][i])) ** -1 for i in range(len(C))]
            M = [D * Cveci for Cveci in Cvec]
            print("M => ", M)

            if(all(x == M[0] for x in M)):
                return (i+1, M[0])

        return "Error"

    def Ogen(self, g, h, d):
        '''
        :Parameters:
           - ``n``: the maximum number of attributes in the system.
                    OR the maximum length of an identity
           - ``d``: the set overlap required to decrypt
        '''
        ahat = group.random(ZR)
        pk = h ** ahat
        sk = ahat

        pkhat = { 'g':g, 'h':h, 'ha':pk }
        skhat = { 'ahat':sk }

        return (pkhat, skhat)
    
    def Oencrypt(self, pkhat, m):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        r = group.random(ZR)
        s = group.random(ZR)

        Yhat = pk['ha'] ** r
        What = pk['h'] ** r

        Fhat = pair(pk['g'] ** s, Yhat)
        Ghat = pair(pk['g'] ** s, What) * pair(m, pk['h'] ** s)
        Hhat = pk['h'] ** s

        return { 'Fhat':Fhat, 'Ghat':Ghat, 'Hhat':Hhat }

    def Odecrypt(self, sk, pk, c):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        Qhat = c['Ghat'] * (c['Fhat'] ** (-1/sk['ahat']))

        #how are you supposed to efficiently test pairings of all m??? that's quite a poor decryption scheme

def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('../param/a.param')
    d = 3
    scheme = CROFRE_CCV(groupObj)
    (g,h) = scheme.setup()
    (pk, sk) = scheme.Igen(g, d)
    if debug:
        print("Parameter Setup...")
        print("pk =>", pk)
        print("sk =>", sk)

    M = groupObj.random(G1)
    print("M => ", M)
    cipher = scheme.Iencrypt(pk, 2, M)
    print("Ciphertext => ", cipher)
    (i, m) = scheme.Idecrypt(d, sk, pk, cipher)
    print("(i, m) => ", i, m)
    print("M => ", M)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!! M => '%s'" % m)

    (pkhat, skhat) = scheme.Ogen(h, d)
    if debug:
        print("Parameter Setup...")
        print("pk =>", pkhat)
        print("sk =>", skhat)

    M = groupObj.random(G1)
    print("M => ", M)
    cipher = scheme.Iencrypt(pk, 2, M)
    print("Ciphertext => ", cipher)
    (i, m) = scheme.Idecrypt(d, sk, pk, cipher)
    print("(i, m) => ", i, m)
    print("M => ", M)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!! M => '%s'" % m)

                
if __name__ == '__main__':
    debug = True
    main()

