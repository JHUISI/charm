import sys
from SDLang import *
from config import *
from DotProd import *

class VarInfo:
    def __init__(self):
        self.assignNode = None
        self.lineNo = None
        self.varDeps = []
        self.varDepsNoExponents = []
        self.hasPairings = None
        self.protectsM = None
        self.initValue = None
        self.beenSet = False
        self.initCall = None
        self.initCallHappenedAlready = False
        self.type = types.NO_TYPE
        self.funcName = None
        self.isList = False
        self.listNodesList = []
        self.dotProdObj = None
        self.outsideForLoopObj = None
        self.outsideIfElseBranchObj = None
        self.hasRandomness = False
        self.isTypeEntryOnly = False
        self.listElementsType = None
    
    @classmethod
    def copy(self, obj):
        v = VarInfo()
        v.assignNode  = obj.assignNode 
        v.lineNo      = obj.lineNo
        v.varDeps     = list(obj.varDeps)
        v.varDepsNoExponents = list(obj.varDepsNoExponents)
        v.hasPairings = obj.hasPairings
        v.protectsM   = obj.protectsM
        v.initValue   = obj.initValue
        v.beenSet     = obj.beenSet
        v.initCall    = obj.initCall
        v.initCallHappenedAlready = obj.initCallHappenedAlready
        v.type        = obj.type
        v.funcName    = obj.funcName
        v.isList      = obj.isList
        v.listNodesList = list(obj.listNodesList)
        v.dotProdObj  = obj.dotProdObj
        v.outsideForLoopObj = obj.outsideForLoopObj
        v.outsideIfElseBranchObj = obj.outsideIfElseBranchObj
        v.hasRandomness = obj.hasRandomness
        v.isTypeEntryOnly = obj.isTypeEntryOnly
        v.listElementsType = obj.listElementsType
        return v
        
    def getAssignNode(self):
        return self.assignNode

    def getLineNo(self):
        return self.lineNo

    def getVarDeps(self):
        return self.varDeps

    def getVarDepsNoExponents(self):
        return self.varDepsNoExponents

    def getAssignVar(self):
        if self.assignNode:
            return self.assignNode.left.getAttribute()
        return None

    def getHasPairings(self):
        return self.hasPairings

    def getProtectsM(self):
        if (self.assignNode == None):
            return False

        # generally, we're not interested in keywords that may reference the message
        if str(self.assignNode.left) in ['input', 'output']:
            return False         
        return self.protectsM

    def getInitValue(self):
        return self.initValue

    def hasBeenSet(self):
        return self.beenSet

    def getInitCall(self):
        return self.initCall

    def getInitCallHappenedAlready(self):
        return self.initCallHappenedAlready

    def getType(self):
        return self.type

    def getFuncName(self):
        return self.funcName

    def getIsList(self):
        return self.isList

    def getListNodesList(self):
        return self.listNodesList

    def getDotProdObj(self):
        return self.dotProdObj

    def getOutsideForLoopObj(self):
        return self.outsideForLoopObj

    def getOutsideIfElseBranchObj(self):
        return self.outsideIfElseBranchObj

    def getHasRandomness(self):
        return self.hasRandomness

    def getIsTypeEntryOnly(self):
        return self.isTypeEntryOnly

    def getListElementsType(self):
        return self.listElementsType

    def traverseAssignNodeRecursive(self, node, isExponent):
        if (node.type == ops.PAIR):
            self.hasPairings = True
        elif (node.type == ops.ATTR):
            varName = getFullVarName(node, True)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)
                if (isExponent == False):
                    self.varDepsNoExponents.append(varName)
        elif (node.type == ops.FUNC):
            userFuncName = getFullVarName(node, True)
            if (userFuncName == INIT_FUNC_NAME):
                if (self.initCallHappenedAlready == True):
                    sys.exit("traverseAssignNodeRecursive found multiple calls to " + INIT_FUNC_NAME + " for the same variable in the same function.")
                self.initCallHappenedAlready = True
                listNodes = getListNodeNames(node)
                if (len(listNodes) != 1):
                    sys.exit("Init function call discovered by traverseAssignNodeRecursive has a number of arguments other than 1 (not supported).")
                self.initValue = listNodes[0]
                if (self.initValue == LIST_TYPE):
                    self.isList = True
                self.initCall = True
        elif (node.type == ops.RANDOM):
            self.hasRandomness = True

        if (self.listElementsType == None):
            addListNodesToList(node, self.varDeps)
            if (isExponent == False):
                addListNodesToList(node, self.varDepsNoExponents)

        if (node.left != None):
            self.traverseAssignNodeRecursive(node.left, False)
        if (node.right != None):
            if (node.type == ops.EXP):
                self.traverseAssignNodeRecursive(node.right, True)
            else:
                self.traverseAssignNodeRecursive(node.right, False)

    def isOnlyListElementsTypeDecl(self, listNode):
        if (listNode.type != ops.LIST):
            sys.exit("isOnlyListElementsTypeDecl in VarInfo.py:  parameter passed in is not of type ops.LIST.")

        listNodeChildren = getListNodeNames(listNode)

        if (len(listNodeChildren) != 1):
            return None

        if (isValidType(listNodeChildren[0]) == True):
            return listNodeChildren[0]

        return None

    def traverseAssignNode(self):
        if (self.assignNode == None):
            sys.exit("Attempting to run traverseAssignNode in VarInfo when self.assignNode is still None.")

        self.hasPairings = False
        self.protectsM = False

        if (self.assignNode.right.type == ops.LIST):
            self.isList = True
            self.type = ops.LIST
            onlyListElementsTypeDecl = self.isOnlyListElementsTypeDecl(self.assignNode.right)
            if (onlyListElementsTypeDecl != None):
                self.listElementsType = onlyListElementsTypeDecl
            else:
                addListNodesToList(self.assignNode.right, self.listNodesList)
        elif ( (self.assignNode.right.type == ops.ON) and (self.assignNode.right.left.type == ops.PROD) ):
            dotProdObj = DotProd()
            dotProdObj.setDotProdObj(self.assignNode.right, self.lineNo, self.funcName)
            self.dotProdObj = dotProdObj

        self.traverseAssignNodeRecursive(self.assignNode.right, False)

        if (M in self.varDeps):
            self.protectsM = True

    def setAssignNode(self, assignNode, funcName, outsideForLoopObj, outsideIfElseBranchObj):
        if (type(assignNode).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("Assignment node passed to VarInfo is invalid.")

        self.initCall = False
        self.assignNode = assignNode
        self.funcName = funcName
        self.outsideForLoopObj = outsideForLoopObj
        self.outsideIfElseBranchObj = outsideIfElseBranchObj

        self.traverseAssignNode()

        self.beenSet = not(self.initCall)

        return self.varDeps

    def updateAssignNode(self, newNode):
        # can only update if assignNode was already set
        if self.assignNode == None: return None
        self.assignNode = newNode
        
    def setLineNo(self, lineNo):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Line number passed to VarInfo is invalid.")

        self.lineNo = lineNo

    def setIsTypeEntryOnly(self, isTypeEntryOnly):
        if (self.isTypeEntryOnly == True):
            sys.exit("setIsTypeEntryOnly in VarInfo.py has been set more than once.")

        if (isTypeEntryOnly != True):
            sys.exit("setIsTypeEntryOnly in VarInfo.py received input that is not valid.")

        self.isTypeEntryOnly = isTypeEntryOnly
