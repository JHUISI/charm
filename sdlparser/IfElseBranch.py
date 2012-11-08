import sys
from SDLang import *

class IfElseBranch:
    def __init__(self):
        self.startLineNo = None
        self.endLineNo = None
        self.elseLineNos = []
        self.conditionalAsNode = None
        self.assignStmtsAsBinNodes_Dict = {}
        self.assignStmtsAsVarInfoObjs_Dict = {}
        self.funcName = None

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
        self.assignStmtsAsVarInfoObjs_Dict[line_number] = varInfoObj

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
