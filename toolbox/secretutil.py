'''
Contains all the auxillary functions to do linear secret sharing (LSS) over an access structure. Mainly, we represent the 
access structure as a binary tree. This could also support matrices for representing access structures.
'''
from charm.pairing import *
from toolbox.policytree import *

class SecretUtil:
    def __init__(self, pairing, verbose=False):
        self.elem = pairing        
        self.parser = PolicyParser()

    def P(self, coeff, x):
        share = self.elem.init(ZR, 0)
        # evaluate polynomial
        for i in range(0, len(coeff)):
            share += (coeff[i] * (x ** i))
        return share

    def genShares(self, secret, k, n):
        if(k <= n):
            rand = self.elem.random
            a = [rand(ZR) for i in range(0, k)]
            a[0] = secret
            Pfunc = self.P
            shares = [Pfunc(a, i) for i in range(0, n+1)]
        return shares
    
    # shares is a dictionary
    def recoverCoefficients(self, list):
        eTop = self.elem.init(ZR)
        eBot = self.elem.init(ZR)
        coeff = {}
        #list = shares.keys()
        for i in list:
            result = self.elem.init(ZR, 1)
            for j in list:
                if(i != j):
                    # lagrange basis poly
                    eTop.set(0 - j) # numerator
                    eBot.set(i - j) # denominator
                    result *= eTop / eBot
#                print("coeff '%d' => '%s'" % (i, result))
            coeff[i] = result
        return coeff
        
    def recoverSecret(self, shares):
        list = shares.keys()
        if self.verbose: print(list)
        coeff = self.recoverCoefficients(list)
        secret = self.elem.init(ZR, 0)
        for i in list:
            secret += (coeff[i] * shares[i])

        return secret

    
    def getCoefficients(self, tree, coeff_list, coeff=1):   
        if tree:
            node = tree.getNodeType()
            if(node == tree.AND):
                this_coeff = self.recoverCoefficients([1,2])
                # left child => coeff[1], right child => coeff[2]
                self.getCoefficients(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self.getCoefficients(tree.getRight(), coeff_list, coeff * this_coeff[2])
            elif(node == tree.OR):
                this_coeff = self.recoverCoefficients([1])
                self.getCoefficients(tree.getLeft(), coeff_list, coeff * this_coeff[1])
                self.getCoefficients(tree.getRight(), coeff_list, coeff * this_coeff[1])
            elif(node == tree.ATTR):
                attr = tree.getAttribute()
                coeff_list[ attr ] = coeff
            else:
                return None
            
    def calculateShares(self, secret, tree, _type=dict):
        attr_list = []
        self.compute_shares(secret, tree, attr_list)
        if _type == list:
            return attr_list
        else: # assume dict
            share = {}
            for i in range(0, len(attr_list)):
                share[ attr_list[i][0] ] = attr_list[i][1]
            return share
    
    def compute_shares(self, secret, subtree, List):
        k = 0
        if(subtree == None):
            return None
        
        type = subtree.getNodeType()
        if(type == subtree.ATTR):
            # visiting a leaf node
            t = (subtree.getAttribute(), secret)
            List.append(t)
            return None
        elif(type == subtree.OR):
            k = 1
        elif(type == subtree.AND):
            k = 2
        else:
            return None
        # generate shares for k and n        
        shares = self.genShares(secret, k, n=2)
        # recursively generate shares for children nodes
        self.compute_shares(shares[1], subtree.getLeft(), List)
        self.compute_shares(shares[2], subtree.getRight(), List)
        
    def createPolicy(self, policy_string):
        return self.parser.parse(policy_string)
    
    def prune(self, policy, attributes):
        return self.parser.prune(policy, attributes)
    
    def getAttributeList(self, Node, List):
        if(Node == None):
            return None
        # V, L, R
        if(Node.getNodeType() == Node.ATTR):
            List.append(Node.getAttribute())
        else:
            self.getAttributeList(Node.getLeft(), List)
            self.getAttributeList(Node.getRight(), List)
        return None
        
