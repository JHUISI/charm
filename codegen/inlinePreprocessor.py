import sys

sys.path.extend(['../', '../sdlparser'])

from SDLParser import *

# reserved keyword
tmpList = "tmpList"

class ListCheck:
    def __init__(self, varCount):
        self.check = False
        self.varCount = varCount
        self.newNodeList = None
        self.newTypes = {}
    
    def visit(self, node, data):
        pass
    
    def visit_eq(self, node, data):
        lhsIsList = False
        self.newNodeList = []
        if Type(node.left) == ops.ATTR:
            lhs = str(node.left)
            if lhs.find(LIST_INDEX_SYMBOL) != -1 and Type(node.right) == ops.LIST:
                #print("DEBUG: isListCheck True: ", node)
                tmpAttrNode = BinaryNode(tmpList + str(self.varCount))
                eqNode1 = BinaryNode(ops.EQ, tmpAttrNode, BinaryNode.copy(node.right))
                eqNode2 = BinaryNode(ops.EQ, BinaryNode.copy(node.left), tmpAttrNode)
                self.varCount += 1
                self.newNodeList.extend([eqNode1, eqNode2])
                # create new var type
                v = VarType()
                v.setType(types.list)
                self.newTypes[ str(tmpAttrNode) ] = v
                lhsIsList = True
        self.check = lhsIsList

    def isMatch(self):
        return self.check
    
    def getNewNodes(self):
        return self.newNodeList
    
    def getVarCount(self):
        return self.varCount
    
    def getNewVarTypes(self):
        return self.newTypes
    

# TODO: add the same functionality for dot products
class DotProdCheck:
    def __init__(self, varCount):
        self.check = False
        self.varCount = varCount
        self.newNodeList = None
        self.newTypes = {}
    
    def visit(self, node, data):
        pass
    
    def visit_on(self, node, data):
        pass