# John Bethencourt, Brent Waters (Pairing-based)
# 
# From: "Ciphertext-Policy Attribute-Based Encryption".
# Published in: 2007
# Available from: 
# Notes: 
# Security Assumption: 

# type:           ciphertext-policy attribute-based encryption (public key)
# setting:        Pairing
#
# Implementer:    J Ayo Akinyele
# Date:            04/2011

from toolbox.pairinggroup import *
from toolbox.secretutil import *
from toolbox.ABEnc import *

class CPabe_BSW07(ABEnc):
    def __init__(self, groupObj):
        ABEnc.__init__(self)
        global util, group
        util = SecretUtil(groupObj.Pairing, verbose=False)
        group = groupObj

        
    def setup(self):
        g, gp = group.random(G1), group.random(G2)
        alpha, beta = group.random(), group.random()

        h = g ** beta; f = g ** ~beta
        e_gg_alpha = pair(g, gp ** alpha)
        
        pk = { 'g':g, 'g2':gp, 'h':h, 'f':f, 'e_gg_alpha':e_gg_alpha }
        mk = {'beta':beta, 'g2_alpha':gp ** alpha }
        return (pk, mk)
    
    def keygen(self, pk, mk, S):
        r = group.random()    
        g_r = (pk['g2'] ** r)    
        D = (mk['g2_alpha'] * g_r) ** (1 / mk['beta'])        
        D_j, D_j_pr = {}, {}
        for j in S:
            r_j = group.random()
            D_j[j] = g_r * (group.hash(j, G2) ** r_j)
            D_j_pr[j] = pk['g'] ** r_j        
        return { 'D':D, 'Dj':D_j, 'Djp':D_j_pr, 'S':S }
    
    def encrypt(self, pk, M, policy_str): 
        policy = util.createPolicy(policy_str)
        a_list = []; util.getAttributeList(policy, a_list)
        s = group.random()
        shares = util.calculateShares(s, policy, dict)      
        
        C = pk['h'] ** s
        C_y, C_y_pr = {}, {}
        for i in a_list:
            C_y[i] = pk['g'] ** shares[i]
            C_y_pr[i] = group.hash(i, G2) ** shares[i] 
        
        return { 'C_tilde':(pk['e_gg_alpha'] ** s) * M,
                 'C':C, 'Cy':C_y, 'Cyp':C_y_pr, 'policy':policy, 'attributes':a_list }
    
    def decrypt(self, pk, sk, ct):
        pruned_list = util.prune(ct['policy'], sk['S'])
        z = {}; util.getCoefficients(ct['policy'], z)

        A = group.init(GT, 1) 
        for i in pruned_list:
            A *= ( pair(ct['Cy'][i], sk['Dj'][i]) / pair(sk['Djp'][i], ct['Cyp'][i]) ) ** z[i]
        
        return ct['C_tilde'] / (pair(ct['C'], sk['D']) / A)
    
if __name__ == "__main__":
    groupObj = PairingGroup('a.param', verbose=True)
    
    cpabe = CPabe_BSW07(groupObj)
    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'
    print("Attributes =>", attrs); print("Policy =>", access_policy)
    
    (pk, mk) = cpabe.setup()
    
    sk = cpabe.keygen(pk, mk, attrs)
   
    rand_msg = groupObj.random(GT) 
    print("msg =>", rand_msg)
    ct = cpabe.encrypt(pk, rand_msg, access_policy)
    print("\n\nCiphertext...\n")
    groupObj.debug(ct) 
    
    rec_msg = cpabe.decrypt(pk, sk, ct)
    print("\n\nDecrypt...\n")
    print("Rec msg =>", rec_msg)

    if rand_msg == rec_msg:
        print("Successful Decryption!!!")
    else:
        print("FAILED Decryption!!!")
    
