
from batchparser import addAsChildNodeToParent
from batchlang import *
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
                    


class Subsitute:
    def __init__(self, op_instance, precomp):
        # assert input is not equal to None
        self.instance = op_instance
        self.precomp = precomp
        self.prefix = 'pre' # self.prefix + self.alpha[cnt]; cnt += 1
        self.alpha = string.ascii_uppercase
        self.cnt = 0

    def canBePrecomputed(self, base, exp):
        print("Count =>", self.instance)
        for i in self.instance.keys():
            for j in self.instance[ i ].keys():
                if self.instance[ i ][ j ] > 1 and (i == str(base) and j == str(exp)):
                    print(i, "^", j, " : can be precomputed!") 
                    # can we find a precomp key for this? if so, return it
                    # otherwise, create one and return it.(IMPORTANT!!!!)
                    return True
        return False

    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        left = node.left
        right = node.right
        if left.type == ops.ATTR:
            if right.type == ops.ATTR:
                key = self.canBePrecomputed(left, right)
                if key:
                    # make substitution
                    new_node = BinaryNode(key)
                    addAsChildNodeToParent(data, new_node)
                else:
                    pass # no need to apply any substitutions
                    
