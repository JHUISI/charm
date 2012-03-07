import sys
from SDLang import *

class ForLoop:
    def __init__(self):
        self.startVal = None
        self.endVal = None
        self.startLineNo = None
        self.endLineNo = None
        self.funcName = None
        self.statementNodeList = None

    def getStartVal(self):
        return self.startVal

    def getEndVal(self):
        return self.endVal

    def getStartLineNo(self):
        return self.startLineNo

    def getEndLineNo(self):
        return self.endLineNo

    def getFuncName(self):
        return self.funcName

    def getStatementNodeList(self):
        return self.statementNodeList
