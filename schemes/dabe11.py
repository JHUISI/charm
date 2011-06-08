# Lewko-Waters Decentralized Attribute-Based Encryption 
# 
# ﻿Lewko, Allison, and Brent Waters, "Decentralizing Attribute-Based Encryption.", Appendix D
# Published in: Eurocrypt 2011
# Available from: http://eprint.iacr.org/2010/351.pdf
#
# type:           encryption (identity-based)
# setting:        bilinear groups (asymmetric)
#
# Implementer:    Gary Belvin
# Date:           06/2011 

from toolbox.pairinggroup import *
from toolbox.secretutil import *
from toolbox.ABEnc import *

class Dabe(ABEnc):
    '''
    Decentralized Attribute-Based Encryption by Lewko and Waters
    '''

    def __init__(self, groupObj):
        ABEnc.__init__(self)
        global util, group
        util = SecretUtil(groupObj.Pairing, verbose=False)  #Create Secret Sharing Scheme
        group = groupObj    #Prime order group                  
   
    def setup(self):
        '''Global Setup'''
        #In global setup, a bilinear group G of prime order p is chosen
        #The gloabl public parameters, GP and p, and a generator g of G. A random oracle H maps global identites GID to elements of G
    
        #group contains 
        #H = group.hash     # The oracle that maps global identites GID onto elements of G
        #the prime order p is contained somewhere within the group object
        g1, g2 = group.random(G1), group.random(G2)
        GP = {'g1': g1, 'g2': g2, 'H': g1.H}

        return GP

    def auth_setup(self, GP, attributes):
        '''Authority Setup for a given set of attributes'''
        #For each attribute i belonging to the authority, the authority chooses two random exponents, 
        #alpha_i, y_i and publishes PK={e(g,g)^alpha_i, g^y_i} for each attribute 
        #it keeps SK = {alpha_i, y_i} as its secret key
        SK = {} #dictionary of {s: {alpha_i, y_i}} 
        PK = {} #dictionary of {s: {e(g,g)^alpha_i, g^y}}
        for i in attributes :
            #TODO: Is ZR an appropriate choice for a random element in Zp?
            alpha_i, y_i = group.random(), group.random()
            e_gg_alpha_i = pair(GP['g1'],GP['g2']) ** alpha_i
            g_y_i = GP['g2'] ** y_i
            SK[i] = {'alpha_i': alpha_i, 'y_i': y_i}
            PK[i] = {'e(gg)^alpha_i': e_gg_alpha_i, 'g^y_i': g_y_i}
        
        return (SK, PK)
        
    def keygen(self, gp, sk, gid):
        '''Create a key for GID on attribute i belonging to authority sk'''
        #sk is the tuple for the specific attribute {'alpha_i': , 'y_i'}
        #To create a key for GID for attribute i belonging to an authority, the authority computes K_{i,GID} = g^alpha_i * H(GID)^y_
    
        K = (gp['g1'] ** sk['alpha_i']) * (gp['H'](gid) ** sk['y_i'])
        print("H(GID): %s" % gp['H'](gid))
        return {'k': K, 'gid': gid}

    def encrypt(self, pk, gp, M, policy_str):
        '''Encrypt'''
        #M is a group element
        #pk is a dictionary with all the attributes of all authorities put together.
        #This is legal because no attribute can be shared by more than one authority
        #{i: {'e(gg)^alpha_i: , 'g^y_i'}
        s = group.random()
        w = group.init(ZR, 0)
        C0 = M * pair(gp['g1'], gp['g2']) ** s
        print("e(gg)^s: %s" % pair(gp['g1'], gp['g2']) ** s )
        C1, C2, C3 = {}, {}, {}
        C4 = {}
        
        #Parse the policy string into a tree
        plist = []
        policy = util.createPolicy(policy_str)
        sshares = util.calculateShares(s, policy, list) 
        wshares = util.calculateShares(w, policy, list) 
        util.getAttributeList(policy, plist)
    
        w_shares = dict([(x[0], x[1]) for x in wshares])
    
        for x in sshares:
            attr, s_share = x[0], x[1]
            w_share = w_shares[attr]
            r_x = group.random()
            C1[attr] = (pair(gp['g1'],gp['g2']) ** s_share) * (pk[attr]['e(gg)^alpha_i'] ** r_x)
            C2[attr] = gp['g2'] ** r_x
            C3[attr] = (pk[attr]['g^y_i'] ** r_x) * (gp['g2'] ** w_share)
            #C4[attr] = pair(gp['g1'], gp['g2']) ** s_share
            C4[attr] = (pair(gp['g1'], gp['g2']) ** s_share) * (pair(gp['H']('bob'),gp['g2']) ** w_share)
        
        return { 'C0':C0, 'C1':C1, 'C2':C2, 'C3':C3, 'C4':C4, 'policy':policy, 'attributes':plist }

    def decrypt(self, gp, sk, ct):
        #sk is a dictionary of attribute private keys {attr: { xxx , xxx }} 
        #ct is ciphertext
    
        pruned = util.prune(ct['policy'], sk['attributes'])
        coeffs = {}; util.getCoefficients(ct['policy'], coeffs)
    
        h_gid = gp['H'](sk['gid'])  #find H(GID)
        print("H(GID): %s" % h_gid)
        egg_s = group.init(GT, 1)
        temp  = group.init(GT, 1)
        for x in pruned:
            num = ct['C1'][x] * pair(h_gid, ct['C3'][x])
            dem = pair(sk[x]['k'], ct['C2'][x])
            egg_s *= ( (num / dem) ** coeffs[x] )
            #temp  *= ct['C4'][x] ** coeffs[x]
            print("temp: %s" % ct['C4'][x])
            print("n/d : %s" % (num/dem))
            #print("coeffs[%s]: %s" % (x, coeffs[x]))
    
        print("e(gg)^s: %s" % egg_s)
        return ct['C0'] / egg_s

if __name__ == '__main__':
    groupObj = PairingGroup('a.param', verbose=True)

    dabe = Dabe(groupObj)
    GP = dabe.setup()
    
    gid = "bob"
    auth_attrs= ['ONE', 'TWO', 'THREE', 'FOUR']
    usr_attrs = ['THREE', 'ONE', 'TWO']
    policy = '((one or three) and (TWO or FOUR))'
    m = groupObj.random(GT)

    print('Acces Policy: %s' % policy)
    print('User credential list: %s' % usr_attrs)

    (SK, PK) = dabe.auth_setup(GP, auth_attrs)

    #Get keys for each attribute
    K = dict([(i, dabe.keygen(GP, SK[i], gid)) for i in usr_attrs])
    K['gid'] = gid
    K['attributes'] = usr_attrs
    #print("\nSecret key: %s" % K)
    #groupObj.debug(K)

    CT = dabe.encrypt(PK, GP, m, policy)
    print("\nCiphertext...")
    #groupObj.debug(CT)    
    
    orig_m = dabe.decrypt(GP, K, CT)
   
    if m == orig_m: 
        print('Successful Decryption!')
    else:
        print('FAILED Decryption!!!')
             
