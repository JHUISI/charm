import sys
from SDLang import *
from config import *

class VarInfo:
    def __init__(self):
        self.assignNode = None
        self.lineNo = None
        self.varDeps = None
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

    def getAssignNode(self):
        return self.assignNode

    def getLineNo(self):
        return self.lineNo

    def getVarDeps(self):
        return self.varDeps

    def getHasPairings(self):
        return self.hasPairings

    def getProtectsM(self):
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

    def traverseAssignNodeRecursive(self, node):
        if (node.type == ops.PAIR):
            self.hasPairings = True
        elif (node.type == ops.ATTR):
            varName = getFullVarName(node)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)
        elif (node.type == ops.FUNC):
            userFuncName = getFullVarName(node)
            if (userFuncName == INIT_FUNC_NAME):
                if (self.initCallHappenedAlready == True):
                    sys.exit("traverseAssignNodeRecursive found multiple calls to " + INIT_FUNC_NAME + " for the same variable in the same function.")
                self.initCallHappenedAlready = True
                listNodes = getListNodeNames(node)
                if (len(listNodes) != 1):
                    sys.exit("Init function call discovered by traverseAssignNodeRecursive has a number of arguments other than 1 (not supported).")
                self.initValue = listNodes[0]
                self.initCall = True
        elif (node.type == ops.TYPE):
            if (self.funcName == TYPES_HEADER):
                varType = getVarType(node)
                if (self.type != types.NO_TYPE):
                    sys.exit("TraverseAssignNodeRecursive found multiple type assignments to same variable in " + str(self.funcName) + " function.")
                self.type = varType

        addListNodesToList(node, self.varDeps)

        if (node.left != None):
            self.traverseAssignNodeRecursive(node.left)
        if (node.right != None):
            self.traverseAssignNodeRecursive(node.right)

    def traverseAssignNode(self):
        if (self.assignNode == None):
            sys.exit("Attempting to run traverseAssignNode in VarInfo when self.assignNode is still None.")

        self.varDeps = []
        self.hasPairings = False
        self.protectsM = False

        if (self.assignNode.right.type == ops.LIST):
            self.isList = True
            self.type = ops.LIST
            addListNodesToList(self.assignNode.right, self.listNodesList)

        self.traverseAssignNodeRecursive(self.assignNode.right)

        if (M in self.varDeps):
            self.protectsM = True

    def setAssignNode(self, assignNode, funcName):
        if (type(assignNode).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("Assignment node passed to VarInfo is invalid.")

        self.initCall = False
        self.assignNode = assignNode
        self.funcName = funcName
        self.traverseAssignNode()

        self.beenSet = not(self.initCall)

    def setLineNo(self, lineNo):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Line number passed to VarInfo is invalid.")

        self.lineNo = lineNo
