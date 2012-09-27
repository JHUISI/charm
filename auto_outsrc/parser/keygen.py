from SDLParser import *
from config import *
from transform import *
from rcca import *
from secretListInKeygen import *
from outsrctechniques import SubstituteVar
import sys

assignInfo = None
varTypes = None
astNodes = None
forLoops = None
publicVarNames = None
secretVarNames = None
varDepList = None
blindingFactors_Lists = []
blindingFactors_NonLists = []
varsThatAreBlinded = []

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
    global assignInfo, varTypes, astNodes, forLoops, publicVarNames, secretVarNames, varDepList

    parseLinesOfCode(getLinesOfCode(), False)
    assignInfo = getAssignInfo()
    varTypes = getVarTypes()
    astNodes = getAstNodes()
    forLoops = getForLoops()
    publicVarNames = getPublicVarNames()
    secretVarNames = getSecretVarNames()
    varDepList = externalGetVarDepList()

    #print(publicVarNames)
    #print(secretVarNames)
    #sys.exit("test")

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
        lastLineNo = possibleNewLastLineNo + 1

    return lastLineNo

def getIsVarList(keygenOutputElem, keygenOutputVarInfo):
    if ( (keygenOutputVarInfo.getIsList() == True) or (keygenOutputVarInfo.getIsSymmap() == True) or (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
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

def writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls):
    global blindingFactors_Lists, varsThatAreBlinded

    currentBlindingFactorName = blindingFactorPrefix + "_" + keygenOutputElem + blindingSuffix

    blindingFactors_Lists.append(currentBlindingFactorName)
    varsThatAreBlinded.append(keygenOutputElem)

    SDLLinesForKeygen = []

    SDLLinesForKeygen.append("BEGIN :: forall\n")
    SDLLinesForKeygen.append("forall{" + blindingLoopVar + " := " + keygenOutputElem + "}\n")

    SDLLinesForKeygen.append(currentBlindingFactorName + LIST_INDEX_SYMBOL + blindingLoopVar + " := random(ZR)\n")


    SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + blindingLoopVar + " ^ (1/" + currentBlindingFactorName + LIST_INDEX_SYMBOL + blindingLoopVar + ")\n")
    SDLLinesForKeygen.append("END :: forall\n")
    varsToBlindList.remove(keygenOutputElem)
    if (keygenOutputElem in varNamesForListDecls):
        sys.exit("writeForAllLoop in keygen.py attempted to add duplicate keygenOutputElem to varNamesForListDecls -- 2 of 2.")
    varNamesForListDecls.append(keygenOutputElem)

    lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
    replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))

def varListContainsParentDict(varList, parentDict):
    for varName in varList:
        varNameWithoutIndices = removeListIndices(varName)
        if (varNameWithoutIndices == parentDict):
            return True

    return False

def getShouldThisElemBeUnblinded(keygenOutputElem, varsModifiedInKeygen):
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

def blindKeygenOutputElement(keygenOutputElem, varsToBlindList, varNamesForListDecls):
    global blindingFactors_NonLists, varsThatAreBlinded

    SDLLinesForKeygen = []

    varsModifiedInKeygen = list(assignInfo[keygenFuncName].keys())
    varsModifiedInKeygen = removeListIndicesAndDupsFromList(varsModifiedInKeygen)

    shouldThisElemBeUnblinded = getShouldThisElemBeUnblinded(keygenOutputElem, varsModifiedInKeygen)

    if (shouldThisElemBeUnblinded == True):
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + "\n")
        if (keygenOutputElem in varsToBlindList):
            varsToBlindList.remove(keygenOutputElem)
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
        return keygenOutputElem

    if (keygenOutputElem not in assignInfo[keygenFuncName]):
        if (varListContainsParentDict(assignInfo[keygenFuncName].keys(), keygenOutputElem) == False):
            sys.exit("keygen output element passed to blindKeygenOutputElement in keygen.py is not in assignInfo[keygenFuncName], and is not a parent dictionary of one of the variables in assignInfo[keygenFuncName].")
        writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls)
        return keygenOutputElem

    keygenOutputVarInfo = assignInfo[keygenFuncName][keygenOutputElem]

    isVarList = getIsVarList(keygenOutputElem, keygenOutputVarInfo)

    currentBlindingFactorName = blindingFactorPrefix + "_" + keygenOutputElem + blindingSuffix

    if (isVarList == False):
        SDLLinesForKeygen.append(currentBlindingFactorName + " := random(ZR)\n")
        blindingFactors_NonLists.append(currentBlindingFactorName)
        varsThatAreBlinded.append(keygenOutputElem)
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + currentBlindingFactorName + ")\n")
        varsToBlindList.remove(keygenOutputElem)
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
        return keygenOutputElem

    if ( (keygenOutputVarInfo.getIsList() == True) and (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        listMembers = keygenOutputVarInfo.getListNodesList()
        listMembersString = ""
        for listMember in listMembers:
            listMembersString += listMember + blindingSuffix + ", "
            blindKeygenOutputElement(listMember, varsToBlindList, varNamesForListDecls)
        listMembersString = listMembersString[0:(len(listMembersString)-2)]
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := list{" + listMembersString + "}\n")
        if (keygenOutputElem in varNamesForListDecls):
            sys.exit("blindKeygenOutputElement in keygen.py attempted to add duplicate keygenOutputElem to varNamesForListDecls -- 1 of 2.")
        lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        replaceVarInstancesInLineNoRange(lineNoAfterThisAddition, getEndLineNoOfFunc(keygenFuncName), keygenOutputElem, (keygenOutputElem + blindingSuffix))
        return keygenOutputElem

    writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls)
    return keygenOutputElem

def getBlindingFactorsLine():
    outputLine = ""

    for blindingFactor_NonList in blindingFactors_NonLists:
        outputLine += blindingFactor_NonList + ", "

    for blindingFactor_List in blindingFactors_Lists:
        outputLine += blindingFactor_List + ", "

    return outputLine

def keygen(file):
    SDLLinesForKeygen = []

    if ( (type(file) is not str) or (len(file) == 0) ):
        sys.exit("First argument passed to keygen.py is invalid.")

    parseFile2(file, False)


    config = __import__('config')


    varsToBlindList = getSecretList(config, False)

    varNamesForListDecls = []

    updateCodeAndStructs()

    if (keygenBlindingExponent in assignInfo[keygenFuncName]):
        sys.exit("keygen.py:  the variable used for keygenBlindingExponent in config.py already exists in the keygen function of the scheme being analyzed.")

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")

    SDLLinesForKeygen.append(keygenBlindingExponent + " := random(ZR)\n")
    lineNoAfterThisAddition = writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, None)

    for keygenOutput_ind in keygenOutput:
        secretKeyName = blindKeygenOutputElement(keygenOutput_ind, varsToBlindList, varNamesForListDecls)

    if (len(varsToBlindList) != 0):
        sys.exit("keygen.py completed without blinding all of the variables passed to it by transform.py.")

    SDLLinesForKeygen = []

    outputLine = ""

    outputLine += "output := list{"
    outputLine += getBlindingFactorsLine()

    outputLine += secretKeyName + blindingSuffix + "}\n"

    SDLLinesForKeygen.append(outputLine)

    lineNoKeygenOutput = getLineNoOfOutputStatement(keygenFuncName)
    removeFromLinesOfCode([lineNoKeygenOutput])
    appendToLinesOfCode(SDLLinesForKeygen, lineNoKeygenOutput)
    updateCodeAndStructs()

    for index_listVars in range(0, len(varNamesForListDecls)):
        varNamesForListDecls[index_listVars] = varNamesForListDecls[index_listVars] + blindingSuffix + " := list\n"

    for blindingFactor_List in blindingFactors_Lists:
        varNamesForListDecls.append(blindingFactor_List + " := list\n")

    lineNoEndTypesSection = getEndLineNoOfFunc(TYPES_HEADER)
    appendToLinesOfCode(varNamesForListDecls, lineNoEndTypesSection)
    updateCodeAndStructs()


    #(varsToBlindList, rccaData) = (transform(False))
    (varsToBlindList, rccaData) = (transform(varsThatAreBlinded))
    rcca(rccaData)

    existingDecOutInputLineNo = getLineNoOfInputStatement(decOutFunctionName)
    existingDecOutInputLineNo -= 1
    existingDecOutInputLine = getLinesOfCode()[existingDecOutInputLineNo]

    replacementBlindingFactorsLine = getBlindingFactorsLine()
    replacementBlindingFactorsLine = replacementBlindingFactorsLine[0:(len(replacementBlindingFactorsLine) - 1)]
    newDecOutInputLine = existingDecOutInputLine.replace(keygenBlindingExponent + ",", replacementBlindingFactorsLine, 1)

    substituteOneLineOfCode(newDecOutInputLine, existingDecOutInputLineNo + 1)

    updateCodeAndStructs()

    return (blindingFactors_NonLists, blindingFactors_Lists)

if __name__ == "__main__":
    keygen(sys.argv[1])
