import sys
from SDLang import *
from VarInfo import *

class IfElseBranch:
    def __init__(self):
        self.startLineNo = None
        self.endLineNo = None
        self.elseLineNos = []
        self.conditionalAsNode = None
        self.assignStmtsAsBinNodes_Dict = {}
        self.assignStmtsAsVarInfoObjs_Dict = {}
        self.funcName = None
        self.topLevelNode = True
        self.varDeps = []
        self.varDepsNoExponents = []
        self.equalityDepsNoExponents = []
        self.hashArgsInAssignNode = []
        
    def getStartLineNo(self):
        return self.startLineNo

    def getEndLineNo(self):
        return self.endLineNo

    def getElseLineNos(self):
        return self.elseLineNos

    def getConditionalAsNode(self):
        return self.conditionalAsNode

    def getAssignStmtsAsBinNodes_Dict(self):
        return self.assignStmtsAsBinNodes_Dict

    def getAssignStmtsAsVarInfoObjs_Dict(self):
        return self.assignStmtsAsVarInfoObjs_Dict

    def getFuncName(self):
        return self.funcName

    def getVarDeps(self):
        return self.varDeps

    def getVarDepsNoExponents(self):
        return self.varDepsNoExponents

    def getEqualityDepsNoExponents(self):
        return self.equalityDepsNoExponents
    
    def isTopLevelNode(self):
        return self.topLevelNode

    def setStartLineNo(self, startLineNo):
        if ( (type(startLineNo) is not int) or (startLineNo < 1) ):
            sys.exit("setStartLineNo in IfElseBranch.py:  starting line number passed in is invalid.")

        self.startLineNo = startLineNo

    def setEndLineNo(self, endLineNo):
        if ( (type(endLineNo) is not int) or (self.startLineNo >= endLineNo) ):
            sys.exit("setEndLineNo in IfElseBranch.py:  ending line number passed in is invalid.")

        self.endLineNo = endLineNo

    def appendToElseLineNos(self, elseLineNo):
        if (type(elseLineNo) is not int):
            sys.exit("appendToElseLineNos in IfElseBranch.py:  else line number passed in is not of type int.")

        lenElseLineNos = len(self.elseLineNos)

        if (lenElseLineNos == 0):
            if (self.startLineNo >= elseLineNo):
                sys.exit("appendToElseLineNos in IfElseBranch.py:  else line number passed in is less than or equal to the starting line number of this if branch.")
        else:
            if (self.elseLineNos[lenElseLineNos - 1] >= elseLineNos):
                sys.exit("appendToElseLineNos in IfElseBranch.py:  else line number passed in is less than or equal to the previously added else line number.")

        self.elseLineNos.append(elseLineNo)

    def checkLineNoAgainstDict(self, dictToCheck, lineNo):
        if (type(lineNo) is not int):
            sys.exit("checkLineNoAgainstDict in IfElseBranch.py:  line number passed in is not of type int.")

        if (len(dictToCheck) == 0):
            if (lineNo <= self.startLineNo):
                sys.exit("checkLineNoAgainstDict in IfElseBranch.py:  line number passed in is less than or equal to the start line number.")
            return

        existingLineNos = list(dictToCheck.keys())
        existingLineNos.sort()
        lastLineNo = existingLineNos[len(existingLineNos) - 1]
        if (lineNo <= lastLineNo):
            sys.exit("checkLineNoAgainstDict in IfElseBranch.py:  line number passed in is less than or equal to the last line number added.")

    def appendToBinaryNodeDict(self, node, line_number):
        if (type(node).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("appendToBinaryNodeDict in IfElseBranch.py:  node parameter passed in is not of type Binary Node.")

        self.checkLineNoAgainstDict(self.assignStmtsAsBinNodes_Dict, line_number)
        self.assignStmtsAsBinNodes_Dict[line_number] = node

    def appendToVarInfoNodeList(self, varInfoObj, line_number):
        if (type(varInfoObj).__name__ != VAR_INFO_CLASS_NAME):
            sys.exit("appendToVarInfoNodeList in IfElseBranch.py:  varInfo object parameter passed in is not of type VarInfo.")

        self.checkLineNoAgainstDict(self.assignStmtsAsVarInfoObjs_Dict, line_number)
        self.assignStmtsAsVarInfoObjs_Dict[line_number] = VarInfo.copy(varInfoObj)
#        self.assignStmtsAsVarInfoObjs_Dict[line_number] = varInfoObj

    def traverseAssignNodeRecursive(self, node, parent_type, isExponent):
        if (node.type == ops.PAIR):
            self.hasPairings = True            
        elif (node.type == ops.HASH):
            if (node.left.type not in [ops.ATTR, ops.CONCAT]): # JAA: added ops.CONCAT to account for hashing a concatenation of multiple variables
                sys.exit("traverseAssignNodeRecursive in VarInfo.py:  left child node of ops.HASH node encountred is not of type ATTR or CONCAT.")
            hashInputName = getFullVarName(node.left, False)
            if (hashInputName not in self.hashArgsInAssignNode):
                self.hashArgsInAssignNode.append(hashInputName)
        if (node.type == ops.ATTR):
            varName = getFullVarName(node, True)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)
                if (isExponent == False):
                    self.varDepsNoExponents.append(varName)

        if (node.left != None):
            self.traverseAssignNodeRecursive(node.left, node.type, False)
        if (node.right != None):
            if (node.type == ops.EXP):
                self.traverseAssignNodeRecursive(node.right, node.type, True)
            else:
                self.traverseAssignNodeRecursive(node.right, node.type, False)


    def traverseAssignNode(self):
        if (self.conditionalAsNode == None):
            sys.exit("IfElseBranch: Attempting to run traverseAssignNode in VarInfo when self.conditionalAsNode is still None.")

        if (self.conditionalAsNode.type in [ops.AND, ops.OR]):
            self.traverseAssignNodeRecursive(self.conditionalAsNode.left, self.conditionalAsNode.type, False)
            self.traverseAssignNodeRecursive(self.conditionalAsNode.right, self.conditionalAsNode.type, False)
        elif (self.conditionalAsNode.type in [ops.EQ_TST, ops.NON_EQ_TST]):
            self.traverseAssignNodeRecursive(self.conditionalAsNode, self.conditionalAsNode.type, False)
        #sys.exit("IfElseBranch: unrecognized conditional structure: ", self.conditionalAsNode)

    def updateIfElseBranchStruct(self, node, startLineNo, funcName):
        if (node.type != ops.IF):
            sys.exit("updateIfElseBranchStruct in IfElseBranch.py was passed a node that is not of type " + str(ops.IF))

        if ( (type(startLineNo) is not int) or (startLineNo < 1) ):
            sys.exit("Problem with start line number passed to updateIfElseBranchStruct in IfElseBranch.py.")
        self.startLineNo = startLineNo

        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("Problem with function name passed to updateIfElseBranchStruct in IfElseBranch.py.")
        self.funcName = funcName

        self.conditionalAsNode = node.left
        self.traverseAssignNode()