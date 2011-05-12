# Allison Lewko, Amit Sahai and Brent Waters (Pairing-based)
# 
# From: "Revocation Systems with Very Small Private Keys", Large Universe Construction
# Published in: IEEE S&P 2010
# Available from: http://eprint.iacr.org/2009/309.pdf
# Notes: 

# type:           key-policy attribute-based encryption (public key)
# setting:        Pairing
#
# Implementer:    J Ayo Akinyele
# Date:            12/2010
from toolbox.pairinggroup import *
from toolbox.secretutil import *
from toolbox.policytree import *
from toolbox.ABEnc import *

class KPabe(ABEnc):
    def __init__(self, groupObj, verbose=False):
        ABEnc.__init__(self)
        global group, util
        group = groupObj
        util = SecretUtil(group.Pairing, verbose)        
        self.parser = PolicyParser()

    def setup(self):
        # pick random exponents
        alpha1, alpha2, b = group.random(), group.random(), group.random()
        
        alpha = alpha1 * alpha2
        g_G1, g_G2 = group.random(G1), group.random(G2) # PK 1,2        
        h_G1, h_G2 = group.random(G1), group.random(G2) # PK 3
        g1b = g_G1 ** b        
        e_gg_alpha = pair(g_G1,g_G2) ** alpha
        
        #public parameters # 'g_G2^b':(g_G2 ** b), 'g_G2^b2':g_G2 ** (b * b),
        pk = { 'g_G1':g_G1, 'g_G2':g_G2, 'g_G1^b':g1b,
              'g_G1^b2':g1b ** b, 'h_G1^b':h_G1 ** b, 'e(gg)^alpha':e_gg_alpha }
        #secret parameters
        mk = { 'alpha1':alpha1, 'alpha2':alpha2, 'b':b, 'h_G1':h_G1, 'h_G2':h_G2 }
        return (pk, mk)
    
    def keygen(self, pk, mk, policy_str):
        #policy = self.parser.parse(policy_str)
        policy = util.createPolicy(policy_str)
        attr_list = []; util.getAttributeList(policy, attr_list)
        
        s = mk['alpha1']; secret = s
        shares = util.calculateShares(secret, policy, dict)
        
        D = {}
        for x in attr_list:
            d = []; r = group.random()
            if not self.negatedAttr(x): # meaning positive
                d.append((pk['g_G1'] ** (mk['alpha2'] * shares[x])) * (group.hash(x, G1) ** r))   # compute D1 for attribute x
                d.append((pk['g_G2'] ** r))  # compute D2 for attribute x
            #else:
            #    d.append((pk['g2_G1'] ** shares[x]) * (pk['g_G1^b2'] ** r)) # compute D3
            #    d.append((pk['g_G1^b'] ** (r * H(x, 'Zr'))) * (mk['h_G1'] ** r)) # compute D4 (not quite right)
            #    d.append(pk['g_G2'] ** -r)
            D[x] = d
        print("Policy: %s" % policy)
        print("Attribute list: %s" % attr_list)
        D['policy'] = policy
        return D
    
    def negatedAttr(self, attribute):
        if attribute[0] == '!':
            print("Checking... => %s" % attribute[0])
            return True
        return False    
    
    def encrypt(self, pk, M, attr_list):   
        print('Encryption Algorithm...')    
        # s will hold secret
        t = group.init(ZR, 0)
        s = group.random(); sx = [s]
        for i in range(1, len(attr_list)):
            sx.append(group.random())
            sx[0] -= sx[i]
        
        # compute E3
        E3 = [group.hash(x, G1) ** s for x in attr_list]
        # compute E4
        E4 = [pk['g_G1^b'] ** sx[i] for i in range(len(attr_list))]
        E5 = [(pk['g_G1^b2'] ** (sx[i] * group.hash(attr_list[i]))) * (pk['h_G1^b'] ** sx[i]) for i in range(len(attr_list))]                
        return {'E1':(pk['e(gg)^alpha'] ** s) * M, 'E2':pk['g_G2'] ** s, 'E3':E3, 'E4':E4, 'E5':E5, 'attributes':attr_list }
    
    def decrypt(self, E, D):
        attrs = E['attributes']
        policy = D['policy']
        coeff = {}; util.getCoefficients(policy, coeff)
        
        Z = {}; prodT = group.init(GT, 1)
        for i in range(len(attrs)):
            x = attrs[i]
            #print("Coeff[%s] = %s" % (x, coeff[x]))
            if not self.negatedAttr(x):
                 z = pair(D[x][0], E['E2']) / pair(E['E3'][i], D[x][1])
            Z[x] = z; prodT *= Z[x] ** coeff[x]
            #print('Z val for %s: %s\n' % (x, Z[x]))
       
        return E['E1'] / prodT 
    
if __name__ == "__main__":
    groupObj = PairingGroup('d224.param')
    kpabe = KPabe(groupObj)
    
    (pk, mk) = kpabe.setup()
    
    policy = '((ONE or TWO) and THREE)'
    attributes = [ 'ONE', 'THREE' ]
    msg = groupObj.random(GT)   
 
    mykey = kpabe.keygen(pk, mk, policy)
    
    ciphertext = kpabe.encrypt(pk, msg, attributes)
    
    rec_msg = kpabe.decrypt(ciphertext, mykey)
   
    if msg == rec_msg: 
       print("Successful Decryption!")
    else:
       print("FAILED Decryption!!!")
    
