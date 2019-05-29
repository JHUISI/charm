"""
Yanjiang Yang, Joseph K Liu, Kaitai Liang, Kim Kwang Raymond Choo, Jianying Zhou

| From: "Extended Proxy-Assisted Approach: Achieving Revocable Fine-Grained Encryption of Cloud Data".
| Published in: 2015
| Available from:
| Notes: adapted from BSW07
| Security Assumption:
|
| type:           ciphertext-policy attribute-based encryption
| setting:

:Authors:    Douglas Hellinger
:Date:       11/2018
"""

from charm.toolbox.ABEnc import ABEnc, Output
from charm.toolbox.pairinggroup import ZR, G1, G2, GT, pair
from charm.toolbox.schemebase import Input
from charm.toolbox.secretutil import SecretUtil

# type annotations
params_t = {'g': G1, 'g2': G2, 'h': G1, 'e_gg_alpha': GT}
msk_t = {'beta': ZR, 'alpha': ZR}
pku_t = G2
sku_t = ZR
pxku_t = {'k': G2, 'k_prime': G2, 'k_attrs': dict}
ct_t = {'policy_str': str,
        'C': GT,
        'C_prime': G1,
        'C_prime_prime': G1,
        'c_attrs': dict
        }
v_t = {'C': GT,
       'e_term': GT}


class YLLC15(ABEnc):
    """
    Possibly a subclass of BSW07?
    """
    def __init__(self, group):
        ABEnc.__init__(self)
        self.group = group
        self.util = SecretUtil(self.group)

    @Output(params_t, msk_t)
    def setup(self):
        g, gp = self.group.random(G1), self.group.random(G2)
        alpha, beta = self.group.random(ZR), self.group.random(ZR)
        # initialize pre-processing for generators
        g.initPP()
        gp.initPP()

        h = g ** beta
        e_gg_alpha = pair(g, gp ** alpha)

        params = {'g': g, 'g2': gp, 'h': h, 'e_gg_alpha': e_gg_alpha}
        msk = {'beta': beta, 'alpha': alpha}
        return params, msk

    @Input(params_t)
    @Output(pku_t, sku_t)
    def ukgen(self, params):
        g2 = params['g2']
        x = self.group.random(ZR)
        pku = g2 ** x
        sku = x
        return pku, sku

    @Input(params_t, msk_t, pku_t, pku_t, [str])
    # @Output(pxku_t)
    def proxy_keygen(self, params, msk, pkcs, pku, attribute_list):
        """
        attributes specified in the `attribute_list` are converted to uppercase
        """
        r1 = self.group.random(ZR)
        r2 = self.group.random(ZR)
        g = params['g']
        g2 = params['g2']

        k = ((pkcs ** r1) * (pku ** msk['alpha']) * (g2 ** r2)) ** ~msk['beta']
        k_prime = g2 ** r1
        k_attrs = {}
        for attr in attribute_list:
            attr_caps = attr.upper()
            r_attr = self.group.random(ZR)
            k_attr1 = (g2 ** r2) * (self.group.hash(str(attr_caps), G2) ** r_attr)
            k_attr2 = g ** r_attr
            k_attrs[attr_caps] = (k_attr1, k_attr2)

        proxy_key_user = {'k': k, 'k_prime': k_prime, 'k_attrs': k_attrs}
        return proxy_key_user

    @Input(params_t, GT, str)
    # @Output(ct_t)
    def encrypt(self, params, msg, policy_str):
        """
         Encrypt a message M under a policy string.

         attributes specified in policy_str are converted to uppercase
         policy_str must use parentheses e.g. (A) and (B)
        """
        policy = self.util.createPolicy(policy_str)
        s = self.group.random(ZR)
        shares = self.util.calculateSharesDict(s, policy)

        C = (params['e_gg_alpha'] ** s) * msg
        c_prime = params['h'] ** s
        c_prime_prime = params['g'] ** s

        c_attrs = {}
        for attr in shares.keys():
            attr_stripped = self.util.strip_index(attr)
            c_i1 = params['g'] ** shares[attr]
            c_i2 = self.group.hash(attr_stripped, G1) ** shares[attr]
            c_attrs[attr] = (c_i1, c_i2)

        ciphertext = {'policy_str': policy_str,
                      'C': C,
                      'C_prime': c_prime,
                      'C_prime_prime': c_prime_prime,
                      'c_attrs': c_attrs}
        return ciphertext

    # @Input(sku_t, pxku_t, ct_t)
    @Output(v_t)
    def proxy_decrypt(self, skcs, proxy_key_user, ciphertext):
        policy_root_node = ciphertext['policy_str']
        k = proxy_key_user['k']
        k_prime = proxy_key_user['k_prime']
        c_prime = ciphertext['C_prime']
        c_prime_prime = ciphertext['C_prime_prime']
        c_attrs = ciphertext['c_attrs']
        k_attrs = proxy_key_user['k_attrs']

        policy = self.util.createPolicy(policy_root_node)
        attributes = proxy_key_user['k_attrs'].keys()
        pruned_list = self.util.prune(policy, attributes)
        if not pruned_list:
            return None
        z = self.util.getCoefficients(policy)
        # reconstitute the policy random secret (A) which was used to encrypt the message
        A = 1
        for i in pruned_list:
            attr_idx = i.getAttributeAndIndex()
            attr = i.getAttribute()
            A *= (pair(c_attrs[attr_idx][0], k_attrs[attr][0]) / pair(k_attrs[attr][1], c_attrs[attr_idx][1])) ** z[attr_idx]

        e_k_c_prime = pair(k, c_prime)
        denominator = (pair(k_prime, c_prime_prime) ** skcs) * A
        encrypted_element_for_user_pkenc_scheme = e_k_c_prime / denominator

        intermediate_value = {'C': ciphertext['C'],
                              'e_term': encrypted_element_for_user_pkenc_scheme}

        return intermediate_value

    @Input(type(None), sku_t, v_t)
    @Output(GT)
    def decrypt(self, params, sku, intermediate_value):
        """
        :param params: Not required - pass None instead. For interface compatibility only.
        :param sku: the secret key of the user as generated by `ukgen()`.
        :param intermediate_value: the partially decrypted ciphertext returned by `proxy_decrypt()`.
        :return: the plaintext message
        """
        ciphertext = intermediate_value['C']
        e_term = intermediate_value['e_term']
        denominator = e_term ** (sku ** -1)
        msg = ciphertext / denominator
        return msg
