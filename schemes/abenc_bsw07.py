'''
John Bethencourt, Brent Waters (Pairing-based)
 
| From: "Ciphertext-Policy Attribute-Based Encryption".
| Published in: 2007
| Available from: 
| Notes: 
| Security Assumption: 
|
| type:           ciphertext-policy attribute-based encryption (public key)
| setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:            04/2011
'''
from toolbox.pairinggroup import *
from toolbox.secretutil import SecretUtil
from toolbox.ABEnc import ABEnc

# type annotations
pk_t = { 'g':G1, 'g2':G2, 'h':G1, 'f':G1, 'e_gg_alpha':GT }
mk_t = {'beta':ZR, 'g2_alpha':G2 }
sk_t = { 'D':G2, 'Dj':G2, 'Djp':G1, 'S':str }
ct_t = { 'C_tilde':GT, 'C':G1, 'Cy':G1, 'Cyp':G2 }

debug = False
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
    
    def keygen(self, pk: pk_t, mk: mk_t, S: str) -> sk_t:
        r = group.random() 
        g_r = (pk['g2'] ** r)    
        D = (mk['g2_alpha'] * g_r) ** (1 / mk['beta'])        
        D_j, D_j_pr = {}, {}
        for j in S:
            r_j = group.random()
            D_j[j] = g_r * (group.hash(j, G2) ** r_j)
            D_j_pr[j] = pk['g'] ** r_j
        return { 'D':D, 'Dj':D_j, 'Djp':D_j_pr, 'S':S }
    
    def encrypt(self, pk: pk_t, M: GT, policy_str : str) -> ct_t: 
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
    
    def decrypt(self, pk: pk_t, sk: sk_t, ct: ct_t) -> GT:
        pruned_list = util.prune(ct['policy'], sk['S'])
        z = {}; util.getCoefficients(ct['policy'], z)

        A = group.init(GT, 1) 
        for i in pruned_list:
            A *= ( pair(ct['Cy'][i], sk['Dj'][i]) / pair(sk['Djp'][i], ct['Cyp'][i]) ) ** z[i]
        
        return ct['C_tilde'] / (pair(ct['C'], sk['D']) / A)

def main():
    groupObj = PairingGroup('../param/a.param')
    
    cpabe = CPabe_BSW07(groupObj)
    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'
    if debug: 
        print("Attributes =>", attrs); print("Policy =>", access_policy)
    
    (pk, mk) = cpabe.setup()
    
    sk = cpabe.keygen(pk, mk, attrs)
   
    rand_msg = groupObj.random(GT) 
    if debug: print("msg =>", rand_msg)
    ct = cpabe.encrypt(pk, rand_msg, access_policy)
    if debug: print("\n\nCiphertext...\n")
    groupObj.debug(ct) 
    
    rec_msg = cpabe.decrypt(pk, sk, ct)
    if debug: print("\n\nDecrypt...\n")
    if debug: print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    if debug: print("Successful Decryption!!!")
    
if __name__ == "__main__":
    debug = True
    main()
    
