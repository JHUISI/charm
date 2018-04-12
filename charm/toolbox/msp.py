"""
This class is adapted from the SecretUtil class in charm/toolbox/secretutil.py.
It provides the following methods:
- createPolicy: convert a Boolean formula encoded as a string into a policy represented like a tree;
- convertPolicyToMSP: convert a policy into a monotone span program (MSP);
- getCoefficients: given a policy, returns a coefficient for every attribute;
- strip_index: remove the index from an attribute (i.e., x_y -> x);
- prune: determine whether a given set of attributes satisfies the policy
    (returns false if it doesn't, otherwise a good enough subset of attributes);
- getAttributeList: retrieve the attributes that occur in a policy tree in order (left to right).
"""

from charm.core.math.pairing import ZR
from charm.toolbox.policytree import *


class MSP:

    def __init__(self, groupObj, verbose=True):
        self.len_longest_row = 1
        self.group = groupObj

    def createPolicy(self, policy_string):
        """
         Convert a Boolean formula represented as a string into a policy represented like a tree.
        """

        assert type(policy_string) in [bytes, str], "invalid type for policy_string"
        if type(policy_string) == bytes:
            policy_string = policy_string.decode('utf-8')
        parser = PolicyParser()
        policy_obj = parser.parse(policy_string)
        _dictCount, _dictLabel = {}, {}
        parser.findDuplicates(policy_obj, _dictCount)
        for i in _dictCount.keys():
            if _dictCount[i] > 1: _dictLabel[i] = 0
        parser.labelDuplicates(policy_obj, _dictLabel)
        return policy_obj

    def convert_policy_to_msp(self, tree):
        """
        Convert a policy into a monotone span program (MSP)
        represented by a dictionary with (attribute, row) pairs
        """

        root_vector = [1]
        # listOfAttributeRowPairs = {}
        self.len_longest_row = 1
        return self._convert_policy_to_msp(tree, root_vector)

    def _convert_policy_to_msp(self, subtree, curr_vector):
        """
         Given a vector for the current node,
         returns the vectors for its children in the form of a dictionary
        """

        if subtree is None:
            return None

        type = subtree.getNodeType()

        if type == OpType.ATTR:
            # print ('ATTR: ', subtree, subtree.getAttributeAndIndex(), currVector)
            return {subtree.getAttributeAndIndex(): curr_vector}

        if type == OpType.OR:
            left_list = self._convert_policy_to_msp(subtree.getLeft(), curr_vector)
            right_list = self._convert_policy_to_msp(subtree.getRight(), curr_vector)
            # print ('OR l: ', leftList, 'r: ', rightList)
            left_list.update(right_list)
            return left_list

        if type == OpType.AND:
            length = len(curr_vector)
            left_vector = curr_vector + [0] * (self.len_longest_row - length) + [1]
            right_vector = [0] * self.len_longest_row + [-1]  # [0]*k creates a vector of k zeroes
            # extendedVector = currVector + [0]*(self.lengthOfLongestRow-length)
            # leftVector = extendedVector + [1]
            # rightVector = extendedVector + [2]  # [0]*k creates a vector of k zeroes
            self.len_longest_row += 1
            left_list = self._convert_policy_to_msp(subtree.getLeft(), left_vector)
            right_list = self._convert_policy_to_msp(subtree.getRight(), right_vector)
            # print ('AND l: ', leftList, 'r: ', rightList)
            left_list.update(right_list)
            return left_list

        return None

    def getCoefficients(self, tree):
        """
        Given a policy, returns a coefficient for every attribute.
        """

        coeffs = {}
        self._getCoefficientsDict(tree, coeffs)
        return coeffs

    def recoverCoefficients(self, list):
        """
        recovers the coefficients over a binary tree.
        """

        coeff = {}
        list2 = [self.group.init(ZR, i) for i in list]
        for i in list2:
            result = 1
            for j in list2:
                if not (i == j):
                    # lagrange basis poly
                    result *= (0 - j) / (i - j)
                    #                print("coeff '%d' => '%s'" % (i, result))
            coeff[int(i)] = result
        return coeff

    def _getCoefficientsDict(self, tree, coeff_list, coeff=1):
        """
        recover coefficient over a binary tree where possible node types are OR = (1 of 2)
        and AND = (2 of 2) secret sharing. The leaf nodes are attributes and the coefficients are
        recorded in a coeff-list dictionary.
        """

        if tree:
            node = tree.getNodeType()
            if (node == OpType.AND):
                this_coeff = self.recoverCoefficients([1, 2])
                # left child => coeff[1], right child => coeff[2]
                self._getCoefficientsDict(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self._getCoefficientsDict(tree.getRight(), coeff_list, coeff * this_coeff[2])
            elif (node == OpType.OR):
                this_coeff = self.recoverCoefficients([1])
                self._getCoefficientsDict(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self._getCoefficientsDict(tree.getRight(), coeff_list, coeff * this_coeff[1])
            elif (node == OpType.ATTR):
                attr = tree.getAttributeAndIndex()
                coeff_list[attr] = coeff
            else:
                return None

    def strip_index(self, node_str):
        """
         Remove the index from an attribute (i.e., x_y -> x).
        """

        if node_str.find('_') != -1:
            return node_str.split('_')[0]
        return node_str

    def prune(self, policy, attributes):
        """
        Determine whether a given set of attributes satisfies the policy
        (returns false if it doesn't, otherwise a good enough subset of attributes).
        """

        parser = PolicyParser()
        return parser.prune(policy, attributes)

    def getAttributeList(self, Node):
        """
         Retrieve the attributes that occur in a policy tree in order (left to right).
        """

        aList = []
        self._getAttributeList(Node, aList)
        return aList

    def _getAttributeList(self, Node, List):
        if (Node == None):
            return None
        # V, L, R
        if (Node.getNodeType() == OpType.ATTR):
            List.append(Node.getAttributeAndIndex())  # .getAttribute()
        else:
            self._getAttributeList(Node.getLeft(), List)
            self._getAttributeList(Node.getRight(), List)
        return None
