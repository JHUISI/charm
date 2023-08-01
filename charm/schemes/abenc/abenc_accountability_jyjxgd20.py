'''
Jiguo Li, Yichen Zhang, Jianting Ning, Xinyi Huang, Geong Sen Poh, Debang Wang (Pairing-based)

| From: "Attribute Based Encryption with Privacy Protection and Accountability for CloudIoT".
| Published in: 2020
| Available from: https://ieeexplore.ieee.org/abstract/document/9003205
| Notes: The paper presents two schemes. The first one is for CP policy hiding in Section 3, which is implemented in
         the class 'CP_Hiding_ABE' and tested in the function 'CP_policy_hiding_ABE_test'.
          The second one is CP policy hiding with accountability under the white box
          assumption, which is implemented in the class 'CP_Hiding_Accountability_ABE' and tested in the function
          'CP_policy_hiding_with_accountability_test'
| Security Assumption:
|
| type:           ciphertext-policy attribute-based encryption (public key)
| setting:        Pairing
|
| Authors:        Ahmed Bakr
| Date:           08/2023
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.ABEnc import ABEnc

from typing import Dict, List


class Attribute:
    def __init__(self, attr_name, values_list: List[str] = []):
        # Validation
        self.__validate_attribute_values_name(attr_name)
        for value_str in values_list:
            self.__validate_attribute_values_name(value_str)

        self.name = attr_name
        self.values = values_list

    @staticmethod
    def __validate_attribute_values_name(attr_value_name: str):
        assert attr_value_name.find('_') == -1, "Attribute name cannot contain an '_'"

    def add_value(self, value: str):
        self.__validate_attribute_values_name(value)  # Validation
        self.values.append(value)

    def set_values(self, values_list: List[str]):
        self.values = values_list

    def get_attribute_values_full_name(self):
        """
        Attribute values full name is in the following format: 'attrName_value'
        """
        full_names_list = []
        for value in self.values:
            full_names_list.append(self.name + "_" + value)

        return full_names_list

    @staticmethod
    def get_full_attribute_value_name(attr_name: str, value_name: str):
        Attribute.__validate_attribute_values_name(attr_name)  # Validation
        Attribute.__validate_attribute_values_name(value_name)  # Validation
        return attr_name + '_' + value_name


class CP_Hiding_ABE(ABEnc):
    """
    Cipher text policy hiding attribute based encryption (Section 3 in the paper).
    """
    def __init__(self, group_obj):
        ABEnc.__init__(self)
        self._group = group_obj
        self.attributes_dict: Dict[str, List[str]] = None

    def setup(self, attributes_dict: Dict[str, List[str]]):
        """
        System Setup algorithm. This algorithm is performed by TA.
        Inputs:
            - None
        Outputs:
            - MSK: TA's master secret key.
            - PK: Public Parameters.
        """
        self.attributes_dict = attributes_dict
        g = self._group.random(G1)
        u = self._group.random(G1)
        v = self._group.random(G1)
        h = self._group.random(G1)
        w = self._group.random(G1)

        alpha = self._group.random(ZR)

        MSK = alpha
        PK = {'g': g,
              'e_gg': pair(g, g),
              'u': u,
              'h': h,
              'w': w,
              'v': v,
              'e_gg_alpha': pair(g, g) ** alpha}
        return MSK, PK

    def key_gen(self, MSK, PK, attributes_list):
        """
        Key generation for a user based on his list of attributes. This algorithm is performed by TA.
        Inputs:
            - MSK: Master Secret Key of the TA.
            - PK: Public parameters and the public key of the TA.
            - attributes_list: List of attributes held by this user, where each attribute is in the format:
                               'attrName_value'
        Outputs:
            - SK: User's secret key.
        """
        self._validate_attributes_list(attributes_list)
        r = self._group.random(ZR)
        g = PK['g']
        w = PK['w']
        u = PK['u']
        h = PK['h']
        v = PK['v']
        alpha = MSK

        K_0 = (g ** alpha) * (w ** r)
        K_1 = g ** r
        K_2 = {}
        K_3 = {}
        for full_attr_value_name in attributes_list:
            # attr_name = full_attr_value_name.split('_')[0]
            r_i = self._group.random(ZR)
            K_i_2 = g ** r_i
            hash_attr_val_in_z_p = self._group.hash(full_attr_value_name, type=ZR)
            K_i_3 = (((u ** hash_attr_val_in_z_p) * h) ** r_i) * v ** (-r)
            K_2[full_attr_value_name] = K_i_2
            K_3[full_attr_value_name] = K_i_3
        SK = {'attributes_list': attributes_list, 'K_0': K_0, 'K_1': K_1, 'K_2': K_2, 'K_3': K_3}
        return SK

    def _validate_attributes_list(self, attributes_list):
        """
        each attribute is in the format: 'attrName_value'
        """
        for attr_value in attributes_list:
            assert attr_value.find('_') == attr_value.rfind('_') and attr_value.find('_') != -1, (
                "The format is 'attrName_value'")
            splitted_str = attr_value.split('_')
            assert len(splitted_str[0]) > 0 and len(splitted_str[1])> 0, "The format is 'attrName_value'"

    def encrypt(self, m, PK, access_policy: Dict[str, List[str]]):
        """
        Encrypt a message using an access policy. This function is performed by a data user who wants to encrypt his 
        message with an access policy. They consider only and-gates in their policy.
        Note: The access policy is hidden into the ciphertext.
        Inputs:
            - PK: Public parameters and the public key of the TA.
            - m: Message to be encrypted in G_T.
            - access_policy: Access policy that will be used to encrypt the message. It has to be and gated policy,
                             which means that each attribute can have only one value.
        Outputs:
            - CT: Cipher text. 
        """
        g = PK['g']
        w = PK['w']
        v = PK['v']
        u = PK['u']
        h = PK['h']
        s = self._group.random(ZR)
        s_n = s
        access_policy_len = len(access_policy)
        C = m * PK['e_gg_alpha'] ** s
        C_1 = g ** s
        C_i_1 = {}
        C_i_3 = {}
        C_i_2 = {}
        for idx, attr_name in enumerate(access_policy):
            if idx < access_policy_len - 1:
                s_i = self._group.random(ZR)
                s_n = s_n - s_i
            else:
                s_i = s_n
            t_i = self._group.random(ZR)
            C_i_1[attr_name] = (w ** s_i) * (v ** t_i)
            C_i_3[attr_name] = g ** t_i

            for attr_value in self.attributes_dict[attr_name]:
                full_attr_value_name = Attribute.get_full_attribute_value_name(attr_name, attr_value)
                if attr_value in access_policy[attr_name]:
                    hash_attr_val_in_z_p = self._group.hash(full_attr_value_name, type=ZR)
                    C_i_ai_2 = ((u ** hash_attr_val_in_z_p) * h) ** (-t_i)
                else:
                    C_i_ai_2 = self._group.random(G1)
                C_i_2[full_attr_value_name] = C_i_ai_2
        CT = {'C': C,
              'C_1': C_1,
              'C_i_1': C_i_1,
              'C_i_3': C_i_3,
              'C_i_ai_2': C_i_2}
        return CT

    def decrypt(self, CT, PK, SK):
        """
        Decrypt a cipher text. This algorithm is performed by a data user who has the required attributes to decipher
        the ciphertext that was encrypted using an access policy.
        Inputs:
            - CT: Cipher text.
            - PK: Public parameters and the public key of the TA.
            - SK: User's secret key.
        Outputs:
            - m: The original decrypted message.
        """
        nominator = pair(CT['C_1'], SK['K_0'])
        denominator = self._group.init(GT, 1)
        for attr_name in CT['C_i_1']:
            # Find the attribute value that exists inside both the user's key for attr_name
            found_attribute_value_full_name = None
            for attr_value_full_name in SK['K_2']:
                if attr_value_full_name.find(attr_name) == 0:
                    found_attribute_value_full_name = attr_value_full_name
            if not found_attribute_value_full_name:
                return False # The user does not have the necessary attributes to decrypt

            denominator = (denominator * pair(CT['C_i_1'][attr_name], SK['K_1']) *
                           pair(CT['C_i_ai_2'][found_attribute_value_full_name],
                                SK['K_2'][found_attribute_value_full_name]) *
                           pair(CT['C_i_3'][attr_name], SK['K_3'][found_attribute_value_full_name]))
        B = nominator / denominator
        recovered_message = CT['C'] / B
        return recovered_message

class CP_Hiding_Accountability_ABE(CP_Hiding_ABE):
    """
    Cipher text policy hiding attribute based encryption (Section 4 in the paper).
    """
    def __init__(self, group_obj):
        CP_Hiding_ABE.__init__(self, group_obj)
        self._user_ID_to_w_pow_k_dict = {}  # Updated inside the key generation function to map the user ID to his
        # associated R = w ** k.

    def setup(self, attributes_dict: Dict[str, List[str]]):
        """
        System Setup algorithm. This algorithm is performed by TA.
        Inputs:
            - None
        Outputs:
            - MSK: TA's master secret key.
            - PK: Public Parameters.
        """
        self.attributes_dict = attributes_dict
        g = self._group.random(G1)
        u = self._group.random(G1)
        v = self._group.random(G1)
        h = self._group.random(G1)
        w = self._group.random(G1)

        alpha = self._group.random(ZR)
        x = self._group.random(ZR)
        y = self._group.random(ZR)

        X = g ** x
        Y = g ** y

        MSK = {
            'alpha': alpha,
            'x': x,
            'y': y
        }
        PK = {'g': g,
              'e_gg': pair(g, g),
              'u': u,
              'h': h,
              'w': w,
              'v': v,
              'e_gg_alpha': pair(g, g) ** alpha,
              'X': X,
              'Y': Y
              }
        return MSK, PK

    def key_gen(self, MSK, PK, ID, attributes_list):
        """
        Key generation for a user based on his list of attributes. This algorithm is performed by TA and the user.
        Part of the key generation is executed as an interaction between the user and the TA, as the user generates
        a random number (k) that he does not share with the TA. However, he shares with it w**k, and proves knowledge of
        (k) to TA using any ZKP algorithm.
        Inputs:
            - MSK: Master Secret Key of the TA.
            - PK: Public parameters and the public key of the TA.
            - ID: User's unique identifier.
            - attributes_list: List of attributes held by this user, where each attribute is in the format:
                               'attrName_value'
        Outputs:
            - SK: User's secret key.
        """
        w = PK['w']

        # The part executed by the user
        k = self._group.random(ZR)  # Select a secret KFN (Key Family Number).
        R = w ** k

        # User is going to send R to the TA and prove knowledge of k using Shnorr's ZKP.
        zkp_prover = ShnorrInteractiveZKP.Prover(k, self._group)  # The user.
        zkp_verifier = ShnorrInteractiveZKP.Verifier(self._group)  # The TA.
        pk = {'g': w}  # Work around to user (w) as the group point instead of (g)
        u = zkp_prover.create_prover_commitments(pk)
        c = zkp_verifier.create_verifier_challenge()
        z = zkp_prover.create_proof(c)
        assert zkp_verifier.is_proof_verified(z, pk, u, R), \
            "User failed to proof knowledge of (k) that is used to calculate R"

        SK = self.key_gen_TA(MSK, PK, ID, R, attributes_list)

        # The user gets the SK and adds his secret KFN to it.
        SK['k'] = k
        return SK

    def key_gen_TA(self, MSK, PK, ID, R, attributes_list):
        """
        Key generation for a user based on his list of attributes. This algorithm is performed by TA and the user.
        Part of the key generation is executed as an interaction between the user and the TA, as the user generates
        a random number (k) that he does not share with the TA. However, he shares with it w**k, and proves knowledge of
        (k) to TA using any ZKP algorithm.
        Inputs:
            - MSK: Master Secret Key of the TA.
            - PK: Public parameters and the public key of the TA.
            - ID: User's unique identifier.
            - R: w ** k, where (w) is a public point on the curve, and (k) is the secret KFN selected by the user.
            - attributes_list: List of attributes held by this user, where each attribute is in the format:
                               'attrName_value'
        Outputs:
            - SK: User's secret key.
        """
        self._validate_attributes_list(attributes_list)
        r = self._group.random(ZR)
        g = PK['g']
        w = PK['w']
        u = PK['u']
        h = PK['h']
        v = PK['v']
        alpha = MSK['alpha']
        x = MSK['x']
        y = MSK['y']

        d = self._group.random(ZR)  # TODO: AB: If (x + ID + y * d) mod p = 0, then choose another d

        K_0 = (g ** (alpha / (x + ID + y * d))) * (R ** r)
        K_1 = g ** r
        K_2 = g ** (x * r)
        K_3 = g ** (y * r)
        T1 = ID
        T3 = d
        K_i_2 = {}
        K_i_3 = {}
        for full_attr_value_name in attributes_list:
            # attr_name = full_attr_value_name.split('_')[0]
            r_i = self._group.random(ZR)
            K_i_2[full_attr_value_name] = g ** r_i
            hash_attr_val_in_z_p = self._group.hash(full_attr_value_name, type=ZR)
            K_i_3[full_attr_value_name] = (((u ** hash_attr_val_in_z_p) * h) ** r_i) * v ** (-r * (x + ID + y * d))

        self._user_ID_to_w_pow_k_dict[T1] = R

        SK = {'attributes_list': attributes_list, 'K_0': K_0, 'K_1': K_1, 'K_2': K_2, 'K_3': K_3, 'K_i_2': K_i_2,
              'K_i_3': K_i_3, 'T1': T1, 'T3': T3}
        return SK

    def encrypt(self, m, PK, access_policy: Dict[str, List[str]]):
        """
        Encrypt a message using an access policy. This function is performed by a data user who wants to encrypt his 
        message with an access policy. They consider only and-gates in their policy.
        Note: The access policy is hidden into the ciphertext.
        Inputs:
            - PK: Public parameters and the public key of the TA.
            - m: Message to be encrypted in G_T.
            - access_policy: Access policy that will be used to encrypt the message. It has to be and gated policy,
                             which means that each attribute can have only one value.
        Outputs:
            - CT: Cipher text. 
        """
        g = PK['g']
        w = PK['w']
        v = PK['v']
        u = PK['u']
        h = PK['h']
        X = PK['X']
        Y = PK['Y']
        s = self._group.random(ZR)
        s_n = s
        access_policy_len = len(access_policy)
        C = m * PK['e_gg_alpha'] ** s
        C_1 = g ** s
        C_2 = X ** s
        C_3 = Y ** s
        C_i_1 = {}
        C_i_3 = {}
        C_i_2 = {}
        for idx, attr_name in enumerate(access_policy):
            if idx < access_policy_len - 1:
                s_i = self._group.random(ZR)
                s_n = s_n - s_i
            else:
                s_i = s_n
            t_i = self._group.random(ZR)
            C_i_1[attr_name] = (w ** s_i) * (v ** t_i)
            C_i_3[attr_name] = g ** t_i

            for attr_value in self.attributes_dict[attr_name]:
                full_attr_value_name = Attribute.get_full_attribute_value_name(attr_name, attr_value)
                if attr_value in access_policy[attr_name]:
                    hash_attr_val_in_z_p = self._group.hash(full_attr_value_name, type=ZR)
                    C_i_ai_2 = ((u ** hash_attr_val_in_z_p) * h) ** (-t_i)
                else:
                    C_i_ai_2 = self._group.random(G1)
                C_i_2[full_attr_value_name] = C_i_ai_2
        CT = {'C': C,
              'C_1': C_1,
              'C_2': C_2,
              'C_3': C_3,
              'C_i_1': C_i_1,
              'C_i_3': C_i_3,
              'C_i_ai_2': C_i_2}
        return CT

    def decrypt(self, CT, PK, SK):
        """
        Decrypt a cipher text. This algorithm is performed by a data user who has the required attributes to decipher
        the ciphertext that was encrypted using an access policy.
        Inputs:
            - CT: Cipher text.
            - PK: Public parameters and the public key of the TA.
            - SK: User's secret key.
        Outputs:
            - m: The original decrypted message.
        """
        nominator = pair((CT['C_1'] ** SK['T1']) * CT['C_2'] * (CT['C_3'] ** SK['T3']), SK['K_0'])
        denominator = self._group.init(GT, 1)
        for attr_name in CT['C_i_1']:
            # Find the attribute value that exists inside both the user's key for attr_name
            found_attribute_value_full_name = None
            for attr_value_full_name in SK['K_i_2']:
                if attr_value_full_name.find(attr_name) == 0:
                    found_attribute_value_full_name = attr_value_full_name
            if not found_attribute_value_full_name:
                return False # The user does not have the necessary attributes to decrypt

            denominator = (denominator * ((pair(CT['C_i_1'][attr_name], (SK['K_1'] ** SK['T1']) * SK['K_2'] * (SK['K_3'] ** SK['T3'])) *
                           pair(CT['C_i_ai_2'][found_attribute_value_full_name],
                                SK['K_i_2'][found_attribute_value_full_name]) *
                           pair(CT['C_i_3'][attr_name], SK['K_i_3'][found_attribute_value_full_name])) ** SK['k']))
        B = nominator / denominator
        recovered_message = CT['C'] / B
        return recovered_message

    def trace(self, SK_suspected, authentic_user_IDs_list, PK):
        """
        Trace function is executed by the auditor. The auditor checks the suspected SK and determines who is misbehaving
        : the user who owns SK or the TA. If this function is called, it means that either the user or the TA is
          misbehaving. The trigger how this function is triggered and how the malicious activity is detected is out of
          this paper's scope.
        Inputs:
            - SK_suspected: Secret key of the suspected user under the white box model, which means that it has access
                            to the full secret key of the user.
            - authentic_user_IDs_list: A list of the authentic user IDs issued by a trusted third party outside the
                                       system.
            - PK: Public parameters and the public key of the TA.
        Outputs:
            - {'user': True/False,
               'TA': True/False} ; Only one of them will be true and the other will be false.
        """
        assert self._is_SK_well_formed(SK_suspected), "SK is not well formed."
        user_id = SK_suspected['T1']
        if user_id not in authentic_user_IDs_list:
            return {'user': False, 'TA': True}  # The TA issued a fake ID for a fake or not illegible user.
        w_pow_k_ID = self._user_ID_to_w_pow_k_dict[user_id]
        k = SK_suspected['k']
        w = PK['w']
        if w**k != w_pow_k_ID:
            return {'user': True, 'TA': False}  # User is misbehaving and gave his keys to someone else.
        else:
            return {'user': False, 'TA': True}  # The TA is misbehaving.

    def _is_SK_well_formed(self, SK):
        search_keys = ['attributes_list', 'K_0', 'K_1', 'K_2', 'K_3', 'K_i_2', 'K_i_3', 'T1', 'T3', 'k']
        for a_search_key in search_keys:
            if a_search_key not in SK:
                return False
        return True



class ShnorrInteractiveZKP():
    """
    Shnorr's Interactive ZKP
    """
    class Prover:
        def __init__(self, secret_x, groupObj):
            self.__r = None
            self.group = groupObj
            self.__x = secret_x

        def create_prover_commitments(self, pk):
            """
            1) This function is executed by the prover to send a random value to the verifier
            """
            self.__r = self.group.random()
            u = (pk['g'] ** self.__r)
            return u

        def create_proof(self, c):
            """
            3) This function is executed by the prover after he received the challenge value (c) from the verifier
            """
            z = self.__r + c * self.__x
            return z  # proof

    class Verifier:

        def __init__(self, groupObj):
            self.group = groupObj

        def create_verifier_challenge(self):
            """
            2) This function is executed by the verifier after he had received the value u from the prover to send a challenge value to the prover.
            """
            self.c = self.group.random()
            return self.c

        def is_proof_verified(self, z, pk, u, h):
            """
            4) This function is executed by the verifier to verify the authenticity of the proof sent by the prover
            z: Created by the prover in create_proof function
            u: Created by the prover in create_prover_commitments function
            h: g^x, where x is the secret key of the prover that he wants to prove that he knows it.
            """
            if (pk['g'] ** z) == u * h ** self.c:
                return True
            return False


def main():
    CP_policy_hiding_ABE_test()
    CP_policy_hiding_with_accountability_test()


def CP_policy_hiding_ABE_test():
    print("************************************* CP policy hiding ABE test *******************************************")
    attr1_values = ['val1', 'val2', 'val3']
    attr2_values = ['val1', 'val4']
    attributes_dict = {
        'attr1': attr1_values,
        'attr2': attr2_values
    }
    user1_attributes = ['attr1_val2', 'attr2_val4']
    user2_attributes = ['attr1_val2', 'attr2_val1']
    # The access policy that will be used to encrypt the message
    access_policy = {'attr1': ['val1', 'val2'],  # Set of attributes allowed for 'attr1' in the access policy.
                     'attr2': ['val4']  # Set of attributes allowed for 'attr2' in the access policy.
                     }
    attr1 = Attribute('attr1', attr1_values)
    attr2 = Attribute('attr2', attr2_values)
    attr1_values = attr1.get_attribute_values_full_name()
    attr2_values = attr2.get_attribute_values_full_name()
    print("attribute 1 full values names: ", attr1_values)
    print("attribute 2 full values names: ", attr2_values)
    group_obj = PairingGroup('SS512')
    cp_hiding_ABE = CP_Hiding_ABE(group_obj)
    MSK, PK = cp_hiding_ABE.setup(attributes_dict)  # TA's MSK, PK
    print("MSK: ", MSK)
    print("PK: ", PK)
    user1_SK = cp_hiding_ABE.key_gen(MSK, PK, user1_attributes)
    print('user1 SK: ', user1_SK)
    user2_SK = cp_hiding_ABE.key_gen(MSK, PK, user2_attributes)
    print('user2 SK: ', user1_SK)
    rand_msg = group_obj.random(GT)
    CT = cp_hiding_ABE.encrypt(rand_msg, PK, access_policy)
    print("CT: ", CT)
    recovered_message = cp_hiding_ABE.decrypt(CT, PK, user1_SK)
    print("recovered message: ", recovered_message)
    # No error is generated since user 1's attributes matches the access policy embedded inside the CT.
    assert recovered_message == rand_msg, "Random message does not match the recovered message"
    # User 2 tries to decrypt CT.
    recovered_message = cp_hiding_ABE.decrypt(CT, PK, user2_SK)
    print("recovered message: ", recovered_message)
    # An error is generated since user 2 does not have the required attributes to decrypt CT.
    # assert recovered_message == rand_msg, "Random message does not match the recovered message"  # Uncomment to raise the error.
    print("***********************************************************************************************************")


def CP_policy_hiding_with_accountability_test():
    print("*************************** CP policy hiding ABE with accountability test *********************************")
    attr1_values = ['val1', 'val2', 'val3']
    attr2_values = ['val1', 'val4']
    attributes_dict = {
        'attr1': attr1_values,
        'attr2': attr2_values
    }
    user1_attributes = ['attr1_val2', 'attr2_val4']
    user2_attributes = ['attr1_val2', 'attr2_val1']

    user1_ID = 123
    user2_ID = 57534
    # The access policy that will be used to encrypt the message
    access_policy = {'attr1': ['val1', 'val2'],  # Set of attributes allowed for 'attr1' in the access policy.
                     'attr2': ['val4']  # Set of attributes allowed for 'attr2' in the access policy.
                     }
    attr1 = Attribute('attr1', attr1_values)
    attr2 = Attribute('attr2', attr2_values)
    attr1_values = attr1.get_attribute_values_full_name()
    attr2_values = attr2.get_attribute_values_full_name()
    print("attribute 1 full values names: ", attr1_values)
    print("attribute 2 full values names: ", attr2_values)
    group_obj = PairingGroup('SS512')
    cp_hiding_ABE = CP_Hiding_Accountability_ABE(group_obj)
    MSK, PK = cp_hiding_ABE.setup(attributes_dict)  # TA's MSK, PK
    print("MSK: ", MSK)
    print("PK: ", PK)

    user1_ID = group_obj.init(ZR, user1_ID)
    user2_ID = group_obj.init(ZR, user2_ID)

    user1_SK = cp_hiding_ABE.key_gen(MSK, PK, user1_ID, user1_attributes)
    print('user1 SK: ', user1_SK)
    user2_SK = cp_hiding_ABE.key_gen(MSK, PK, user2_ID, user2_attributes)
    print('user2 SK: ', user1_SK)
    rand_msg = group_obj.random(GT)
    CT = cp_hiding_ABE.encrypt(rand_msg, PK, access_policy)
    print("CT: ", CT)
    recovered_message = cp_hiding_ABE.decrypt(CT, PK, user1_SK)
    print("recovered message: ", recovered_message)
    # No error is generated since user 1's attributes matches the access policy embedded inside the CT.
    assert recovered_message == rand_msg, "Random message does not match the recovered message"

    # User 2 tries to decrypt CT.
    recovered_message = cp_hiding_ABE.decrypt(CT, PK, user2_SK)
    print("recovered message: ", recovered_message)
    # An error is generated since user 2 does not have the required attributes to decrypt CT.
    # assert recovered_message == rand_msg, "Random message does not match the recovered message"  # Uncomment to raise the error.

    authentic_user_IDs_list = [123]
    # User 2's ID is not in the authentic list, which means that his ID is fabricated and this malicious action is
    # traced to the TA.
    misbehaving_result = cp_hiding_ABE.trace(user2_SK, authentic_user_IDs_list, PK)
    print("Misbehaving result for user2 SK: ", misbehaving_result)
    print("***********************************************************************************************************")


if __name__ == "__main__":
    main()
