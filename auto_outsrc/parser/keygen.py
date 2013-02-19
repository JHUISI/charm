import sdlpath
#from __future__ import print_function
from sdlparser.SDLParser import *
from transformNEW import *
from secretListInKeygen import getSecretList
from outsrctechniques import SubstituteVar, GetAttributeVars
import os, sys, string, random, importlib

linesOfCode = None
assignInfo = None
overflowAssignInfo = None
varTypes = None
astNodes = None
forLoops = None
publicVarNames = None
secretVarNames = None
varDepList = None
blindingFactors_Lists = []
blindingFactors_NonLists = []
varsThatAreBlinded = []
varsNameToSecretVarsUsed = {}
sharedBlindingFactorNames = {}
sharedBlindingFactorCounter = 0
#namesOfAllNonListBlindingFactors = []
mappingOfSecretVarsToBlindingFactors = {}
mappingOfSecretVarsToGroupType = {}
keygenElemToExponents = {}
overflowKeygenElemToExponents = {}
keygenElemToSMTExp = {}
SMTaddCounter = 0
SMTmulCounter = 0
#SMTleafCounter = 0
secretKeyElements = []
masterSecretKeyElements = []
allMskAndRndVars = []
varNamesForListDecls = []
bfsThatNeedRandomAssignments = []

mskVars = []
rndVars = []

nilType = 'nil'
bfMapKeyword = 'bfMap'
skBfMapKeyword = 'skBfMap'

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

def replaceVarInstancesInLineNoRange(startLineNo, endLineNo, origVarName, newVarName):
    for lineNoIndex in range(startLineNo, (endLineNo + 1)):
        indexIntoCodeStructs = lineNoIndex - 1
        currentBinNode = astNodes[indexIntoCodeStructs]
        ASTVisitor(SubstituteVar(origVarName,newVarName)).preorder(currentBinNode)
        processListOrExpandNodes(currentBinNode, origVarName, newVarName)
        binNodeAsString = str(currentBinNode)
        if (binNodeAsString == 'NONE'):
            binNodeAsString = "\n"
        substituteOneLineOfCode(binNodeAsString, lineNoIndex)

    updateCodeAndStructs()

def updateCodeAndStructs():
    global linesOfCode, assignInfo, varTypes, astNodes, forLoops, publicVarNames, secretVarNames, varDepList
    global overflowAssignInfo

    parseLinesOfCode(getLinesOfCode(), False)
    linesOfCode = getLinesOfCode()
    assignInfo = getAssignInfo()
    overflowAssignInfo = getOverflowAssignInfo()
    varTypes = getVarTypes()
    astNodes = getAstNodes()
    forLoops = getForLoops()
    publicVarNames = getPublicVarNames()
    secretVarNames = getSecretVarNames()
    varDepList = externalGetVarDepList()

def writeLinesToFuncAfterVarLastAssign(funcName, lineList, varName):
    if (varName == None):
        lineNo = getLineNoOfInputStatement(funcName) + 1
    else:
        lineNo = getLineNoOfLastAssign(funcName, varName) + 1
        if (lineNo == 1):
            lineNo = getLineNoOfInputStatement(funcName) + 1

    appendToLinesOfCode(lineList, lineNo)
    updateCodeAndStructs()
    return (lineNo + (len(lineList)))

def getLineNosOfAllAssigns(funcName, varNameToFind):
    if (funcName not in assignInfo):
        sys.exit("getLineNosOfAllAssigns in keygen.py:  funcName is not in assignInfo.")

    lineNos = []

    for currentVarName in assignInfo[funcName]:
        currentVarName_NoIndices = removeListIndices(currentVarName)
        if (currentVarName_NoIndices != varNameToFind):
            continue

        currentLineNo = assignInfo[funcName][currentVarName].getLineNo()
        lineNos.append(currentLineNo)

    return lineNos

def getLineNoOfLastAssign(funcName, varNameToFind):
    if (funcName not in assignInfo):
        sys.exit("getLineNoOfLastAssign in keygen.py:  funcName is not in assignInfo.")

    lastLineNo = 0

    for currentVarName in assignInfo[funcName]:
        currentVarName_NoIndices = removeListIndices(currentVarName)
        if (currentVarName_NoIndices != varNameToFind):
            continue

        currentLineNo = assignInfo[funcName][currentVarName].getLineNo()

        if (currentLineNo > lastLineNo):
            lastLineNo = currentLineNo

    #if (lastLineNo == 0):
        #sys.exit("getLineNoOfLastAssign in keygen.py:  could not find any line numbers matching the variable name and function name passed in.")

    possibleNewLastLineNo = getEndLineNoOfForLoop(funcName, lastLineNo)
    if (possibleNewLastLineNo != 0):
        lastLineNo = possibleNewLastLineNo

    return lastLineNo

def getIsVarList(keygenOutputElem, keygenOutputVarInfo):
    if ( (keygenOutputVarInfo.getIsList() == True) or (keygenOutputVarInfo.getIsSymmap() == True) or (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        return True

    if (str(keygenOutputVarInfo.getAssignNode().left).find(LIST_INDEX_SYMBOL) != -1):
        return True

    try:
        currentVarType = varTypes[TYPES_HEADER][keygenOutputElem].getType()
    except:
        return False

    if (currentVarType == ops.LIST):
        sys.exit("getIsVarList in keygen.py:  currentVarType is ops.LIST, not types.list.")

    if (currentVarType == types.list):
        return True

    return False

def removeListIndices(inputString):
    inputStringSplit = inputString.split(LIST_INDEX_SYMBOL)
    return inputStringSplit[0]

def removeListIndicesAndDupsFromList(inputList):
    retList = []

    for inputListEntry in inputList:
        entryWithoutIndices = removeListIndices(inputListEntry)
        if (entryWithoutIndices not in retList):
            retList.append(entryWithoutIndices)

    return retList

def isLastCharThisChar(inputString, possibleLastChar):
    lenString = len(inputString)
    if (inputString[lenString - 1] == possibleLastChar):
        return True

    return False

def writeForAllLoop(keygenOutputElem, resultDictionary, config):
    global blindingFactors_Lists, varNamesForListDecls, bfsThatNeedRandomAssignments

    listBlindingFactorName = config.blindingFactorPrefix + keygenOutputElem + config.blindingSuffix

    sameBFForWholeList = False
    currentBlindingFactorName = resultDictionary[keygenOutputElem]
    if (isLastCharThisChar(currentBlindingFactorName, LIST_INDEX_SYMBOL) == True):
        sameBFForWholeList = False
        currentBlindingFactorName = currentBlindingFactorName[0:(len(currentBlindingFactorName)-1)]
        resultDictionary[keygenOutputElem] = listBlindingFactorName + LIST_INDEX_SYMBOL
    else:
        sameBFForWholeList = True

    # if it's the same BF for whole list, we only need to grab the BF.  Otherwise, we need the whole
    # list of BFs.
    if (sameBFForWholeList == True):
        if (currentBlindingFactorName not in blindingFactors_Lists):
            blindingFactors_Lists.append(currentBlindingFactorName)
        if (currentBlindingFactorName not in bfsThatNeedRandomAssignments):
            bfsThatNeedRandomAssignments.append(currentBlindingFactorName)
    else:
        if (listBlindingFactorName not in blindingFactors_Lists):
            blindingFactors_Lists.append(listBlindingFactorName)

    if (keygenOutputElem not in varNamesForListDecls):
        varNamesForListDecls.append(keygenOutputElem)

    SDLLinesForKeygen = []

    SDLLinesForKeygen.append("BEGIN :: forall\n")
    SDLLinesForKeygen.append("forall{" + config.blindingLoopVar + " := " + keygenOutputElem + "}\n")

    if (sameBFForWholeList == True):
        #SDLLinesForKeygen.append(listBlindingFactorName + LIST_INDEX_SYMBOL + config.blindingLoopVar + " := " + currentBlindingFactorName + "\n")
        SDLLinesForKeygen.append(keygenOutputElem + config.blindingSuffix + LIST_INDEX_SYMBOL + config.blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + config.blindingLoopVar + " ^ (1/" + currentBlindingFactorName + ")\n")
    else:
        SDLLinesForKeygen.append(listBlindingFactorName + LIST_INDEX_SYMBOL + config.blindingLoopVar + " := random(ZR)\n")
        SDLLinesForKeygen.append(keygenOutputElem + config.blindingSuffix + LIST_INDEX_SYMBOL + config.blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + config.blindingLoopVar + " ^ (1/" + listBlindingFactorName + LIST_INDEX_SYMBOL + config.blindingLoopVar + ")\n")

    SDLLinesForKeygen.append("END :: forall\n")

    lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
    replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), keygenOutputElem, (keygenOutputElem + config.blindingSuffix))

'''
#def writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls, sharedBlindingFactorName, repeatBlindingFactor):
def writeForAllLoop(keygenOutputElem, resultDictionary, config):
    global blindingFactors_Lists, varsThatAreBlinded, blindingFactors_NonLists
    global mappingOfSecretVarsToBlindingFactors

    #sameMasterSecret = False

    listBlindingFactorName = blindingFactorPrefix + keygenOutputElem + blindingSuffix
    #(sharedBlindingFactorName, repeatBlindingFactor) = getCurrentBlindingFactorName(keygenOutputElem)
    #if (listBlindingFactorName != sharedBlindingFactorName):
        #sameMasterSecret = True

    sameBFForWholeList = False
    currentBlindingFactorName = resultDictionary[keygenOutputElem]
    if (isLastCharThisChar(currentBlindingFactorName, LIST_INDEX_SYMBOL) == True):
        sameBFForWholeList = False
        currentBlindingFactorName = currentBlindingFactorName[0:(len(currentBlindingFactorName)-1)]
    else:
        sameBFForWholeList = True

    if (currentBlindingFactorName not in blindingFactors_Lists):
        blindingFactors_Lists.append(currentBlindingFactorName)

    #if (sameMasterSecret == False):
    #blindingFactors_Lists.append(keygenOutputElem)

    #varsThatAreBlinded.append(keygenOutputElem)

    SDLLinesForKeygen = []

    #SDLLinesForKeygen.append(blindingLoopVarLength + " := len(" + keygenOutputElem + ")\n")

    #SDLLinesForKeygen.append(keygenOutputElem + keysForKeygenElemSuffix + " := " + KEYS_FUNC_NAME + "(" + keygenOutputElem + ")\n")

    SDLLinesForKeygen.append("BEGIN :: forall\n")
    #SDLLinesForKeygen.append("BEGIN :: for\n")

    SDLLinesForKeygen.append("forall{" + blindingLoopVar + " := " + keygenOutputElem + "}\n")
    #SDLLinesForKeygen.append("for{" + blindingLoopVar + " := 0, " + blindingLoopVarLength + "}\n")

    #SDLLinesForKeygen.append(keygenOutputElem + loopVarForKeygenElemKeys + " := " + keygenOutputElem + keysForKeygenElemSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + "\n")

    #if (sameMasterSecret == True):
        #SDLLinesForKeygen.append(listBlindingFactorName + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + sharedBlindingFactorName + "\n")
        #if (sharedBlindingFactorName not in blindingFactors_NonLists):
            #blindingFactors_NonLists.append(sharedBlindingFactorName)
    #else:

    if (sameBFForWholeList == True):
        SDLLinesForKeygen.append(listBlindingFactorName + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + currentBlindingFactorName + "\n")
    else:
        SDLLinesForKeygen.append(listBlindingFactorName + LIST_INDEX_SYMBOL + blindingLoopVar + " := random(ZR)\n")

    SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + blindingLoopVar + " ^ (1/" + listBlindingFactorName + LIST_INDEX_SYMBOL + config.blindingLoopVar + ")\n")

    SDLLinesForKeygen.append("END :: forall\n")
    #SDLLinesForKeygen.append("END :: for\n")


    if (sameMasterSecret == True):
        mappingOfSecretVarsToBlindingFactors[keygenOutputElem] = [sharedBlindingFactorName]
    else:
        mappingOfSecretVarsToBlindingFactors[keygenOutputElem] = [listBlindingFactorName]
        mappingOfSecretVarsToBlindingFactors[keygenOutputElem].append(listNameIndicator)


    #varsToBlindList.remove(keygenOutputElem)
    #if (keygenOutputElem in varNamesForListDecls):
        #sys.exit("writeForAllLoop in keygen.py attempted to add duplicate keygenOutputElem to varNamesForListDecls -- 2 of 2.")

    #if (sameMasterSecret == False):
    #varNamesForListDecls.append(keygenOutputElem)

    lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
    replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
'''

def varListContainsParentDict(varList, parentDict):
    for varName in varList:
        varNameWithoutIndices = removeListIndices(varName)
        if (varNameWithoutIndices == parentDict):
            return True

    return False

def getShouldThisElemBeUnblinded(keygenOutputElem, varsModifiedInKeygen, keygenFuncName):
    if (keygenOutputElem == keygenSecVar):
        return False

    if (keygenOutputElem in publicVarNames):
        return True

    if ( (keygenOutputElem not in secretVarNames) and (keygenOutputElem not in varsModifiedInKeygen) ):
        return True

    if (keygenFuncName not in varDepList):
        sys.exit("getShouldThisElemBeUnblinded in keygen.py:  keygen function name is not in varDepList.")

    if (keygenOutputElem not in varDepList[keygenFuncName]):
        sys.exit("getShouldThisElemBeUnblinded in keygen.py:  keygenOutputElem parameter passed in is not in varDepList[keygenFuncName].")

    varDepsOfThisElem = varDepList[keygenFuncName][keygenOutputElem]

    for varDep in varDepsOfThisElem:
        tempVarDep = varDep
        listSymIndex = tempVarDep.find(LIST_INDEX_SYMBOL)
        if (listSymIndex != -1):
            tempVarDep = tempVarDep[0:listSymIndex]
        if (tempVarDep in secretVarNames):
            return False

    return True

def getSecretVarsUsed(keygenOutputElem, keygenFuncName):
    retList = []

    if keygenOutputElem not in varDepList[keygenFuncName]:
        return []

    varDepsOfThisElem = varDepList[keygenFuncName][keygenOutputElem]

    for varDep in varDepsOfThisElem:
        tempVarDep = varDep
        listSymIndex = tempVarDep.find(LIST_INDEX_SYMBOL)
        if (listSymIndex != -1):
            #tempVarDep = tempVarDep[0:listSymIndex]
            pass
        #if (tempVarDep in secretVarNames):
        if (isVarNameInList(tempVarDep, secretVarNames) == True):
            if (tempVarDep not in retList):
                retList.append(tempVarDep)

    return retList

def isVarNameInList(varName, varList):
    listSymIndex = varName.find(LIST_INDEX_SYMBOL)
    if (listSymIndex != -1):
        varName = varName[0:listSymIndex]

    if (varName in varList):
        return True

    return False

def getElementsOfSameGroupType(keygenOutputElem):
    retList = []

    groupTypeOfThisElement = mappingOfSecretVarsToGroupType[keygenOutputElem]

    for currentElement in mappingOfSecretVarsToGroupType:
        currentGroupType = mappingOfSecretVarsToGroupType[currentElement]
        if ( (currentGroupType == groupTypeOfThisElement) and (currentElement != keygenOutputElem) ):
            retList.append(currentElement)

    return retList

def getBlindingNonListFactorsOfSameGroupType(elementsOfSameGroupType):
    retList = []

    for element in elementsOfSameGroupType:
        if element not in mappingOfSecretVarsToBlindingFactors:
            continue
        currentBlindingFactorList = mappingOfSecretVarsToBlindingFactors[element]
        if ( (currentBlindingFactorList[0] not in retList) and (currentBlindingFactorList[0] in blindingFactors_NonLists) ):
            retList.append(currentBlindingFactorList[0])

    return retList

def getCurrentBlindingFactorName(keygenOutputElem):
    global sharedBlindingFactorNames, sharedBlindingFactorCounter, blindingFactors_NonLists
    #global namesOfAllNonListBlindingFactors

    groupTypeOfThisElement = mappingOfSecretVarsToGroupType[keygenOutputElem]

    elementsOfSameGroupType = getElementsOfSameGroupType(keygenOutputElem)

    #print("current element is ", keygenOutputElem)
    #print("of same type are ", elementsOfSameGroupType)

    blindingNonListFactorsOfSameGroupType = getBlindingNonListFactorsOfSameGroupType(elementsOfSameGroupType)

    #print("BFs of same group type:  ", blindingNonListFactorsOfSameGroupType)

    if (len(blindingNonListFactorsOfSameGroupType) > 1):
        sys.exit("getCurrentBlindingFactorName in keygen.py:  more than one blinding factor of same group type; should never happen -- error in system logic.")

    if (len(blindingNonListFactorsOfSameGroupType) == 1):
        return (blindingNonListFactorsOfSameGroupType[0], True)

    if (len(varsNameToSecretVarsUsed[keygenOutputElem]) > 1):
        return (blindingFactorPrefix + keygenOutputElem + blindingSuffix, False)

    secretVarForThisKeygenElem = varsNameToSecretVarsUsed[keygenOutputElem][0]

    if (secretVarForThisKeygenElem in sharedBlindingFactorNames):
        return (sharedBlindingFactorNames[secretVarForThisKeygenElem], True)

    sharedBlindingFactorNames[secretVarForThisKeygenElem] = blindingFactorPrefix + str(sharedBlindingFactorCounter) + blindingSuffix
    sharedBlindingFactorCounter += 1

    if (sharedBlindingFactorNames[secretVarForThisKeygenElem] not in blindingFactors_NonLists):
        blindingFactors_NonLists.append(sharedBlindingFactorNames[secretVarForThisKeygenElem])

    #if (sharedBlindingFactorNames[secretVarForThisKeygenElem] not in namesOfAllNonListBlindingFactors):
        #namesOfAllNonListBlindingFactors.append(sharedBlindingFactorNames[secretVarForThisKeygenElem])

    return (sharedBlindingFactorNames[secretVarForThisKeygenElem], False)

def rearrangeListWRTSecretVars(inputList, keygenFuncName):
    mappingOfVarNameToSecretVarsUsedLocal = {}

    for element in inputList:
        secretVarsUsed = getSecretVarsUsed(element, keygenFuncName)
        mappingOfVarNameToSecretVarsUsedLocal[element] = secretVarsUsed

    outputList = []

    for element in mappingOfVarNameToSecretVarsUsedLocal:
        if (len(mappingOfVarNameToSecretVarsUsedLocal[element]) > 0):
            outputList.append(element)

    for element in mappingOfVarNameToSecretVarsUsedLocal:
        if (element not in outputList):
            outputList.append(element)

    return outputList

def getVarsUsedInFuncs(funcName):
    retList = []

    if funcName not in assignInfo:
        sys.exit("getVarsUsedInFuncs in keygen.py:  function name passed in is not in AssignInfo.")

    varsInThatFunc = assignInfo[funcName]

    for currentVarName in varsInThatFunc:
        varInfoObj = varsInThatFunc[currentVarName]
        assignNode = varInfoObj.getAssignNode()
        assignNodeRight = assignNode.right
        if (assignNodeRight.type != ops.FUNC):
            continue

        if (str(assignNodeRight.attr) == LEN_FUNC_NAME):
            continue

        for listNode in assignNodeRight.listNodes:
            if (listNode not in retList):
                retList.append(listNode)

    return retList

def useAlternateBlinding(keygenOutputElem):
    return False

    elementType = getVarTypeInfoRecursive(BinaryNode(keygenOutputElem), keygenFuncName)

    decryptVarsUsedInFuncs = getVarsUsedInFuncs(decryptFuncName)
    if (keygenOutputElem in decryptVarsUsedInFuncs):
        return False

    if (elementType in [types.G1, types.G2, types.GT, types.ZR]):
        return True

    if (elementType in [types.listG1, types.listG2, types.listGT, types.listZR]):
        return True

    return False

def getWhichNonListBFToShare():
    if (len(sharedBlindingFactorNames) == 0):
        return blindingFactors_NonLists[0]

    for keyName in sharedBlindingFactorNames:
        return sharedBlindingFactorNames[keyName]

def addExponentsToAllMskAndRndVarsList(node):
    global allMskAndRndVars

    allExponentNames = GetAttributeVars(node, True)

    for exp in allExponentNames:
        if (exp not in allMskAndRndVars):
            allMskAndRndVars.append(exp)

def stringIsNumber(inputString):
    if (inputString[0] == "-"):
        inputString = inputString[1:len(inputString)]

    if (inputString.isdigit() == True):
        return True

    return False

def searchForExponentsRecursive(node, exponentsList, levelNumber):
    if (node.type == ops.EXP):
        if ( (str(node.right) not in exponentsList) and (stringIsNumber(str(node.right)) == False) ):
            exponentsList.append((node.right, levelNumber + 1))
            addExponentsToAllMskAndRndVarsList(node.right)
    #else:
    if (node.left != None):
        if (node.type == ops.EXP):
            searchForExponentsRecursive(node.left, exponentsList, levelNumber - 1)
        else:
            searchForExponentsRecursive(node.left, exponentsList, levelNumber)
    if (node.right != None):
        if (node.type == ops.EXP):
            searchForExponentsRecursive(node.right, exponentsList, levelNumber + 1)
        else:
            searchForExponentsRecursive(node.right, exponentsList, levelNumber)

def arrangeExponentsForArithmetic(exponentsList):
    expression = ""
    previousLevelNumber = -9999

    if (len(exponentsList) == 0):
        return []

    if (len(exponentsList) == 1):
        return [exponentsList[0][0]]

    exponent = exponentsList[0][0]
    previousLevelNumber = exponentsList[0][1]

    expression += str(exponent)

    firstOne = True

    for indivEntry in exponentsList:
        if (firstOne == True):
            firstOne = False
            continue

        exponent = indivEntry[0]
        currentLevelNumber = indivEntry[1]

        if (previousLevelNumber <= currentLevelNumber):
            expression += " + "
        else:
            expression += " * "

        expression += str(exponent)

        previousLevelNumber = currentLevelNumber

    parser = SDLParser()
    node = parser.parse(expression)

    return [node]

def searchForExponents(node):
    exponentsList = []

    searchForExponentsRecursive(node, exponentsList, 0)
    exponentsArrangedForArithmetic = arrangeExponentsForArithmetic(exponentsList)
    return exponentsArrangedForArithmetic

def shouldWeUseFullBaseElems(keygenOutputElem, config):
    if (keygenOutputElem not in assignInfo[config.keygenFuncName]):
        sys.exit("shouldWeUseFullBaseElems in keygen.py:  keygenOutputElem parameter passed in is not in assignInfo[keygenFuncName].")

    assignInfoVarEntry = assignInfo[config.keygenFuncName][keygenOutputElem]
    baseElemsOnlyNode = assignInfoVarEntry.getAssignBaseElemsOnlyThisFunc()
    baseElemsOnly = GetAttributeVars(baseElemsOnlyNode, True)
    for baseElem in baseElemsOnly:
        if baseElem in masterSecretKeyElements:
            groupTypeOfThisElem = getVarTypeInfoRecursive(BinaryNode(baseElem), config.setupFuncName)
            if (groupTypeOfThisElem in [types.G1, types.G2, types.GT]):
                return True

    return False

def getWhichBaseElemsOnlyToUse(keygenOutputElem, config):
    assignInfoVarEntry = assignInfo[config.keygenFuncName][keygenOutputElem]
    useFullBaseElems = shouldWeUseFullBaseElems(keygenOutputElem, config)
    if (useFullBaseElems == True):
        baseElemsOnly = assignInfoVarEntry.getAssignBaseElemsOnly()
    else:
        baseElemsOnly = assignInfoVarEntry.getAssignBaseElemsOnlyThisFunc()

    if (baseElemsOnly.type != ops.LIST):
        baseElemsOnly = makeReplacementsForMasterPublicVars(baseElemsOnly, config)

    return baseElemsOnly

def getListElementsOfKeygenOutputElem(keygenOutputElem, config):
    retList = []

    for varInfoObj in assignInfo[config.keygenFuncName]:
        if (varInfoObj.startswith(keygenOutputElem + LIST_INDEX_SYMBOL) == True):
            retList.append(varInfoObj)

    return retList

def getKeygenElemToExponentsDictEntry(keygenOutputElem, keygenFuncName, config):
    global keygenElemToExponents

    if (keygenOutputElem not in assignInfo[config.keygenFuncName]):
        #sys.exit("getKeygenElemToExponentsDictEntry in keygen.py:  keygenOutputElem parameter passed in is not in assignInfo[keygenFuncName].")
        keygenElemToExponents[keygenOutputElem] = []
        return

    listElementsOfThisElem = getListElementsOfKeygenOutputElem(keygenOutputElem, config)
    #print(listElementsOfThisElem)

    if (len(listElementsOfThisElem) == 0):
        baseElemsOnly = getWhichBaseElemsOnlyToUse(keygenOutputElem, config)
        keygenElemToExponents[keygenOutputElem] = searchForExponents(baseElemsOnly)
        return

    keygenElemToExponents[keygenOutputElem] = 'placeholder_so_it_is_picked_up_later_as_having_list_entries'

    for listElem in listElementsOfThisElem:
        baseElemsOnly = getWhichBaseElemsOnlyToUse(listElem, config)
        keygenElemToExponents[listElem] = searchForExponents(baseElemsOnly)

def getAllMasterPubVarsAsStrings(config):
    if (config.setupFuncName not in assignInfo):
        sys.exit("getAllMasterPubVarsAsStrings in keygen.py:  config.setupFuncName not in assignInfo.")

    retList = {}

    for mpk in config.masterPubVars:
        if (mpk not in assignInfo[config.setupFuncName]):
            sys.exit("getAllMasterPubVarsAsStrings in keygen.py:  one of the pub vars was not in assignInfo[config.setupFuncName].")

        mpkVarInfoObj = assignInfo[config.setupFuncName][mpk]
        mpkVarDeps = mpkVarInfoObj.getVarDeps()
        for mpkVarDep in mpkVarDeps:
            if (mpkVarDep not in assignInfo[config.setupFuncName]):
                continue #I wanted to throw an error here, but LW would be a problem if I did, so continue is fine for now

            if (mpkVarDep in retList):
                continue

            baseElemsOnly = assignInfo[config.setupFuncName][mpkVarDep].getAssignBaseElemsOnly()
            retList[mpkVarDep] = str(baseElemsOnly)

    return retList

def ensureParenthesesAround(inputString):
    if (inputString[0] != "("):
        inputString = "(" + inputString

    lenInputString = len(inputString)

    if (inputString[(lenInputString - 1)] != ")"):
        inputString = inputString + ")"

    return inputString

def makeReplacementsForMasterPublicVars(node, config):
    nodeAsStr = str(node)
    masterPubVarsAsStrings = getAllMasterPubVarsAsStrings(config)
    for mpkString in masterPubVarsAsStrings:
        whatToReplaceWith = mpkString
        whatToLookFor = (masterPubVarsAsStrings[mpkString])
        #putting parenthese around everything means we might not catch something, but so be it
        whatToLookFor = ensureParenthesesAround(whatToLookFor)
        #print("what to look for:  ", whatToLookFor)
        #print("what to replace with:  ", whatToReplaceWith)
        if (whatToLookFor == whatToReplaceWith):
            continue

        nodeAsStr = nodeAsStr.replace(whatToLookFor, whatToReplaceWith)

    #print(node)
    #print(nodeAsStr)

    parser = SDLParser()
    newNode = parser.parse(nodeAsStr)
    if (type(newNode).__name__ == 'str'):
        newNode = BinaryNode(newNode)
    return newNode

def getAllKeygenElemsToExponentsDictEntries(keygenOutputElem, keygenFuncName, config):
    #global keygenElemToExponents
    global secretKeyElements

    if (keygenOutputElem not in secretKeyElements):
        secretKeyElements.append(keygenOutputElem)

    getKeygenElemToExponentsDictEntry(keygenOutputElem, keygenFuncName, config)

    if (keygenOutputElem not in assignInfo[keygenFuncName]):
        return

    keygenOutputVarInfo = assignInfo[keygenFuncName][keygenOutputElem]

    if ( (keygenOutputVarInfo.getIsList() == True) and (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        listMembers = keygenOutputVarInfo.getListNodesList()
        listMembersORIGINAL = listMembers
        listMembers = rearrangeListWRTSecretVars(listMembers, keygenFuncName)

        for listMember in listMembers:
            getAllKeygenElemsToExponentsDictEntries(listMember, keygenFuncName, config)

def getIndividualKeygenElemToSMTExpression(exponents, config):
    global SMTaddCounter, SMTmulCounter

    SMTaddCounter = 0
    SMTmulCounter = 0
    #SMTleafCounter = 0

    retExpression = {}

    if (len(exponents) == 0):
        return {}

    retExpression[config.rootNodeName] = []

    if ( (len(exponents) == 1) and (exponents[0].type == ops.ATTR) ):
        retExpression[config.rootNodeName].append(config.leafNodeName)
        retExpression[config.leafNodeName] = []
        retExpression[config.leafNodeName].append(str(exponents[0]))
        return retExpression

    if (len(exponents) == 1):
        getSMTExpressionForOneExponent(exponents[0], config.rootNodeName, retExpression, config)
        return retExpression

    currentKey = config.addNodePrefix+str(SMTaddCounter)
    SMTaddCounter += 1
    retExpression[config.rootNodeName].append(currentKey)
    retExpression[currentKey] = []

    for exponent in exponents:
        getSMTExpressionForOneExponent(exponent, currentKey, retExpression, config)

    return retExpression

def getSMTExpressionForOneExponent(exponent, parentKey, retExpression, config):
    global SMTaddCounter, SMTmulCounter

    if ( (exponent.type == ops.ADD) or (exponent.type == ops.SUB) ):
        currentKey = config.addNodePrefix+str(SMTaddCounter)
        SMTaddCounter += 1
        if (parentKey != None):
            retExpression[parentKey].append(currentKey)
        retExpression[currentKey] = []
        getSMTExpressionForOneExponent(exponent.left, currentKey, retExpression, config)
        getSMTExpressionForOneExponent(exponent.right, currentKey, retExpression, config)

    if ( (exponent.type == ops.MUL) or (exponent.type == ops.DIV) ):
        currentKey = config.mulNodePrefix+str(SMTmulCounter)
        SMTmulCounter += 1
        if (parentKey != None):
            retExpression[parentKey].append(currentKey)
        retExpression[currentKey] = []
        getSMTExpressionForOneExponent(exponent.left, currentKey, retExpression, config)
        getSMTExpressionForOneExponent(exponent.right, currentKey, retExpression, config)

    if (exponent.type == ops.ATTR):
        retExpression[parentKey].append(str(exponent))

'''
def getSMTExpressionForOneExponent(exponent):
    pass

def getIndividualKeygenElemToSMTExpression(exponents):
    retExpression = {}

    #print(exponents)

    if (len(exponents) == 0):
        return {}

    if (len(exponents) == 1):
        if (exponents[0].type == ops.ATTR):
            retExpression['root'] = str(exponents[0])
        else:
            retExpression['root'] = getSMTExpressionForOneExponent(exponents[0])

        return retExpression

    retExpression['root'] = 'ADD0'
    retExpression['ADD0'] = []

    for exponent in exponents:
        if (exponent.type == ops.ATTR):
            retExpression['ADD0'].append(str(exponent))
            continue

        nextExpToAdd = getSMTExpressionForOneExponent(exponent)
        retExpression['ADD0'].append(nextExpToAdd)

    return retExpression
'''

def isResultOfFunctionWithZRRetType(exp, config):
    if (exp not in assignInfo[config.keygenFuncName]):
        return False

    varInfoObj = assignInfo[config.keygenFuncName][exp]
    assignNodeRight = varInfoObj.getAssignNode().right

    if (assignNodeRight.type != ops.FUNC):
        return False

    funcName = str(assignNodeRight.attr)

    if (funcName not in builtInTypes):
        return False

    retType = builtInTypes[funcName]

    if (retType in [types.ZR, types.listZR, types.symmapZR]):
        return True

    return False

def addMskRndVars(config):
    global keygenElemToSMTExp, mskVars, rndVars

    #keygenElemToSMTExp[mskVars] = []
    #keygenElemToSMTExp[rndVars] = []

    for exp in allMskAndRndVars:
        if ( (exp in assignInfo[config.setupFuncName]) and (exp not in assignInfo[config.keygenFuncName]) ):
            if (exp not in mskVars):
                mskVars.append(exp)
        elif (isResultOfFunctionWithZRRetType(exp, config) == True):
            if (exp not in mskVars):
                mskVars.append(exp)
        elif ( (exp not in assignInfo[config.setupFuncName]) and (exp in assignInfo[config.keygenFuncName]) ):
            if (exp not in rndVars):
                rndVars.append(exp)
        else:
            print(exp)
            print(mskVars)
            print(rndVars)
            sys.exit("addMskRndVars in keygen.py:  exponent name is supposed to appear in either config.setupFuncName or config.keygenFuncName, but not both and not neither, which is what is happening here.")

def getKeygenElemToSMTExpressions_Ind(keygenElemToExp, config):
    global keygenElemToSMTExp

    listElementsOfThisElem = getListElementsOfKeygenOutputElem(keygenElemToExp, config)

    if (len(listElementsOfThisElem) == 0):
        exponents = keygenElemToExponents[keygenElemToExp]
        keygenElemToSMTExp[keygenElemToExp] = getIndividualKeygenElemToSMTExpression(exponents, config)
        return

    keygenElemToSMTExp[keygenElemToExp] = {}
    keygenElemToSMTExp[keygenElemToExp][config.rootNodeName] = [config.listNodeName]
    keygenElemToSMTExp[keygenElemToExp][config.listNodeName] = listElementsOfThisElem

    for listElem in listElementsOfThisElem:
        exponents = keygenElemToExponents[listElem]
        keygenElemToSMTExp[keygenElemToExp][listElem] = getIndividualKeygenElemToSMTExpression(exponents, config)

def getKeygenElemToSMTExpressions(config):
    global keygenElemToSMTExp

    for keygenElemToExp in keygenElemToExponents:
        # DFA.  If it has a LIST_INDEX_SYMBOL, it's actually a subelement, which we'll handle later.
        if (keygenElemToExp.count(LIST_INDEX_SYMBOL) > 0):
            continue
        if (keygenElemToExp == config.keygenSecVar):
            secVarRetList = []
            for secretKeyElem in secretKeyElements:
                if (secretKeyElem != config.keygenSecVar):
                    secVarRetList.append(secretKeyElem)
            keygenElemToSMTExp[keygenElemToExp] = secVarRetList
        else:
            getKeygenElemToSMTExpressions_Ind(keygenElemToExp, config)

    addMskRndVars(config)

def getBFCountsDict(resultDictionary):
    retDict = {}

    for skElem in resultDictionary:
        bfOfThisElem = resultDictionary[skElem]
        if (bfOfThisElem not in retDict):
            retDict[bfOfThisElem] = 0
        countOfThisBF = retDict[bfOfThisElem]
        retDict[bfOfThisElem] = countOfThisBF + 1

    #we don't want nilType factoring into our counts during the apply group optimization
    retDict[nilType] = 0

    return retDict

def turnListBFsIntoSingleBFs(resultDictionary):
    for key in resultDictionary:
        value = resultDictionary[key]
        if (isLastCharThisChar(value, LIST_INDEX_SYMBOL) == True):
            value = value[0:(len(value) - 1)]
            resultDictionary[key] = value

def applyGroupSharingOptimization(resultDictionary, config):
    global mappingOfSecretVarsToGroupType

    turnListBFsIntoSingleBFs(resultDictionary)

    bfCountsDict = getBFCountsDict(resultDictionary)

    for skElem in resultDictionary:
        groupTypeOfSkElem = getVarTypeInfoRecursive(BinaryNode(skElem), config.keygenFuncName)
        mappingOfSecretVarsToGroupType[skElem] = groupTypeOfSkElem

    newResultDictionary = copy.deepcopy(resultDictionary)

    for skElem in resultDictionary:
        bfOfThisElem = newResultDictionary[skElem]
        groupTypeOfThisElem = mappingOfSecretVarsToGroupType[skElem]
        mappingOfSameGroupTypeElemToBFCount = {}
        for skElem2 in resultDictionary:
            if (skElem == skElem2):
                continue

            if (mappingOfSecretVarsToGroupType[skElem] != mappingOfSecretVarsToGroupType[skElem2]):
                continue

            if (newResultDictionary[skElem] == newResultDictionary[skElem2]):
                continue

            #mappingOfSameGroupTypeElemToBFCount[skElem2] = bfCountsDict[skElem2]

            bfOfThisElem2 = newResultDictionary[skElem2]

            if (bfOfThisElem2 == nilType):
                continue

            if (bfCountsDict[bfOfThisElem2] >= bfCountsDict[bfOfThisElem]):
                newResultDictionary[skElem] = bfOfThisElem2

        #sameGroupTypeElemWithHighestBFCount = getSameGroupTypeElemWithHighestBFCount(mappingOfSameGroupTypeElemToBFCount)
        #bfToUseForThisElem = resultDictionary[sameGroupTypeElemWithHighestBFCount]
        #newResultDictionary[skElem] = bfToUseForThisElem

    for skElem in resultDictionary:
        if (skElem not in newResultDictionary):
            newResultDictionary[skElem] = resultDictionary[skElem]

    return newResultDictionary

def getSameGroupTypeElemWithHighestBFCount(mappingOfSameGroupTypeElemToBFCount):
    highestBFCountSoFar = -1
    elemWithHighestBFCountSoFar = None

    for elem in mappingOfSameGroupTypeElemToBFCount:
        currentBFCount = mappingOfSameGroupTypeElemToBFCount[elem]
        if (currentBFCount > highestBFCountSoFar):
            highestBFCountSoFar = currentBFCount
            elemWithHighestBFCountSoFar = elem

    return elemWithHighestBFCountSoFar

def applyBlindingFactorsToScheme(resultDictionary, config):
    for skElem in resultDictionary:
        applyBlindingFactorsToScheme_Individual(resultDictionary, skElem, config)

def applyBlindingFactorsToScheme_Individual(resultDictionary, keygenOutputElem, config):
    global blindingFactors_NonLists, secretKeyElements

    if keygenOutputElem not in secretKeyElements:
        secretKeyElements.append(keygenOutputElem)

    SDLLinesForKeygen = []

    if (resultDictionary[keygenOutputElem] == nilType):
        SDLLinesForKeygen.append(keygenOutputElem + config.blindingSuffix + " := " + keygenOutputElem + "\n")
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), keygenOutputElem, (keygenOutputElem + config.blindingSuffix))
        return

    if (keygenOutputElem not in assignInfo[config.keygenFuncName]):
        if (varListContainsParentDict(assignInfo[config.keygenFuncName].keys(), keygenOutputElem) == False):
            sys.exit("keygen output element passed to applyBlindingFactorsToScheme_Individual in keygen.py is not in assignInfo[keygenFuncName], and is not a parent dictionary of one of the variables in assignInfo[keygenFuncName].")
        writeForAllLoop(keygenOutputElem, resultDictionary, config)
        return

    keygenOutputVarInfo = assignInfo[config.keygenFuncName][keygenOutputElem]
    isVarList = getIsVarList(keygenOutputElem, keygenOutputVarInfo)

    currentBlindingFactorName = resultDictionary[keygenOutputElem]

    if (isVarList == False):
        if (isLastCharThisChar(currentBlindingFactorName, LIST_INDEX_SYMBOL) == True):
            sys.exit("applyBlindingFactorsToScheme_Individual in keygen.py:  variable isn't supposed to be a list, but the blinding factor from resultDictionary has a pound sign at the end of it.")
        if (currentBlindingFactorName not in blindingFactors_NonLists):
            blindingFactors_NonLists.append(currentBlindingFactorName)
        SDLLinesForKeygen.append(keygenOutputElem + config.blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + currentBlindingFactorName + ")\n")
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), keygenOutputElem, (keygenOutputElem + config.blindingSuffix))
        return

    if ( (keygenOutputVarInfo.getIsList() == True) and (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        listMembers = keygenOutputVarInfo.getListNodesList()
        listMembersString = ""
        for listMember in listMembers:
            listMembersString += listMember + config.blindingSuffix + ", "
        listMembersString = listMembersString[0:(len(listMembersString) - 2)]
        SDLLinesForKeygen.append(keygenOutputElem + config.blindingSuffix + " := list{" + listMembersString + "}\n")
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), keygenOutputElem, (keygenOutputElem + config.blindingSuffix))
        return

    writeForAllLoop(keygenOutputElem, resultDictionary, config)
    return

def addAssignmentForSKBlinded(config):
    skVarInfo = assignInfo[config.keygenFuncName][config.keygenSecVar]
    skVarDeps = skVarInfo.getVarDeps()
    if (len(skVarDeps) == 0):
        sys.exit("addAssignmentForSKBlinded in keygen.py:  no variable dependencies found for secret key variable name given in config file.")

    #print(skVarDeps)
    #sys.exit("test")

    outputString = ""
    outputString += config.keygenSecVar + config.blindingSuffix + " := list{"
    for varDep in skVarDeps:
        outputString += varDep + ", "
    outputString = outputString[0:(len(outputString) - len(", "))]
    outputString += "}\n"

    lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(config.keygenFuncName, [outputString], config.keygenSecVar)
    replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(config.keygenFuncName), config.keygenSecVar, (config.keygenSecVar + config.blindingSuffix))

def blindKeygenOutputElement(keygenOutputElem, varsToBlindList, varNamesForListDecls, keygenFuncName):
    global blindingFactors_NonLists, varsThatAreBlinded, varsNameToSecretVarsUsed
    global mappingOfSecretVarsToBlindingFactors, mappingOfSecretVarsToGroupType
    #global keygenElemToExponents
    global secretKeyElements

    #keygenElemToExponents[keygenOutputElem] = []
    #getKeygenElemToExponentsDictEntry(keygenOutputElem)

    #print(keygenElemToExponents)

    if (keygenOutputElem not in secretKeyElements):
        secretKeyElements.append(keygenOutputElem)

    groupTypeOfThisElement = getVarTypeInfoRecursive(BinaryNode(keygenOutputElem), keygenFuncName)
    mappingOfSecretVarsToGroupType[keygenOutputElem] = groupTypeOfThisElement

    SDLLinesForKeygen = []

    varsModifiedInKeygen = list(assignInfo[keygenFuncName].keys())
    varsModifiedInKeygen = removeListIndicesAndDupsFromList(varsModifiedInKeygen)

    shouldThisElemBeUnblinded = getShouldThisElemBeUnblinded(keygenOutputElem, varsModifiedInKeygen, keygenFuncName)

    if (shouldThisElemBeUnblinded == True):
        #if (isGroupElement(keygenOutputElem) == False):
        if ( (useAlternateBlinding(keygenOutputElem) == False) or (len(blindingFactors_NonLists) == 0) or (keygenOutputElem not in assignInfo[keygenFuncName]) ):
            varsNameToSecretVarsUsed[keygenOutputElem] = []
            SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + "\n")
            lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
            replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
            return keygenOutputElem
        varsNameToSecretVarsUsed[keygenOutputElem] = []
        currentBlindingFactorName = getWhichNonListBFToShare()
        repeatBlindingFactor = True
    else:
        secretVarsUsed = getSecretVarsUsed(keygenOutputElem, keygenFuncName)
        varsNameToSecretVarsUsed[keygenOutputElem] = secretVarsUsed
        (currentBlindingFactorName, repeatBlindingFactor) = getCurrentBlindingFactorName(keygenOutputElem)

    if (keygenOutputElem not in assignInfo[keygenFuncName]):
        if (varListContainsParentDict(assignInfo[keygenFuncName].keys(), keygenOutputElem) == False):
            sys.exit("keygen output element passed to blindKeygenOutputElement in keygen.py is not in assignInfo[keygenFuncName], and is not a parent dictionary of one of the variables in assignInfo[keygenFuncName].")
        writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls, currentBlindingFactorName, repeatBlindingFactor)
        return keygenOutputElem

    keygenOutputVarInfo = assignInfo[keygenFuncName][keygenOutputElem]

    isVarList = getIsVarList(keygenOutputElem, keygenOutputVarInfo)

    #currentBlindingFactorName = blindingFactorPrefix + keygenOutputElem + blindingSuffix

    if (isVarList == False):
        if (repeatBlindingFactor == False):
            if (currentBlindingFactorName not in blindingFactors_NonLists):
                blindingFactors_NonLists.append(currentBlindingFactorName)
            #SDLLinesForKeygen.append(currentBlindingFactorName + " := random(ZR)\n")
            #blindingFactors_NonLists.append(currentBlindingFactorName)
        varsThatAreBlinded.append(keygenOutputElem)
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + currentBlindingFactorName + ")\n")
        mappingOfSecretVarsToBlindingFactors[keygenOutputElem] = [currentBlindingFactorName]
        #varsToBlindList.remove(keygenOutputElem)
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
        return keygenOutputElem

    if ( (keygenOutputVarInfo.getIsList() == True) and (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        listMembers = keygenOutputVarInfo.getListNodesList()
        listMembersORIGINAL = listMembers
        listMembers = rearrangeListWRTSecretVars(listMembers, keygenFuncName)
        listMembersString = ""
        for listMember in listMembers:
            #listMembersString += listMember + blindingSuffix + ", "
            blindKeygenOutputElement(listMember, varsToBlindList, varNamesForListDecls, keygenFuncName)
        #listMembersString = listMembersString[0:(len(listMembersString)-2)]
        for listMember in listMembersORIGINAL:
            listMembersString += listMember + blindingSuffix + ", "
        listMembersString = listMembersString[0:(len(listMembersString) - 2)]
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := list{" + listMembersString + "}\n")
        if (keygenOutputElem in varNamesForListDecls):
            sys.exit("blindKeygenOutputElement in keygen.py attempted to add duplicate keygenOutputElem to varNamesForListDecls -- 1 of 2.")
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
        return keygenOutputElem

    writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls, currentBlindingFactorName, repeatBlindingFactor)
    return keygenOutputElem

def removeAssignmentOfOrigKeygenSecretKeyName(secretKeyName, keygenFuncName):
    assignLineNos = getLineNosOfAllAssigns(keygenFuncName, secretKeyName)    
    if (len(assignLineNos) == 0):
        sys.exit("removeAssignmentOfOrigKeygenSecretKeyName in keygen.py:  could not locate any assignment statements for the secret key name passed in (" + secretKeyName + ").")

    removeFromLinesOfCode(assignLineNos)

def getBlindingFactorsLine():
    outputLine = ""

    addedAlready = []

    for blindingFactor_NonList in blindingFactors_NonLists:
        outputLine += blindingFactor_NonList + ", "
        addedAlready.append(blindingFactor_NonList)

    for blindingFactor_List in blindingFactors_Lists:
        if (blindingFactor_List not in addedAlready):
            outputLine += blindingFactor_List + ", "

    outputLine = outputLine[0:(len(outputLine) - len(", "))]

    return outputLine

def writeOutputLineForKeygen(secretKeyName, keygenFuncName, config):
    SDLLinesForKeygen = []

    outputLine = ""

    outputLine += "output := list{"

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    for outputEntry in keygenOutput:
        if ( (outputEntry == config.keygenSecVar) or (outputEntry == (config.keygenSecVar + blindingSuffix)) ):
            continue

        outputLine += outputEntry + ", "

    outputLine += getBlindingFactorsLine() + ", "

    outputLine += secretKeyName + blindingSuffix + "}\n"

    SDLLinesForKeygen.append(outputLine)

    lineNoKeygenOutput = getLineNoOfOutputStatement(keygenFuncName)
    removeFromLinesOfCode([lineNoKeygenOutput])
    appendToLinesOfCode(SDLLinesForKeygen, lineNoKeygenOutput)
    updateCodeAndStructs()

def getMasterSecretKeyElements(config):
    global masterSecretKeyElements

    mskFunc = config.setupFuncName
    if (mskFunc not in assignInfo):
        sys.exit("getMasterSecretKeyElements in keygen.py:  setupFuncName from config file isn't in assignInfo.")

    mskFuncAssignInfoEntry = assignInfo[mskFunc]

    for mskElem in config.masterSecVars:
        if (mskElem not in mskFuncAssignInfoEntry):
            sys.exit("getMasterSecretKeyElements in keygen.py:  one of the var names in masterSecVars (from config file) isn't in assignInfo[name_of_setup_function_from_config_file].")

        if (mskElem not in masterSecretKeyElements):
            masterSecretKeyElements.append(mskElem)

        assignInfoVarEntry = mskFuncAssignInfoEntry[mskElem]
        varDeps = assignInfoVarEntry.getVarDeps()
        for varDep in varDeps:
            if (varDep not in masterSecretKeyElements):
                masterSecretKeyElements.append(varDep)

    #print(masterSecretKeyElements)
    #sys.exit("test")

def instantiateBFSolver(config):
    # get random file
    name = ""
    length = 5
    for i in range(length):
        name += random.choice(string.ascii_lowercase + string.digits)
    name += ".py"
    # prepare input configuration file
    skVarsOutputVar = "skVar = '" + str(config.keygenSecVar) + "'\n"
    mskVarsOutputVar = "mskVars = " + str(mskVars) + "\n"
    rndVarsOutputVar = "rndVars = " + str(rndVars) + "\n"
    infoOutputVar = "info = " + str(keygenElemToSMTExp) + "\n"
    
    f = open(name, 'w')
    f.write(skVarsOutputVar)
    f.write(mskVarsOutputVar)
    f.write(rndVarsOutputVar)
    f.write(infoOutputVar)
    f.close()
    
    print("See: ", name)    
    print("<================== BFSolver ==================>")
    os.system("python2.7 BFSolver.py %s" % name)
    print("<================== BFSolver ==================>")

    newName = name.split('.')[0]
    mapVars = importlib.import_module(newName)
    
    bfMap = None
    skBfMap = None
    if hasattr(mapVars, bfMapKeyword):
        bfMap = getattr(mapVars, bfMapKeyword)
    if hasattr(mapVars, skBfMapKeyword):
        skBfMap = getattr(mapVars, skBfMapKeyword)
    #os.system("rm -f " + name + " " + name + "c")
    
    #print(results.resultDictionary)
    #os.system("rm -f " + name + "*")    
    #return results.resultDictionary
    return (bfMap, skBfMap)

def prepareDictForTransform(resultDictionary, config):
    retDict = {}

    for skElem in resultDictionary:
        retDict[skElem] = []
        bfName = resultDictionary[skElem]
        if (isLastCharThisChar(bfName, LIST_INDEX_SYMBOL) == True):
            bfName = bfName[0:(len(bfName) - 1)]
            retDict[skElem].append(bfName)
            retDict[skElem].append(config.listNameIndicator)
        else:
            retDict[skElem].append(bfName)

    return retDict

def removeStringEntriesFromKeygenElemToSMTExp(config):
    global keygenElemToSMTExp

    retList = []
    newKeygenElemToSMTExp = {}

    for keygenElem in keygenElemToSMTExp:
        varType = getVarTypeInfoRecursive(BinaryNode(keygenElem), config.keygenFuncName)
        if (varType in [types.str, types.listStr]):
            retList.append(keygenElem)
        else:
            newKeygenElemToSMTExp[keygenElem] = keygenElemToSMTExp[keygenElem]

    keygenElemToSMTExp = newKeygenElemToSMTExp
    return retList

def removeStringEntriesFromSKinKeygenElemToSMTExp(stringEntriesInKeygenElemToSMTExp, config):
    global keygenElemToSMTExp

    skListInKeygenElemToSMTExp = keygenElemToSMTExp[config.keygenSecVar]
    for stringToRemove in stringEntriesInKeygenElemToSMTExp:
        skListInKeygenElemToSMTExp.remove(stringToRemove)

def keygen(file, config):
    SDLLinesForKeygen = []

    if ( (type(file) is not str) or (len(file) == 0) ):
        sys.exit("First argument passed to keygen.py is invalid.")
    
    parseFile2(file, False)
    updateCodeAndStructs()
    getMasterSecretKeyElements(config)
    keygenFuncName = config.keygenFuncName

    if (keygenBlindingExponent in assignInfo[keygenFuncName]):
        sys.exit("keygen.py:  the variable used for keygenBlindingExponent in config.py already exists in the keygen function of the scheme being analyzed.")

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")

    for keygenOutput_ind in keygenOutput:
        if (keygenOutput_ind not in keygenPubVar):
            getAllKeygenElemsToExponentsDictEntries(keygenOutput_ind, keygenFuncName, config)

    getKeygenElemToSMTExpressions(config)

    stringEntriesInKeygenElemToSMTExp = removeStringEntriesFromKeygenElemToSMTExp(config)
    removeStringEntriesFromSKinKeygenElemToSMTExp(stringEntriesInKeygenElemToSMTExp, config)

    bfMap, skBfMap = instantiateBFSolver(config)

    print("First BFSolver Result:  ", skBfMap)

    skBfMap = {'LVector': 'uf0#', 'YVector': 'uf1#'}

    for stringEntry in stringEntriesInKeygenElemToSMTExp:
        skBfMap[stringEntry] = nilType
    
    print("BFSolver Results: ", skBfMap)
    # produce proof
    # generateTKProof(bfMap, config)

    skBfMap = applyGroupSharingOptimization(skBfMap, config)
    applyBlindingFactorsToScheme(skBfMap, config)
    secretKeyName = config.keygenSecVar
    addAssignmentForSKBlinded(config)
    removeAssignmentOfOrigKeygenSecretKeyName(secretKeyName, config.keygenFuncName)

    SDLLinesForKeygen = []
    for bfName in bfsThatNeedRandomAssignments:
        SDLLinesForKeygen.append(bfName + " := random(ZR)\n")

    for nonListBlindingFactor in blindingFactors_NonLists:
        if (nonListBlindingFactor not in bfsThatNeedRandomAssignments):
            SDLLinesForKeygen.append(nonListBlindingFactor + " := random(ZR)\n")

    inputLineOfKeygenFunc = getLineNoOfInputStatement(config.keygenFuncName)
    appendToLinesOfCode(SDLLinesForKeygen, inputLineOfKeygenFunc + 1)
    updateCodeAndStructs()
    writeOutputLineForKeygen(secretKeyName, config.keygenFuncName, config)

    for index_listVars in range(0, len(varNamesForListDecls)):
        varNamesForListDecls[index_listVars] = varNamesForListDecls[index_listVars] + blindingSuffix + " := list\n"

    for blindingFactor_List in blindingFactors_Lists:
        varNamesForListDecls.append(blindingFactor_List + " := list\n")

    lineNoEndTypesSection = getEndLineNoOfFunc(TYPES_HEADER)
    appendToLinesOfCode(varNamesForListDecls, lineNoEndTypesSection)
    updateCodeAndStructs()

    resultDictionaryForTransform = prepareDictForTransform(skBfMap, config)

    #varsThatAreBlinded = {"c":["zz"], "d0":["yy"], "d1":["aa", "bb"]}
    transformNEW(resultDictionaryForTransform, secretKeyElements, config)

    #rcca(rccaData)

    existingDecOutInputLineNo = getLineNoOfInputStatement(decOutFunctionName)
    existingDecOutInputLineNo -= 1
    existingDecOutInputLine = getLinesOfCode()[existingDecOutInputLineNo]

    replacementBlindingFactorsLine = getBlindingFactorsLine()
    #replacementBlindingFactorsLine = replacementBlindingFactorsLine[0:(len(replacementBlindingFactorsLine) - 1)]
    newDecOutInputLine = existingDecOutInputLine.replace(transformOutputList + "}", transformOutputList + ", " + replacementBlindingFactorsLine + "}", 1)

    substituteOneLineOfCode(newDecOutInputLine, existingDecOutInputLineNo + 1)

    updateCodeAndStructs()

    printLinesOfCode()

    #print(newDecOutInputLine)
    #sys.exit("TESTTEST")

    return (getLinesOfCode(), blindingFactors_NonLists, blindingFactors_Lists)

if __name__ == "__main__":
    keygen(sys.argv[1])
