from batchlang import *
from batchtechniques import AbstractTechnique

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
        self.debug      = False
        
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
        if (lsize == 1 and rsize > 1) or (lsize == rsize):
            # move from left to right
            if self.debug: print("Moving from L to R: ", node)
            new_left = self.createExp(BinaryNode.copy(node.left), BinaryNode.copy(self.inverse))
            new_node = self.createMul(BinaryNode.copy(node.right), new_left)
            if self.debug: print("Result L to R: ", new_node)
            return new_node
        elif lsize > 1 and rsize == 1:
            # move from right to left
            if self.debug: print("Moving from R to L: ", node)
            new_right = self.createExp(BinaryNode.copy(node.right), BinaryNode.copy(self.inverse))
            new_node = self.createMul(BinaryNode.copy(node.left), new_right)
            if self.debug: print("Result R to L: ", new_node)
            return new_node
        else:
            print("CE: missing case!")
            print("node: ", lsize, rsize, node)
            return
        