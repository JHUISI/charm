import sys
from SDLang import *
from config import *

class DotProd:
    def __init__(self):
        self.startVal = None
        self.endVal = None
        self.loopVar = None
        self.lineNo = None
        self.funcName = None
        self.binaryNode = None
        self.distinctVarsInCalcList = None
        self.distinctIndVarsInCalcList = None

    def getStartVal(self):
        return self.startVal

    def getEndVal(self):
        return self.endVal

    def getLoopVar(self):
        return self.loopVar

    def getLineNo(self):
        return self.lineNo

    def getFuncName(self):
        return self.funcName

    def getBinaryNode(self):
        return self.binaryNode

    def getDistinctVarsInCalcList(self):
        return self.distinctVarsInCalcList

    def getDistinctIndVarsInCalcList(self):
        return self.distinctIndVarsInCalcList

    def findDistinctVarsInCalc(self, node):
        if (node.type == ops.ATTR):
            nodeName = getFullVarName(node, False)
            if ( (nodeName not in self.distinctVarsInCalcList) and (nodeName.isdigit() == False) ):
                self.distinctVarsInCalcList.append(nodeName)

            nodeNameSplit = nodeName.split(LIST_INDEX_SYMBOL)
            if (len(nodeNameSplit) > 1):
                for nodeNameCounter in range(1, len(nodeNameSplit)):
                    nodeNameSplit_Ind = nodeNameSplit[nodeNameCounter]
                    if (nodeNameSplit_Ind.isdigit() == True):
                        continue
                    if (nodeNameSplit_Ind not in self.distinctVarsInCalcList):
                        self.distinctVarsInCalcList.append(nodeNameSplit_Ind)
                    if (nodeNameSplit_Ind not in self.distinctIndVarsInCalcList):
                        self.distinctIndVarsInCalcList.append(nodeNameSplit_Ind)
                if (nodeNameSplit[0] not in self.distinctIndVarsInCalcList):
                    self.distinctIndVarsInCalcList.append(nodeNameSplit[0])
            else:
                if (nodeName not in self.distinctIndVarsInCalcList):
                    self.distinctIndVarsInCalcList.append(nodeName)

        if (node.left != None):
            self.findDistinctVarsInCalc(node.left)
        if (node.right != None):
            self.findDistinctVarsInCalc(node.right)

    def setDistinctVarsInCalcList(self):
        self.distinctVarsInCalcList = []
        self.distinctIndVarsInCalcList = []

        self.findDistinctVarsInCalc(self.binaryNode.right)

        if (len(self.distinctVarsInCalcList) > len(lambdaLetters) ):
            sys.exit("setDistinctVarsInCalcList in DotProd.py:  number of distinct variables in calculation found exceeds maximum limit allowed (the number of elements in lambdaLetters in config.py.")

    def setDotProdObj(self, node, lineNo, funcName):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Problem with line number passed in to setDotProdObj in DotProd.py.")

        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("Problem with function name passed in to setDotProdObj in DotProd.py.")

        self.binaryNode = node
        self.lineNo = lineNo
        self.funcName = funcName

        self.startVal = str(node.left.left.right.attr)
        self.endVal = str(node.left.right.attr)
        self.loopVar = str(node.left.left.left.attr)

        self.setDistinctVarsInCalcList()
