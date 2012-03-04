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
        self.type = None

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

    def getType(self):
        return self.type

    def traverseAssignNodeRecursive(self, node):
        if (node.type == ops.PAIR):
            self.hasPairings = True
        elif (node.type == ops.ATTR):
            varName = getFullVarName(node)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)
        elif (node.type == ops.TYPE):
            varType = getVarType(node)
            if (varType not in types):
                sys.exit("Variable type extracted by SDL parser in traverseAssignNodeRecursive is not one of the supported types.")
            if (self.type != None):
                sys.exit("Node passed to traverseAssignNodeRecursive in VarInfo has multiple subnodes on right side of assignment of type " + ops.TYPE)
            self.type = varType

        listNodes = None

        try:
            listNodes = node.listNodes
        except:
            pass

        if (listNodes != None):
            for listNode in listNodes:
                self.varDeps.append(listNode)

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

        self.traverseAssignNodeRecursive(self.assignNode.right)

        if (M in self.varDeps):
            self.protectsM = True

        if ( (len(self.varDeps) == 1) and (self.varDeps[0] in OTHER_TYPES) ):
            if (self.type != None):
                sys.exit("Node passed to traverseAssignNode in VarInfo has multiple node types in right subnode.")
            self.type = self.varDeps[0]

    def setAssignNode(self, assignNode):
        if (type(assignNode).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("Assignment node passed to VarInfo is invalid.")

        self.assignNode = assignNode

        self.traverseAssignNode()

    def setLineNo(self, lineNo):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Line number passed to VarInfo is invalid.")

        self.lineNo = lineNo
