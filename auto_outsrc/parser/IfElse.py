import sys
from SDLang import *

class IfElse:
    def __init__(self):
        self.startLineNo = None
        self.endLineNo = None
        self.conditionalAsNode = None
        self.conditionalAsString = None
        self.thenNodesAsBinNodes_List = None
        self.thenNodesAsVarInfoObjs_List = None
        self.elseNodesAsBinNodes_List = None
        self.elseNodesAsVarInfoObjs_List = None

    def getStartLineNo(self):
        return self.startLineNo

    def getEndLineNo(self):
        return self.endLineNo

    def getConditionalAsNode(self):
        return self.conditionalAsNode

    def getConditionalAsString(self):
        return self.conditionalAsString

    def getThenNodesAsBinNodes_List(self):
        return self.thenNodesAsBinNodes_List

    def getThenNodesAsVarInfoObjs_List(self):
        return self.thenNodesAsVarInfoObjs_List

    def getElseNodesAsBinNodes_List(self):
        return self.elseNodesAsBinNodes_List

    def getElseNodesAsVarInfoObjs_List(self):
        return self.elseNodesAsVarInfoObjs_List

    def setIfElseStruct(node):
        pass
