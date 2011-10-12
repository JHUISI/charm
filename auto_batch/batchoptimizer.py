
from batchlang import *
import batchparser
import string

class InstanceFinder:
    def __init__(self):
        # keys must match
        self.instance = {}
    
    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        left = node.left
        right = node.right
        if left.type == ops.ATTR:
            if right.type == ops.ATTR:
                self.record(str(left), str(right))
            elif right.type == ops.MUL:
                # a ^ (b * c) ==> a : b, a : c
                value_1 = right.left
                value_2 = right.right
                if value_1.type == ops.ATTR:
                    self.record(str(left), str(value_1))
                if value_2.type == ops.ATTR:
                    self.record(str(left), str(value_2))
            else:
                # dont care for now
                return

    def record(self, key, value):
#        print("key =>", key, ", value =>", value)
        if self.instance.get( key ):
            if self.instance[ key ].get( value ):
                self.instance[ key ][ value ] += 1
            else:
                self.instance[ key ][ value ] = 1
            return

        self.instance[ key ] = { value: 1 }
        return


# substitute nodes that can be precomputed with a stub
# variable that is computed later
class Substitute:
    def __init__(self, op_instance, precomp, variables):
        # assert input is not equal to None
        self.instance = op_instance
        self.inst_map = {}
        self.precomp = precomp
        self.vars = variables
        self.prefix = 'pre' # self.prefix + self.alpha[cnt]; cnt += 1
        self.alpha = string.ascii_uppercase
        self.cnt = 0

    def canExpBePrecomputed(self, base, exp):
        for i in self.instance.keys():
            for j in self.instance[ i ].keys():
                if self.instance[ i ][ j ] > 1 and (i == str(base) and j == str(exp)):
                    print(i, "^", j, " : can be precomputed!")
                    if base.attr_index: index = base.attr_index[0] 
                    elif exp.attr_index: index = exp.attr_index[0]
                    else: index = None
                    _key = self.record(str(i), str(j), index)

# COMMENT OUT FOR NOW => STRINGS FOR NOW                    
                    k = BinaryNode(_key)
#                    n = BinaryNode(ops.EXP)
#                    n.left = base
#                    n.right = exp
                    self.precomp[ _key ] = str(i) + "^" + str(j)
                    self.vars[ k.getAttribute() ] = self.vars[ base.getAttribute() ]  
                    # can we find a precomp key for this? if so, return it
                    # otherwise, create one and return it.(IMPORTANT!!!!)
                    return _key
        return False

    def record(self, key, value, index=None):
#        print("key =>", key, ", value =>", value)
        if self.inst_map.get( key ):
            if self.inst_map[ key ].get( value ):
                var = self.inst_map[ key ][ value ]
                print("recovered key =>", var)
                return var
            else:
                self.cnt += 1
                if index: var_index = index
                else: var_index = ''
                self.inst_map[ key ][ value ] = self.prefix + self.alpha[self.cnt] + '_' + var_index
                return self.inst_map[ key ][ value ]
            return 
        
        if index: var_index = index
        else: var_index = ''
        self.inst_map[ key ] = { value: self.prefix + self.alpha[self.cnt] + '_' + var_index }
        self.cnt += 1
        print("found key =>", self.inst_map[ key ][ value ])
        return self.inst_map[ key ][ value ]

    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        left = node.left
        right = node.right
        if left.type == ops.ATTR:
            if right.type == ops.ATTR:
                key = self.canExpBePrecomputed(left, right)
                if key:
                    # make substitution
                    new_node = BinaryNode(key)
                    batchparser.addAsChildNodeToParent(data, new_node)
                else:
                    pass # no need to apply any substitutions
            elif right.type == ops.MUL:
                node_1 = right.left
                node_2 = right.right
                if node_1.type == ops.ATTR:
                    key = self.canExpBePrecomputed(left, node_1)
                    if key:
                        # a ^ (b * c) ==> A ^ c (if a^b can be precomputed)
                        new_node1 = BinaryNode(ops.EXP)
                        new_node1.left = BinaryNode(key)
                        new_node1.right = node_2                        
                        batchparser.addAsChildNodeToParent(data, new_node1)
                
                if node_2.type == ops.ATTR:
                    key = self.canExpBePrecomputed(left, node_2)
                    if key:
                        # a ^ (b * c) ==> A ^ b (if a^c can be precomputed)                        
                        new_node2 = BinaryNode(ops.EXP)
                        new_node2.left = BinaryNode(key)
                        new_node2.right = node_1
                        batchparser.addAsChildNodeToParent(data, new_node2)
