import sdlpath
from sdlparser.SDLParser import *
from outsrctechniques import *
import sys

transformListCounter = 0
decoutListCounter = 0

forLoopsStruct = None
forLoopsInnerStruct = None

currentNumberOfForLoops = 0
iterationNo = 0
withinForLoop = False

def getOriginalVarNameFromBlindedName(blindedName):
    retName = blindedName.lstrip(blindingFactorPrefix)
    retName = retName.rstrip(blindingSuffix)
    return retName

def getForLoopStructsInfo():
    global forLoopsStruct, forLoopsInnerStruct

    parseLinesOfCode(getLinesOfCode(), False)
    forLoopsStruct = getForLoops()
    forLoopsInnerStruct = getForLoopsInner()

def getPairingNodesRecursive(node, pairingNodesList):
    if (node.left != None):
        getPairingNodesRecursive(node.left, pairingNodesList)

    if (node.right != None):
        getPairingNodesRecursive(node.right, pairingNodesList)

    if (node.type == ops.PAIR):
        pairingNodesList.append(node)

def getNumPairingsInForLoopFromLineNo(lineNo, astNodes):
    forLoopIndivStruct = getForLoopStructFromLineNo(lineNo)
    if (forLoopIndivStruct == None):
        sys.exit("getNumPairingsInForLoopFromLineNo in transformNEW.py:  couldn't get for loop structure from getForLoopStructFromLineNo.")

    startLineNo = forLoopIndivStruct.getStartLineNo()
    endLineNo = forLoopIndivStruct.getEndLineNo()

    pairingNodesList = []

    for forLoopLineNo in range(startLineNo, (endLineNo + 1)):
        currentNode = astNodes[forLoopLineNo - 1]        
        getPairingNodesRecursive(currentNode, pairingNodesList)

    return (len(pairingNodesList))

def getForLoopStructFromLineNo(lineNo):
    forLoopIndivStruct = None

    for funcName in forLoopsInnerStruct:
        for forLoopInnerObj in forLoopsInnerStruct[funcName]:
            startLineNo = forLoopInnerObj.getStartLineNo()
            endLineNo = forLoopInnerObj.getEndLineNo()
            if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
                forLoopIndivStruct = forLoopInnerObj

    if (forLoopIndivStruct == None):
        for funcName in forLoopsStruct:
            for forLoopObj in forLoopsStruct[funcName]:
                startLineNo = forLoopObj.getStartLineNo()
                endLineNo = forLoopObj.getEndLineNo()
                if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
                    forLoopIndivStruct = forLoopObj

    if (forLoopIndivStruct == None):
        return None

    return forLoopIndivStruct

def getNumStatementsInForLoopFromLineNo(lineNo):

    forLoopIndivStruct = getForLoopStructFromLineNo(lineNo)
    if (forLoopIndivStruct == None):
        sys.exit("getNumStatementsInForLoopFromLineNo in transformNEW.py:  couldn't get for loop structure from getForLoopStructFromLineNo.")

    # the "- 2" is b/c of how we structure for loops in SDLParser (3 statements for the for loop itself,
    # but you have to add 1 b/c the # of total lines is end line no - start line no + 1
    numStatementsInForLoop = forLoopIndivStruct.getEndLineNo() - forLoopIndivStruct.getStartLineNo() - 2
    return numStatementsInForLoop

def getLoopVarNameFromLineNo(lineNo):

    for funcName in forLoopsInnerStruct:
        for forLoopInnerObj in forLoopsInnerStruct[funcName]:
            startLineNo = forLoopInnerObj.getStartLineNo()
            endLineNo = forLoopInnerObj.getEndLineNo()
            if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
                return str(forLoopInnerObj.getLoopVar())

    for funcName in forLoopsStruct:
        for forLoopObj in forLoopsStruct[funcName]:
            startLineNo = forLoopObj.getStartLineNo()
            endLineNo = forLoopObj.getEndLineNo()
            if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
                return str(forLoopObj.getLoopVar())

    return None

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

    return retList

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
                if ( (blindingExponent not in retList) and (blindingExponent != listNameIndicator) ):
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

def dropNegativeSign(nodeAsString):
    if (nodeAsString[0] != "-"):
        return nodeAsString

    return nodeAsString[1:len(nodeAsString)]

def shouldWeAddToUnknownVarsList(node, nodeAsString, knownVars, dotProdLoopVar, varsNotKnownByTransform):
    if (dropNegativeSign(dropListSymbol(str(node))) in knownVars):
        return False

    if (nodeAsString.isdigit() == True):
        return False

    if (str(node) in varsNotKnownByTransform):
        return False

    if ( (dotProdLoopVar != None) and (nodeAsString == str(dotProdLoopVar)) ):
        return False

    return True

def getAreAllVarsOnLineKnownByTransformRecursive(node, knownVars, dotProdLoopVar, varsNotKnownByTransform):
    if (node == None):
        return

    if (node.left != None):
        getAreAllVarsOnLineKnownByTransformRecursive(node.left, knownVars, dotProdLoopVar, varsNotKnownByTransform)

    if (node.right != None):
        getAreAllVarsOnLineKnownByTransformRecursive(node.right, knownVars, dotProdLoopVar, varsNotKnownByTransform)

    if (node.type == ops.ATTR):
        nodeAsString = str(node)
        nodeAsString = dropNegativeSign(nodeAsString)
        addToUnknownVarsList = shouldWeAddToUnknownVarsList(node, nodeAsString, knownVars, dotProdLoopVar, varsNotKnownByTransform)
        if (addToUnknownVarsList == True):
            varsNotKnownByTransform.append(str(node))

def getAreAllVarsOnLineKnownByTransform(node, knownVars, dotProdLoopVar):
    varsNotKnownByTransform = []
    getAreAllVarsOnLineKnownByTransformRecursive(node, knownVars, dotProdLoopVar, varsNotKnownByTransform)
    if (len(varsNotKnownByTransform) == 0):
        return True
    else:
        return False

def getTransformListIndex(currentLineNo, astNodes):
    if (withinForLoop == False):
        return transformListCounter

    return getForLoopListIndex(currentLineNo, astNodes)

def getDecoutListIndex(currentLineNo, astNodes):
    if (withinForLoop == False):
        return decoutListCounter

    return getForLoopListIndex(currentLineNo, astNodes)

def getForLoopListIndex(currentLineNo, astNodes):
    numStatementsInForLoop = int(getNumStatementsInForLoopFromLineNo(currentLineNo))
    numPairingsInForLoop = int(getNumPairingsInForLoopFromLineNo(currentLineNo, astNodes))
    currentForLoopSeed = int(forLoopSeed * currentNumberOfForLoops)
    loopVarName = getLoopVarNameFromLineNo(currentLineNo)

    return str(str(currentForLoopSeed + int(iterationNo)) + "+" + str(numStatementsInForLoop + numPairingsInForLoop) + "*" + str(loopVarName))

def writeOutPairingCalcs(groupedPairings, transformLines, decoutLines, currentNode, blindingVarsThatAreLists, currentLineNo, astNodes):
    global transformListCounter, decoutListCounter, iterationNo

    decoutListCounter = transformListCounter
    origIterationNo = iterationNo

    #transformListIndex = getTransformListIndex(currentLineNo)
    #decoutListIndex = getDecoutListIndex(currentLineNo)

    for groupedPairing in groupedPairings:
        transformListIndex = getTransformListIndex(currentLineNo, astNodes)

        lineForTransformLines = ""

        if (withinForLoop == True):
            lineForTransformLines += transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
        else:
            lineForTransformLines += transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "

        if (currentNode.right.type == ops.ON):
            lineForTransformLines += "{ " + str(currentNode.right.left) + " on ( "

        listOfPairings = groupedPairing[1]
        for pairing in listOfPairings:
            lineForTransformLines += str(pairing) + " * " 

        lineForTransformLines = lineForTransformLines[0:(len(lineForTransformLines) - len(" * "))]

        if (currentNode.right.type == ops.ON):
            lineForTransformLines += " ) }"

        transformLines.append(lineForTransformLines + "\n")

        if (withinForLoop == True):
            lineForTransformLines = str(currentNode.left) + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + "?"
        else:
            lineForTransformLines = str(currentNode.left) + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex)

        transformLines.append(lineForTransformLines + "\n")

        if (withinForLoop == False):
            transformListCounter += 1

        iterationNo += 1

    lineForDecoutLines = ""
    lineForDecoutLines += str(currentNode.left) + " := "
    subLineForDecoutLines = ""
    iterationNo = origIterationNo

    for groupedPairing in groupedPairings:
         decoutListIndex = getDecoutListIndex(currentLineNo, astNodes)

         if (withinForLoop == True):
             subLineForDecoutLines += "(" + transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex) + "?"
         else:
             subLineForDecoutLines += "(" + transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex)
             decoutListCounter += 1
         blindingExponents = groupedPairing[0]
         if (len(blindingExponents) > 0):
             subLineForDecoutLines += " ^ ("
         for blindingExponent in blindingExponents:
             originalVarName = getOriginalVarNameFromBlindedName(blindingExponent)
             if (originalVarName in blindingVarsThatAreLists):
                 loopVarNameToUse = getLoopVarNameFromLineNo(currentLineNo)
                 subLineForDecoutLines += blindingExponent + LIST_INDEX_SYMBOL + loopVarNameToUse + " * "
             else:
                 subLineForDecoutLines += blindingExponent + " * "
         if (len(blindingExponents) > 0):
             subLineForDecoutLines = subLineForDecoutLines[0:(len(subLineForDecoutLines) - len(" * "))]
             subLineForDecoutLines += ") ) "
         else:
             subLineForDecoutLines += ") "
         subLineForDecoutLines += " * "

         iterationNo += 1

    subLineForDecoutLines = subLineForDecoutLines[0:(len(subLineForDecoutLines) - len(" * "))]

    lineForDecoutLines += subLineForDecoutLines

    decoutLines.append(lineForDecoutLines + "\n")

def writeOutLineKnownByTransform(currentNode, transformLines, decoutLines, currentLineNo, astNodes):
    global transformListCounter, decoutListCounter, iterationNo

    decoutListCounter = transformListCounter
    origIterationNo = iterationNo

    transformListIndex = getTransformListIndex(currentLineNo, astNodes)
    #decoutListIndex = getDecoutListIndex(currentLineNo)

    if (withinForLoop == True):
        lineForTransformLines = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
        #iterationNo += 1
    else:
        lineForTransformLines = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "

    lineForTransformLines += str(currentNode.right)

    transformLines.append(lineForTransformLines + "\n")

    #iterationNo = origIterationNo

    #decoutListIndex = getDecoutListIndex(currentLineNo)

    if (withinForLoop == True):
        lineForTransformLines = str(currentNode.left) + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + "?"
        iterationNo += 1
    else:
        lineForTransformLines = str(currentNode.left) + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex)

    transformLines.append(lineForTransformLines + "\n")

    if (withinForLoop == False):
        transformListCounter += 1

    lineForDecoutLines = str(currentNode.left) + " := "

    iterationNo = origIterationNo
    decoutListIndex = getDecoutListIndex(currentLineNo, astNodes)

    if (withinForLoop == True): 
        lineForDecoutLines += transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex) + "?"
        iterationNo += 1
    else:
        lineForDecoutLines += transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex)

    if (withinForLoop == False):
        decoutListCounter += 1

    decoutLines.append(lineForDecoutLines + "\n")

'''
def writeOutNonPairingCalcs(currentNode, transformLines, decoutLines):
    global transformListCounter

    lineForTransformLines = transformOutputList + LIST_INDEX_SYMBOL + str(transformListCounter) + " := "
    transformListCounter += 1
    lineForTransformLines += str(
'''

def getDotProdLoopVar(node):
    dotProdLoopVar = None

    try:
        dotProdLoopVar = node.right.left.left.left
    except:
        sys.exit("getDotProdLoopVar in transformNEW.py:  couldn't obtain the dot product loop variable name.")

    return str(dotProdLoopVar)

def getBlindingVarsThatAreLists(varsThatAreBlindedDict):
    retList = []

    for blindingVarName in varsThatAreBlindedDict:
        blindingVarListObj = varsThatAreBlindedDict[blindingVarName]
        if (listNameIndicator in blindingVarListObj):
            if (blindingVarName not in retList):
                retList.append(blindingVarName)

    return retList

def transformNEW(varsThatAreBlindedDict):
    global currentNumberOfForLoops, withinForLoop, iterationNo

    #addTransformFuncIntro()
    (stmtsDec, typesDec, depListDec, depListNoExponentsDec, infListDec, infListNoExponentsDec) = getFuncStmts(decryptFuncName)
    astNodes = getAstNodes()
    firstLineOfDecryptFunc = getStartLineNoOfFunc(decryptFuncName)
    lastLineOfDecryptFunc = getEndLineNoOfFunc(decryptFuncName)
    lastLineOfTransform = getLastLineOfTransform(stmtsDec)
    getForLoopStructsInfo()

    #print("\n\n\n")
    #printLinesOfCode()
    #print("fristlinedecrypt", firstLineOfDecryptFunc)

    knownVars = []
    startLineNoOfSearch = None

    blindingVarsThatAreLists = getBlindingVarsThatAreLists(varsThatAreBlindedDict)

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

    #transformLines += transformOutputList + " = []\n"

    for lineNo in range(startLineNoOfSearch, (lastLineOfTransform + 1)):
        currentNode = astNodes[lineNo - 1]
        if (currentNode.type == ops.NONE):
            continue
        path_applied = []
        currentNode = SimplifySDLNode(currentNode, path_applied)
        currentNodeTechnique11RightSide = applyTechnique11(currentNode)
        if (currentNodeTechnique11RightSide != None):
            currentNode.right = currentNodeTechnique11RightSide
        currentNodePairings = getNodePairingObjs(currentNode)
        dotProdLoopVar = None
        if ( (currentNode.right != None) and (currentNode.right.type == ops.ON) ):
            dotProdLoopVar = getDotProdLoopVar(currentNode)
        areAllVarsOnLineKnownByTransform = getAreAllVarsOnLineKnownByTransform(currentNode.right, knownVars, dotProdLoopVar)

        if (currentNode.type != ops.EQ):
            if (currentNode.type == ops.FOR):
                withinForLoop = True
                currentNumberOfForLoops += 1
                iterationNo = 0
            if ( (currentNode.type == ops.END) and (withinForLoop == True) ):
                withinForLoop = False
            transformLines.append(str(currentNode) + "\n")
            decoutLines.append(str(currentNode) + "\n")
        elif (str(currentNode.left) == M):
            decoutLines.append(str(currentNode) + "\n")
        elif (str(currentNode.left) in doNotIncludeInTransformList):
            decoutLines.append(str(currentNode) + "\n")
        elif ( (len(currentNodePairings) > 0) and (areAllVarsOnLineKnownByTransform == True) ):
            groupedPairings = groupPairings(currentNodePairings, varsThatAreBlindedDict)
            writeOutPairingCalcs(groupedPairings, transformLines, decoutLines, currentNode, blindingVarsThatAreLists, lineNo, astNodes)
            if (groupedPairings[0][0] == []):
                knownVars.append(str(currentNode.left))
        elif (areAllVarsOnLineKnownByTransform == True):
            writeOutLineKnownByTransform(currentNode, transformLines, decoutLines, lineNo, astNodes)
            knownVars.append(str(currentNode.left))
        else:
            decoutLines.append(str(currentNode) + "\n")

    transformLines.append("output := " + transformOutputList + "\n")
    transformLines.append("END :: func:" + transformFuncName + "\n")

    transformLines.append("\n")

    decoutLines.append("output := " + M + "\n")
    decoutLines.append("END :: func:" + decOutFunctionName + "\n\n")

    transformPlusDecoutLines = transformLines + decoutLines

    transformOutputListDecl = [transformOutputList + " := list\n"]

    appendToLinesOfCode(transformOutputListDecl, getEndLineNoOfFunc(TYPES_HEADER))

    #printLinesOfCode()

    parseLinesOfCode(getLinesOfCode(), False)

    appendToLinesOfCode(transformPlusDecoutLines, getStartLineNoOfFunc(decryptFuncName))

    printLinesOfCode()

    parseLinesOfCode(getLinesOfCode(), False)

    removeRangeFromLinesOfCode(getStartLineNoOfFunc(decryptFuncName), getEndLineNoOfFunc(decryptFuncName))

    parseLinesOfCode(getLinesOfCode(), False)
