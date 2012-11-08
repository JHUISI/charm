import sys
from SDLang import *

class ForLoopInner:
    def __init__(self):
        self.startVal = None
        self.endVal = None
        self.loopVar = None
        self.startLineNo = None
        self.endLineNo = None
        self.funcName = None
        self.binaryNodeList = []
        self.varInfoNodeList = []

    def getStartVal(self):
        return self.startVal

    def getEndVal(self):
        return self.endVal

    def getLoopVar(self):
        return self.loopVar

    def getStartLineNo(self):
        return self.startLineNo

    def getEndLineNo(self):
        return self.endLineNo

    def getFuncName(self):
        return self.funcName

    def getBinaryNodeList(self):
        return self.binaryNodeList

    def getVarInfoNodeList(self):
        return self.varInfoNodeList

    def updateForLoopInnerStruct(self, node, startLineNo, funcName):
        if (node.type != ops.FORINNER):
            sys.exit("updateForLoopInnerStruct in ForLoopInner was passed a node that is not of type " + str(ops.FORINNER))

        if ( (type(startLineNo) is not int) or (startLineNo < 1) ):
            sys.exit("Problem with start line number passed to updateForLoopInnerStruct in ForLoopInner.")
        self.startLineNo = startLineNo

        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("Problem with function name passed to updateForLoopInnerStruct in ForLoopInner.")
        self.funcName = funcName

        loopVar = node.left.left.attr
        if ( (type(loopVar) is not str) or (len(loopVar) == 0) ):
            sys.exit("Problem with loop variable extracted in updateForLoopInnerStruct method in ForLoopInner.")
        self.loopVar = loopVar

        self.startVal = node.left.right.attr
        self.endVal = node.right.attr

    def setEndLineNo(self, endLineNo):
        if ( (type(endLineNo) is not int) or (endLineNo < 1) ):
            sys.exit("Problem with ending line number passed to setEndLineNo in ForLoopInner.")

        if (self.startLineNo >= endLineNo):
            sys.exit("setEndLineNo in ForLoopInner.py:  end line number passed in is less than or equal to start line number.")

        self.endLineNo = endLineNo

    def appendToBinaryNodeList(self, binaryNode):
        self.binaryNodeList.append(binaryNode)

    def appendToVarInfoNodeList(self, varInfoNode):
        self.varInfoNodeList.append(varInfoNode)
