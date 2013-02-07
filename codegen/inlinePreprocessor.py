import sys

sys.path.extend(['../', '../sdlparser'])

from SDLParser import *

# reserved keyword
tmpList = "tmpList"

def traceTypeInVarType(varName):
    varTs = getVarTypes()[TYPES_HEADER]
    v = varName.split(LIST_INDEX_SYMBOL)
    v0 = v[0]
    v1 = varTs[v0].getListNodesList()
    if len(v1) > 0 and v1[0] in varTs.keys():
        v1Key = v1[0] # next level
        v2 = varTs[v1Key]
        v2List = v2.getListNodesList()
        if v2.getType() == types.list and len(v2List) == 1:
            #print("v2List: ", str(types.list) + v2List[0])
            newType = str(types.list) + str(v2List[0])
            if newType in types.getList(): return types[newType]
    
    print("ERROR: need to include type in TYPES section for %s" % v0)
    return types.NO_TYPE


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
            if lhs.find(LIST_INDEX_SYMBOL) != -1 and Type(node.right) == ops.FUNC:
                if str(node.right).find(INIT_FUNC_NAME) != -1: #str(node.listNodes[0]) == types.list:
                    if str(node.right.listNodes[0]) == str(types.list):
                        #print("DEBUG: transform this: ", node)
                        tmpAttrNode = BinaryNode(tmpList + str(self.varCount))
                        eqNode1 = BinaryNode(ops.EQ, tmpAttrNode, BinaryNode.copy(node.right))
                        eqNode2 = BinaryNode(ops.EQ, BinaryNode.copy(node.left), tmpAttrNode)
                        self.varCount += 1
                        self.newNodeList.extend([eqNode1, eqNode2])
                        # create new var type
                        v = VarType()
                        tmpType = traceTypeInVarType(lhs)
                        if tmpType == types.NO_TYPE:
                            v.setType(types.list)
                        else:
                            v.setType(tmpType)
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
