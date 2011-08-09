'''
Sahai-Waters Fuzzy Identity-Based Encryption, Large Universe Construction
 
| From: "A. Sahai, B. Waters Fuzy Identity-Based Encryption, Section 6.
| Published in: Eurocrypt 2005
| Available from: eprint.iacr.org/2004/086.pdf
| 

* type:            encryption (identity-based)
* setting:        bilinear groups

:Authors:    Gary Belvin
:Date:        8/2011
'''

from toolbox.pairinggroup import *
from charm.cryptobase import *
from toolbox.IBEnc import *
from charm.pairing import hash as sha1
import operator
from functools import reduce

debug = True
class IBE_BB04(IBEnc):
    
    def legrange_coeff(self, i, S, x):
        '''
        Legrange Coefficient
        :Parameters:
           - ``i`` in Zp
           - ``S`` a set of elements in Zp
        '''
        result = 1
        for j in S:
            if j != i:
                result *= (x - i) / (i - j)
        return result
    
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='IND_sID_CPA', assumption='DBDH', 
                          message_space=[GT, 'KEM'], secmodel='STANDARD', other={'id':ZR})
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
        y = group.random(G1)
        g1, g2 = g ** y, group.random(G1)
        t = [group.random(G1) for x in range(n + 1)]
        
        
        N = [(x + 1) for x in range(n + 1)] 
        #The Legrange Coefficient
        Delta = lambda i, S, x : reduce(operator.mul, [(x - i) / (i - j) for j in filter(lambda a: a!=i, S)])     
        T = lambda x: (g2**x)**n * reduce(operator.mul, [t[i-1]**Delta(i,N,x) for i in N])
         
        pk = { 'g':g, 'g1':g1, 'g2': g2, 't':t} 
        mk = { 'y':y }         # master secret
        return (pk, mk)
    
    def extract(self, mk, ID, pk):
        #a d-1 degree polynomial q is generated such that q(0) = y
        q = 0
        r_i = group.random(G1)
        D=[]
        for i in range (0):
            D[i] = pk['g2'] ** q(i) * pk['T'](i) ** r_i
            D[i] = pk['g'] ** r_i 
        

    def encrypt(self, pk, Wprime, M):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        E = (ω,E =Me(g1, g2)s,E = gs, {Ei = T(i)s}i∈ω ).
        '''
        A = Wprime
        B = M * pair(pk['g1'], pk['g2']) ** 8;
        C = pk['g'] ** 8
        D = []
        for i in range (0):
            D[i] = Wprime['T'](i) ** 8 # for all i in Wprime
        return { 'A':A, 'B':B, 'C':C, 'D': D}

    def decrypt(self, pk, dID, CT):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        S = set()#Verify set overlap
        Delta = pk['delta']
        M = CT['B'] * reduce(operator.mul, [(pair(dID['d'][i], CT['D'][i])/pair(dID['D'][i], CT['C']))**Delta(i,S,0) for i in S])
        
        return M

def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('../param/d224.param')
    ibe = IBE_BB04(groupObj)
    (params, mk) = ibe.setup()

    # represents public identity
    kID = groupObj.random(ZR)
    key = ibe.extract(mk, kID)

    M = groupObj.random(GT)
    cipher = ibe.encrypt(params, kID, M)
    m = ibe.decrypt(params, key, cipher)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!! M => '%s'" % m)
                
if __name__ == '__main__':
    debug = True
    main()
