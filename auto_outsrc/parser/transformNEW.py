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
            #print("last lineNo transform is ", lineNo)
            return lineNo

    sys.exit("getLastLineOfTransform in transformNEW:  could not locate the line in decrypt where the message is assigned its value.")

def createDecoutInputLine(node, decoutLines):
    listNodes = []

    try:
        listNodes = node.listNodes
    except:
        sys.exit("createDecoutInputLine in transformNEW:  could not obtain listNodes of node passed in.")

    outputString = "input := list{"

    for listNode in listNodes:
        outputString += str(listNode) + ", "

    outputString += str(transformOutputList)

    outputString += "}\n"

    decoutLines.append(outputString)

def appendToKnownVars(node, knownVars):
    listNodes = []

    try:
        listNodes = node.listNodes
    except:
        sys.exit("appendToKnownVars in transformNEW.py:  couldn't extract listNodes from node passed in.")

    for listNode in listNodes:
        if (listNode not in knownVars):
            knownVars.append(listNode)

def nodeHasPairings(node):
    #if (node.left 
    return

def getAllATTRSRecursive(node, allATTRSList):
    if (node.left != None):
        getAllATTRSRecursive(node.left, allATTRSList)

    if (node.right != None):
        getAllATTRSRecursive(node.right, allATTRSList)

    if (node.type == ops.ATTR):
        allATTRSList.append(getFullVarName(node, False))

def getAllATTRS(node):
    allATTRSList = []
    getAllATTRSRecursive(node, allATTRSList)
    return allATTRSList

def addExpsAndPairingNodeToRetList(blindingExponents, pairing, retList):
    for tuple in retList:
        currentExponentList = tuple[0]
        if (blindingExponents == currentExponentList):
            tuple[1].append(pairing)
            return

    newTuple = blindingExponents, [pairing]
    retList.append(newTuple)

def groupPairings(nodePairings, varsThatAreBlindedDict):
    retList = []

    for pairing in nodePairings:
        blindingExponents = getAllBlindingExponentsForThisPairing(pairing, varsThatAreBlindedDict)
        blindingExponents.sort()
        addExpsAndPairingNodeToRetList(blindingExponents, pairing, retList)

def dropListSymbol(attrName):
    listIndexSymbolPos = attrName.find(LIST_INDEX_SYMBOL)
    if (listIndexSymbolPos == -1):
        return attrName

    return attrName[0:listIndexSymbolPos]

def getAllBlindingExponentsForThisPairing(pairing, varsThatAreBlindedDict):
    retList = []

    allATTRS = getAllATTRS(pairing)
    for ATTRind in allATTRS:
        ATTRNoListSym = dropListSymbol(ATTRind)
        if (ATTRNoListSym in varsThatAreBlindedDict):
            for blindingExponent in varsThatAreBlindedDict[ATTRNoListSym]:
                if blindingExponent not in retList:
                    retList.append(blindingExponent)

    return retList

def getNodePairingObjsRecursive(node, pairingsList):
    if (node.left != None):
        getNodePairingObjsRecursive(node.left, pairingsList)

    if (node.right != None):
        getNodePairingObjsRecursive(node.right, pairingsList)

    if (node.type == ops.PAIR):
        pairingsList.append(node)

def getNodePairingObjs(node):
    pairingsList = []
    getNodePairingObjsRecursive(node, pairingsList)
    return pairingsList

def getAreAllVarsOnLineKnownByTransformRecursive(node, knownVars, varsNotKnownByTransform):
    if (node.left != None):
        getAreAllVarsOnLineKnownByTransformRecursive(node.left, knownVars, varsNotKnownByTransform)

    if (node.right != None):
        getAreAllVarsOnLineKnownByTransformRecursive(node.right, knownVars, varsNotKnownByTransform)

    if (node.type == ops.ATTR):
        if (dropListSymbol(str(node)) not in knownVars):
            if (str(node) not in varsNotKnownByTransform):
                varsNotKnownByTransform.append(str(node))

def getAreAllVarsOnLineKnownByTransform(node, knownVars):
    varsNotKnownByTransform = []
    getAreAllVarsOnLineKnownByTransformRecursive(node, knownVars, varsNotKnownByTransform)
    if (len(varsNotKnownByTransform) == 0):
        return True
    else:
        return False

def writeOutPairingCalcs(groupedPairings, transformLines, decoutLines):
    pass
    
def transformNEW(varsThatAreBlindedDict):
    #addTransformFuncIntro()
    (stmtsDec, typesDec, depListDec, depListNoExponentsDec, infListDec, infListNoExponentsDec) = getFuncStmts(decryptFuncName)
    astNodes = getAstNodes()
    firstLineOfDecryptFunc = getStartLineNoOfFunc(decryptFuncName)
    lastLineOfDecryptFunc = getEndLineNoOfFunc(decryptFuncName)
    lastLineOfTransform = getLastLineOfTransform(stmtsDec)

    print("\n\n\n")
    #printLinesOfCode()
    #print("fristlinedecrypt", firstLineOfDecryptFunc)

    knownVars = []
    startLineNoOfSearch = None

    transformLines = ["BEGIN :: func:" + transformFuncName + "\n"]
    decoutLines = ["BEGIN :: func:" + decOutFunctionName + "\n"]

    # get knownVars
    for lineNo in range((firstLineOfDecryptFunc + 1), (lastLineOfTransform + 1)):
        if (str(astNodes[lineNo - 1].left) == inputKeyword):
            appendToKnownVars(astNodes[lineNo - 1].right, knownVars)
            startLineNoOfSearch = lineNo
            transformLines.append(str(astNodes[lineNo - 1]) + "\n")
            #print(transformLines)
            createDecoutInputLine(astNodes[lineNo - 1].right, decoutLines)
            #print(decoutLines)
            continue
        currentNode = astNodes[lineNo - 1].right
        if (currentNode == None):
            continue
        if (currentNode.type == ops.EXPAND):
            appendToKnownVars(currentNode, knownVars)
            transformLines.append(str(astNodes[lineNo - 1]) + "\n")
            decoutLines.append(str(astNodes[lineNo - 1]) + "\n")
        else:
            startLineNoOfSearch = lineNo
            break

    if (startLineNoOfSearch == None):
        sys.exit("transformNEW in transformNEW.py:  couldn't locate either input statement or EXPAND nodes.")

    for lineNo in range(startLineNoOfSearch, (lastLineOfTransform + 1)):
        currentNode = astNodes[lineNo - 1]
        path_applied = []
        currentNode = SimplifySDLNode(currentNode, path_applied)
        applyTechnique11(currentNode)
        currentNodePairings = getNodePairingObjs(currentNode)
        if (len(currentNodePairings) > 0):
            groupedPairings = groupPairings(currentNodePairings, varsThatAreBlindedDict)
            writeOutPairingCalcs(groupedPairings, transformLines, decoutLines)
        else:
            areAllVarsOnLineKnownByTransform = getAreAllVarsOnLineKnownByTransform(currentNode.right, knownVars)

    sys.exit("TEST")
