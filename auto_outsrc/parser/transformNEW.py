import sdlpath
from sdlparser.SDLParser import *
from outsrctechniques import *
#from keygen import processListOrExpandNodes
import sys

transformOutputListForLoop = "transformOutputListForLoop"
atLeastOneForLoop = False
writeToDecout = True
#isRegDotProdVar = False

transformListCounter = 0
decoutListCounter = 0

forLoopsStruct = None
forLoopsInnerStruct = None

currentNumberOfForLoops = 0
iterationNo = 0
withinForLoop = False

#transformInputLineGlobal = ""
#decoutInputLineGlobal = ""

varsWithNonStandardTypes = []

varsUsedInDecout = []

listOfStandardTypes = [types.G1, types.G2, types.GT, types.ZR, types.listG1, types.listG2, types.listGT, types.listZR] #types.int, types.str, types.list, types.listInt, types.listStr, types.listG1, types.listG2, types.listGT, types.listZR]

nilType = 'nil'

singleBF = False

canCollapseForLoopsInDecout = False

def getRightSideOfStringAssignStatement(inputString):
    inputStringSeparated = inputString.split(" := ")
    if (len(inputStringSeparated) != 2):
        sys.exit("getRightSideOfStringAssignStatement in transformNEW.py:  inputStringSeparated isn't of length 2.")

    return inputStringSeparated[1]

def addVarsUsedInDecoutToGlobalList(lineForDecout):
    global varsUsedInDecout

    if (type(lineForDecout).__name__) == "str":
        parser = SDLParser()
        lineForDecout = parser.parse(lineForDecout)

    #print(type(lineForDecout).__name__)
    allAttrNodeNames = GetAttributeVars(lineForDecout, True)

    for attrName in allAttrNodeNames:
        if (attrName not in varsUsedInDecout) and (attrName != 'for'):
            varsUsedInDecout.append(attrName)

def getCTVarNames():
    ctVarNames = []

    assignInfo = getAssignInfo()

    if (encryptFuncName not in assignInfo):
        sys.exit("getCTVarName in transformNEW.py:  encryptFuncName not in assignInfo.")

    if (outputVarName not in assignInfo[encryptFuncName]):
        sys.exit("getCTVarName in transformNEW.py:  outputVarName not in assignInfo[encryptFuncName].")

    encryptOutputAssignNode = assignInfo[encryptFuncName][outputVarName].getAssignNode()

    possibleCTVarNames = encryptOutputAssignNode.right
    if (possibleCTVarNames.type == ops.ATTR):
        if (str(possibleCTVarNames) not in ctVarNames):
            ctVarNames.append(str(possibleCTVarNames))
    elif (possibleCTVarNames.type == ops.LIST):
        for listNode in possibleCTVarNames.listNodes:
            if (listNode not in ctVarNames):
                ctVarNames.append(listNode)
    else:
        sys.exit("getCTVarNames in transformNEW.py:  output of encrypt is neither an attribute nor a list.")

    return ctVarNames

#TODO:  right now, this function is verbatim the same as the one in keygen.py.
#Consolidate so there's only one copy of the code.
def processListOrExpandNodes(binNode, origVarName, newVarName):
    binNodeRight = binNode.right
    if (binNodeRight == None):
        return

    binNodeRightType = binNodeRight.type
    if ( (binNodeRightType != ops.LIST) and (binNodeRightType != ops.EXPAND) ):
        return

    nodeListNodes = binNodeRight.listNodes
    if (len(nodeListNodes) == 0):
        return

    retNodeList = []

    for currentNode in nodeListNodes:
        if (currentNode == origVarName):
            retNodeList.append(newVarName)
        else:
            retNodeList.append(currentNode)

    binNodeRight.listNodes = retNodeList

def makeSecretKeyBlindedNameReplacements(node, secretKeyElements):
    origVarName = keygenSecVar
    newVarName = keygenSecVar + blindingSuffix
    ASTVisitor(SubstituteVar(origVarName,newVarName)).preorder(node)
    processListOrExpandNodes(node, origVarName, newVarName)

    #print(secretKeyElements)

    for element in secretKeyElements:
        ASTVisitor(SubstituteVar(element, element+blindingSuffix)).preorder(node)
        processListOrExpandNodes(node, element, element+blindingSuffix)

def getOriginalVarNameFromBlindedName(blindedName):
    retName = blindedName.lstrip(blindingFactorPrefix)
    #retName = retName.rstrip(blindingSuffix)
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
        #TODO:  ADD FORALL PARSING TO SDLPARSER.PY.  THIS IS A NASTY HACK INSTEAD.
        return 10
        #sys.exit("getNumPairingsInForLoopFromLineNo in transformNEW.py:  couldn't get for loop structure from getForLoopStructFromLineNo.")

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
        #TODO:  ADD FORALL PARSING TO SDLPARSER.PY.  THIS IS A NASTY HACK INSTEAD.
        return 10
        #sys.exit("getNumStatementsInForLoopFromLineNo in transformNEW.py:  couldn't get for loop structure from getForLoopStructFromLineNo.")

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

def getLastLineOfTransform(stmtsDec, config):
    for lineNo in stmtsDec:
        stmt = stmtsDec[lineNo]
        #print(type(stmt).__name__)
        print(stmt)
        if (type(stmt).__name__ == VAR_INFO_CLASS_NAME):
            if (str(stmt.getAssignNode().left) == config.M):
                return lineNo

    sys.exit("getLastLineOfTransform in transformNEW:  could not locate the line in decrypt where the message is assigned its value.")

def createDecoutInputLine(node, ctVarNames, allPossibleBlindingFactors):
    listNodes = []

    try:
        listNodes = node.listNodes
    except:
        sys.exit("createDecoutInputLine in transformNEW:  could not obtain listNodes of node passed in.")

    outputString = "input := list{"

    pkBlindedList = []
    for pubVar in keygenPubVar:
        pkBlindedList.append(pubVar + blindingSuffix)

    for listNode in listNodes:
        if (listNode == (keygenSecVar + blindingSuffix)):
            continue

        if (listNode in ctVarNames):
            continue

        if (listNode in pkBlindedList):
            continue

        outputString += str(listNode) + ", "

    outputString += str(transformOutputList)

    #outputString += "}\n"

    #decoutLines.append(outputString)

    for bfName in allPossibleBlindingFactors:
        if (bfName != nilType):
            outputString += ", " + bfName

    return outputString

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

def groupPairings(nodePairings, varsThatAreBlindedDict, config):
    retList = []

    for pairing in nodePairings:
        blindingExponents = getAllBlindingExponentsForThisPairing(pairing, varsThatAreBlindedDict, config)
        blindingExponents.sort()
        addExpsAndPairingNodeToRetList(blindingExponents, pairing, retList)

    return retList

def dropListSymbol(attrName):
    listIndexSymbolPos = attrName.find(LIST_INDEX_SYMBOL)
    if (listIndexSymbolPos == -1):
        return attrName

    return attrName[0:listIndexSymbolPos]

def getAllBlindingExponentsForThisPairing(pairing, varsThatAreBlindedDict, config):
    retList = []

    allATTRS = getAllATTRS(pairing)
    for ATTRind in allATTRS:
        ATTRNoListSym = dropListSymbol(ATTRind)
        if (ATTRNoListSym in varsThatAreBlindedDict):
            for blindingExponent in varsThatAreBlindedDict[ATTRNoListSym]:
                if ( (blindingExponent not in retList) and (blindingExponent != config.listNameIndicator) ):
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

    if (str(node) in ["True", "true", "False", "false"]):
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

def getTransformListIndex(currentLineNo, astNodes, config):
    if (withinForLoop == False):
        return transformListCounter

    return getForLoopListIndex(currentLineNo, astNodes, config)

def getDecoutListIndex(currentLineNo, astNodes, config):
    if (withinForLoop == False):
        return decoutListCounter

    return getForLoopListIndex(currentLineNo, astNodes, config)

def getForLoopListIndex(currentLineNo, astNodes, config):
    numStatementsInForLoop = int(getNumStatementsInForLoopFromLineNo(currentLineNo))
    numPairingsInForLoop = int(getNumPairingsInForLoopFromLineNo(currentLineNo, astNodes))
    currentForLoopSeed = int(config.forLoopSeed * currentNumberOfForLoops)
    loopVarName = getLoopVarNameFromLineNo(currentLineNo)

    return str(str(currentForLoopSeed + int(iterationNo)) + "+" + str(numStatementsInForLoop + numPairingsInForLoop) + "*" + str(loopVarName))

def getIndexVarNameFromBinaryNodeRecursive(node, varName, possibleIndexVarNames):
    if (node.left != None):
        getIndexVarNameFromBinaryNodeRecursive(node.left, varName, possibleIndexVarNames)

    if (node.right != None):
        getIndexVarNameFromBinaryNodeRecursive(node.right, varName, possibleIndexVarNames)

    if (node.type == ops.ATTR):
        nodeName = node.attr
        nodeNameIndexPos = nodeName.find(LIST_INDEX_SYMBOL)
        if (nodeNameIndexPos != -1):
            if (nodeName[0:nodeNameIndexPos] == varName):
                possibleIndexVarNames.append(nodeName[(nodeNameIndexPos + 1):(len(nodeName))])

def getIndexVarNameFromBinaryNode(node, varName):
    possibleIndexVarNames = []
    getIndexVarNameFromBinaryNodeRecursive(node, varName, possibleIndexVarNames)
    if (len(possibleIndexVarNames) == 1):
        return possibleIndexVarNames[0]

    firstPossibleName = possibleIndexVarNames[0]
    for possibleName in possibleIndexVarNames:
        if (possibleName != firstPossibleName):
            sys.exit("getIndexVarNameFromBinaryNode in transformNEW.py:  found different possible index names in binary node passed in for the variable name passed in; not supported.")

    return firstPossibleName

def writeOutPairingCalcs(groupedPairings, transformLines, decoutLines, currentNode, blindingVarsThatAreLists, currentLineNo, astNodes, config):
    global transformListCounter, decoutListCounter, iterationNo

    decoutListCounter = transformListCounter
    origIterationNo = iterationNo

    #transformListIndex = getTransformListIndex(currentLineNo)
    #decoutListIndex = getDecoutListIndex(currentLineNo)

    for groupedPairing in groupedPairings:
        transformListIndex = getTransformListIndex(currentLineNo, astNodes, config)

        lineForTransformLines = ""

        if (withinForLoop == True):
            lineForTransformLines += transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
            lineForTypesSection = transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := GT\n"
            appendToLinesOfCode([lineForTypesSection], getEndLineNoOfFunc(TYPES_HEADER))
            parseLinesOfCode(getLinesOfCode(), False)
        else:
            lineForTransformLines += transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "
            lineForTypesSection = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := GT\n"
            appendToLinesOfCode([lineForTypesSection], getEndLineNoOfFunc(TYPES_HEADER))
            parseLinesOfCode(getLinesOfCode(), False)

        if (currentNode.right.type == ops.ON):
            lineForTransformLines += "{ " + str(currentNode.right.left) + " on ( "

        listOfPairings = groupedPairing[1]
        listOfPairings = CombinePairings(listOfPairings)
        for pairing in listOfPairings:
            lineForTransformLines += str(pairing) + " * " 

        lineForTransformLines = lineForTransformLines[0:(len(lineForTransformLines) - len(" * "))]

        if (currentNode.right.type == ops.ON):
            lineForTransformLines += " ) }"

        transformLines.append(lineForTransformLines + "\n")

        if (len(groupedPairings) == 1):
            if (withinForLoop == True):
                lineForTransformLines = str(currentNode.left) + " := " + transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "?"
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
         decoutListIndex = getDecoutListIndex(currentLineNo, astNodes, config)

         if (withinForLoop == True):
             subLineForDecoutLines += "(" + transformOutputListForLoop + LIST_INDEX_SYMBOL + str(decoutListIndex) + "?"
         else:
             subLineForDecoutLines += "(" + transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex)
             decoutListCounter += 1
         blindingExponents = groupedPairing[0]
         if (len(blindingExponents) > 0):
             subLineForDecoutLines += " ^ ("
         for blindingExponent in blindingExponents:
             originalVarName = getOriginalVarNameFromBlindedName(blindingExponent)
             #if ( (originalVarName in blindingVarsThatAreLists) and (withinForLoop == True) ):
                 #loopVarNameToUse = getLoopVarNameFromLineNo(currentLineNo)
                 #subLineForDecoutLines += blindingExponent + LIST_INDEX_SYMBOL + loopVarNameToUse + " * "
             if (originalVarName in blindingVarsThatAreLists):
                 indexVarNameToUse = getIndexVarNameFromBinaryNode(currentNode, originalVarName)
                 subLineForDecoutLines += blindingExponent + LIST_INDEX_SYMBOL + indexVarNameToUse + " * "
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

    if (writeToDecout == True):
        decoutLines.append(lineForDecoutLines + "\n")
        addVarsUsedInDecoutToGlobalList(getRightSideOfStringAssignStatement(lineForDecoutLines))

def makeListTypeReplacement(inputType):
    if (inputType == types.listInt):
        return "list{int}"

    if (inputType == types.listStr):
        return "list{str}"

    if (inputType == types.listG1):
        return "list{G1}"

    if (inputType == types.listG2):
        return "list{G2}"

    if (inputType == types.listGT):
        return "list{GT}"

    if (inputType == types.listZR):
        return "list{ZR}"

    return str(inputType)

def writeOutLineKnownByTransform(currentNode, transformLines, decoutLines, currentLineNo, astNodes, config, ctExpandListNodes, ctVarsThatNeedBuckets, regDotProdVar, allPossibleBlindingFactors):
    global transformListCounter, decoutListCounter, iterationNo, varsWithNonStandardTypes

    decoutListCounter = transformListCounter
    origIterationNo = iterationNo

    transformListIndex = getTransformListIndex(currentLineNo, astNodes, config)
    #decoutListIndex = getDecoutListIndex(currentLineNo)

    currentNodeRightType = getVarTypeInfoRecursive(currentNode.right, config.decryptFuncName)

    if (currentNodeRightType in listOfStandardTypes):
        if (withinForLoop == True):
            lineForTransformLines = transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
            lineForTypesSection = transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
            lineForTypesSection += makeListTypeReplacement(currentNodeRightType) + "\n"
            appendToLinesOfCode([lineForTypesSection], getEndLineNoOfFunc(TYPES_HEADER))
            parseLinesOfCode(getLinesOfCode(), False)
        else:
            lineForTransformLines = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "
            lineForTypesSection = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "
            lineForTypesSection += makeListTypeReplacement(currentNodeRightType) + "\n"
            appendToLinesOfCode([lineForTypesSection], getEndLineNoOfFunc(TYPES_HEADER))
            parseLinesOfCode(getLinesOfCode(), False)
    else:
        if (str(currentNode.left) not in varsWithNonStandardTypes):
            varsWithNonStandardTypes.append(str(currentNode.left))
        transformLines.append(str(currentNode) + "\n")
        # LW
        if ( (withinForLoop == True) and (writeToDecout == True) ):
            decoutLines.append(str(currentNode) + "\n")
            addVarsUsedInDecoutToGlobalList(currentNode.right)
            searchForCTVarsThatNeedBuckets(currentNode.right, ctExpandListNodes, ctVarsThatNeedBuckets)
        return

        '''
        if (withinForLoop == True):
            lineForTransformLines = transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "? := "
        else:
            lineForTransformLines = transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex) + " := "
        '''

    lineForTransformLines += str(currentNode.right)

    transformLines.append(lineForTransformLines + "\n")

    #iterationNo = origIterationNo

    #decoutListIndex = getDecoutListIndex(currentLineNo)

    if (withinForLoop == True):
        lineForTransformLines = str(currentNode.left) + " := " + transformOutputListForLoop + LIST_INDEX_SYMBOL + str(transformListIndex) + "?"
        iterationNo += 1
    else:
        lineForTransformLines = str(currentNode.left) + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListIndex)

    transformLines.append(lineForTransformLines + "\n")

    if (withinForLoop == False):
        transformListCounter += 1

    lineForDecoutLines = str(currentNode.left) + " := "

    iterationNo = origIterationNo
    decoutListIndex = getDecoutListIndex(currentLineNo, astNodes, config)

    if (withinForLoop == True): 
        lineForDecoutLines += transformOutputListForLoop + LIST_INDEX_SYMBOL + str(decoutListIndex) + "?"
        iterationNo += 1
    else:
        lineForDecoutLines += transformOutputList + LIST_INDEX_SYMBOL + str(decoutListIndex)

    if (withinForLoop == False):
        decoutListCounter += 1

    if (writeToDecout == True):

        if ( (canCollapseForLoopsInDecout == True) and (regDotProdVar != None) and (str(currentNode.right) == regDotProdVar) and (singleBF == True) ):
            decoutLines.append(lineForDecoutLines + " ^ " + allPossibleBlindingFactors[0] + "\n")
        else:
            decoutLines.append(lineForDecoutLines + "\n")
        addVarsUsedInDecoutToGlobalList(getRightSideOfStringAssignStatement(lineForDecoutLines))
        searchForCTVarsThatNeedBuckets(getRightSideOfStringAssignStatement(lineForDecoutLines), ctExpandListNodes, ctVarsThatNeedBuckets)

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

def getBlindingVarsThatAreLists(varsThatAreBlindedDict, config):
    retList = []

    for blindingVarName in varsThatAreBlindedDict:
        blindingVarListObj = varsThatAreBlindedDict[blindingVarName]
        if (config.listNameIndicator in blindingVarListObj):
            if (blindingVarName not in retList):
                retList.append(blindingVarName)

    return retList

def getForLoopIndexVarName(node):

    return str(node.left.left)

def addBlindingSufficesToDict(dict):
    retDict = {}

    for key in dict:
        retDict[key+blindingSuffix] = dict[key]

    return retDict

def getListNodes(node):
    if ( (node.type != ops.LIST) and (node.type != ops.SYMMAP) and (node.type != ops.EXPAND) and (node.type != ops.FUNC) ):
        return []

    listNodes = node.listNodes
    return listNodes

def searchForCTVarsThatNeedBuckets(node, ctExpandListNodes, ctVarsThatNeedBuckets):
    #see if we need to put any of the ciphertext elements into buckets for decout

    if (type(node).__name__) == "str":
        parser = SDLParser()
        node = parser.parse(node)

    varsOnThisLine = GetAttributeVars(node, True)
    for varOnThisLine in varsOnThisLine:
        if ( (varOnThisLine in ctExpandListNodes) and (varOnThisLine not in ctVarsThatNeedBuckets) ):
            ctVarsThatNeedBuckets.append(varOnThisLine)

def writeOutCTVarsThatNeedBuckets(ctVarsThatNeedBuckets, transformInputExpandNumStatements, decoutInputExpandNumStatements, transformLines, decoutLines):
    global transformListCounter, decoutListCounter

    for var in ctVarsThatNeedBuckets:
        lineForTransform = ""
        lineForDecout = ""
        lineForTransform += transformOutputList + LIST_INDEX_SYMBOL + str(transformListCounter) + " := " + var + "\n"
        lineForDecout += var + " := " + transformOutputList + LIST_INDEX_SYMBOL + str(transformListCounter) + "\n"

        #print(lineForTransform)
        #print(lineForDecout)

        transformListCounter += 1
        decoutListCounter += 1
        #reverse order b/c we're not keeping a counter
        transformLines.insert(transformInputExpandNumStatements, lineForTransform)
        decoutLines.insert(decoutInputExpandNumStatements, lineForDecout)
        addVarsUsedInDecoutToGlobalList(getRightSideOfStringAssignStatement(lineForDecout))

def addListNodesForThisLineToCtExpandListNodes(ctExpandListNodes, ctExpandListNodesForThisLine):
    for listNode in ctExpandListNodesForThisLine:
        if (listNode not in ctExpandListNodes):
            ctExpandListNodes.append(listNode)

def getAllBlindingExponentsForDecoutLine(varsThatAreBlindedDict):
    retList = []

    for varName in varsThatAreBlindedDict:
        possibleNewEntry = varsThatAreBlindedDict[varName][0]
        if (possibleNewEntry not in retList):
            retList.append(possibleNewEntry)

    return retList

def getSkVarsThatDecoutNeeds(currentNode, skExpandListNodes):
    retList = []

    varsOnThisLine = GetAttributeVars(currentNode, True)
    for var in varsOnThisLine:
        if ( (var == "for") or (var == "if") or (var == "forall") ):
            continue

        if ( (var in skExpandListNodes) and (var not in retList) ):
            retList.append(var)

    return retList

def combineListsNoDups(listToAddTo, listToAddFrom):
    for varName in listToAddFrom:
        if (varName not in listToAddTo):
            listToAddTo.append(varName)

def seeIfSingleBF(varsThatAreBlindedDict):
    global singleBF

    firstOne = True

    for varName in varsThatAreBlindedDict:
        if (firstOne == True):
            firstBF = varsThatAreBlindedDict[varName]
            if (firstBF[0].find(LIST_INDEX_SYMBOL) != -1):
                singleBF = False
                return
            firstOne = False
            continue

        currentBF = varsThatAreBlindedDict[varName]
        if (currentBF[0].find(LIST_INDEX_SYMBOL) != -1):
            singleBF = False
            return
        if (firstBF != currentBF):
            singleBF = False
            return

    singleBF = True

def getRegDotProdVar(currentNode):
    if (withinForLoop == False):
        return None

    if (currentNode.type != ops.EQ):
        return None

    varName = str(currentNode.left)
    allVarsOnRight = GetAttributeVars(currentNode.right, True)

    if (varName not in allVarsOnRight):
        return None

    #TODO:  THIS IS A HACK!!  THERE NEED TO BE MORE CHECKS HERE

    return str(currentNode.left)

def getIsForLoopStart(node):
    if (node.type != ops.BEGIN):
        return False

    if ( (str(node.left) != "for") and (str(node.left) != "forall") ):
        return False

    return True

def getIsForLoopEnd(node):
    if (node.type != ops.END):
        return False

    if ( (str(node.left) != "for") and (str(node.left) != "forall") ):
        return False

    return True

def getPairingAttrNamesRecursive(astNode, attrNames):
    if (astNode.left != None):
        getPairingAttrNamesRecursive(astNode.left, attrNames)

    if (astNode.right != None):
        getPairingAttrNamesRecursive(astNode.right, attrNames)

    if (astNode.type == ops.PAIR):
        allAttrNodeNames = GetAttributeVars(astNode, True)
        attrNames.append(allAttrNodeNames)
        '''
        for attrNodeName in allAttrNodeNames:
            if (attrNodeName not in attrNames):
                attrNames.append(attrNodeName)
        '''

def getPairingAttrNames(astNode):
    attrNames = []
    getPairingAttrNamesRecursive(astNode, attrNames)
    return attrNames

def determineIfWeCanCollapseForLoopsInDecout(astNodes, firstLineOfDecryptFunc, lastLineOfDecryptFunc, varsThatAreBlindedDict, config):
    global canCollapseForLoopsInDecout

    withinForLoopLocalVar = False

    #print(firstLineOfDecryptFunc)
    #print(lastLineOfDecryptFunc)

    for lineNumber in range(firstLineOfDecryptFunc, (lastLineOfDecryptFunc + 1)):
        currentNode = astNodes[lineNumber - 1]

        isForLoopStart = getIsForLoopStart(currentNode)
        if (isForLoopStart == True):
            withinForLoopLocalVar = True
            continue

        isForLoopEnd = getIsForLoopEnd(currentNode)
        if (isForLoopEnd == True):
            withinForLoopLocalVar = False
            continue

        if (withinForLoopLocalVar == False):
            continue

        pairingAttrNamesLists = getPairingAttrNames(currentNode)
        if (len(pairingAttrNamesLists) == 0):
            continue

        for pairingAttrNameList in pairingAttrNamesLists:
            foundOneWithBlindedVar = False
            for pairingAttrName in pairingAttrNameList:
                nameWithBlindingSuffix = pairingAttrName + config.blindingSuffix
                if (nameWithBlindingSuffix in varsThatAreBlindedDict):
                    foundOneWithBlindedVar = True
            if (foundOneWithBlindedVar == False):
                canCollapseForLoopsInDecout = False
                return 

    canCollapseForLoopsInDecout = True

def transformNEW(varsThatAreBlindedDict, secretKeyElements, config):
    global currentNumberOfForLoops, withinForLoop, iterationNo, atLeastOneForLoop, writeToDecout

    #print(varsThatAreBlindedDict)

    varsThatAreBlindedDict = addBlindingSufficesToDict(varsThatAreBlindedDict)

    seeIfSingleBF(varsThatAreBlindedDict)

    ctVarNames = getCTVarNames()
    #print(ctVarNames)
    #sys.exit("test")

    #addTransformFuncIntro()
    (stmtsDec, typesDec, depListDec, depListNoExponentsDec, infListDec, infListNoExponentsDec) = getFuncStmts(config.decryptFuncName)
    astNodes = getAstNodes()
    firstLineOfDecryptFunc = getStartLineNoOfFunc(config.decryptFuncName)
    lastLineOfDecryptFunc = getEndLineNoOfFunc(config.decryptFuncName)
    lastLineOfTransform = getLastLineOfTransform(stmtsDec, config)
    getForLoopStructsInfo()

    determineIfWeCanCollapseForLoopsInDecout(astNodes, firstLineOfDecryptFunc, lastLineOfDecryptFunc, varsThatAreBlindedDict, config)
    #print(canCollapseForLoopsInDecout)
    #sys.exit("test")

    #print("\n\n\n")
    #printLinesOfCode()
    #print("fristlinedecrypt", firstLineOfDecryptFunc)

    knownVars = []
    startLineNoOfSearch = None

    blindingVarsThatAreLists = getBlindingVarsThatAreLists(varsThatAreBlindedDict, config)

    transformLines = ["BEGIN :: func:" + config.transformFuncName + "\n"]
    decoutLines = ["BEGIN :: func:" + config.decOutFunctionName + "\n"]

    ctExpandListNodes = []
    skExpandListNodes = []

    transformRunningOutputLine = ""
    decoutRunningInputLine = ""

    allPossibleBlindingFactors = getAllBlindingExponentsForDecoutLine(varsThatAreBlindedDict)
    #seeIfSingleBF(varsThatAreBlindedDict)

    regDotProdVar = None

    # get knownVars
    for lineNo in range((firstLineOfDecryptFunc + 1), (lastLineOfTransform + 1)):
        currentFullNode = astNodes[lineNo - 1]
        makeSecretKeyBlindedNameReplacements(currentFullNode, secretKeyElements)
        if (str(currentFullNode.left) == inputKeyword):
            appendToKnownVars(currentFullNode.right, knownVars)
            startLineNoOfSearch = lineNo
            transformLines.append(str(currentFullNode) + "\n")
            decoutRunningInputLine = createDecoutInputLine(currentFullNode.right, ctVarNames, allPossibleBlindingFactors)
            continue
        currentNode = currentFullNode.right
        if (currentNode == None):
            continue
        if (currentNode.type == ops.EXPAND):
            appendToKnownVars(currentNode, knownVars)
            transformLines.append(str(currentFullNode) + "\n")
            if ( (writeToDecout == True) and (str(currentFullNode.left) not in ctVarNames) and (str(currentFullNode.left) != (keygenSecVar + blindingSuffix)) ):
                decoutLines.append(str(currentFullNode) + "\n")
            if (str(currentFullNode.left) in ctVarNames):
                ctExpandListNodesForThisLine = getListNodes(currentFullNode.right)
                addListNodesForThisLineToCtExpandListNodes(ctExpandListNodes, ctExpandListNodesForThisLine)
            if (str(currentFullNode.left) == (config.keygenSecVar + config.blindingSuffix)):
                skExpandListNodes = getListNodes(currentFullNode.right)
        else:
            startLineNoOfSearch = lineNo
            break

    #print(skExpandListNodes)
    #sys.exit("test")

    if (startLineNoOfSearch == None):
        sys.exit("transformNEW in transformNEW.py:  couldn't locate either input statement or EXPAND nodes.")

    #transformLines += transformOutputList + " = []\n"

    ctVarsThatNeedBuckets = []
    skVarsThatDecoutNeeds = []
    transformInputExpandNumStatements = len(transformLines)
    decoutInputExpandNumStatements = len(decoutLines)

    '''
    #see if we need to put any of the ciphertext elements into buckets for decout
    for lineNo in range(startLineNoOfSearch, (lastLineOfTransform + 1)):
        currentNode = astNodes[lineNo - 1]
        if (currentNode.type == ops.NONE):
            continue
        varsOnThisLine = GetAttributeVars(currentNode.right, True)
        for varOnThisLine in varsOnThisLine:
            if ( (varOnThisLine in ctExpandListNodes) and (varOnThisLine not in ctVarsThatNeedBuckets) ):
                ctVarsThatNeedBuckets.append(varOnThisLine)
        print(currentNode)
        print(varsOnThisLine)
        print("\n")

    print(ctVarsThatNeedBuckets)
    '''



    #main loop
    for lineNo in range(startLineNoOfSearch, (lastLineOfTransform + 1)):
        currentNode = astNodes[lineNo - 1]
        makeSecretKeyBlindedNameReplacements(currentNode, secretKeyElements)
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
        regDotProdVarOnThisLine = getRegDotProdVar(currentNode)
        if (regDotProdVar == None):
            regDotProdVar = getRegDotProdVar(currentNode)

        if (currentNode.type != ops.EQ):
            skVarsThatDecoutNeedsForThisLine = getSkVarsThatDecoutNeeds(currentNode, skExpandListNodes)
            combineListsNoDups(skVarsThatDecoutNeeds, skVarsThatDecoutNeedsForThisLine)
            #if (currentNode.type == ops.FOR):
            if ( (currentNode.type == ops.BEGIN) and ( (str(currentNode.left) == "for") or (str(currentNode.left) == "forall"))):
                withinForLoop = True
                if ( (canCollapseForLoopsInDecout == True) and (singleBF == True) ):
                    writeToDecout = False
                currentNumberOfForLoops += 1
                iterationNo = 0
                atLeastOneForLoop = True

            if ( (currentNode.type == ops.FOR) or (currentNode.type == ops.IF) ):
                transformLines.append(str(currentNode) + "\nNOP\n")
                if (writeToDecout == True):
                    decoutLines.append(str(currentNode) + "\nNOP\n")
                    addVarsUsedInDecoutToGlobalList(currentNode)
                    searchForCTVarsThatNeedBuckets(currentNode, ctExpandListNodes, ctVarsThatNeedBuckets)
            else:
                transformLines.append(str(currentNode) + "\n")
                if (writeToDecout == True):
                    decoutLines.append(str(currentNode) + "\n")
                    addVarsUsedInDecoutToGlobalList(currentNode)
                    searchForCTVarsThatNeedBuckets(currentNode, ctExpandListNodes, ctVarsThatNeedBuckets)

            if ( (currentNode.type == ops.END) and ( (str(currentNode.left) == "for") or (str(currentNode.left) == "forall")) and (withinForLoop == True) ):
                withinForLoop = False
                writeToDecout = True


        elif (str(currentNode.left) == M):
            if (writeToDecout == True):
                decoutLines.append(str(currentNode) + "\n")
                addVarsUsedInDecoutToGlobalList(currentNode.right)
                searchForCTVarsThatNeedBuckets(currentNode.right, ctExpandListNodes, ctVarsThatNeedBuckets)
        elif (str(currentNode.left) in config.doNotIncludeInTransformList):
            if (writeToDecout == True):
                decoutLines.append(str(currentNode) + "\n")
                addVarsUsedInDecoutToGlobalList(currentNode.right)
                searchForCTVarsThatNeedBuckets(currentNode.right, ctExpandListNodes, ctVarsThatNeedBuckets)
        elif ( (len(currentNodePairings) > 0) and (areAllVarsOnLineKnownByTransform == True) ):
            groupedPairings = groupPairings(currentNodePairings, varsThatAreBlindedDict, config)
            writeOutPairingCalcs(groupedPairings, transformLines, decoutLines, currentNode, blindingVarsThatAreLists, lineNo, astNodes, config)
            if (groupedPairings[0][0] == []):
                knownVars.append(str(currentNode.left))
        elif (areAllVarsOnLineKnownByTransform == True):
            writeOutLineKnownByTransform(currentNode, transformLines, decoutLines, lineNo, astNodes, config, ctExpandListNodes, ctVarsThatNeedBuckets, regDotProdVar, allPossibleBlindingFactors)
            knownVars.append(str(currentNode.left))
        elif ( (regDotProdVarOnThisLine != None) and (singleBF == True) and (canCollapseForLoopsInDecout == True) ):
            writeOutLineKnownByTransform(currentNode, transformLines, decoutLines, lineNo, astNodes, config, ctExpandListNodes, ctVarsThatNeedBuckets, regDotProdVar, allPossibleBlindingFactors)
            knownVars.append(str(currentNode.left))
        #elif ( (regDotProdVar != None) and (str(currentNode.right) == regDotProdVar) and (singleBF == True) ):
            #decoutLines.append(str(currentNode) + " ^ " + allPossibleBlindingFactors[0])
        else:
            if (writeToDecout == True):
                decoutLines.append(str(currentNode) + "\n")
                addVarsUsedInDecoutToGlobalList(currentNode.right)
                searchForCTVarsThatNeedBuckets(currentNode.right, ctExpandListNodes, ctVarsThatNeedBuckets)

        if (currentNode.type == ops.FOR):
            forLoopIndexVarName = getForLoopIndexVarName(currentNode)
            knownVars.append(forLoopIndexVarName)

    #print(skVarsThatDecoutNeeds)
    #sys.exit("test")

    if (len(ctVarsThatNeedBuckets) > 0):
        writeOutCTVarsThatNeedBuckets(ctVarsThatNeedBuckets, transformInputExpandNumStatements, decoutInputExpandNumStatements, transformLines, decoutLines)

    #print(varsUsedInDecout)
    #sys.exit("test")

    varsToAddToTransformOutputAndDecoutInput = []

    for varName in varsWithNonStandardTypes:
        if (varName in varsUsedInDecout):
            varsToAddToTransformOutputAndDecoutInput.append(varName)

    for varName in skVarsThatDecoutNeeds:
        if (varName not in varsToAddToTransformOutputAndDecoutInput):
            varsToAddToTransformOutputAndDecoutInput.append(varName)

    if ( (len(varsToAddToTransformOutputAndDecoutInput) == 0) and (atLeastOneForLoop == False) ):
        transformRunningOutputLine = "output := " + transformOutputList + "\n"
    else:
        transformRunningOutputLine = "output := list{" + transformOutputList
        #if (atLeastOneForLoop == True):
            #transformRunningOutputLine += ", " + transformOutputListForLoop
        for varName in varsToAddToTransformOutputAndDecoutInput:
            transformRunningOutputLine += ", " + varName
        if ( (atLeastOneForLoop == True) and (singleBF == False) and (canCollapseForLoopsInDecout == False) ):
            transformRunningOutputLine += ", " + transformOutputListForLoop
        transformRunningOutputLine += "}\n"

    transformLines.append(transformRunningOutputLine)
    transformLines.append("END :: func:" + config.transformFuncName + "\n")

    transformLines.append("\n")

    for varName in varsToAddToTransformOutputAndDecoutInput:
        decoutRunningInputLine += ", " + varName

    if ( (atLeastOneForLoop == True) and (singleBF == False) and (canCollapseForLoopsInDecout == False) ):
        decoutRunningInputLine += ", " + transformOutputListForLoop

    decoutRunningInputLine += "}\n"
    decoutLines.insert(1, decoutRunningInputLine)

    decoutLines.append("output := " + config.M + "\n")
    decoutLines.append("END :: func:" + decOutFunctionName + "\n\n")

    transformPlusDecoutLines = transformLines + decoutLines

    transformOutputListDecl = [transformOutputList + " := list\n"]
    transformOutputListDecl.append(transformOutputListForLoop + " := list\n")

    appendToLinesOfCode(transformOutputListDecl, getEndLineNoOfFunc(TYPES_HEADER))

    #printLinesOfCode()

    parseLinesOfCode(getLinesOfCode(), False)

    appendToLinesOfCode(transformPlusDecoutLines, getStartLineNoOfFunc(config.decryptFuncName))

    #printLinesOfCode()

    parseLinesOfCode(getLinesOfCode(), False)

    removeRangeFromLinesOfCode(getStartLineNoOfFunc(config.decryptFuncName), getEndLineNoOfFunc(config.decryptFuncName))

    parseLinesOfCode(getLinesOfCode(), False)
