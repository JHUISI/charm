from SDLParser import *
from config import *
from transform import *
from rcca import *
from outsrctechniques import SubstituteVar
import sys

assignInfo = None
varTypes = None
astNodes = None

def applyReplacementsDict(replacementsDict, currentStrName):
    if (replacementsDict == None):
        return currentStrName

    retString = ""

    currentStrName_Split = currentStrName.split(LIST_INDEX_SYMBOL)
    for indStr in currentStrName_Split:
        if (indStr in replacementsDict):
            retString += replacementsDict[indStr]
        else:
            retString += indStr
        retString += LIST_INDEX_SYMBOL

    retString = retString[0:(len(retString) - len(LIST_INDEX_SYMBOL))]

    return retString

def replacePoundsWithBrackets(nameWithPounds):
    if ( (type(nameWithPounds) is not str) or (len(nameWithPounds) == 0) ):
        sys.exit("replacePoundsWithBrackets in codegen.py:  problem with nameWithPounds parameter passed in.")

    nameSplit = nameWithPounds.split(LIST_INDEX_SYMBOL)
    if (len(nameSplit) == 1):
        return nameWithPounds

    nameToReturn = nameSplit[0]
    lenNameSplit = len(nameSplit)

    for counter in range(0, (lenNameSplit - 1)):
        nameToReturn += "[" + nameSplit[counter + 1] + "]"

    return nameToReturn

def getLambdaReplacementsString(lambdaReplacements, includeFirstLambdaVar):
    if (type(lambdaReplacements) is not dict):
        sys.exit("getLambdaReplacementsString in keygen.py:  lambda replacements argument passed in is not of type dictionary.")

    if (len(lambdaReplacements) == 0):
        return ""

    reverseDict = {}

    for lambdaReplacementKey in lambdaReplacements:
        lambdaReplacementValue = lambdaReplacements[lambdaReplacementKey]
        reverseDict[lettersMapping[lambdaReplacementValue]] = lambdaReplacementKey

    if (len(lambdaReplacements) != len(reverseDict) ):
        sys.exit("getLambdaReplacementsString in keygen.py:  reverseDict is not the same length as lambdaReplacements.")

    retString = ""

    for counter in range(0, len(reverseDict)):
        if ( (counter == 0) and (includeFirstLambdaVar == False) ):
            continue
        retString += reverseDict[counter]
        retString += ", "

    return (retString, reverseDict[0])

def processDotProdAsNonInt(dotProdObj, currentLambdaFuncName, lambdaReplacements, userFuncsFile, userFuncsList):
    startVal = dotProdObj.getStartVal()
    startValSplit = startVal.split(LIST_INDEX_SYMBOL)
    startVal = startValSplit[0]

    userFuncsOutputString = ""
    userFuncsOutputString += "def " + getStringFunctionName + "(" + getStringFunctionName + argSuffix + "):\n\t"
    userFuncsOutputString += userGlobalsFuncName + "()\n\t"
    userFuncsOutputString += "return " + getStringFunctionName + argSuffix + ".getAttribute()\n\n"
    userFuncsOutputString += "def "
    userFuncsOutputString += currentLambdaFuncName
    userFuncsOutputString += "("
    (lambdaReplacementOutputString, lambdaLoopVar) = getLambdaReplacementsString(lambdaReplacements, False)
    userFuncsOutputString += lambdaLoopVar + ", " + startVal + ", "
    userFuncsOutputString += lambdaReplacementOutputString
    userFuncsOutputString = userFuncsOutputString[0:(len(userFuncsOutputString) - len(", "))]
    userFuncsOutputString += "):\n\t"
    userFuncsOutputString += userGlobalsFuncName + "()\n\t"
    userFuncsOutputString += lambdaLoopVar + " = " + getStringFunctionName + "("
    userFuncsOutputString += startVal + "[" + lambdaLoopVar + "])\n\t"
    userFuncsOutputString += "return " + getAssignStmtAsString(dotProdObj.getBinaryNode().right, None, None, None, False, userFuncsFile, userFuncsList, currentLambdaFuncName)
    userFuncsOutputString += "\n\n"

    if (userFuncsFile != None):
        userFuncsFile.write(userFuncsOutputString)

    dotProdOutputString = ""
    dotProdOutputString += "dotprod2(range(0, "
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getEndVal()))
    dotProdOutputString += "), "
    dotProdOutputString += currentLambdaFuncName + ", " + startVal + ", "
    (lambdaReplacementOutputString, lambdaLoopVar) = getLambdaReplacementsString(lambdaReplacements, False)
    dotProdOutputString += lambdaReplacementOutputString
    dotProdOutputString = dotProdOutputString[0:(len(dotProdOutputString) - len(", "))]
    dotProdOutputString += ")"

    return dotProdOutputString

def processDotProdAsInt(dotProdObj, currentLambdaFuncName, lambdaReplacements):
    dotProdOutputString = "dotprod2(range("
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getStartVal()))
    dotProdOutputString += ","
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getEndVal()))
    dotProdOutputString += "), "
    dotProdOutputString += currentLambdaFuncName
    dotProdOutputString += ", "
    (lambdaReplacementOutputString, lambdaLoopVar) = getLambdaReplacementsString(lambdaReplacements, True)
    dotProdOutputString += lambdaReplacementOutputString
    dotProdOutputString = dotProdOutputString[0:(len(dotProdOutputString) - len(", "))]
    dotProdOutputString += ")"

    return dotProdOutputString

def getAssignStmtAsString(node, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName):
    if (type(node) is str):
        strNameToReturn = applyReplacementsDict(replacementsDict, node)
        strNameToReturn = replacePoundsWithBrackets(strNameToReturn)
        return strNameToReturn
    elif ( (node.type == ops.ATTR) or (node.type == ops.TYPE) ):
        if (node.type == ops.ATTR):
            strNameToReturn = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        elif (node.type == ops.TYPE):
            strNameToReturn = applyReplacementsDict(replacementsDict, str(node.attr))
        strNameToReturn = replacePoundsWithBrackets(strNameToReturn)
        if (node.negated == True):
            strNameToReturn = "-" + strNameToReturn
        return strNameToReturn
    elif (node.type == ops.ADD):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        return "(" + leftString + " + " + rightString + ")"
    elif (node.type == ops.SUB):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        return "(" + leftString + " - " + rightString + ")"
    elif (node.type == ops.MUL):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        return "(" + leftString + " * " + rightString + ")"
    elif (node.type == ops.DIV):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        return "(" + leftString + " / " + rightString + ")"
    elif (node.type == ops.EXP):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        return "(" + leftString + " ** " + rightString + ")"
    elif (node.type == ops.LIST):
        if (forOutput == True):
            listOutputString = "("
        else:
            listOutputString = "["

        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
            listOutputString += listNodeAsString + ", "
        listOutputString = listOutputString[0:(len(listOutputString) - len(", "))]

        if (forOutput == True):
            listOutputString += ")"
        else:
            listOutputString += "]"

        return listOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        randomOutputString = groupObjName + ".random(" + randomGroupType + ")"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        hashGroupType = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        hashOutputString = groupObjName + ".hash(" + hashMessage + ", " + hashGroupType + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        pairRightSide = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
        pairOutputString = "pair(" + pairLeftSide + ", " + pairRightSide + ")"
        return pairOutputString
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        funcOutputString = nodeName + "("
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNodeInFunc, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)
            funcOutputString += listNodeAsString + ", "
        funcOutputString = funcOutputString[0:(len(funcOutputString) - len(", "))]
        funcOutputString += ")"
        if ( (nodeName not in pythonDefinedFuncs) and (nodeName not in userFuncsList) and (userFuncsList != None) and (userFuncsFile != None) ):
            userFuncsList.append(nodeName)
            funcOutputForUser = funcOutputString
            funcOutputForUser = funcOutputForUser.replace("[", "")
            funcOutputForUser = funcOutputForUser.replace("]", "")
            userFuncsOutputString = ""
            userFuncsOutputString += "def " + funcOutputForUser + ":\n"
            userFuncsOutputString += "\t" + userGlobalsFuncName + "()\n"
            userFuncsOutputString += "\treturn\n\n"
            userFuncsFile.write(userFuncsOutputString)
        return funcOutputString
    elif ( (node.type == ops.ON) and (node.left.type == ops.PROD) ):
        if ( (dotProdObj == None) or (lambdaReplacements == None) ):
            sys.exit("getAssignStmtAsString in codegen.py:  dot prod node detected, but there was a problem with either the dot product object or the lambda replacements dictionary passed in.")
        startValIsInt = None
        try:
            dummyIntVar = int(dotProdObj.getStartVal())
            startValIsInt = True
        except:
            startValIsInt = False
        if (startValIsInt == True):
            dotProdOutputString = processDotProdAsInt(dotProdObj, currentLambdaFuncName, lambdaReplacements)
        else:
            dotProdOutputString = processDotProdAsNonInt(dotProdObj, currentLambdaFuncName, lambdaReplacements, userFuncsFile, userFuncsList)
        return dotProdOutputString
    elif (node.type == ops.EXPAND):
        expandOutputString = ""
        for listNode in node.listNodes:
            expandOutputString += replacePoundsWithBrackets(str(listNode))
            expandOutputString += ", "
        expandOutputString = expandOutputString[0:(len(expandOutputString) - len(", "))]
        expandOutputString += " = "
        return expandOutputString

    sys.exit("getAssignStmtAsString in keygen.py:  unsupported node type detected.")

def replaceVarInstancesInLineNoRange(startLineNo, endLineNo, origVarName, newVarName):
    for lineNoIndex in range(startLineNo, (endLineNo + 1)):
        indexIntoCodeStructs = lineNoIndex - 1
        currentBinNode = astNodes[indexIntoCodeStructs]
        ASTVisitor(SubstituteVar(origVarName,newVarName)).preorder(currentBinNode)
        binNodeAsString = currentBinNode.__str__
        #substituteOneLineOfCode(binNodeAsString, lineNoIndex)

getAssignStmtAsString(node, replacementsDict, dotProdObj, lambdaReplacements, forOutput, userFuncsFile, userFuncsList, currentLambdaFuncName)

    updateCodeAndStructs()

def updateCodeAndStructs():
    global assignInfo, varTypes, astNodes

    parseLinesOfCode(getLinesOfCode(), False)
    assignInfo = getAssignInfo()
    varTypes = getVarTypes()
    astNodes = getAstNodes()

def writeLinesToFuncAfterVarLastAssign(funcName, lineList, varName):
    if (varName == None):
        lineNo = 0
    else:
        lineNo = getLineNoOfLastAssign(funcName, varName) + 1

    if (lineNo == 0):
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
    SDLLinesForKeygen = []

    SDLLinesForKeygen.append("BEGIN :: forall\n")
    SDLLinesForKeygen.append("forall{" + blindingLoopVar + " := " + keygenOutputElem + "}\n")
    SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + blindingLoopVar + " ^ (1/" + keygenBlindingExponent + ")\n")
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

def blindKeygenOutputElement(keygenOutputElem, varsToBlindList, varNamesForListDecls):
    SDLLinesForKeygen = []

    varsModifiedInKeygen = list(assignInfo[keygenFuncName].keys())
    varsModifiedInKeygen = removeListIndicesAndDupsFromList(varsModifiedInKeygen)

    if (keygenOutputElem not in varsModifiedInKeygen):
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + "\n")
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

    if (isVarList == False):
        SDLLinesForKeygen.append(keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + keygenBlindingExponent + ")\n")
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

def keygen(file):
    SDLLinesForKeygen = []

    if ( (type(file) is not str) or (len(file) == 0) ):
        sys.exit("First argument passed to keygen.py is invalid.")

    parseFile2(file, False)
    (varsToBlindList, rccaData) = (transform(False))
    rcca(rccaData)
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
    SDLLinesForKeygen.append("output := list{" + keygenBlindingExponent + ", " + secretKeyName + blindingSuffix + "}\n")

    lineNoKeygenOutput = getLineNoOfOutputStatement(keygenFuncName)
    removeFromLinesOfCode([lineNoKeygenOutput])
    appendToLinesOfCode(SDLLinesForKeygen, lineNoKeygenOutput)
    updateCodeAndStructs()

    for index_listVars in range(0, len(varNamesForListDecls)):
        varNamesForListDecls[index_listVars] = varNamesForListDecls[index_listVars] + blindingSuffix + " := list\n"

    lineNoEndTypesSection = getEndLineNoOfFunc(TYPES_HEADER)
    appendToLinesOfCode(varNamesForListDecls, lineNoEndTypesSection)
    updateCodeAndStructs()

if __name__ == "__main__":
    keygen(sys.argv[1])
