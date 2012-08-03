'''
Chandran-Chase-Vaikuntanathan : Obsfucated and Functional Re-encryption
 
Chandran, N. and Chase, M. and Vaikuntanathan V., "Collusion-Resistant Obfuscation and Functional Re-encryption"
Published in: 
Available from: http://eprint.iacr.org/2011/337

* type:           encryption (functional-re-encryption)
* setting:        bilinear groups (asymmetric)

:Authors:    J Ayo Akinyele
:Date:       03/2012 
:Status:     NOT FINISHED/DOESN'T EXECUTE
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair as e

debug = False
class InputEnc:
    def __init__(self, groupObj):
        global group, proof
        group = groupObj
        proof = lambda a,b,c,d: group.hash((a, b, c, d), ZR) 
        
    def setup(self, d):
        a = [group.random(ZR) for i in range(d)]
        g = group.random(G1)
        C = [g ** a[i] for i in range(d)]
    
        # need to add 'crs'
        i_pk = { 'g':g, 'C':C, 'd':d }
        i_sk = { 'a':a }
        return (i_pk, i_sk)
        
    def encrypt(self, i_pk, i, M : G1):
        if i > i_pk['d'] or i < 0: 
            print("i not in d. try again!")
            return None        
        r, r_pr = group.random(ZR, 2)

        C   = [ i_pk['C'][i] ** r for i in range(i_pk['d']) ] 
        Cpr = [ i_pk['C'][i] ** r_pr for i in range(i_pk['d']) ]
        D = (i_pk['g'] ** r) * M
        Dpr = i_pk['g'] ** r_pr
        E   = { 'C':C, 'D':D }
        Epr = { 'Cpr':Cpr, 'Dpr':Dpr }
        
        # is this correct?
        pi = None
#        pi = proof(C, D, Cpr, Dpr) # group.hash((C, D, Cpr, Dpr), ZR)
        return (E, Epr, pi)
    
    def decrypt(self, i_sk, ct, M : [G1]):
        E, Epr, pi = ct
        C, D = E['C'], E['D']
        a = i_sk['a']
#        if pi != proof(C, D, Epr['Cpr'], Epr['Dpr']):
#            print("proof did not verify.")
#            return False
        result = {}
        for i in range(len(a)):
            result[i] = D * ~(C ** (1 / a[i]))
        
        m = result[0]
        for i in range(1, len(result)):
            if m != result[i]: return False        
        return m
    

class OutputEnc:
    def __init__(self, groupObj):
        global group
        group = groupObj
    
    def setup(self):
        h = group.random(G2)
        a = group.random(ZR)
        
        o_pk = { 'h':h, 'pk':h ** a }
        o_sk = a 
        return (o_pk, o_sk)
    
    def encrypt(self, i_pk, o_pk, M : G1):        
        r, s = group.random(ZR, 2)
        Y = o_pk['pk'] ** r
        W = o_pk['h'] ** r
        S = i_pk['g'] ** s
        
        F = e(S, Y)
        H = o_pk['h'] ** s
        G = e(S, W) * e(M, H)
        return { 'F':F, 'G':G, 'H':H }
    
    def decrypt(self, a, ct, M : [G1]):
        F, G, H = ct['F'], ct['G'], ct['H']
        Q = G * (F ** -(1 / a))
        
        for m in M:
            if e(m, H) == Q: return m
        return False
        
