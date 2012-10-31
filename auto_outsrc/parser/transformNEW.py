from SDLParser import *
from outsrctechniques import *
import config
import sys

def addTransformFuncIntro():
    firstLineOfDecryptFunc = getStartLineNoOfFunc(decryptFuncName)
    transformFuncIntro = ["BEGIN :: func:" + transformFuncName + "\n"]
    appendToLinesOfCode(transformFuncIntro, firstLineOfDecryptFunc)

def getLastLineOfTransform(stmtsDec):
    for lineNo in stmtsDec:
        stmt = stmtsDec[lineNo]
        if (str(stmt.getAssignNode().left) == M):
            return (lineNo - 1)

    sys.exit("getLastLineOfTransform in transformNEW:  could not locate the line in decrypt where the message is assigned its value.")

def appendToKnownVars(node, knownVars):
    listNodes = []

    try:
        listNodes = node.listNodes
    except:
        sys.exit("appendToKnownVars in transformNEW.py:  couldn't extract listNodes from node passed in.")

    for listNode in listNodes:
        if (listNode not in knownVars):
            knownVars.append(listNode)
    
def transformNEW(varsThatAreBlindedDict):
    addTransformFuncIntro()
    (stmtsDec, typesDec, depListDec, depListNoExponentsDec, infListDec, infListNoExponentsDec) = getFuncStmts(decryptFuncName)
    astNodes = getAstNodes()
    firstLineOfDecryptFunc = getStartLineNoOfFunc(decryptFuncName)
    lastLineOfDecryptFunc = getEndLineNoOfFunc(decryptFuncName)
    lastLineOfTransform = getLastLineOfTransform(stmtsDec)

    print("\n\n\n")

    knownVars = []

    for lineNo in range((firstLineOfDecryptFunc + 1), (lastLineOfTransform + 1)):
        if (str(astNodes[lineNo - 1].left) == inputKeyword):
            appendToKnownVars(astNodes[lineNo - 1].right, knownVars)
        currentNode = astNodes[lineNo - 1].right
        if (currentNode == None):
            continue
        if (currentNode.type == ops.EXPAND):
            appendToKnownVars(currentNode, knownVars)

    print(knownVars)

    #print(stmtsDec)
    sys.exit("TEST")
