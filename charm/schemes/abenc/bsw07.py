'''
John Bethencourt, Amit Sahai, Brent Waters

| From: "Ciphertext-Policy Attribute-Based Encryption"
| Published in: 2007
| Available from: https://doi.org/10.1109/SP.2007.11
| Notes: Implemented an asymmetric version of the scheme in Section 4.2
| Security Assumption: Generic group model
|
| type:           ciphertext-policy attribute-based encryption
| setting:        Pairing

:Authors:         Shashank Agrawal
:Date:            05/2016
'''

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.ABEnc import ABEnc
from charm.toolbox.msp import MSP

debug = False


class BSW07(ABEnc):

    def __init__(self, group_obj, verbose=False):
        ABEnc.__init__(self)
        self.group = group_obj
        self.util = MSP(self.group, verbose)

    def setup(self):
        """
        Generates public key and master secret key.
        """

        if debug:
            print('Setup algorithm:\n')

        # pick a random element each from two source groups
        g1 = self.group.random(G1)
        g2 = self.group.random(G2)

        beta = self.group.random(ZR)
        h = g2 ** beta
        f = g2 ** (1/beta)

        alpha = self.group.random(ZR)
        g1_alpha = g1 ** alpha
        e_gg_alpha = pair (g1_alpha, g2)

        pk = {'g1': g1, 'g2': g2, 'h': h, 'f': f, 'e_gg_alpha': e_gg_alpha}
        msk = {'beta': beta, 'g1_alpha': g1_alpha}
        return pk, msk

    def keygen(self, pk, msk, attr_list):
        """
        Generate a key for a set of attributes.
        """

        if debug:
            print('Key generation algorithm:\n')

        r = self.group.random(ZR)
        g1_r = pk['g1'] ** r
        beta_inverse = 1 / msk['beta']
        k0 = (msk['g1_alpha'] * g1_r) ** beta_inverse

        K = {}
        for attr in attr_list:
            r_attr = self.group.random(ZR)
            k_attr1 = g1_r * (self.group.hash(str(attr), G1) ** r_attr)
            k_attr2 = pk['g2'] ** r_attr
            K[attr] = (k_attr1, k_attr2)

        return {'attr_list': attr_list, 'k0': k0, 'K': K}

    def encrypt(self, pk, msg, policy_str):
        """
         Encrypt a message M under a policy string.
        """

        if debug:
            print('Encryption algorithm:\n')

        policy = self.util.createPolicy(policy_str)
        mono_span_prog = self.util.convert_policy_to_msp(policy)
        num_cols = self.util.len_longest_row

        # pick randomness
        u = []
        for i in range(num_cols):
            rand = self.group.random(ZR)
            u.append(rand)
        s = u[0]    # shared secret

        c0 = pk['h'] ** s

        C = {}
        for attr, row in mono_span_prog.items():
            cols = len(row)
            sum = 0
            for i in range(cols):
                sum += row[i] * u[i]
            attr_stripped = self.util.strip_index(attr)
            c_i1 = pk['g2'] ** sum
            c_i2 = self.group.hash(str(attr_stripped), G1) ** sum
            C[attr] = (c_i1, c_i2)

        c_m = (pk['e_gg_alpha'] ** s) * msg

        return {'policy': policy, 'c0': c0, 'C': C, 'c_m': c_m}

    def decrypt(self, pk, ctxt, key):
        """
         Decrypt ciphertext ctxt with key key.
        """

        if debug:
            print('Decryption algorithm:\n')

        nodes = self.util.prune(ctxt['policy'], key['attr_list'])
        if not nodes:
            print ("Policy not satisfied.")
            return None

        prod = 1

        for node in nodes:
            attr = node.getAttributeAndIndex()
            attr_stripped = self.util.strip_index(attr)
            (c_attr1, c_attr2) = ctxt['C'][attr]
            (k_attr1, k_attr2) = key['K'][attr_stripped]
            prod *= (pair(k_attr1, c_attr1) / pair(c_attr2, k_attr2))

        return (ctxt['c_m'] * prod) / (pair(key['k0'], ctxt['c0']))
