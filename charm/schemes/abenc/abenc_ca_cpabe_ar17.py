'''
Jiguo Li, Wei Yao, Jinguang Han, Yichen Zhang, Jian Shen (Pairing-based)

| From: "User Collusion Avoidance CP-ABE With Efficient Attribute Revocation for Cloud Storage".
| Published in: 2017
| Available from: https://ieeexplore.ieee.org/abstract/document/7867082
| Notes:
| Security Assumption:
|
| type:           ciphertext-policy attribute-based encryption (public key)
| setting:        Pairing
|
| Authors:        Ahmed Bakr
| Date:           07/2023
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import ABEnc, Input, Output

from typing import Dict, List, Tuple
import queue

# type annotations
mk_t = {'beta':ZR, 'g_alpha':G1 }
pp_t = { 'g':G1, 'g_beta':G1, 'g_1_over_beta':G1, 'e_gg_alpha':GT }



class TreeNode:
    def __init__(self, sequence_number, value, parent=None):
        self.parent = parent
        self.sequence_number = sequence_number
        self.value = value
        self.left = None
        self.right = None

    def __str__(self):
        return str(self.sequence_number)

    def __repr__(self):
        return self.__str__()


class UsersBinaryTree:
    """
    A binary tree that is used to assign users to leafs in a deterministic way.
    The tree is created and maintained by the AM.
    """
    def __init__(self, group_obj):
        self.group = group_obj
        self.leafs_queue = queue.Queue()
        self.sequence_number = 0
        self.root = self.create_node()
        self.leafs_queue.put(self.root)
        self.__curr_node = self.leafs_queue.get()

    def create_node(self) -> TreeNode:
        self.sequence_number += 1
        return TreeNode(self.sequence_number, self.group.random(ZR))

    def add_node_to_tree(self, tree_node: TreeNode):
        """
        Add a node to the tree.
        Inputs:
            - tree_node: a node to be added to the tree
        """
        if self.__curr_node.left and self.__curr_node.right:
            assert not self.leafs_queue.empty(), "Leafs queue is empty and pull attempts was made"
            self.__curr_node = self.leafs_queue.get()
        if not self.__curr_node.left:
            self.__curr_node.left = tree_node
        elif not self.__curr_node.right:
            self.__curr_node.right = tree_node
        else:
            assert True, "This statement should not be reached"
        tree_node.parent = self.__curr_node
        self.leafs_queue.put(tree_node)

    def print_tree(self):
        print("{", end='')
        self.__print_tree_rec(self.root)
        print("}")

    def __print_tree_rec(self, node: TreeNode):
        print(node, end=', ')
        if node.left:
            self.__print_tree_rec(node.left)
        if node.right:
            self.__print_tree_rec(node.right)


class AM:
    """Attribute Manager (AM)"""
    def __init__(self, group_obj):
        self.users_to_attrs_dict: Dict[str, list] = {}
        self.attrs_to_users_dict: Dict[str, list] = {}

        self.users_binary_tree = UsersBinaryTree(group_obj)

    def add_attr_to_user(self, attr_str: str, user_name: str):
        if user_name not in self.users_to_attrs_dict:
            self.users_to_attrs_dict[user_name] = []
            self.__create_node_in_binary_tree_for_new_user()

        if attr_str not in self.attrs_to_users_dict:
            self.attrs_to_users_dict[attr_str] = []

        self.users_to_attrs_dict[user_name].append(attr_str)  # AB: It is assumed that this attribute does not already
        # exist in the list
        self.attrs_to_users_dict[attr_str].append(user_name)  # AB: It is assumed that the username does not already
        # exist in the list

    def __create_node_in_binary_tree_for_new_user(self):
        current_number_of_users = len(list(self.users_to_attrs_dict.keys()))  # AB: make sure to add the new user to the
        # dict first before calling this function
        while not current_number_of_users == self.users_binary_tree.leafs_queue.qsize():
            new_node = self.users_binary_tree.create_node()
            self.users_binary_tree.add_node_to_tree(new_node)

    def remove_attr_from_user(self, attr_str: str, user_name: str):
        index = self.attrs_to_users_dict[attr_str].index(user_name)
        self.attrs_to_users_dict[attr_str].pop(index)

        index = self.users_to_attrs_dict[user_name].index(attr_str)
        self.users_to_attrs_dict[user_name].pop(index)

    def get_user_assignation_to_leafs_dict(self) -> Dict[str, TreeNode]:
        user_names_list = list(self.users_to_attrs_dict.keys())
        assert len(user_names_list) == self.users_binary_tree.leafs_queue.qsize(), "The number of usernames list ({})" \
                                                                                " has to match the number of leaf" \
                                                                                " elements ({}) in the binary tree".format(
            len(user_names_list), self.users_binary_tree.leafs_queue.qsize())
        ret_dict: Dict[str, TreeNode] = {}
        for user_name, leaf in zip(user_names_list, self.users_binary_tree.leafs_queue.queue):
            ret_dict[user_name] = leaf

        return ret_dict

    def get_minimum_nodes_list_that_represent_users_list(self, user_names_list: List[str]) -> List[TreeNode]:
        """
        This is represented in the paper as calculating node(Gi)
        """
        visited_arr = [False] * (self.users_binary_tree.sequence_number + 1)
        list_of_leaves_to_traverse = []

        user_assignation_to_leafs_dict = self.get_user_assignation_to_leafs_dict()
        for user_name in user_names_list:
            user_leaf_node = user_assignation_to_leafs_dict[user_name]
            visited_arr[user_leaf_node.sequence_number] = True
            list_of_leaves_to_traverse.append(user_leaf_node)

        self.__traverse_to_mark_all_children_visited_arr(self.users_binary_tree.root, visited_arr)

        return self.__traverse_bfs_to_get_minimum_number_nodes_to_cover_users_list(visited_arr)

    def __traverse_to_mark_all_children_visited_arr(self, node: TreeNode, visited_arr: List[bool]):
        is_leaf = not node.left and not node.right
        if is_leaf:
            return
        if node.left:
            self.__traverse_to_mark_all_children_visited_arr(node.left, visited_arr)
        if node.right:
            self.__traverse_to_mark_all_children_visited_arr(node.right, visited_arr)

        visited_arr[node.sequence_number] = visited_arr[node.left.sequence_number] and visited_arr[
            node.right.sequence_number]

    def __traverse_bfs_to_get_minimum_number_nodes_to_cover_users_list(self, visited_arr) -> List[TreeNode]:
        ret_list = []
        q = queue.Queue()
        q.put(self.users_binary_tree.root)

        while not q.empty():
            node: TreeNode = q.get()
            if visited_arr[node.sequence_number]:
                ret_list.append(node)
            else:
                if node.left:
                    q.put(node.left)
                if node.right:
                    q.put(node.right)

        return ret_list

    def get_user_path(self, user_name) -> List[TreeNode]:
        ret_list = []
        user_assignation_to_leafs_dict = self.get_user_assignation_to_leafs_dict()
        assert user_name in user_assignation_to_leafs_dict, \
            "Username ({}) must be inside user_assignation_to_leafs_dict ({})".format(user_name,
                                                                                      user_assignation_to_leafs_dict)
        user_leaf_node = user_assignation_to_leafs_dict[user_name]
        curr_node: TreeNode = user_leaf_node
        while curr_node:
            ret_list.append(curr_node)
            curr_node = curr_node.parent

        return ret_list

    @staticmethod
    def get_user_path_intersection_with_node_gi(user_path: List[TreeNode], node_gi: List[TreeNode]) -> List[TreeNode]:
        ret_intersection_list = []
        for user_node in user_path:
            if user_node in node_gi:
                ret_intersection_list.append(user_node)

        return ret_intersection_list


class CaCpabeAr(ABEnc):
    def __init__(self, group_obj):
        ABEnc.__init__(self)
        self.util = SecretUtil(group_obj, verbose=False)
        self.group = group_obj

    def system_setup(self) -> (mk_t, pp_t):
        """
        System Setup algorithm. This algorithm is performed by TA
        Inputs:
            - None
        Outputs:
            - MK: TA's master secret key.
            - PP: Public Parameters.
        """
        alpha, beta = self.group.random(ZR), self.group.random(ZR)
        g = self.group.random(G1)

        MK = {'beta': beta, 'g_alpha': g ** alpha}
        e_gg_alpha = pair(g, g) ** alpha
        PP = {'g': g, 'g_beta': g ** beta, 'g_1_over_beta': g ** ~beta, 'e_gg_alpha': e_gg_alpha}

        return MK, PP

    def manager_setup(self, attribute_names: List[str], PP: pp_t):
        """
        Manager Setup algorithm performed by AM.
        Inputs:
            - attribute_names: The name of attributes that AM is responsible for.
            - PP: Public Parameters from the system setup algorithm.
        Outputs:
            - MMK: Manager master key represented as a dictionary.
            - MPK: Manager public key represented as a dictionary.
        """
        MMK = {}
        MPK = {}
        for attr in attribute_names:
            t_i = self.group.random(ZR)
            g = PP['g']
            T_i = g ** t_i
            MMK[attr] = t_i
            MPK[attr] = T_i

        return MMK, MPK

    def key_generation(self, PP, MK, MPK, user_attribute_names_list: List[str], user_name: str,
                       attributes_manager: AM, UMK, users_TA_KEK):
        """
        This function is responsible for generating the decryption keys used by the user according to his list of
        attributes.
        Inputs:
            - PP: Public Parameters from the system setup algorithm.
            - MK: TA's master secret key.
            - MPK: Manager public key represented as a dictionary.
            - user_attribute_names_list: Attribute names hold by the user.
            - user_name: User name.
            - attributes_manager: AM.
        Inputs/outputs:
            - UMK: User Master Key. A value stored privately by TA for each user. Represented as a dictionary, where the
              user_name is the key and a group element is the value.
        Outputs:
            - DSK: Attributes decryption keys as in the original CP-ABE paper (abenc_bsw07.py). (shared with the user)
            - KEK: Key Encryption Keys generated for each attribute hold by the user using the users binary tree
              generated by AM. (shared with the user)
            - users_TA_KEK: A dictionary that holds the TA KEK for each user. (stored privately by AM)
        """
        # Attribute key generation. Executed by TA.
        DSK, TA_KEK = self.user_attributes_key_gen(MK, MPK, PP, user_attribute_names_list, user_name, UMK)

        users_TA_KEK[user_name] = TA_KEK

        # KEK generation by AM.
        KEK = self.user_attributes_kek_generation(TA_KEK, attributes_manager, user_attribute_names_list, user_name)

        return DSK, KEK

    def user_attributes_key_gen(self, MK, MPK, PP, user_attribute_names_list, user_name, UMK):
        """
        This function is executed by TA and considered as part of key generation procedure.
        Inputs:
            - MK: TA's master secret key.
            - MPK: Manager public key represented as a dictionary.
            - PP: Public Parameters from the system setup algorithm.
            - user_attribute_names_list: Attribute names hold by the user.
            - user_name: User name.
        Inputs/outputs:
            - UMK: User Master Key. A value stored privately by TA for each user. Represented as a dictionary, where the
              user_name is the key and a group element is the value.
        Outputs:
            - DSK: Attributes decryption keys as in the original CP-ABE paper (abenc_bsw07.py). (shared with the user)
            - KEK: Key Encryption Keys generated for each attribute hold by the user using the users binary tree
              generated by AM. It is a preliminary one that will be changed by AM in the next algorithm.
        """
        r = self.group.random(ZR)
        g = PP['g']
        g_r = g ** r
        D = (MK['g_alpha'] * g_r) ** (1 / MK['beta'])
        D_i = {}
        D_i_dash = {}
        KEK = {}
        for attr in user_attribute_names_list:
            r_i = self.group.random(ZR)
            D_i[attr] = g_r * (self.group.hash(attr, G1) ** r_i)
            D_i_dash[attr] = g ** r_i

            kek_i = MPK[attr] ** r_i
            KEK[attr] = kek_i
        DSK = {'D': D, 'D_i': D_i, 'D_i_dash': D_i_dash, 'attrs': user_attribute_names_list}
        UMK[user_name] = g_r

        return DSK, KEK

    def user_attributes_kek_generation(self, TA_KEK, attributes_manager, user_attribute_names_list, user_name):
        """
        This function is executed by AM and considered as part of key generation procedure.
        Inputs:
            - TA_KEK: Preliminary KEK list generated by TA.
            - attributes_manager: AM.
            - user_attribute_names_list: Attribute names hold by the user.
            - user_name: User name.
        Outputs:
            - KEK: Key Encryption Keys generated for each attribute hold by the user using the users binary tree
              generated by AM.
        """
        KEK = {}
        for attr in user_attribute_names_list:
            KEK_attr = self.generate_kek_for_user_with_attr(TA_KEK, attr, attributes_manager, user_name)
            KEK[attr] = KEK_attr
        return KEK

    def generate_kek_for_user_with_attr(self, TA_KEK, attr, attributes_manager, user_name):
        """
        This function is executed by AM and considered as part of key generation procedure.
        Inputs:
            - TA_KEK: Preliminary KEK list generated by TA.
            - attributes_manager: AM.
            - user_attribute_names_list: Attribute names hold by the user.
            - user_name: User name.
        Outputs:
            - KEK: Key Encryption Key generated for a specific attribute hold by the user using the users binary tree
              generated by AM.
        """
        list_of_users_hold_attr = attributes_manager.attrs_to_users_dict[attr]
        node_G_i = attributes_manager.get_minimum_nodes_list_that_represent_users_list(list_of_users_hold_attr)
        user_path = attributes_manager.get_user_path(user_name)
        intersection = attributes_manager.get_user_path_intersection_with_node_gi(user_path, node_G_i)
        if len(intersection) == 0:
            # AB: Do nothing, as mentioned in the paper.
            return None
        else:
            assert len(intersection) == 1, "The intersection list should have only one element."
            vj_node: TreeNode = intersection[0]
            kek_i = TA_KEK[attr]  # TODO: AB: The attribute has to be added before to any other user in the system setup.
            # Consider fixing it later if this functionality is needed.
            KEK_i = kek_i ** (1 / vj_node.value)
            KEK_attr = {'seq(vj)': vj_node.sequence_number, 'kek_i': kek_i, 'KEK_i': KEK_i}
            return KEK_attr


    def encrypt(self, PP, MMK, M, A: str, attributes_manager: AM):
        """
        This function is executed by anyone who wants to encrypt a message with an access policy, then by AM to
        perform the re-encryption.
        Inputs:
            - PP: Public Parameters from the system setup algorithm.
            - MMK: Manager master key represented as a dictionary.
            - M: Message to by encrypted.
            - A: Access policy represented as a boolean expression string.
        Outputs:
            - CT_dash: Ciphertext.
            - Hdr: Header message.
        """
        # Local Encryption
        CT = self.local_encryption(A, M, PP)
        CT, Hdr = self.reencryption(CT, MMK, PP, attributes_manager)
        return CT, Hdr

    def reencryption(self, CT, MMK, PP, attributes_manager):
        """
        This function is performed by AM and it is the second part of the encryption procedure.
        """
        Hdr = {}  # AB: TODO:
        g = PP['g']
        kys_dict = {}
        for attr_name_with_idx in CT['Cy_tilde']:
            # Index is appended only if the attribute is repeated more than one time to the access policy
            k_y = self.group.random(ZR)
            kys_dict[attr_name_with_idx] = k_y
            g_k_y = g ** k_y
            CT['Cy_tilde'][attr_name_with_idx] = CT['Cy_tilde'][attr_name_with_idx] * g_k_y

            attr_name_without_idx = self.__get_attr_name_without_idx(attr_name_with_idx)
            if not attr_name_without_idx in attributes_manager.attrs_to_users_dict:
                # Attribute manager is not responsible for this attribute
                # AB: TODO: Attention here. You might need to revisit this part.
                continue
            Gi = attributes_manager.attrs_to_users_dict[attr_name_without_idx]
            node_Gi = attributes_manager.get_minimum_nodes_list_that_represent_users_list(Gi)
            if not attr_name_with_idx in Hdr:
                Hdr[attr_name_with_idx] = []
            for a_node_Gi in node_Gi:
                a_node_Gi: TreeNode = a_node_Gi
                E_k_y = g_k_y ** (a_node_Gi.value / MMK[attr_name_without_idx])
                Hdr[attr_name_with_idx].append({'seq': a_node_Gi.sequence_number, 'E(k_y)': E_k_y})
        return CT, Hdr

    def __get_attr_name_without_idx(self, attr_name: str):
        if attr_name.find('_') == -1:
            return attr_name
        val = attr_name.split('_')
        return val[0]

    def local_encryption(self, A, M, PP):
        """
        This function is executed by anyone who wants to encrypt a message with an access policy.
        Inputs:
            - A: Access policy represented as a boolean expression string.
            - M: Message to by encrypted.
            - PP: Public Parameters from the system setup algorithm.
        Outputs:
            - CT: Ciphertext.
        """
        s = self.group.random(ZR)
        e_gg_alpha_s = PP['e_gg_alpha'] ** s
        g = PP['g']
        policy = self.util.createPolicy(A)
        a_list = self.util.getAttributeList(policy)
        shares = self.util.calculateSharesDict(s, policy)
        C0 = e_gg_alpha_s * M
        C1 = PP['g_beta'] ** s
        C_y, C_y_pr = {}, {}
        for i in shares.keys():
            j = self.util.strip_index(i)
            C_y[i] = g ** shares[i]
            C_y_pr[i] = self.group.hash(j, G1) ** shares[i]
        CT = {'C0': C0, 'C1': C1, 'Cy': C_y, 'Cy_tilde': C_y_pr, 'A': A, 'attributes': a_list}
        return CT

    def decrypt(self, PP, CT_tilde, Hdr, DSK, KEK, user_name: str, attributes_manager: AM):
        """
        This function is used by any user who has sufficient, non revoked attributes to decrypted a message under a
        specific access policy.
        Inputs:
            - PP: Public Parameters from the system setup algorithm.
            - CT_tilde: Ciphertext after re-encryption by the AM.
            - Hdr: Header message.
            - DSK: Attributes decryption keys as in the original CP-ABE paper (abenc_bsw07.py). (shared with the user).
            - KEK: Key Encryption Keys generated for each attribute hold by the user using the users binary tree
            - user_name: Username who is decrypting the ciphertext.
            - attributes_manager: AM.
        Outputs:
            - M: Recovered message, if the user has the decryption keys of the attributes that satisfy the policy.
        """
        ct = CT_tilde
        policy_str = ct['A']
        policy = self.util.createPolicy(policy_str)
        pruned_list = self.util.prune(policy, DSK['attrs'])
        if not pruned_list:
            return False
        z = self.util.getCoefficients(policy)
        A = 1
        for i in pruned_list:
            j = i.getAttributeAndIndex()
            k = i.getAttribute()
            KEK_i = KEK[k]['KEK_i']
            Hdr_for_attr: list = Hdr[j]
            chosen_Hdr_element = None
            user_path = attributes_manager.get_user_path(user_name)
            for hdr_elem in Hdr_for_attr:
                # If hdr_ele intersect with the user path, then it is the chosen element
                found = False
                for user_node in user_path:
                    if user_node.sequence_number == hdr_elem['seq']:
                        found = True
                if found:
                    chosen_Hdr_element = hdr_elem
            E_k_y = chosen_Hdr_element['E(k_y)']
            A *= ( (pair(ct['Cy'][j], DSK['D_i'][k]) * pair(KEK_i, E_k_y) )/ pair(DSK['D_i_dash'][k], ct['Cy_tilde'][j]) ) ** z[j]

        return ct['C0'] / (pair(ct['C1'], DSK['D']) / A)

    def revoke_attribute(self, revoked_user_name, attribute_name, attributes_manager: AM, PP, users_kek_i, MMK, MPK):
        """
        This function is executed by AM when an attribute is revoked from a user.
        Inputs:
            - revoked_user_name: The name of the revoked user.
            - attribute_name: revoked attribute name.
            - attributes_manager: AM.
            - PP: Public Parameters from the system setup algorithm.
            - users_kek_i: A list privately acquired by AM from TA as part of key_generation function.
        Inputs/Outputs:
            - MMK: Manager master key represented as a dictionary.
            - MPK: Manager public key represented as a dictionary.
        Outputs:
            - updated_KEK_dict: The key is the user-name of the user whose KEK key is updated and the value is the
                                updated KEK key value.
        """
        attributes_manager.remove_attr_from_user(attribute_name, revoked_user_name)

        # Key Updating
        g = PP['g']
        t_i = self.group.random(ZR)
        old_t_i = MMK[attribute_name]
        t_i = t_i * old_t_i
        T_i = g ** t_i
        MMK[attribute_name] = t_i
        MPK[attribute_name] = T_i

        # Get List of the users affects. (The users who hold this attribute)
        affected_users_names = attributes_manager.attrs_to_users_dict[attribute_name]
        updated_KEK_dict = {}
        for a_user_name in affected_users_names:
            users_kek_i[a_user_name][attribute_name] = users_kek_i[a_user_name][attribute_name] ** t_i
            user_attribute_names_list = attributes_manager.users_to_attrs_dict[a_user_name]
            # KEK generation by AM
            new_user_KEK = self.user_attributes_kek_generation(users_kek_i[a_user_name], attributes_manager,
                                                               user_attribute_names_list, a_user_name)
            updated_KEK_dict[a_user_name] = new_user_KEK
        return updated_KEK_dict

    def add_attribute(self, user_name, attribute_name, attributes_manager: AM, PP, UMK, users_kek_i, MMK, MPK):
        """
        This function is executed by AM when an attribute is added to a user.
        Inputs:
            - user_name: The name of the user who has an attribute to be added.
            - attribute_name: To be added attribute name.
            - attributes_manager: AM.
            - PP: Public Parameters from the system setup algorithm.
            - UMK: User Master Key. A value stored privately by TA for each user. Represented as a dictionary, where the
              user_name is the key and a group element is the value.
            - users_kek_i: A list privately acquired by AM from TA as part of key_generation function.
        Inputs/Outputs:
            - MMK: Manager master key represented as a dictionary.
            - MPK: Manager public key represented as a dictionary.
        Outputs:
            - updated_KEK_dict: The key is the user-name of the user whose KEK key is updated and the value is the
                                updated KEK key value.
        """
        # TA updates D_i, D_i_tilde and send it to the user for him to append it to his DSK
        g = PP['g']
        r_i = self.group.random(ZR)
        g_r = UMK[user_name]
        D_i = g_r * self.group.hash(attribute_name, G1) ** r_i
        D_i_tilde = g ** r_i
        kek_i = MPK[attribute_name] ** r_i
        users_kek_i[user_name][attribute_name] = kek_i

        # AM updates the users tree and returns to each affected user its updated KEK for this attribute.
        attributes_manager.add_attr_to_user(attribute_name, user_name)
        list_of_users_hold_attr = attributes_manager.attrs_to_users_dict[attribute_name]
        node_G_i = attributes_manager.get_minimum_nodes_list_that_represent_users_list(list_of_users_hold_attr)
        KEK_user_names_dict_for_attr = {}  # Each user gets an entry from this dict that is associated to him and
        # adds/updates it in his KEK.
        for a_user in list_of_users_hold_attr:
            KEK_attr = self.generate_kek_for_user_with_attr(users_kek_i[a_user], attribute_name, attributes_manager,
                                                            a_user)
            KEK_user_names_dict_for_attr[a_user] = KEK_attr

        return D_i, D_i_tilde, KEK_user_names_dict_for_attr

def main():
    group_obj = PairingGroup('SS512')

    attributes_manager = AM(group_obj)
    user_names_list = ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8']
    attributes_manager.add_attr_to_user('ONE', 'U1')
    attributes_manager.add_attr_to_user('FOUR', 'U1')
    attributes_manager.add_attr_to_user('TWO', 'U1')
    attributes_manager.add_attr_to_user('ONE', 'U2')
    attributes_manager.add_attr_to_user('THREE', 'U2')
    attributes_manager.add_attr_to_user('ONE', 'U3')
    attributes_manager.add_attr_to_user('THREE', 'U4')
    attributes_manager.add_attr_to_user('ONE', 'U5')
    attributes_manager.add_attr_to_user('TWO', 'U6')
    attributes_manager.add_attr_to_user('ONE', 'U7')
    attributes_manager.add_attr_to_user('THREE', 'U8')
    print("Users attributes list: ", attributes_manager.users_to_attrs_dict)

    ca_cpabe_ar = CaCpabeAr(group_obj)
    MK, PP = ca_cpabe_ar.system_setup()
    print("MK: ", MK)
    print("PP: ", PP)

    attributes_names = ['ONE', 'TWO', 'THREE', 'FOUR']
    MMK, MPK = ca_cpabe_ar.manager_setup(attributes_names, PP)
    print("MMK: ", MMK)
    print("MPK: ", MPK)

    UMK = {} # A value stored privately by TA for each user.
    users_private_keys_dict = {}
    users_kek_i = {} # Held privately by AM
    for user_name in user_names_list:
        # Attribute key generation. Executed by TA.
        user_attribute_names_list = attributes_manager.users_to_attrs_dict[user_name]
        # KEK generation by AM.
        DSK, KEK = ca_cpabe_ar.key_generation(PP, MK, MPK, user_attribute_names_list, user_name, attributes_manager,
                                         UMK, users_kek_i)
        users_private_keys_dict[user_name] = {'DSK': DSK, 'KEK': KEK}
        print("KEK for {}: {}".format(user_name, users_private_keys_dict[user_name]))

    rand_msg = group_obj.random(GT)
    print("Message: ", rand_msg)
    policy_str = '((four or three) and (three or one))'
    CT_tilde, Hdr = ca_cpabe_ar.encrypt(PP, MMK, rand_msg, policy_str, attributes_manager)
    print("CT: ", CT_tilde)
    user_private_keys_dict = users_private_keys_dict['U2']
    DSK = user_private_keys_dict['DSK']
    KEK = user_private_keys_dict['KEK']
    recovered_M = ca_cpabe_ar.decrypt(PP, CT_tilde, Hdr, DSK, KEK, 'U2', attributes_manager)
    print('Recovered Message: ', recovered_M)
    assert rand_msg == recovered_M, "FAILED Decryption: message is incorrect"

    # Revoke the attribute `THREE` from user `U2`
    updated_users_kek_values = ca_cpabe_ar.revoke_attribute('U2', 'THREE', attributes_manager, PP, users_kek_i, MMK,
                                                            MPK)
    for a_user_name in updated_users_kek_values:  # The updated users KEK keys need to be distributed to the users
        users_private_keys_dict[user_name]['KEK'] = updated_users_kek_values[a_user_name]

    # Now `U7` does not have the ability to decrypt the message because his attributes ['ONE'] does not match the policy
    user_private_keys_dict = users_private_keys_dict['U7']
    DSK = user_private_keys_dict['DSK']
    KEK = user_private_keys_dict['KEK']
    recovered_M = ca_cpabe_ar.decrypt(PP, CT_tilde, Hdr, DSK, KEK, 'U7', attributes_manager)
    print("Wrong recovered M for U7: ", recovered_M)
    # Uncomment the following line and an error will be raised
    # assert rand_msg == recovered_M, "FAILED Decryption: message is incorrect"

    # Add attribute `FOUR` to user `U7`
    attr_to_be_added = 'FOUR'
    D_i, D_i_tilde, KEK_user_names_dict_for_attr = ca_cpabe_ar.add_attribute('U7', attr_to_be_added, attributes_manager,
                                                                             PP, UMK, users_kek_i, MMK, MPK)
    user_private_keys_dict = users_private_keys_dict['U7']
    # Update DSK for the user
    DSK = user_private_keys_dict['DSK']
    DSK['D_i'][attr_to_be_added] = D_i
    DSK['D_i_dash'][attr_to_be_added] = D_i_tilde
    DSK['attrs'].append(attr_to_be_added)
    # Each user receives the updated KEK for the attribute 'U7'
    for a_user_name in KEK_user_names_dict_for_attr:
        user_KEK_for_added_attr = KEK_user_names_dict_for_attr[a_user_name]  # KEK for attribute 'FOUR' for a specific
        # user.
        user_private_keys_dict = users_private_keys_dict[a_user_name]
        KEK_for_user = user_private_keys_dict['KEK']
        KEK_for_user[attr_to_be_added] = user_KEK_for_added_attr

    # Encrypt the same message again.
    CT_tilde, Hdr = ca_cpabe_ar.encrypt(PP, MMK, rand_msg, policy_str, attributes_manager)
    print("CT: ", CT_tilde)
    user_private_keys_dict = users_private_keys_dict['U2']
    DSK = user_private_keys_dict['DSK']
    KEK = user_private_keys_dict['KEK']
    # Now `U2` does not have the ability to decrypt the message because his attributes no longer match the policy after
    # one of his attributes was revoked.
    recovered_M = ca_cpabe_ar.decrypt(PP, CT_tilde, Hdr, DSK, KEK, 'U2', attributes_manager)
    print("Wrong recovered M for U2: ", recovered_M)
    # Uncomment the following line and an error will be raised
    # assert rand_msg == recovered_M, "FAILED Decryption: message is incorrect"

    # U7 now has the ability to decrypt the message after because his attributes now match the policy [ONE, FOUR]
    user_private_keys_dict = users_private_keys_dict['U7']
    DSK = user_private_keys_dict['DSK']
    KEK = user_private_keys_dict['KEK']
    # `U7` has the ability to decrypt the message because his attributes match the policy after adding attribute FOUR
    recovered_M = ca_cpabe_ar.decrypt(PP, CT_tilde, Hdr, DSK, KEK, 'U7', attributes_manager)
    print("Recovered M for U7: ", recovered_M)
    assert rand_msg == recovered_M, "FAILED Decryption: message is incorrect"


if __name__ == "__main__":
    main()