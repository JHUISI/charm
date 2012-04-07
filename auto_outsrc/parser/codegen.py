from keygen import *
from config import *
import sys

assignInfo = None
varNamesToFuncs_All = None
varNamesToFuncs_Assign = None
setupFile = None
transformFile = None
decOutFile = None
userFuncsFile = None
currentFuncName = NONE_FUNC_NAME
numTabsIn = 1
returnValues = {}
globalVarNames = []
lineNoBeingProcessed = 0
numLambdaFunctions = 0

def writeCurrentNumTabsIn(outputFile):
    outputString = ""

    for numTabs in range(0, numTabsIn):
        outputString += "\t"

    outputFile.write(outputString)

def addImportLines():
    global setupFile, transformFile, decOutFile

    pythonImportLines = ""
    pythonImportLines += "from " + str(userFuncsFileName) + " import *\n"

    pythonImportLines += "\n"

    cppImportLines = ""

    cppImportLines += "\n"

    setupFile.write(pythonImportLines)
    transformFile.write(pythonImportLines)
    #decOutFile.write(cppImportLines)
    decOutFile.write(pythonImportLines)

def addGroupObjGlobalVar():
    global setupFile, transformFile, decOutFile

    if ( (type(groupObjName) is not str) or (len(groupObjName) == 0) ):
        sys.exit("addGroupObjGlobalVar in codegen.py:  groupObjName in config.py is invalid.")

    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(groupObjName)
    if ( (possibleFuncName != None) or (possibleVarInfoObj != None) ):
        sys.exit("addGroupObjGlobalVar in codegen.py:  groupObjName in config.py is also the name of a variable in the cryptoscheme (not allowed).")

    outputString = groupObjName + " = None\n\n"

    setupFile.write(outputString)
    transformFile.write(outputString)
    decOutFile.write(outputString)

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

def writeFunctionEnd_Python(outputFile, functionName):
    global returnValues

    outputString = ""

    outputVariables = None

    try:
        outputVariables = assignInfo[functionName][outputKeyword].getVarDeps()
    except:
        sys.exit("writeFunctionEnd_Python in codegen.py:  could not obtain function's output variables from getVarDeps() on VarInfo obj.")

    outputVariablesString = ""

    if (len(outputVariables) > 0):
        outputVariablesString += "("
        for outputVariable in outputVariables:
            outputVariablesString += outputVariable + ", "
        outputVariablesString = outputVariablesString[0:(len(outputVariablesString) - len(", "))]
        outputVariablesString += ")"

    outputString += "\treturn output"
    #outputString += outputVariablesString
    outputString += "\n\n"

    if (functionName in returnValues):
        sys.exit("writeFunctionEnd_Python in codegen.py:  function name passed in is already in returnValues.")

    returnValues[functionName] = outputVariablesString

    outputFile.write(outputString)

def writeGlobalVarDecls(outputFile, functionName):
    outputString = ""

    for varName in globalVarNames:
        if (varName in assignInfo[functionName]):
            outputString += "\tglobal " + varName + "\n"

    outputString += "\n"

    outputFile.write(outputString)

def writeFunctionDecl_Python(outputFile, functionName):
    outputString = ""

    inputVariables = None

    try:
        inputVariables = assignInfo[functionName][inputKeyword].getVarDeps()
    except:
        sys.exit("writeFunctionDecl_Python in codegen.py:  could not obtain function's input variables from getVarDeps() on VarInfo obj.")

    inputVariablesString = ""

    if (len(inputVariables) > 0):
        for inputVariable in inputVariables:
            inputVariablesString += inputVariable + ", "
        inputVariablesString = inputVariablesString[0:(len(inputVariablesString) - len(", "))]

    outputString += "def "
    outputString += functionName
    outputString += "("
    outputString += inputVariablesString
    outputString += "):\n"

    outputFile.write(outputString)

    writeGlobalVarDecls(outputFile, functionName)

def writeFunctionDecl_CPP(outputFile, functionName):
    pass

def writeFunctionDecl(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionDecl_Python(transformFile, functionName)
    elif (currentFuncName == decOutFunctionName):
        #writeFunctionDecl_CPP(decOutFile, functionName)
         writeFunctionDecl_Python(decOutFile, functionName)
    else:
        writeFunctionDecl_Python(setupFile, functionName)

def writeFunctionEnd_CPP(outputFile, functionName):
    return

def writeFunctionEnd(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionEnd_Python(transformFile, functionName)
    elif (currentFuncName == decOutFunctionName):
        #writeFunctionEnd_CPP(decOutFile, functionName)
        writeFunctionEnd_Python(decOutFile, functionName)
    else:
        writeFunctionEnd_Python(setupFile, functionName)

def isForLoopStart(binNode):
    if (binNode.type == ops.FOR):
        return True

    return False

def isForLoopEnd(binNode):
    if ( (binNode.type == ops.END) and (binNode.left.attr == FOR_LOOP_HEADER) ):
        return True

    return False

def isAssignStmt(binNode):
    if (binNode.type == ops.EQ):
        return True

    return False

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

def getAssignStmtAsString(node, replacementsDict, dotProdObj, lambdaReplacements, forOutput):
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
        return strNameToReturn
    elif (node.type == ops.ADD):
        leftString = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        rightString = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        return "(" + leftString + " + " + rightString + ")"
    elif (node.type == ops.SUB):
        leftString = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        rightString = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        return "(" + leftString + " - " + rightString + ")"
    elif (node.type == ops.MUL):
        leftString = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        rightString = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        return "(" + leftString + " * " + rightString + ")"
    elif (node.type == ops.DIV):
        leftString = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        rightString = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        return "(" + leftString + " / " + rightString + ")"
    elif (node.type == ops.EXP):
        leftString = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        rightString = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        return "(" + leftString + " ** " + rightString + ")"
    elif (node.type == ops.LIST):
        if (forOutput == True):
            listOutputString = "("
        else:
            listOutputString = "["

        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode, replacementsDict, None, None, False)
            listOutputString += listNodeAsString + ", "
        listOutputString = listOutputString[0:(len(listOutputString) - len(", "))]

        if (forOutput == True):
            listOutputString += ")"
        else:
            listOutputString += "]"

        return listOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        randomOutputString = groupObjName + ".random(" + randomGroupType + ")"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        hashGroupType = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        hashOutputString = groupObjName + ".hash(" + hashMessage + ", " + hashGroupType + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString(node.left, replacementsDict, None, None, False)
        pairRightSide = getAssignStmtAsString(node.right, replacementsDict, None, None, False)
        pairOutputString = "pair(" + pairLeftSide + ", " + pairRightSide + ")"
        return pairOutputString
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        funcOutputString = nodeName + "("
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNodeInFunc, replacementsDict, None, None, False)
            funcOutputString += listNodeAsString + ", "
        funcOutputString = funcOutputString[0:(len(funcOutputString) - len(", "))]
        funcOutputString += ")"
        if (nodeName != lenFuncName):
            global userFuncsFile
            userFuncsOutputString = ""
            userFuncsOutputString += "def " + funcOutputString + ":\n" + "\treturn\n\n"
            userFuncsFile.write(userFuncsOutputString)
        return funcOutputString
    elif ( (node.type == ops.ON) and (node.left.type == ops.PROD) ):
        if ( (dotProdObj == None) or (lambdaReplacements == None) ):
            sys.exit("getAssignStmtAsString in codegen.py:  dot prod node detected, but there was a problem with either the dot product object or the lambda replacements dictionary passed in.")
        dotProdOutputString = "dotprod2(range("
        dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getStartVal()))
        dotProdOutputString += ","
        dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getEndVal()))
        dotProdOutputString += "), "
        dotProdOutputString += lamFuncName
        dotProdOutputString += str(numLambdaFunctions)
        dotProdOutputString += ", "
        dotProdOutputString += getLambdaReplacementsString(lambdaReplacements)
        dotProdOutputString = dotProdOutputString[0:(len(dotProdOutputString) - len(", "))]
        dotProdOutputString += ")"
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

def getLambdaReplacementsString(lambdaReplacements):
    if (type(lambdaReplacements) is not dict):
        sys.exit("getLambdaReplacementsString in codegen.py:  lambda replacements argument passed in is not of type dictionary.")

    if (len(lambdaReplacements) == 0):
        return ""

    reverseDict = {}

    for lambdaReplacementKey in lambdaReplacements:
        lambdaReplacementValue = lambdaReplacements[lambdaReplacementKey]
        reverseDict[lettersMapping[lambdaReplacementValue]] = lambdaReplacementKey

    if (len(lambdaReplacements) != len(reverseDict) ):
        sys.exit("getLambdaReplacementsString in codegen.py:  reverseDict is not the same length as lambdaReplacements.")

    retString = ""

    for counter in range(0, len(reverseDict)):
        retString += reverseDict[counter]
        retString += ", "

    return retString

def writeLambdaFuncAssignStmt(outputFile, binNode):
    global numLambdaFunctions

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

    lambdaOutputString = ""
    lambdaOutputString += lamFuncName
    lambdaOutputString += str(numLambdaFunctions)
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
    outputFile.write(lambdaOutputString)
    return (dotProdObj, lambdaReplacements)

def writeAssignStmt_Python(outputFile, binNode):
    #if (binNode.right.type == ops.EXPAND):
        #return

    writeCurrentNumTabsIn(outputFile)

    outputString = ""
    dotProdObj = None
    lambdaReplacements = None

    if ( (binNode.right.type == ops.ON) and (binNode.right.left.type == ops.PROD) ):
        (dotProdObj, lambdaReplacements) = writeLambdaFuncAssignStmt(outputFile, binNode)
        writeCurrentNumTabsIn(outputFile)

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

def writeAssignStmt_CPP(outputFile, binNode):
    return

def writeAssignStmt(binNode):
    if (currentFuncName == transformFunctionName):
        writeAssignStmt_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        #writeAssignStmt_CPP(decOutFile, binNode)
        writeAssignStmt_Python(decOutFile, binNode)
    else:
        writeAssignStmt_Python(setupFile, binNode)

def writeForLoopDecl_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    outputString += "for "
    outputString += getAssignStmtAsString(binNode.left.left, None, None, None, False)
    outputString += " in range("
    outputString += getAssignStmtAsString(binNode.left.right, None, None, None, False)
    outputString += ", "
    outputString += getAssignStmtAsString(binNode.right, None, None, None, False)
    outputString += "):\n"

    outputFile.write(outputString)

def writeForLoopDecl(binNode):
    if (currentFuncName == transformFunctionName):
        writeForLoopDecl_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        #writeForLoopDecl_CPP(decOutFile, binNode)
        writeForLoopDecl_Python(decOutFile, binNode)
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

    varName = str(binNode.left.attr)
    if (varName.find(LIST_INDEX_SYMBOL) != -1):
        sys.exit("addTypeDeclToGlobalVars in codegen.py:  variable name in types section has # sign in it.")

    if ( (varName not in globalVarNames) and (varName != inputKeyword) and (varName != outputKeyword) ):
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
    writeGlobalVars_Python(transformFile)
    #writeGlobalVars_CPP(decOutFile)
    writeGlobalVars_Python(decOutFile)

def writeSDLToFiles(astNodes):
    global currentFuncName, numTabsIn, setupFile, transformFile, lineNoBeingProcessed

    for astNode in astNodes:
        lineNoBeingProcessed += 1

        if (isFunctionStart(astNode) == True):
            currentFuncName = getFuncNameFromBinNode(astNode)
            writeFunctionDecl(currentFuncName)
        elif (isFunctionEnd(astNode) == True):
            writeFunctionEnd(currentFuncName)
            currentFuncName = NONE_FUNC_NAME
        elif (isTypesStart(astNode) == True):
            currentFuncName = TYPES_HEADER
        elif (isTypesEnd(astNode) == True):
            currentFuncName = NONE_FUNC_NAME
            writeGlobalVars()
            setupFile.write("\n")
            transformFile.write("\n")
            decOutFile.write("\n")

        if (currentFuncName == NONE_FUNC_NAME):
            continue

        if (currentFuncName == TYPES_HEADER):
            addTypeDeclToGlobalVars(astNode)
        elif (isForLoopStart(astNode) == True):
            writeForLoopDecl(astNode)
            numTabsIn += 1
        elif (isForLoopEnd(astNode) == True):
            numTabsIn -= 1
        elif (isAssignStmt(astNode) == True):
            writeAssignStmt(astNode)

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

def getStringOfInputArgsToFunc(funcName):
    inputVariables = []

    try:
        inputVariables = assignInfo[funcName][inputKeyword].getVarDeps()
    except:
        sys.exit("getStringOfInputArgsToFunc in codegen.py:  could not obtain the input line for function currently being processed.")

    outputString = ""

    if (len(inputVariables) == 0):
        return outputString

    for inputVar in inputVariables:
        outputString += inputVar + ", "

    lenOutputString = len(outputString)
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
        if (counter == 0):
            outputString += getStringOfFirstFuncArgs(argsToFirstFunc)
        else:
            outputString += getStringOfInputArgsToFunc(funcName)
        outputString += ")\n"
        counter += 1

    return outputString

def writeMainFuncOfSetup():
    global setupFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"

    outputString += writeGroupObjToMain()
    outputString += writeFuncsCalledFromMain(setupFunctionOrder, argsToFirstSetupFunc)

    setupFile.write(outputString)

def writeMainFuncOfTransform():
    global transformFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()
    outputString += writeFuncsCalledFromMain(transformFunctionOrder, argsToFirstTransformFunc)

    transformFile.write(outputString)

def writeMainFuncOfDecOut():
    global decOutFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()
    outputString += writeFuncsCalledFromMain(decOutFunctionOrder, argsToFirstDecOutFunc)

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
        if (len(listForThisVar) == 1):
            continue
        if ( (varName not in globalVarNames) and (varName != inputKeyword) and (varName != outputKeyword) ):
            globalVarNames.append(varName)

def main(SDL_Scheme):
    global setupFile, transformFile, decOutFile, userFuncsFile, assignInfo, varNamesToFuncs_All
    global varNamesToFuncs_Assign

    if ( (type(SDL_Scheme) is not str) or (len(SDL_Scheme) == 0) ):
        sys.exit("codegen.py:  sys.argv[1] argument (file name for SDL scheme) passed in was invalid.")

    keygen(SDL_Scheme)
    astNodes = getAstNodes()
    assignInfo = getAssignInfo()
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

    getGlobalVarNames()

    addImportLines()
    addGroupObjGlobalVar()
    writeSDLToFiles(astNodes)
    writeMainFuncs()

    setupFile.close()
    transformFile.close()
    decOutFile.close()
    userFuncsFile.close()

if __name__ == "__main__":
    main(sys.argv[1])
    parseLinesOfCode(getLinesOfCode(), True)
