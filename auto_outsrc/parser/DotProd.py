import sys
from SDLang import *

class DotProd:
    def __init__(self):
        self.startVal = None
        self.endVal = None
        self.loopVar = None
        self.lineNo = None
        self.funcName = None
        self.binaryNode = None

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

    def setDotProdObj(self, node, lineNo, funcName):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Problem with line number passed in to setDotProdObj in DotProd.py.")

        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("Problem with function name passed in to setDotProdObj in DotProd.py.")

        self.binaryNode = node
        self.lineNo = lineNo
        self.funcName = funcName

        self.startVal = int(node.left.left.right.attr)
        self.endVal = str(node.left.right.attr)
        self.loopVar = str(node.left.left.left.attr)
