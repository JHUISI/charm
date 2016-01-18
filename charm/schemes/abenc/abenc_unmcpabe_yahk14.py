'''
Yamada, Attrapadung, Hanaoka, Kunihiro

| From: "A Framework and Compact Constructions for Non-monotonic Attribute-Based Encryption"
| Published in:  Public-Key Cryptography--PKC 2014
| Pages: 275--292
| Available from: http://eprint.iacr.org/2014/181 Sec. 7
| Notes:

* type:          attribute-based encryption (public key)
* setting:       bilinear pairing group of prime order
* assumption:    complex q-type assumption

:Authors:        al, artjomb
:Date:          07/15
'''

from charm.toolbox.pairinggroup import *
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import *


debug = False
class CPABE_YAHK14(ABEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
    >>> group = PairingGroup('SS512')
    >>> cpabe = CPABE_YAHK14(group)
    >>> msg = group.random(GT)
    >>> attributes = ['2', '3'] # must be integer strings
    >>> access_policy = '2 and !1' # must be integer strings
    >>> (master_public_key, master_key) = cpabe.setup()
    >>> secret_key = cpabe.keygen(master_public_key, master_key, attributes)
    >>> cipher_text = cpabe.encrypt(master_public_key, msg, access_policy)
    >>> decrypted_msg = cpabe.decrypt(master_public_key, secret_key, cipher_text)
    >>> msg == decrypted_msg
    True
    """ 
    
    def __init__(self, groupObj, verbose = False):
        ABEnc.__init__(self)
        global util, group
        group = groupObj
        util = SecretUtil(group, verbose)

    # Defining a function to pick explicit exponents in the group
    def exp(self,value):
        return group.init(ZR, value)

    def setup(self):
        g = group.random(G1) # this element can also be in G2 and then PairingGroup('MNT224') can be used
        g2, u, h, w, v = group.random(G1), group.random(G1), group.random(G1), group.random(G1), group.random(G1)
        alpha, beta = group.random( ), group.random( )#from ZR
        vDot = u ** beta
        egg = pair(g2,g)**alpha
        pp = {'g':g, 'g2':g2, 'u':u, 'h':h, 'w':w, 'v':v, 'vDot':vDot,'egg':egg}
        mk = {'g2_alpha':g2 ** alpha, 'beta': beta }
        return (pp, mk)

    def keygen(self, pp, mk, S):
        # S is a set of attributes written as STRINGS i.e. {'1', '2', '3',...}
        r = group.random( )

        D1 = mk['g2_alpha'] * (pp['w']**r)
        D2 = pp['g']**r

        vR = pp['v']**(-r)

        K1, K1Dot, K2, K2Dot = {}, {}, {}, {}
        rDotCumulative = r
        for i, idx in zip(S, range(len(S))):
            ri = group.random( )
            if idx + 1 is len(S):
                riDot = rDotCumulative
            else:
                riDot = group.random( )
                rDotCumulative -= riDot

            omega_i = self.exp(int(i))
            K1[i] = vR * (pp['u']**omega_i  * pp['h'])**ri
            K1Dot[i] = (pp['u']**(omega_i * mk['beta']) * pp['h']**mk['beta'])**riDot

            K2[i] = pp['g']**ri
            K2Dot[i] = pp['g']**(mk['beta']*riDot)
        S = [s for s in S] #Have to be an array for util.prune

        return { 'S':S, 'D1': D1, 'D2' : D2, 'K1':K1, 'K1Dot':K1Dot, 'K2':K2, 'K2Dot':K2Dot }

    def encrypt(self, pp, message, policy_str):
        s = group.random()

        policy = util.createPolicy(policy_str)
        a_list = util.getAttributeList(policy)

        shares = util.calculateSharesDict(s, policy) #These are correctly set to be exponents in Z_p

        C0 = message * (pp['egg']**s)
        C1 = pp['g']**s

        C_1, C_2, C_3 = {}, {}, {}
        for i in a_list:
            ti = group.random()
            if i[0] == '!':
                inti = util.strip_index(i[1:])
                C_1[i] = pp['w']**shares[i] * pp['vDot']**ti
            else:
                inti = util.strip_index(i)
                C_1[i] = pp['w']**shares[i] * pp['v']**ti
            
            inti = self.exp(int(inti))
            C_2[i] = (pp['u']**inti * pp['h'])**(-ti)
            C_3[i] = pp['g']**ti

            #print('The exponent is ',inti)

        return { 'Policy':policy_str, 'C0':C0, 'C1':C1, 'C_1':C_1, 'C_2':C_2, 'C_3':C_3 }

    def decrypt(self, pp, sk, ct):
        policy = util.createPolicy(ct['Policy'])
        z = util.getCoefficients(policy)

        # workaround to let the charm policy parser successfully parse the non-monotonic attributes
        a_list = util.getAttributeList(policy)
        nS = sk['S'][:]
        for att in a_list:
            if att[0] == '!' and att[1:] not in sk['S']:
                nS.append(att)

        pruned_list = util.prune(policy, nS)

        if (pruned_list == False):
            return group.init(GT,1)

        B = pair(ct['C1'], sk['D1'])
        for i in range(len(pruned_list)):
            x = pruned_list[i].getAttribute( ) #without the underscore
            y = pruned_list[i].getAttributeAndIndex( ) #with the underscore

            a = pair( ct['C_1'][x], sk['D2'])
            if x[0] == '!':
                b = group.init(GT, 1)
                inti = self.exp(int(x[1:]))
                for xj in sk['S']:
                    if xj[0] == '!':
                        intj = self.exp(int(xj[1:]))
                    else:
                        intj = self.exp(int(xj))
                    b *= ( pair( ct['C_2'][x], sk['K2Dot'][str(intj)]) * pair( ct['C_3'][x], sk['K1Dot'][str(intj)]) ) ** (1 / (inti - intj))
            else:
                b = pair( ct['C_2'][x], sk['K2'][x]) * pair( ct['C_3'][x], sk['K1'][x])
            d = - z[y]
            B *= ( a * b )**d

        return ct['C0'] / B

    def randomMessage(self):
        return group.random(GT)

def main():
    curve = 'SS512'

    groupObj = PairingGroup(curve)
    scheme = CPABE_YAHK14(groupObj)

    (pp, mk) = scheme.setup()

    testCases = [
        ( '2 and !1', [
            ({'1', '2'}, False),
            ({'1'}, False),
            ({'2'}, True),
            ({'3'}, False),
            ({'2', '3'}, True)
        ] ),
        ( '2 and 1', [
            ({'1', '2'}, True),
            ({'1'}, False),
            ({'2'}, False),
            ({'3'}, False)
        ] ),
        ( '2', [
            ({'1', '2'}, True),
            ({'1'}, False),
            ({'2'}, True)
        ] ),
        ( '!2', [
            ({'1', '2'}, False),
            ({'1'}, True),
            ({'2'}, False)
        ] ),
    ]

    for policy_str, users in testCases:
        for S, success in users:
            m = group.random(GT)
            sk = scheme.keygen(pp, mk, S)
            ct = scheme.encrypt(pp, m, policy_str)
            res = scheme.decrypt(pp, sk, ct)

            if (m == res) == success:
                print("PASS", S, '' if success else 'not', "in '" + policy_str + "'")
            else:
                print("FAIL", S, '' if success else 'not', "in '" + policy_str + "'")

    m = group.random(GT)
    sk = scheme.keygen(pp, mk, {'1', '2'})
    ct = scheme.encrypt(pp, m, '!1 and 2')
    sk['S'].remove('1')
    res = scheme.decrypt(pp, sk, ct)

    if (m == res) == False:
        print("PASS: attack failed")
    else:
        print("FAIL: attack succeeded")

if __name__ == '__main__':
    debug = True
    main()
