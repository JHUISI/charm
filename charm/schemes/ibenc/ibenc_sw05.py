'''
Sahai-Waters Fuzzy Identity-Based Encryption, Original Construction

| From: "A. Sahai, B. Waters Fuzzy Identity-Based Encryption.
| Published in: Eurocrypt 2005
| Available from: eprint.iacr.org/2004/086.pdf
| Notes: Original construction (Section 4) and large universe construction (Section 6). 

* type:            encryption (identity-based)
* setting:        bilinear groups

:Authors:    Christina Garman
:Date:       10/2011
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import IBEnc
from charm.toolbox.secretshare import SecretShare

debug = False
class IBE_SW05(IBEnc): 
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> group = PairingGroup('SS512')
    >>> max_attributes = 6
    >>> required_overlap = 4
    >>> ibe = IBE_SW05_LUC(group)
    >>> (master_public_key, master_key) = ibe.setup(max_attributes, required_overlap)
    >>> private_identity = ['insurance', 'id=2345', 'oncology', 'doctor', 'nurse', 'JHU'] #private identity
    >>> public_identity = ['insurance', 'id=2345', 'doctor', 'oncology', 'JHU', 'billing', 'misc'] #public identity for encrypt
    >>> (pub_ID_hashed, secret_key) = ibe.extract(master_key, private_identity, master_public_key, required_overlap, max_attributes)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, public_identity, msg, max_attributes)
    >>> decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text, pub_ID_hashed, required_overlap)
    >>> msg == decrypted_msg
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group, H, util
        group = groupObj
        H = lambda x: group.hash(('0', x), ZR)
        util = SecretShare(group, False)
        
    def setup(self, n, d):
        '''
        :Parameters:
           - ``n``: the maximum number of attributes in the system.
                    OR the maximum length of an identity
           - ``d``: the set overlap required to decrypt
        '''
        g = group.random(G1)
        y = group.random(ZR)
        Y = pair(g, g) ** y

        t = [ group.random(ZR) for x in range( n )]
        T = [ g ** i for i in t]
        
        pk = { 'g':g, 'Y':Y, 'T': T } 
        mk = { 'y':y, 't':t }         # master secret
        return (pk, mk)

    def intersection_subset(self, w, wPrime, d):
        S = []
        for i in range(len(w)):
            for j in range(len(wPrime)):
                if(w[i] == wPrime[j]):
                    S.append(w[i])

        if(len(S) < d):
            assert False, "Cannot decrypt.  w and w' do not have enough attributes in common."

        S_sub  = [S[k] for k in range(d)]
        return S_sub
    
    def extract(self, mk, ID, pk, dOver, n):
        w_hash = [H(x) for x in ID] # assumes ID is a list

        #a d-1 degree polynomial q is generated such that q(0) = y
        q = [group.random(ZR) for x in range(dOver)]
        q[0] = mk['y']
        # use secret sharing as building block
        shares = util.genShares(mk['y'], dOver, n, q, w_hash)
        D = {}; t_index = {};
        for i in w_hash:       
            j = w_hash.index(i)
            D[i] = (pk['g'] ** (shares[j][1] / mk['t'][j]))
            # dictionary for finding corresponding T public value when encrypting 
            # this eliminates ordering of attribute issues
            t_index[i] = j; 
            
        pk['T_index'] = t_index
        return (w_hash, { 'D':D })

    def encrypt(self, pk, w_prime, M, n):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        w_prime_hash = [H(x) for x in w_prime]
        s = group.random(ZR)

        Eprime = M * (pk['Y'] ** s)
        E = {}
        for i in w_prime_hash:
            k = pk['T_index'][i]
            E[i] = pk['T'][k] ** s

        return { 'wPrime':w_prime_hash, 'Eprime':Eprime, 'E':E}

    def decrypt(self, pk, sk, CT, w, d):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        S = self.intersection_subset(w, CT['wPrime'], d)
        coeffs = util.recoverCoefficients(S)
        prod = 1
        for i in S:            
            prod *= pair(sk['D'][i], CT['E'][i]) ** coeffs[i]
            
        return CT['Eprime'] / prod
 

'''
Sahai-Waters Fuzzy Identity-Based Encryption, Large Universe Construction

| From: "A. Sahai, B. Waters Fuzzy Identity-Based Encryption.
| Published in: Eurocrypt 2005
| Available from: eprint.iacr.org/2004/086.pdf
| Notes: Original construction (Section 4) and large universe construction (Section 6). 

* type:            encryption (identity-based)
* setting:        bilinear groups

:Authors:    Christina Garman
:Date:       10/2011
'''
class IBE_SW05_LUC(IBEnc):    
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group, H, util
        group = groupObj
        H = lambda x: group.hash(('0', x), ZR)
        util = SecretShare(group, False)
        
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
        
        t = [ group.random(G1) for x in range( n+1 )]
        
        pk = { 'g':g, 'g1':g1, 'g2':g2, 't':t } 
        mk = { 'y':y }         # master secret
        return (pk, mk)

    def eval_T(self, pk, n, x):
        N = [group.init(ZR,(x + 1)) for x in range(n + 1)]        
        N_int = [(x + 1) for x in range(n + 1)]
        
        coeffs = util.recoverCoefficients(N)
        prod_result = 1
        for i in N_int:
            j = group.init(ZR, i)
            prod_result *= (pk['t'][i-1] ** coeffs[j])
        
        T = (pk['g2'] ** (x * n)) * prod_result
        return T

    def intersection_subset(self, w, wPrime, d):
        S = []
        for i in range(len(w)):
            for j in range(len(wPrime)):
                if(w[i] == wPrime[j]):
                    S.append(w[i])

        if(len(S) < d):
            assert False, "Cannot decrypt.  w and w' do not have enough attributes in common."

        S_sub  = [S[k] for k in range(d)]
        return S_sub
    
    def extract(self, mk, ID, pk, dOver, n):
        w_hash = [H(x) for x in ID] # assumes ID is a list

        r = group.random(ZR)
        #a d-1 degree polynomial q is generated such that q(0) = y
        q = [group.random(ZR) for x in range(dOver)]
        q[0] = mk['y']
        shares = util.genShares(mk['y'], dOver, n, q, w_hash)
        D = {}
        d = {}
        for i in w_hash:       
            j = w_hash.index(i)
            D[i] = (pk['g2'] ** shares[j][1]) * (self.eval_T(pk, n, i) ** r)
            d[i] = pk['g'] ** r

        return (w_hash, { 'D':D, 'd':d })

    def encrypt(self, pk, w_prime, M, n):
        '''       
        Encryption with the public key, Wprime and the message M in G2
        '''
        w_prime_hash = [H(x) for x in w_prime]
        s = group.random(ZR)

        Eprime = M * (pair(pk['g1'], pk['g2']) ** s)
        Eprimeprime = pk['g'] ** s
        
        E = {}
        for i in w_prime_hash:
            E[i] = self.eval_T(pk, n, i) ** s

        return { 'wPrime':w_prime_hash, 'Eprime':Eprime, 'Eprimeprime':Eprimeprime,'E':E}

    def decrypt(self, pk, sk, CT, w, d):
        '''dID must have an intersection overlap of at least d with Wprime to decrypt
        '''
        S = self.intersection_subset(w, CT['wPrime'], d)
        #print("S :=", S)
        coeffs = util.recoverCoefficients(S)
        prod = 1
        for i in S:
            prod *= (pair(sk['d'][i], CT['E'][i]) / pair(sk['D'][i], CT['Eprimeprime'])) ** coeffs[i]
            
        return CT['Eprime'] * prod
