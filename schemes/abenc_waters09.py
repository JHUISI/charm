'''
Brent Waters (Pairing-based)
 
| From: "Ciphertext-Policy Attribute-Based Encryption: An Expressive, Efficient, and Provably Secure Realization", Appendix C.
| Published in: 2008
| Available from: http://eprint.iacr.org/2008/290.pdf
| Notes: Security Assumption: parallel q-DBDHE. The sole disadvantage of this scheme is the high number of pairings
| that must be computed during the decryption process (2 + N) for N attributes mathing in the key.

* type:            ciphertext-policy attribute-based encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:            11/2010
'''
from toolbox.pairinggroup import *
from toolbox.secretutil import *
from toolbox.ABEnc import *

debug = False
class CPabe(ABEnc):
    def __init__(self, groupObj):
        ABEnc.__init__(self)
        global util, group
        util = SecretUtil(groupObj.Pairing, groupObj._verbose)
        group = groupObj
                        
    def setup(self):
        g1, g2 = group.random(G1), group.random(G2)
        alpha, a = group.random(), group.random()        
        e_gg_alpha = pair(g1,g2) ** alpha
        msk = {'g1^alpha':g1 ** alpha, 'g2^alpha':g2 ** alpha}        
        pk = {'g1':g1, 'g2':g2, 'e(gg)^alpha':e_gg_alpha, 'g1^a':g1 ** a, 'g2^a':g2 ** a}
        return (msk, pk)
    
    def keygen(self, pk, msk, attributes):
        t = group.random()
        K = msk['g2^alpha'] * (pk['g2^a'] ** t)
        L = pk['g2'] ** t
        k_x = [group.hash(s, G1) ** t for s in attributes]
        
        K_x = {}
        for i in range(0, len(k_x)):
            K_x[ attributes[i] ] = k_x[i]    
        
        key = { 'K':K, 'L':L, 'K_x':K_x, 'attributes':attributes }
        return key
    
    def encrypt(self, pk, M, policy_str):
        # Extract the attributes as a list
        policy = util.createPolicy(policy_str)
        p_list = []
        util.getAttributeList(policy, p_list)
        s = group.random()
        C_tilde = (pk['e(gg)^alpha'] ** s) * M
        C_0 = pk['g1'] ** s
        C, D = {}, {}
        secret = s
        shares = util.calculateShares(secret, policy, list)

        # ciphertext
        for i in range(len(p_list)):
            r = group.random()
            if shares[i][0] == p_list[i]:
               C[ p_list[i] ] = ((pk['g1^a'] ** shares[i][1]) * (group.hash(p_list[i], G1) ** -r))
               D[ p_list[i] ] = (pk['g2'] ** r)
        
        if debug: print("SessionKey: %s" % C_tilde)
        return { 'C0':C_0, 'C':C, 'D':D , 'C_tilde':C_tilde, 'policy':policy, 'attribute':p_list }
    
    def decrypt(self, sk, ct):
        pruned = util.prune(ct['policy'], sk['attributes'])
        coeffs = {}; util.getCoefficients(ct['policy'], coeffs)
        numerator = pair(ct['C0'], sk['K'])
        
        # create list for attributes in order...
        k_x, w_i = {}, {}
        for j in pruned:
            k_x[ j ] = sk['K_x'][j]
            w_i[ j ] = coeffs[j]
            #print('Attribute %s: coeff=%s, k_x=%s' % (j, w_i[j], k_x[j]))
            
        C, D = ct['C'], ct['D']
        denominator = group.init(GT, 1)
        for i in pruned:
            denominator *= ( pair(C[i] ** w_i[i], sk['L']) * pair(k_x[i] ** w_i[i], D[i]) )   
        return ct['C_tilde'] / (numerator / denominator)

def main():
    #Get the eliptic curve with the bilinear mapping feature needed.
    groupObj = PairingGroup('../param/a.param', verbose=True)

    cpabe = CPabe(groupObj)
    (msk, pk) = cpabe.setup()
    policy = '((one or three) and (TWO or FOUR))'
    attr_list = ['THREE', 'ONE', 'TWO']

    if debug: print('Acces Policy: %s' % policy)
    if debug: print('User credential list: %s' % attr_list)
    m = groupObj.random(GT)
    
    cpkey = cpabe.keygen(pk, msk, attr_list)
    if debug: print("\nSecret key: %s" % attr_list)
    if debug:groupObj.debug(cpkey)
    cipher = cpabe.encrypt(pk, m, policy)

    if debug: print("\nCiphertext...")
    if debug:groupObj.debug(cipher)    
    orig_m = cpabe.decrypt(cpkey, cipher)
   
    assert m == orig_m, 'FAILED Decryption!!!' 
    if debug: print('Successful Decryption!')    
    del groupObj
    
if __name__ == '__main__':
    debug = True
    main()