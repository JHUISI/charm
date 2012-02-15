from batchlang import *
from batchtechniques import AbstractTechnique
from batchparser import *

class TestForMultipleEq:
    def __init__(self):
        self.multiple = False
    
    def visit_and(self, node, data):
        if Type(node.left) == Type(node.right) and Type(node.left) == ops.EQ_TST:
            self.multiple = True
            
    def visit(self, node, data):
        pass

class CombineMultipleEq(AbstractTechnique):
    def __init__(self, sdl_data=None, variables=None, meta=None):
        if sdl_data:
            AbstractTechnique.__init__(self, sdl_data, variables, meta)
        self.inverse = BinaryNode("-1")
        self.finalAND   = [ ]
        self.deltaCount = { }
        self.debug      = True
        
    def visit_and(self, node, data):
        left = right = BinaryNode("1")
        #print("handle left :=>", node.left, node.left.type)
        #print("handle right :=>", node.right, node.right.type)        
        if Type(node.left) == ops.EQ_TST:
            left = self.visit_equality(node.left)
        if Type(node.right) == ops.EQ_TST:
            right = self.visit_equality(node.right)
        combined_eq = BinaryNode(ops.EQ_TST, left, right)
        if self.debug: print("Combined eq: ", combined_eq)
        self.finalAND.append(combined_eq)
        return
    
    # won't be called automatically (ON PURPOSE)
    def visit_equality(self, node):
        # count number of nodes on each side
        lchildnodes = []
        rchildnodes = []
        getListNodes(node.left, Type(node), lchildnodes)
        getListNodes(node.right, Type(node), rchildnodes)        
        lsize = len(lchildnodes)
        rsize = len(rchildnodes)
        _list = [ops.EXP, ops.PAIR, ops.ATTR]
        if (lsize == 1 and rsize > 1) or (lsize == rsize):
            # move from left to right
            if self.debug: print("Moving from L to R: ", node)
            new_left = self.createExp2(BinaryNode.copy(node.left), BinaryNode.copy(self.inverse), _list)
            new_node = self.createMul(BinaryNode.copy(node.right), new_left)
            if self.debug: print("Result L to R: ", new_node)
            return new_node
        elif lsize > 1 and rsize == 1:
            # move from right to left
            if str(node.right) != "1":
                if self.debug: print("Moving from R to L: ", node)
                new_right = self.createExp2(BinaryNode.copy(node.right), BinaryNode.copy(self.inverse), _list)
                new_node = self.createMul(BinaryNode.copy(node.left), new_right)
            else:
                new_node = node.left
            if self.debug: print("Result R to L: ", new_node)
            return new_node
        else:
            print("CE: missing case!")
            print("node: ", lsize, rsize, node)
            return

class SmallExpTestMul:
    def __init__(self, prefix=None):
        self.prefix = prefix
        
    def visit(self, node, data):
        pass

    # find  'prod{i} on x' transform into ==> 'prod{i} on (x)^delta_i'
    def visit_eq_tst(self, node, data):
        # Restrict to only product nodes that we've introduced for 
        # iterating over the N signatures
        delta = BinaryNode("delta")
        _list = [ops.EXP, ops.PAIR, ops.ATTR]
        if str(node.left) != "1":
            node.left = AbstractTechnique.createExp2(BinaryNode.copy(node.left), delta, _list)            
        if str(node.right) != "1":
            node.right = AbstractTechnique.createExp2(BinaryNode.copy(node.right), BinaryNode.copy(delta), _list)
            