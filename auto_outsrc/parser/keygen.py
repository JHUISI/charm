from SDLParser import *
from config import *
from transform import *
from rcca import *
import sys

#SDLLinesForKeygen = []

assignInfo = None
varTypes = None

def writeLinesToFuncAfterVarLastAssign(funcName, lineList, varName):
    global assignInfo, varTypes

    if (varName == None):
        lineNo = 0
    else:
        lineNo = getLineNoOfLastAssign(funcName, varName) + 1

    if (lineNo == 0):
        lineNo = getLineNoOfInputStatement(funcName) + 1

    appendToLinesOfCode(lineList, lineNo)
    parseLinesOfCode(getLinesOfCode(), False)
    assignInfo = getAssignInfo()
    varTypes = getVarTypes()

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

    return lastLineNo

def getIsVarList(keygenOutputElem, keygenOutputVarInfo):
    if ( (keygenOutputVarInfo.getIsList() == True) or (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        return True

    try:
        currentVarType = varTypes[TYPES_HEADER][keygenOutputElem].getType()
    except:
        return False

    if ( (currentVarType == types.list) or (currentVarType == ops.LIST) ):
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
    #global SDLLinesForKeygen

    SDLLinesForKeygen = []

    SDLLinesForKeygen.append("BEGIN :: forall\n")
    SDLLinesForKeygen.append("forall{" + blindingLoopVar + " := " + keygenOutputElem + "}\n")
    SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + blindingLoopVar + " ^ (1/" + keygenBlindingExponent + ")\n")
    SDLLinesForKeygen.append("END :: forall\n")
    varsToBlindList.remove(keygenOutputElem)
    if (keygenOutputElem in varNamesForListDecls):
        sys.exit("writeForAllLoop in keygen.py attempted to add duplicate keygenOutputElem to varNamesForListDecls -- 2 of 2.")
    varNamesForListDecls.append(keygenOutputElem)

    writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)

def varListContainsParentDict(varList, parentDict):
    for varName in varList:
        varNameWithoutIndices = removeListIndices(varName)
        if (varNameWithoutIndices == parentDict):
            return True

    return False

def blindKeygenOutputElement(keygenOutputElem, varsToBlindList, varNamesForListDecls):
    #global SDLLinesForKeygen

    SDLLinesForKeygen = []

    varsModifiedInKeygen = list(assignInfo[keygenFuncName].keys())
    varsModifiedInKeygen = removeListIndicesAndDupsFromList(varsModifiedInKeygen)

    if (keygenOutputElem not in varsModifiedInKeygen):
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + "\n")
        varsToBlindList.remove(keygenOutputElem)
        writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        return keygenOutputElem

    if (keygenOutputElem not in assignInfo[keygenFuncName]):
        if (varListContainsParentDict(assignInfo[keygenFuncName].keys(), keygenOutputElem) == False):
            sys.exit("keygen output element passed to blindKeygenOutputElement in keygen.py is not in assignInfo[keygenFuncName], and is not a parent dictionary of one of the variables in assignInfo[keygenFuncName].")
        writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls)
        return keygenOutputElem

    keygenOutputVarInfo = assignInfo[keygenFuncName][keygenOutputElem]

    isVarList = getIsVarList(keygenOutputElem, keygenOutputVarInfo)

    if (isVarList == False):
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + keygenBlindingExponent + ")\n")
        varsToBlindList.remove(keygenOutputElem)
        writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
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
        writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, keygenOutputElem)
        return keygenOutputElem

    writeForAllLoop(keygenOutputElem, varsToBlindList, varNamesForListDecls)
    return keygenOutputElem

def keygen(file):
    #global SDLLinesForKeygen

    global assignInfo, varTypes

    SDLLinesForKeygen = []

    if ( (type(file) is not str) or (len(file) == 0) ):
        sys.exit("First argument passed to keygen.py is invalid.")

    parseFile2(file, False)
    (varsToBlindList, rccaData) = (transform(False))
    rcca(rccaData)
    varNamesForListDecls = []

    assignInfo = getAssignInfo()
    varTypes = getVarTypes()

    if (keygenBlindingExponent in assignInfo[keygenFuncName]):
        sys.exit("keygen.py:  the variable used for keygenBlindingExponent in config.py already exists in the keygen function of the scheme being analyzed.")

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")

    SDLLinesForKeygen.append(keygenBlindingExponent + " := random(ZR)\n")
    writeLinesToFuncAfterVarLastAssign(keygenFuncName, SDLLinesForKeygen, None)

    for keygenOutput_ind in keygenOutput:
        secretKeyName = blindKeygenOutputElement(keygenOutput_ind, varsToBlindList, varNamesForListDecls)

    if (len(varsToBlindList) != 0):
        sys.exit("keygen.py completed without blinding all of the variables passed to it by transform.py.")

    SDLLinesForKeygen = []
    SDLLinesForKeygen.append("output := list{" + keygenBlindingExponent + ", " + secretKeyName + blindingSuffix + "}\n")

    lineNoKeygenOutput = getLineNoOfOutputStatement(keygenFuncName)
    removeFromLinesOfCode([lineNoKeygenOutput])
    appendToLinesOfCode(SDLLinesForKeygen, lineNoKeygenOutput)
    parseLinesOfCode(getLinesOfCode(), False)
    assignInfo = getAssignInfo()
    varTypes = getVarTypes()

    for index_listVars in range(0, len(varNamesForListDecls)):
        varNamesForListDecls[index_listVars] = varNamesForListDecls[index_listVars] + blindingSuffix + " := list\n"

    lineNoEndTypesSection = getEndLineNoOfFunc(TYPES_HEADER)
    appendToLinesOfCode(varNamesForListDecls, lineNoEndTypesSection)
    parseLinesOfCode(getLinesOfCode(), False)
    assignInfo = getAssignInfo()
    varTypes = getVarTypes()

if __name__ == "__main__":
    keygen(sys.argv[1])
    #printLinesOfCode()
