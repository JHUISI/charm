from keygen import *
from config import *
import sys, os

assignInfo = None
inputOutputVars = None
varNamesToFuncs_All = None
varNamesToFuncs_Assign = None
setupFile = None
transformFile = None
decOutFile = None
userFuncsFile = None
userFuncsCPPFile = None
currentFuncName = NONE_FUNC_NAME
numTabsIn = 1
returnValues = {}
globalVarNames = []
lineNoBeingProcessed = 0
numLambdaFunctions = 0
userFuncsList_CPP = []
userFuncsList = []
currentLambdaFuncName = None

def writeCurrentNumTabsToString():
    outputString = ""

    for numTabs in range(0, numTabsIn):
        outputString += "\t"

    return outputString

def writeCurrentNumTabsIn(outputFile):
    outputString = ""

    for numTabs in range(0, numTabsIn):
        outputString += "\t"

    outputFile.write(outputString)

def addImportLines():
    global setupFile, transformFile, decOutFile, userFuncsFile, userFuncsCPPFile

    userFuncsLibName = userFuncsFileName
    if (userFuncsLibName.endswith(pySuffix) == True):
        userFuncsLibName = userFuncsLibName[0:(len(userFuncsLibName) - len(pySuffix))]

    pythonImportLines = ""
    pythonImportLines += "from " + str(userFuncsLibName) + " import *\n\n"

    setupFile.write(pythonImportLines)
    transformFile.write(pythonImportLines)
    #decOutFile.write(cppImportLines)
    #decOutFile.write(pythonImportLines)

    pythonImportLines = ""
    for charmImportFunc in charmImportFuncs:
        pythonImportLines += charmImportFunc + "\n"

    pythonImportLines += "\n"

    cppImportLines = ""
    cppImportLines += "#include \"sdlconfig.h\"\n"
    cppImportLines += "#include <iostream>\n"
    cppImportLines += "#include <sstream>\n"
    cppImportLines += "#include <string>\n"
    cppImportLines += "using namespace std;\n"
    cppImportLines += "#define DEBUG  true\n"
    cppImportLines += "\n"

    #setupFile.write(pythonImportLines)
    #transformFile.write(pythonImportLines)
    #decOutFile.write(cppImportLines)
    #decOutFile.write(pythonImportLines)
    decOutFile.write("#include \"" + userFuncsCPPFileName + "\"\n\n")
    userFuncsFile.write("from builtInFuncs import *\n\n")
    userFuncsCPPFile.write(cppImportLines)

def addGroupObjGlobalVar():
    global setupFile, transformFile, decOutFile, userFuncsFile, userFuncsCPPFile

    if ( (type(groupObjName) is not str) or (len(groupObjName) == 0) ):
        sys.exit("addGroupObjGlobalVar in codegen.py:  groupObjName in config.py is invalid.")

    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(groupObjName)
    if ( (possibleFuncName != None) or (possibleVarInfoObj != None) ):
        sys.exit("addGroupObjGlobalVar in codegen.py:  groupObjName in config.py is also the name of a variable in the cryptoscheme (not allowed).")

    outputString = groupObjName + " = None\n\n"

    #setupFile.write(outputString)
    #transformFile.write(outputString)
    #decOutFile.write(outputString)

    outputString = ""
    outputString += groupObjName + "UserFuncs = None\n\n"
    userFuncsFile.write(outputString)

    outputString = ""
    outputString += groupObjName + "UserFuncs = NULL\n\n"
    userFuncsCPPFile.write(outputString)

def isFunctionStart(binNode):
    if (binNode.type != ops.BEGIN):
        return False

    try:
        if (binNode.left.attr.startswith(DECL_FUNC_HEADER) == True):
            return True
    except:
        return False

def isFunctionEnd(binNode):
    if (binNode.type != ops.END):
        return False

    try:
        if (binNode.left.attr.startswith(DECL_FUNC_HEADER) == True):
            return True
    except:
        return False

def getFuncNameFromBinNode(binNode):
    funcNameWhole = binNode.left.attr

    return funcNameWhole[len(DECL_FUNC_HEADER):len(funcNameWhole)]

def getOutputVariablesList(funcName):
    outputVariables = None

    try:
        outputVariables = assignInfo[funcName][outputKeyword].getVarDeps()
    except:
        sys.exit("getOutputVariablesList in codegen.py:  could not obtain function's output variables from getVarDeps() on VarInfo obj.")

    return outputVariables

def writeFunctionEnd_Python(outputFile, functionName, retainGlobals):
    global returnValues

    outputVariables = getOutputVariablesList(functionName)

    outputString = ""

    outputVariablesString = ""
    numOutputVariables = 0

    if (len(outputVariables) > 0):
        outputVariablesString += "("
        for outputVariable in outputVariables:
            if ( (retainGlobals == True) or (outputVariable not in globalVarNames) ):
                outputVariablesString += outputVariable + ", "
                numOutputVariables += 1
        outputVariablesString = outputVariablesString[0:(len(outputVariablesString) - len(", "))]
        outputVariablesString += ")"

    if (functionName in returnValues):
        sys.exit("writeFunctionEnd_Python in codegen.py:  function name passed in is already in returnValues.")

    if (numOutputVariables > 0):
        returnValues[functionName] = outputVariablesString
        outputString += "\treturn output\n"
    else:
        returnValues[functionName] = ""

    outputString += "\n"
    outputFile.write(outputString)

def writeGlobalVarDecls(outputFile, functionName):
    outputString = ""

    for varName in globalVarNames:
        if (varName not in varNamesToFuncs_Assign):
            sys.exit("writeGlobalVarDecls in codegen.py:  current global variable name is not in varNamesToFuncs_Assign.")

        funcsInWhichThisVarHasAssignment = varNamesToFuncs_Assign[varName]
        if (functionName in funcsInWhichThisVarHasAssignment):
            outputString += "\tglobal " + varName + "\n"

    outputString += "\n"

    outputFile.write(outputString)

def getInputVariablesList(functionName):
    inputVariables = None

    try:
        inputVariables = assignInfo[functionName][inputKeyword].getVarDeps()
    except:
        sys.exit("getInputVariablesList in codegen.py:  could not obtain function's input variables from getVarDeps() on VarInfo obj.")

    return inputVariables

def writeFunctionDecl_Python(outputFile, functionName, toWriteGlobalVarDecls, retainGlobals):
    outputString = ""

    inputVariables = getInputVariablesList(functionName)

    inputVariablesString = ""

    if (len(inputVariables) > 0):
        for inputVariable in inputVariables:
            if ( (retainGlobals == True) or (inputVariable not in globalVarNames) ):
                inputVariablesString += inputVariable + ", "
        inputVariablesString = inputVariablesString[0:(len(inputVariablesString) - len(", "))]

    outputString += "def "
    outputString += functionName
    outputString += "("
    outputString += inputVariablesString
    outputString += "):\n"

    outputFile.write(outputString)

    if (toWriteGlobalVarDecls == True):
        writeGlobalVarDecls(outputFile, functionName)

def makeTypeReplacementsForCPP(SDL_Type):
    SDLTypeAsString = str(SDL_Type)

    if (SDLTypeAsString == "str"):
        return "string"
    if (SDLTypeAsString == "list"):
        return charmListType
    if (SDLTypeAsString == "symmap"):
        return charmDictType

    return SDLTypeAsString

def getFinalVarType(varName, funcName):
    return getVarTypeFromVarName(varName, funcName)

def writeFunctionDecl_CPP(outputFile, functionName):
    outputString = ""

    inputVariables = getInputVariablesList(functionName)
    outputVariables = getOutputVariablesList(functionName)

    if (len(outputVariables) != 1):
        sys.exit("writeFunctionDecl_CPP in codegen.py:  length of output variables for function name passed in is unequal to one (unsupported).")

    funcOutputType = getFinalVarType(outputVariables[0], currentFuncName)

    outputString += makeTypeReplacementsForCPP(funcOutputType) + " " + functionName + "("
    outputString += PairingGroupClassName_CPP + " & " + groupObjName + ", "

    for inputVariable in inputVariables:
        currentType = getFinalVarType(inputVariable, currentFuncName)
        outputString += makeTypeReplacementsForCPP(currentType) + " & " + inputVariable + ", "

    outputString = outputString[0:(len(outputString) - len(", "))]
    outputString += ")\n{\n"

    outputFile.write(outputString)

def writeFunctionDecl(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionDecl_Python(transformFile, functionName, False, True)
    elif (currentFuncName == decOutFunctionName):
        writeFunctionDecl_CPP(decOutFile, functionName)
        #writeFunctionDecl_Python(decOutFile, functionName, False, True)
    else:
        writeFunctionDecl_Python(setupFile, functionName, True, False)

def writeFunctionEnd_CPP(outputFile, functionName):
    global returnValues

    outputVariables = getOutputVariablesList(functionName)

    if (len(outputVariables) > 1):
        sys.exit("writeFunctionEnd_CPP in codegen.py:  number of output variables obtained from getOutputVariables List is greater than one (unsupported).")

    if (len(outputVariables) == 0):
        return

    returnValues[functionName] = str(outputVariables[0])
    #outputFile.write("\treturn " + str(outputVariables[0]) + ";\n}\n\n")
    outputFile.write("\treturn " + outputKeyword + ";\n}\n\n")

def writeFunctionEnd(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionEnd_Python(transformFile, functionName, True)
    elif (currentFuncName == decOutFunctionName):
        writeFunctionEnd_CPP(decOutFile, functionName)
        #writeFunctionEnd_Python(decOutFile, functionName, True)
    else:
        writeFunctionEnd_Python(setupFile, functionName, False)

def isErrorFunc(binNode):
    if (binNode.type == ops.ERROR):
        return True

    return False

def isIfStmtStart(binNode):
    if (binNode.type == ops.IF):
        return True

    return False

def isElseStmtStart(binNode):
    if (binNode.type == ops.ELSE):
        return True

    return False

def isForLoopStart(binNode):
    if ( (binNode.type == ops.FOR) or (binNode.type == ops.FORALL) ):
        return True

    return False

def isIfStmtEnd(binNode):
    if ( (binNode.type == ops.END) and (binNode.left.attr == IF_BRANCH_HEADER) ):
        return True

    return False

def isForLoopEnd(binNode):
    if (binNode.type == ops.END):
        if ( (binNode.left.attr == FOR_LOOP_HEADER) or (binNode.left.attr == FORALL_LOOP_HEADER) ):
            return True

    return False

def isAssignStmt(binNode):
    if (binNode.type == ops.EQ):
        return True

    return False

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

def processDotProdAsNonInt(dotProdObj, currentLambdaFuncName, lambdaReplacements):
    global userFuncsFile

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
    userFuncsOutputString += "return " + getAssignStmtAsString(dotProdObj.getBinaryNode().right, None, None, None, False)
    userFuncsOutputString += "\n\n"
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

def processStrAssignStmt(node, replacementsDict):
    strNameToReturn = applyReplacementsDict(replacementsDict, node)
    strNameToReturn = replacePoundsWithBrackets(strNameToReturn)
    return strNameToReturn

def processAttrOrTypeAssignStmt(node, replacementsDict):
    if (node.type == ops.ATTR):
        strNameToReturn = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
    elif (node.type == ops.TYPE):
        strNameToReturn = applyReplacementsDict(replacementsDict, str(node.attr))
    strNameToReturn = replacePoundsWithBrackets(strNameToReturn)
    if (node.negated == True):
        strNameToReturn = "-" + strNameToReturn
    return strNameToReturn

def getAssignStmtAsString_CPP(node, replacementsDict, variableName):
    global userFuncsCPPFile, userFuncsList_CPP

    variableType = types.NO_TYPE

    if (variableName != None):
        variableType = getFinalVarType(variableName, currentFuncName)

    if (type(node) is str):
        return processStrAssignStmt(node, replacementsDict)
    elif ( (node.type == ops.ATTR) or (node.type == ops.TYPE) ):
        return processAttrOrTypeAssignStmt(node, replacementsDict)
    elif (node.type == ops.ADD):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return groupObjName + ".add(" + leftSide + ", " + rightSide + ")"
    elif (node.type == ops.SUB):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return groupObjName + ".sub(" + leftSide + ", " + rightSide + ")"
    elif (node.type == ops.MUL):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return groupObjName + ".mul(" + leftSide + ", " + rightSide + ")"
    elif (node.type == ops.DIV):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return groupObjName + ".div(" + leftSide + ", " + rightSide + ")"
    elif (node.type == ops.EXP):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return groupObjName + ".exp(" + leftSide + ", " + rightSide + ")"
    elif (node.type == ops.AND):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return "( (" + leftSide + ") && (" + rightSide + ") )"
    elif (node.type == ops.EQ_TST):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        return "( (" + leftSide + ") == (" + rightSide + ") )"
    elif ( (node.type == ops.LIST) ): #or ( (node.type == ops.EXPAND) and (variableType == types.list) ) ):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  encountered node of type ops.LIST, but variableName parameter passed in is of type None.")
        listOutputString = ""
        listOutputString += ";\n"
        for listNode in node.listNodes:
            listOutputString += writeCurrentNumTabsToString()
            listOutputString += variableName + ".append("
            listNodeAsString = getAssignStmtAsString_CPP(listNode, replacementsDict, variableName)
            listOutputString += listNodeAsString + ");\n"
        return listOutputString
    elif ( (node.type == ops.SYMMAP) ): #or ( (node.type == ops.EXPAND) and (variableType == types.symmap) ) ):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  encountered node of type ops.SYMMAP, but variable name parameter passed in is of None type.")
        symmapOutputString = ""
        symmapOutputString += ";\n"
        for symmapNode in node.listNodes:
            symmapOutputString += writeCurrentNumTabsToString()
            symmapOutputString += variableName + ".set(\""
            symmapNodeAsString = getAssignStmtAsString_CPP(symmapNode, replacementsDict, variableName)
            symmapOutputString += "\":" + variableName + ");\n"
        return symmapOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        randomOutputString = groupObjName + ".random(" + randomGroupType + ")"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        hashGroupType = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        hashOutputString = groupObjName + ".hashListTo" + (str(hashGroupType)).upper() + "(" + hashMessage + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName)
        pairRightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName)
        pairOutputString = groupObjName + ".pair(" + pairLeftSide + ", " + pairRightSide + ")"
        return pairOutputString
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        funcOutputString = nodeName + "("
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getAssignStmtAsString_CPP(listNodeInFunc, replacementsDict, variableName)
            funcOutputString += listNodeAsString + ", "
        funcOutputString = funcOutputString[0:(len(funcOutputString) - len(", "))]
        funcOutputString += ")"
        if ( (nodeName not in userFuncsList_CPP) and (nodeName not in builtInTypes) ):
            userFuncsList_CPP.append(nodeName)
            funcOutputForUser = funcOutputString
            funcOutputForUser = funcOutputForUser.replace("[", "")
            funcOutputForUser = funcOutputForUser.replace("]", "")
            userFuncsOutputString = ""
            userFuncsOutputString += "void " + funcOutputForUser + "\n{\n"
            userFuncsOutputString += "\t" + userGlobalsFuncName + "();\n"
            userFuncsOutputString += "\treturn;\n}\n\n"
            userFuncsCPPFile.write(userFuncsOutputString)
        return funcOutputString
    elif (node.type == ops.EXPAND):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  ops.EXPAND node encountered, but variableName is set to None.")
        return getCPPAsstStringForExpand(node, variableName, replacementsDict)

    sys.exit("getAssignStmtAsString_CPP in codegen.py:  unsupported node type detected.")

def getCPPAsstStringForExpand(node, variableName, replacementsDict):
    outputString = ""
    outputString += "\n"

    for listNode in node.listNodes:
        listNodeName = applyReplacementsDict(replacementsDict, listNode)
        listNodeName = replacePoundsWithBrackets(listNodeName)
        listNodeType = getFinalVarType(listNodeName, currentFuncName)
        if (listNodeType == types.NO_TYPE):
            sys.exit("getCPPAsstStringForExpand in codegen.py:  could not obtain one of the types for the variable names included in the expand node.")
        outputString += writeCurrentNumTabsToString()
        outputString += makeTypeReplacementsForCPP(listNodeType) + " " + listNodeName + " = "
        outputString += variableName + "[\"" + listNodeName + "\"]."
        if (listNodeType == types.G1):
            outputString += "getG1()"
        elif (listNodeType == types.G2):
            outputString += "getG2()"
        elif (listNodeType == types.GT):
            outputString += "getGT()"
        elif (listNodeType == types.ZR):
            outputString += "getZR()"
        elif (listNodeType == types.str):
            outputString += "strPtr"
        else:
            sys.exit("getCPPAsstStringForExpand in codegen.py:  one of the types of the listNodes is not one of the supported types (G1, G2, GT, ZR, or string).")

        outputString += ";\n"

    return outputString

def getAssignStmtAsString(node, replacementsDict, dotProdObj, lambdaReplacements, forOutput):
    global userFuncsFile, userFuncsList

    if (type(node) is str):
        return processStrAssignStmt(node, replacementsDict)
    elif ( (node.type == ops.ATTR) or (node.type == ops.TYPE) ):
        return processAttrOrTypeAssignStmt(node, replacementsDict)
    elif (node.type == ops.ADD):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "(" + leftString + " + " + rightString + ")"
    elif (node.type == ops.SUB):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "(" + leftString + " - " + rightString + ")"
    elif (node.type == ops.MUL):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "(" + leftString + " * " + rightString + ")"
    elif (node.type == ops.DIV):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "(" + leftString + " / " + rightString + ")"
    elif (node.type == ops.EXP):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "(" + leftString + " ** " + rightString + ")"
    elif (node.type == ops.AND):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "( (" + leftString + ") and (" + rightString + ") )"
    elif (node.type == ops.EQ_TST):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "( (" + leftString + ") == (" + rightString + ") )"
    #elif (node.type == ops.OR):
        #leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #return "(" + leftString + " or " + rightString + ")"
    elif (node.type == ops.LIST):
        if (forOutput == True):
            listOutputString = "("
        else:
            listOutputString = "["
        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
            listOutputString += listNodeAsString + ", "
        listOutputString = listOutputString[0:(len(listOutputString) - len(", "))]
        if (forOutput == True):
            listOutputString += ")"
        else:
            listOutputString += "]"
        return listOutputString
    elif (node.type == ops.SYMMAP):
        symmapOutputString = ""
        symmapOutputString += "{"
        for symmapNode in node.listNodes:
            symmapNodeAsString = getAssignStmtAsString(symmapNode, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
            symmapOutputString += "\"" + symmapNodeAsString + "\":" + symmapNodeAsString + ", "
        symmapOutputString = symmapOutputString[0:(len(symmapOutputString) - len(", "))]
        symmapOutputString += "}"
        return symmapOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        randomOutputString = groupObjName + ".random(" + randomGroupType + ")"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        hashGroupType = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        hashOutputString = groupObjName + ".hash(" + hashMessage + ", " + hashGroupType + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        pairRightSide = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        pairOutputString = "pair(" + pairLeftSide + ", " + pairRightSide + ")"
        return pairOutputString
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        funcOutputString = nodeName + "("
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNodeInFunc, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
            funcOutputString += listNodeAsString + ", "
        funcOutputString = funcOutputString[0:(len(funcOutputString) - len(", "))]
        funcOutputString += ")"
        if ( (nodeName not in pythonDefinedFuncs) and (nodeName not in userFuncsList) and (nodeName not in builtInTypes) ):
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
            dotProdOutputString = processDotProdAsNonInt(dotProdObj, currentLambdaFuncName, lambdaReplacements)
        return dotProdOutputString
    elif (node.type == ops.EXPAND):
        expandOutputString = ""
        for listNode in node.listNodes:
            expandOutputString += replacePoundsWithBrackets(str(listNode))
            expandOutputString += ", "
        expandOutputString = expandOutputString[0:(len(expandOutputString) - len(", "))]
        expandOutputString += " = "
        return expandOutputString

    sys.exit("getAssignStmtAsString in codegen.py:  unsupported node type detected.")

def writeLambdaFuncAssignStmt(outputFile, binNode):
    global numLambdaFunctions, currentLambdaFuncName

    numLambdaFunctions += 1

    if ( (binNode.right.type != ops.ON) or (binNode.right.left.type != ops.PROD) ):
        sys.exit("writeLambdaFuncAssignStmt in codegen.py:  binary node passed in is not of the dot product type.")

    varName = getFullVarName(binNode.left, True)

    (funcName, varInfoObj) = getVarNameEntryFromAssignInfo(varName)
    if ( (funcName == None) or (varInfoObj == None) or (varInfoObj.getDotProdObj() == None) ):
        sys.exit("writeLambdaFuncAssignStmt in codegen.py:  problem with values returned from getVarNameEntryFromAssignInfo.")

    dotProdObj = varInfoObj.getDotProdObj()
    distinctVarsList = dotProdObj.getDistinctIndVarsInCalcList()
    numDistinctVars = len(distinctVarsList)

    currentLambdaFuncName = lamFuncName + str(numLambdaFunctions)

    lambdaOutputString = ""
    lambdaOutputString += currentLambdaFuncName
    lambdaOutputString += " = lambda "

    lambdaReplacements = {}

    for counter in range(0, numDistinctVars):
        lambdaOutputString += lambdaLetters[counter] + ","
        lambdaReplacements[distinctVarsList[counter]] = lambdaLetters[counter]

    lambdaOutputString = lambdaOutputString[0:(len(lambdaOutputString) - 1)]
    lambdaOutputString += ": "

    lambdaExpression = getAssignStmtAsString(dotProdObj.getBinaryNode().right, lambdaReplacements, None, None, False)
    lambdaOutputString += lambdaExpression

    lambdaOutputString += "\n"
    #outputFile.write(lambdaOutputString)
    return (dotProdObj, lambdaReplacements)

def writeAssignStmt_CPP(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    variableName = getFullVarName(binNode.left, False)
    if ( (variableName.find(LIST_INDEX_SYMBOL) == -1) and (binNode.right.type != ops.EXPAND) ):
        variableType = getFinalVarType(variableName, currentFuncName)
        outputString += makeTypeReplacementsForCPP(variableType) + " "

    variableName = replacePoundsWithBrackets(variableName)
    
    if (binNode.right.type != ops.EXPAND):
        outputString += variableName

    if ( (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
        outputString += " = "

    outputString += getAssignStmtAsString_CPP(binNode.right, None, variableName)
    if ( (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
        outputString += ";\n"
    outputFile.write(outputString)

def writeAssignStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""
    dotProdObj = None
    lambdaReplacements = None

    if ( (binNode.right.type == ops.ON) and (binNode.right.left.type == ops.PROD) ):
        (dotProdObj, lambdaReplacements) = writeLambdaFuncAssignStmt(outputFile, binNode)
        #writeCurrentNumTabsIn(outputFile)

    variableName = replacePoundsWithBrackets(getFullVarName(binNode.left, False))

    if (binNode.right.type != ops.EXPAND):
        outputString += variableName
        outputString += " = "

    if (variableName == outputKeyword):
        outputString += getAssignStmtAsString(binNode.right, None, dotProdObj, lambdaReplacements, True)
    else:
        outputString += getAssignStmtAsString(binNode.right, None, dotProdObj, lambdaReplacements, False)

    if (binNode.right.type == ops.EXPAND):
        outputString += variableName
    
    outputString += "\n"
    outputFile.write(outputString)

def writeAssignStmt(binNode):
    if (currentFuncName == transformFunctionName):
        writeAssignStmt_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeAssignStmt_CPP(decOutFile, binNode)
        #writeAssignStmt_Python(decOutFile, binNode)
    else:
        writeAssignStmt_Python(setupFile, binNode)

def writeErrorFunc_Python(outputFile, binNode):
    global userFuncsFile, userFuncsList

    writeCurrentNumTabsIn(outputFile)
    outputString = ""
    outputString += errorFuncName + "("
    outputString += getAssignStmtAsString(binNode.attr, None, None, None, False)
    outputString += ")\n"
    outputFile.write(outputString)

    writeCurrentNumTabsIn(outputFile)
    outputString = "return\n"
    outputFile.write(outputString)

    if (errorFuncName not in userFuncsList):
        userFuncsList.append(errorFuncName)
        userFuncsOutputString = ""
        userFuncsOutputString += "def " + errorFuncName + "(" + errorFuncArgString + "):\n"
        userFuncsOutputString += "\t" + userGlobalsFuncName + "()\n"
        userFuncsOutputString += "\treturn\n\n"
        userFuncsFile.write(userFuncsOutputString)

def writeErrorFunc_CPP(outputFile, binNode):
    global userFuncsCPPFile, userFuncsList_CPP

    writeCurrentNumTabsIn(outputFile)
    outputString = ""
    outputString += errorFuncName + "("
    outputString += getAssignStmtAsString_CPP(binNode.attr, None, None)
    outputString += ");\n"
    outputFile.write(outputString)

    writeCurrentNumTabsIn(outputFile)
    outputString = "return NULL;\n"
    outputFile.write(outputString)

    if (errorFuncName not in userFuncsList_CPP):
        userFuncsList_CPP.append(errorFuncName)
        userFuncsOutputString = ""
        userFuncsOutputString += "void " + errorFuncName + "(" + errorFuncArgString + ")\n"
        userFuncsOutputString += "{\n"
        userFuncsOutputString += "\t" + userGlobalsFuncName + "();\n"
        userFuncsOutputString += "\treturn;\n"
        userFuncsOutputString += "}\n\n"
        userFuncsCPPFile.write(userFuncsOutputString)

def writeElseStmt_CPP(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)
    outputString = ""
    outputString += "}\n"
    outputString += writeCurrentNumTabsToString()

    if (binNode.left == None):
        outputString += "else\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
    else:
        outputString += "else if ( \n"
        outputString += getAssignStmtAsString_CPP(binNode.left, None, None)
        outputString += " )\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"

    outputFile.write(outputString)

def writeElseStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)
    outputString = ""

    if (binNode.left == None):
        outputString += "else:\n"
    else:
        outputString += "elif ( "
        outputString += getAssignStmtAsString(binNode.left, None, None, None, False)
        outputString += " ):\n"

    outputFile.write(outputString)

def writeIfStmt_CPP(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)
    outputString = ""

    outputString += "if ( "
    outputString += getAssignStmtAsString_CPP(binNode.left, None, None)
    outputString += " )\n"
    outputString += writeCurrentNumTabsToString()
    outputString += "{\n"

    outputFile.write(outputString)

def writeIfStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)
    outputString = ""

    outputString += "if ( "
    outputString += getAssignStmtAsString(binNode.left, None, None, None, False)
    outputString += " ):\n"

    outputFile.write(outputString)

def writeForLoopDecl_CPP(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    if (binNode.type == ops.FOR):
        outputString += "for (int "
        currentLoopIncVarName = getAssignStmtAsString_CPP(binNode.left.left, None, None)
        outputString += currentLoopIncVarName + " = "
        outputString += getAssignStmtAsString_CPP(binNode.left.right, None, None)
        outputString += "; " + currentLoopIncVarName + " < "
        outputString += getAssignStmtAsString_CPP(binNode.right, None, None)
        outputString += "; " + currentLoopIncVarName + "++)\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
    elif (binNode.type == ops.FORALL):
        currentLoopVariableName = getAssignStmtAsString_CPP(binNode.left.right, None, None)
        outputString += charmListType + " " + currentLoopVariableName + KeysListSuffix_CPP + " = " + currentLoopVariableName + ".keys();\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "int " + currentLoopVariableName + ListLengthSuffix_CPP + " = " + currentLoopVariableName + ".length();\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "for (int "
        currentLoopIncVarName = getAssignStmtAsString_CPP(binNode.left.left, None, None)
        outputString += currentLoopIncVarName + TempLoopVar_CPP + "; " + currentLoopIncVarName + TempLoopVar_CPP + " < " + currentLoopVariableName + ListLengthSuffix_CPP + "; " + currentLoopIncVarName + TempLoopVar_CPP + "++)\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
        outputString += writeCurrentNumTabsToString() + "\t"
        outputString += currentLoopIncVarName + " = " + currentLoopVariableName + KeysListSuffix_CPP + "[" + currentLoopIncVarName + TempLoopVar_CPP + "];\n"
    else:
        sys.exit("writeForLoopDecl_CPP in codegen.py:  encounted node that is neither type ops.FOR nor ops.FORALL (unsupported).")

    outputFile.write(outputString)

def writeForLoopDecl_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    if (binNode.type == ops.FOR):
        outputString += "for "
        outputString += getAssignStmtAsString(binNode.left.left, None, None, None, False)
        outputString += " in range("
        outputString += getAssignStmtAsString(binNode.left.right, None, None, None, False)
        outputString += ", "
        outputString += getAssignStmtAsString(binNode.right, None, None, None, False)
        outputString += "):\n"
    elif (binNode.type == ops.FORALL):
        outputString += "for "
        outputString += getAssignStmtAsString(binNode.left.left, None, None, None, False)
        outputString += " in "
        outputString += getAssignStmtAsString(binNode.left.right, None, None, None, False)
        outputString += ":\n"
    else:
        sys.exit("writeForLoopDecl_Python in codegen.py:  encountered node that is neither type ops.FOR nor ops.FORALL.")

    outputFile.write(outputString)

def writeErrorFunc(binNode):
    if (currentFuncName == transformFunctionName):
        writeErrorFunc_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeErrorFunc_CPP(decOutFile, binNode)
        #writeErrorFunc_Python(decOutFile, binNode)
    else:
        writeErrorFunc_Python(setupFile, binNode)

def writeElseStmtDecl(binNode):
    if (currentFuncName == transformFunctionName):
        writeElseStmt_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeElseStmt_CPP(decOutFile, binNode)
        #writeElseStmt_Python(decOutFile, binNode)
    else:
        writeElseStmt_Python(setupFile, binNode)

def writeIfStmtDecl(binNode):
    if (currentFuncName == transformFunctionName):
        writeIfStmt_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeIfStmt_CPP(decOutFile, binNode)
        #writeIfStmt_Python(decOutFile, binNode)
    else:
        writeIfStmt_Python(setupFile, binNode)

def writeForLoopEnd_CPP(outputFile, binNode):
    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    outputFile.write(outputString)

def writeForLoopEnd(binNode):
    if (currentFuncName == decOutFunctionName):
        writeForLoopEnd_CPP(decOutFile, binNode)

def writeIfStmtEnd(binNode):
    if (currentFuncName == decOutFunctionName):
        writeIfStmtEnd_CPP(decOutFile, binNode)

def writeIfStmtEnd_CPP(outputFile, binNode):
    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    outputFile.write(outputString)

def writeForLoopDecl(binNode):
    if (currentFuncName == transformFunctionName):
        writeForLoopDecl_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeForLoopDecl_CPP(decOutFile, binNode)
        #writeForLoopDecl_Python(decOutFile, binNode)
    else:
        writeForLoopDecl_Python(setupFile, binNode)

def isTypesStart(binNode):
    if ( (binNode.type == ops.BEGIN) and (binNode.left.attr == TYPES_HEADER) ):
        return True

    return False

def isTypesEnd(binNode):
    if ( (binNode.type == ops.END) and (binNode.left.attr == TYPES_HEADER) ):
        return True

    return False

def addTypeDeclToGlobalVars(binNode):
    global globalVarNames

    if (binNode.right == None):
        return

    if (str(binNode.right.attr) != LIST_TYPE):
        return

    #varName = str(binNode.left.attr)

    varName = getFullVarName(binNode.left, False)

    if (varName.find(LIST_INDEX_SYMBOL) != -1):
        sys.exit("addTypeDeclToGlobalVars in codegen.py:  variable name in types section has # sign in it.")

    varName = getVarNameWithoutIndices(binNode.left)

    if (varName not in varNamesToFuncs_Assign):
        return

    if ( (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
        globalVarNames.append(varName)

def writeGlobalVars_Python(outputFile):
    outputString = ""

    for varName in globalVarNames:
        outputString += varName
        outputString += " = {}\n"

    outputFile.write(outputString)

def writeGlobalVars_CPP(outputFile):
    return

def writeGlobalVars():
    writeGlobalVars_Python(setupFile)
    #writeGlobalVars_Python(transformFile)
    #writeGlobalVars_CPP(decOutFile)
    #writeGlobalVars_Python(decOutFile)

def isUnnecessaryNodeForCodegen(astNode):
    if (astNode.type == ops.NONE):
        return True

    if ( (astNode.type == ops.BEGIN) and (astNode.left.attr == FOR_LOOP_HEADER) ):
        return True

    if ( (astNode.type == ops.BEGIN) and (astNode.left.attr == FORALL_LOOP_HEADER) ):
        return True

    if ( (astNode.type == ops.BEGIN) and (astNode.left.attr == IF_BRANCH_HEADER) ):
        return True

    return False

def writeSDLToFiles(astNodes):
    global currentFuncName, numTabsIn, setupFile, transformFile, lineNoBeingProcessed

    for astNode in astNodes:
        lineNoBeingProcessed += 1
        processedAsFunctionStart = False

        if (isFunctionStart(astNode) == True):
            currentFuncName = getFuncNameFromBinNode(astNode)
            writeFunctionDecl(currentFuncName)
            processedAsFunctionStart = True
        elif (isFunctionEnd(astNode) == True):
            writeFunctionEnd(currentFuncName)
            currentFuncName = NONE_FUNC_NAME
        elif (isTypesStart(astNode) == True):
            currentFuncName = TYPES_HEADER
        elif (isTypesEnd(astNode) == True):
            currentFuncName = NONE_FUNC_NAME
            writeGlobalVars()
            setupFile.write("\n")

        if (currentFuncName == NONE_FUNC_NAME):
            continue

        if (currentFuncName == TYPES_HEADER):
            addTypeDeclToGlobalVars(astNode)
            #pass
        elif (isForLoopStart(astNode) == True):
            writeForLoopDecl(astNode)
            numTabsIn += 1
        elif (isForLoopEnd(astNode) == True):
            numTabsIn -= 1
            writeForLoopEnd(astNode)
        elif (isAssignStmt(astNode) == True):
            writeAssignStmt(astNode)
        elif (isIfStmtStart(astNode) == True):
            writeIfStmtDecl(astNode)
            numTabsIn += 1
        elif (isElseStmtStart(astNode) == True):
            numTabsIn -= 1
            writeElseStmtDecl(astNode)
            numTabsIn += 1
        elif (isIfStmtEnd(astNode) == True):
            numTabsIn -= 1
            writeIfStmtEnd(astNode)
        elif (isErrorFunc(astNode) == True):
            writeErrorFunc(astNode)
        elif ( (processedAsFunctionStart == True) or (isUnnecessaryNodeForCodegen(astNode) == True) ):
            continue
        else:
            sys.exit("writeSDLToFiles in codegen.py:  unrecognized type of statement in SDL.")

def getStringOfFirstFuncArgs(argsToFirstFunc):
    if (type(argsToFirstFunc) is not list):
        sys.exit("getStringOfFirstFuncArgs in codegen.py:  argsToFirstFunc is not of type list.")

    if (len(argsToFirstFunc) == 0):
        return ""

    outputString = ""

    for argName in argsToFirstFunc:
        try:
            argNameAsStr = str(argName)
        except:
            sys.exit("getStringOfFirstFuncArgs in codegen.py:  could not convert one of the argument names to a string.")

        outputString += str(argName) + ", "

    lenOutputString = len(outputString)
    outputString = outputString[0:(lenOutputString - len(", "))]

    return outputString

def checkNumUserSuppliedArgs(userSuppliedArgs, funcName):
    try:
        inputVariables = assignInfo[funcName][inputKeyword].getVarDeps()
    except:
        sys.exit("checkNumUserSuppliedArgs in codegen.py:  could not obtain the input line for function currently being processed.")

    if (len(userSuppliedArgs) != len(inputVariables)):
        sys.exit("checkNumUserSuppliedArgs in codegen.py:  error in number of user-supplied args for function currently being processed.")

def getStringOfInputArgsToFunc(funcName, retainGlobals):
    inputVariables = []

    try:
        inputVariables = assignInfo[funcName][inputKeyword].getVarDeps()
    except:
        sys.exit("getStringOfInputArgsToFunc in codegen.py:  could not obtain the input line for function currently being processed.")

    outputString = ""

    if (len(inputVariables) == 0):
        return outputString

    for inputVar in inputVariables:
        if ( (retainGlobals == True) or (inputVar not in globalVarNames) ):
            outputString += inputVar + ", "

    lenOutputString = len(outputString)
    if (lenOutputString > 0):
        outputString = outputString[0:(lenOutputString - len(", "))]

    return outputString

def writeGroupObjToMain():
    if ( (type(groupArg) is not str) or (len(groupArg) == 0) ):
        sys.exit("writeMainFuncOfSetup in codegen.py:  groupArg from config.py is invalid.")

    outputString = ""
    outputString += "\tglobal " + groupObjName + "\n"
    outputString += "\t" + groupObjName + " = PairingGroup(" + groupArg + ")\n\n"

    return outputString

def writeFuncsCalledFromMain(functionOrder, argsToFirstFunc):
    outputString = ""

    if ( (type(functionOrder) is not list) or (len(functionOrder) == 0) ):
        sys.exit("writeFuncsCalledFromMain in codegen.py:  functionOrder parameter passed in is invalid.")

    counter = 0
    for funcName in functionOrder:
        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("writeFuncsCalledFromMain in codegen.py:  one of the entries in functionOrder is invalid.")
        outputString += "\t"
        if (funcName not in returnValues):
            sys.exit("writeFuncsCalledFromMain in codegen.py:  current function name in functionOrder is not in return values.")
        if (len(returnValues[funcName]) > 0):
            outputString += returnValues[funcName] + " = "
        outputString += funcName + "("
        #if (counter == 0):
        if (counter == -1):
            checkNumUserSuppliedArgs(argsToFirstFunc, funcName)
            outputString += getStringOfFirstFuncArgs(argsToFirstFunc)
        else:
            if ( (funcName == transformFunctionName) or (funcName == decOutFunctionName) ):
                outputString += getStringOfInputArgsToFunc(funcName, True)
            else:
                outputString += getStringOfInputArgsToFunc(funcName, False)                
        outputString += ")\n"
        counter += 1

    return (outputString, funcName)

def writeMainFuncOfSetup():
    global setupFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"

    outputString += writeGroupObjToMain()

    for lineForSetupMain in linesForSetupMain:
        outputString += "\t" + lineForSetupMain + "\n"

    outputString += "\n"

    #outputString += "\tgetUserFuncsGlobals()\n\n"
    (outputFromFuncsCalledFromMain, lastFuncNameWrittenToMain) = writeFuncsCalledFromMain(setupFunctionOrder, argsToFirstSetupFunc)
    outputString += outputFromFuncsCalledFromMain + "\n"

    varsToPickle = getOutputVariablesList(lastFuncNameWrittenToMain)

    transformInputVariables = getInputVariablesList(transformFunctionName)

    for transformInputVar in transformInputVariables:
        if transformInputVar not in varsToPickle:
            varsToPickle.append(transformInputVar)

    for lastFuncOutputVar in varsToPickle:
        currentVariableName = lastFuncOutputVar + "_" + schemeName
        outputString += "\tf_" + currentVariableName + " = open('" + currentVariableName + charmPickleExt + "', 'wb')\n"
        outputString += "\tpick_" + currentVariableName + " = " + objectToBytesFuncName + "(" + lastFuncOutputVar + ", " + groupObjName + ")\n"
        outputString += "\tf_" + currentVariableName + ".write(pick_" + currentVariableName + ")\n"
        outputString += "\tf_" + currentVariableName + ".close()\n\n"

    outputString += "\t" + serializeKeysName + " = {'" + keygenSecVar + "':" + keygenBlindingExponent + ", '" + keygenPubVar[0] + "':" + serializePubKey + "}\n"
    outputString += "\t" + serializeFuncName + "('" + serializeKeysName + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + serializeKeysName + "))\n\n"

    #outputString += "\n"

    setupFile.write(outputString)

def writeMainFuncOfTransform():
    global transformFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()

    varsToUnpickle = getInputVariablesList(transformFunctionName)
    for varToUnpickle in varsToUnpickle:
        fileNameForThisVar = varToUnpickle + "_" + schemeName + charmPickleExt
        outputString += "\t" + varToUnpickle + unpickleFileSuffix + " = open('" + fileNameForThisVar + "', 'rb').read()\n"
        outputString += "\t" + varToUnpickle + " = " + bytesToObjectFuncName + "(" + varToUnpickle + unpickleFileSuffix + ", " + groupObjName + ")\n\n"
        #outputString += "\t" + varToUnpickle + unpickleFileSuffix + ".close()\n\n"

    #outputString += "\n"

    (outputFromFuncsCalledFromMain, lastFuncNameWrittenToMain) = writeFuncsCalledFromMain(transformFunctionOrder, argsToFirstTransformFunc)
    outputString += outputFromFuncsCalledFromMain
    outputString += "\n"

    varsToPickle = getOutputVariablesList(transformFunctionName)
    for varToPickle in varsToPickle:
        outputString += "\t" + serializeFuncName + "('" + varToPickle + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + varToPickle + "))\n"

    transformFile.write(outputString)

def writeMainFuncOfDecOut():
    global decOutFile

    outputString = ""
    outputString += CPP_Main_Line + "\n"
    outputString += "{\n"
    outputString += "\t" + PairingGroupClassName_CPP + " " + groupObjName + "(" + SecurityParameter_CPP + ");\n\n"

    outputString += "\t" + charmDictType + " dict;\n"

    secretKeyType = getFinalVarType(keygenBlindingExponent, keygenFuncName)

    outputString += "\t" + str(secretKeyType) + " " + keygenBlindingExponent + ";\n"
    outputString += "\t" + serializePubKeyType + " " + serializePubKey_DecOut + ";\n\n"
    outputString += "\t" + "Element T0, T1, T2;\n"
    outputString += "\t" + "dict.set(\"T0\", T0);\n"
    outputString += "\t" + "dict.set(\"T1\", T1);\n"
    outputString += "\t" + "dict.set(\"T2\", T2);\n\n"
    outputString += "\t" + parseParCT_FuncName_DecOut + "('"

    transformOutputVar = getOutputVariablesList(transformFunctionName)
    if (len(transformOutputVar) != 1):
        sys.exit("writeMainFuncOfDecOut in codegen.py:  getOutputVariablesList(transformFunctionName) returned list of length != 1.")
 
    outputString += transformOutputVar[0] + "_" + schemeName + "_" + serializeExt + "', dict);\n"
    outputString += "\t" + parseKeys_FuncName_DecOut + "('"
    outputString += serializeKeysName + "_" + schemeName + "_" + serializeExt + "', "
    outputString += keygenBlindingExponent + ", " + serializePubKey_DecOut + ");\n"
    #outputString += 

    #STILL LEFT TO DO DDDDDDD TODO HERE STARTHERE
    #string M = decout(group, dict, sk, pk);
    #return 0;
    #}

    decOutFile.write(outputString)

def writeMainFuncOfDecOut_Python():
    global decOutFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()
    (outputFromFuncsCalledFromMain, lastFuncNameWrittenToMain) = writeFuncsCalledFromMain(decOutFunctionOrder, argsToFirstDecOutFunc)
    outputString += outputFromFuncsCalledFromMain

    decOutFile.write(outputString)

def writeMainFuncs():
    writeMainFuncOfSetup()
    writeMainFuncOfTransform()
    writeMainFuncOfDecOut()

def getGlobalVarNames():
    global globalVarNames

    for varName in varNamesToFuncs_All:
        listForThisVar = varNamesToFuncs_All[varName]
        if (len(listForThisVar) == 0):
            sys.exit("getGlobalVarNames in codegen.py:  list extracted from varNamesToFuncs_All for current variable is empty.")
        if (transformFunctionName in listForThisVar):
            listForThisVar.remove(transformFunctionName)
        if (decOutFunctionName in listForThisVar):
            listForThisVar.remove(decOutFunctionName)
        if (len(listForThisVar) <= 1):
            continue
        if ( (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
            globalVarNames.append(varName)

def addGetGlobalsToUserFuncs():
    global userFuncsFile, userFuncsCPPFile

    outputString = ""

    outputString += "def " + userGlobalsFuncName + "():\n"
    outputString += "\tglobal " + groupObjName + "UserFuncs\n\n"
    outputString += "\tif (" + groupObjName + "UserFuncs == None):\n"
    outputString += "\t\t" + groupObjName + "UserFuncs = PairingGroup(" + groupArg + ")\n"

    userFuncsFile.write(outputString)

    outputString = ""
    outputString += "void " + userGlobalsFuncName + "()\n"
    outputString += "{\n"
    outputString += "\tif (" + groupObjName + "UserFuncs == NULL)\n"
    outputString += "\t{\n"
    outputString += "\t\t" + PairingGroupClassName_CPP + " " + groupObjName + "UserFuncs(" + SecurityParameter_CPP + ");\n"
    outputString += "\t}\n"
    outputString += "}\n"

    userFuncsCPPFile.write(outputString)

def main(SDL_Scheme):
    global setupFile, transformFile, decOutFile, userFuncsFile, assignInfo, varNamesToFuncs_All
    global varNamesToFuncs_Assign, inputOutputVars, userFuncsCPPFile

    if ( (type(SDL_Scheme) is not str) or (len(SDL_Scheme) == 0) ):
        sys.exit("codegen.py:  sys.argv[1] argument (file name for SDL scheme) passed in was invalid.")

    keygen(SDL_Scheme)
    astNodes = getAstNodes()
    assignInfo = getAssignInfo()
    inputOutputVars = getInputOutputVars()
    varNamesToFuncs_All = getVarNamesToFuncs_All()
    varNamesToFuncs_Assign = getVarNamesToFuncs_Assign()

    if ( (type(setupFileName) is not str) or (len(setupFileName) <= len(pySuffix) ) or (setupFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with setupFileName in config.py.")

    if ( (type(transformFileName) is not str) or (len(transformFileName) <= len(pySuffix) ) or (transformFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with transformFileName in config.py.")

    if ( (type(decOutFileName) is not str) or (len(decOutFileName) <= len(cppSuffix) ) or (decOutFileName.endswith(cppSuffix) == False) ):
        sys.exit("codegen.py:  problem with decOutFileName in config.py.")

    setupFile = open(setupFileName, 'w')
    transformFile = open(transformFileName, 'w')
    decOutFile = open(decOutFileName, 'w')
    userFuncsFile = open(userFuncsFileName, 'w')
    userFuncsCPPFile = open(userFuncsCPPFileName, 'w')

    getGlobalVarNames()

    addImportLines()
    addGroupObjGlobalVar()
    writeSDLToFiles(astNodes)
    writeMainFuncs()
    addGetGlobalsToUserFuncs()

    setupFile.close()
    transformFile.close()
    decOutFile.close()
    userFuncsFile.close()
    userFuncsCPPFile.close()

if __name__ == "__main__":
    main(sys.argv[1])
    parseLinesOfCode(getLinesOfCode(), True)
    #os.system("cp userFuncsPermanent.py userFuncs.py")
    writeLinesOfCodeToFile(outputSDLFileName)
    #print("io vars:  ", getInputOutputVars())
