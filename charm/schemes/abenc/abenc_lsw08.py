'''
Allison Lewko, Amit Sahai and Brent Waters (Pairing-based)
 
| From: "Revocation Systems with Very Small Private Keys", Large Universe Construction
| Published in: IEEE S&P 2010
| Available from: http://eprint.iacr.org/2008/309.pdf
| Notes: 

* type:           key-policy attribute-based encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:            12/2010
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import ABEnc

debug = False
class KPabe(ABEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> group = PairingGroup('MNT224')
    >>> kpabe = KPabe(group)
    >>> (master_public_key, master_key) = kpabe.setup()
    >>> policy = '(ONE or THREE) and (THREE or TWO)'
    >>> attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]
    >>> secret_key = kpabe.keygen(master_public_key, master_key, policy)
    >>> msg=group.random(GT)
    >>> cipher_text = kpabe.encrypt(master_public_key, msg, attributes)
    >>> decrypted_msg = kpabe.decrypt(cipher_text, secret_key)
    >>> decrypted_msg == msg
    True
    """

    def __init__(self, groupObj, verbose=False):
        ABEnc.__init__(self)
        global group, util
        group = groupObj
        util = SecretUtil(group, verbose)        

    def setup(self):
        # pick random exponents
        alpha1, alpha2, b = group.random(ZR), group.random(ZR), group.random(ZR)
        
        alpha = alpha1 * alpha2
        g_G1, g_G2 = group.random(G1), group.random(G2) # PK 1,2        
        h_G1, h_G2 = group.random(G1), group.random(G2) # PK 3
        g1b = g_G1 ** b        
        e_gg_alpha = pair(g_G1,g_G2) ** alpha
        
        #public parameters # 'g_G2^b':(g_G2 ** b), 'g_G2^b2':g_G2 ** (b * b),
        pk = { 'g_G1':g_G1, 'g_G2':g_G2, 'g_G1_b':g1b,
              'g_G1_b2':g1b ** b, 'h_G1_b':h_G1 ** b, 'e(gg)_alpha':e_gg_alpha }
        #secret parameters
        mk = { 'alpha1':alpha1, 'alpha2':alpha2, 'b':b, 'h_G1':h_G1, 'h_G2':h_G2 }
        return (pk, mk)
    
    def keygen(self, pk, mk, policy_str):
        policy = util.createPolicy(policy_str)
        attr_list = util.getAttributeList(policy)
        
        s = mk['alpha1']; secret = s
        shares = util.calculateSharesDict(secret, policy)
        
        D = { 'policy': policy_str }
        for x in attr_list:
            y = util.strip_index(x)
            d = []; r = group.random(ZR)
            if not self.negatedAttr(x): # meaning positive
                d.append((pk['g_G1'] ** (mk['alpha2'] * shares[x])) * (group.hash(y, G1) ** r))   # compute D1 for attribute x
                d.append((pk['g_G2'] ** r))  # compute D2 for attribute x
            #else:
                #d.append((pk['g2_G1'] ** shares[x]) * (pk['g_G1_b2'] ** r)) # compute D3
                #d.append((pk['g_G1_b'] ** (r * group.hash(x))) * (pk['h_G1'] ** r)) # compute D4
                #d.append(pk['g_G1'] ** -r) # compute D5
            D[x] = d
        if debug: print("Access Policy for key: %s" % policy)
        if debug: print("Attribute list: %s" % attr_list)
        return D
    
    def negatedAttr(self, attribute):
        if type(attribute) != str: attr = attribute.getAttribute()
        else: attr = attribute
        if attr[0] == '!':
            if debug: print("Checking... => %s" % attr[0])
            return True
        return False    
    
    def encrypt(self, pk, M, attr_list):   
        if debug: print('Encryption Algorithm...')    
        # s will hold secret
        t = group.init(ZR, 0)
        s = group.random(); sx = [s]
        for i in range(len(attr_list)):
            sx.append(group.random(ZR))
            sx[0] -= sx[i]
            
        E3 = {}
        #E4, E5 = {}, {}
        for i in range(len(attr_list)):
            attr = attr_list[i]
            E3[attr] = group.hash(attr, G1) ** s
            #E4[attr] = pk['g_G1_b'] ** sx[i]
            #E5[attr] = (pk['g_G1_b2'] ** (sx[i] * group.hash(attr))) * (pk['h_G1_b'] ** sx[i])
        
        E1 = (pk['e(gg)_alpha'] ** s) * M
        E2 = pk['g_G2'] ** s
        return {'E1':E1, 'E2':E2, 'E3':E3, 'attributes':attr_list }
    
    def decrypt(self, E, D):
        policy = util.createPolicy(D['policy'])
        attrs = util.prune(policy, E['attributes'])
        if attrs == False:
            return False              
        coeff = util.getCoefficients(policy)
        
        Z = {}; prodT = 1
        for i in range(len(attrs)):
            x = attrs[i].getAttribute()
            y = attrs[i].getAttributeAndIndex()
            if not self.negatedAttr(y):
                 Z[y] = pair(D[y][0], E['E2']) / pair(E['E3'][x], D[y][1])
                 prodT *= Z[y] ** coeff[y] 
       
        return E['E1'] / prodT 

def main():
    groupObj = PairingGroup('MNT224')
    kpabe = KPabe(groupObj)

    (pk, mk) = kpabe.setup()

    policy = '(ONE or THREE) and (THREE or TWO)'
    attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]
    msg = groupObj.random(GT)

    mykey = kpabe.keygen(pk, mk, policy)

    if debug: print("Encrypt under these attributes: ", attributes)
    ciphertext = kpabe.encrypt(pk, msg, attributes)
    if debug: print(ciphertext)

    rec_msg = kpabe.decrypt(ciphertext, mykey)

    assert msg == rec_msg
    if debug: print("Successful Decryption!")

if __name__ == "__main__":
    debug = True
    main()
