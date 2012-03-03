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

    def traverseAssignNodeRecursive(self, node):
        if (node.type == ops.PAIR):
            self.hasPairings = True
        elif (node.type == ops.ATTR):
            varName = getFullVarName(node)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)

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

    def setAssignNode(self, assignNode):
        if (type(assignNode).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("Assignment node passed to VarInfo is invalid.")

        self.assignNode = assignNode

        self.traverseAssignNode()

    def setLineNo(self, lineNo):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Line number passed to VarInfo is invalid.")

        self.lineNo = lineNo
