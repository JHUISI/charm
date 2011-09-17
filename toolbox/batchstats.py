# Used for benchmarking operations of intermediate representation
# and providing routines to determine when independent verification 
# is more efficient than batch verification.

from batchlang import *

class RecordOperations:
    def __init__(self, vars):
        print("vars =>", vars)
        self.debug = False
        self.vars_def = vars
        # need to have type assignments 
        grps = {'G1':0, 'G2':0, 'GT':0 }
        self.ops = {'pair':0, 'mul':grps.copy(), 'exp':grps.copy() }
    
    def visit(self, node, data):
        pass
    
    def visit_pair(self, node, data):
        self.ops['pair'] += 1

    # track operations in G1, G2, GT      
    def visit_mul(self, node, data):
        if node.left:
            base_type = self.deriveNodeType(node.left)
            self.ops[ 'mul' ][ base_type ] += 1
            if self.debug: 
                print("mul: node.left =>", node.left)            
                print("mul: type =>", base_type)

    # track operations in G1, G2, GT    
    def visit_exp(self, node, data):
        if node.left:
            base_type = self.deriveNodeType(node.left)
            self.ops[ 'exp' ][ base_type ] += 1
            if self.debug:
                print("exp: node.left =>", node.left)
                print("exp: type =>", base_type)
    
    def __str__(self):
        return str(self.ops)
    
    def deriveNodeType(self, node):
        if node.type == ops.ATTR:
            _type = node.attr
        elif node.type == ops.HASH:
            _type = str(node.right.attr)
            return _type
        elif node.type == ops.EXP:
            return self.deriveNodeType(node.left)
        elif node.type == ops.PAIR:
            return 'GT'
        elif node == None:
            return None
        else:
            return self.deriveNodeType(node.left)
#        print("printing type =>", _type)
#        print("node =>", node)
        return self.vars_def[_type]
            