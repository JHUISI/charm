#from keygen import *
import sys, os

sys.path.extend(['../', '../sdlparser']) 

from SDLParser import *
from config import *

ignoreCloudSourcing = None
nonCloudSourcingFileName = None

assignInfo = None
inputOutputVars = None
functionNameOrder = None
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
CPP_varTypesLines = None
CPP_funcBodyLines = None

blindingFactors_NonLists = None
blindingFactors_Lists = None

initDictDefsAlreadyMade = None

def writeCurrentNumTabsToString():
    outputString = ""

    for numTabs in range(0, numTabsIn):
        #outputString += "\t"
        outputString += "    "

    return outputString

def writeCurrentNumTabsIn(outputFile):
    outputString = ""

    for numTabs in range(0, numTabsIn):
        #outputString += "\t"
        outputString += "    "

    outputFile.write(outputString)

def addImportLines():
    global setupFile, transformFile, decOutFile, userFuncsFile, userFuncsCPPFile

    userFuncsLibName = userFuncsFileName
    if (userFuncsLibName.endswith(pySuffix) == True):
        userFuncsLibName = userFuncsLibName[0:(len(userFuncsLibName) - len(pySuffix))]

    pythonImportLines = ""
    if (ignoreCloudSourcing == False):
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

    if (ignoreCloudSourcing == True):
        setupFile.write("from charm.toolbox.pairinggroup import *\n")
        setupFile.write("from charm.core.engine.util import *\n")
        setupFile.write("from charm.core.math.integer import randomBits\n\n")


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

    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(assignInfo, groupObjName)
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
    #userFuncsCPPFile.write(outputString)

    if (ignoreCloudSourcing == True):
        setupFile.write("group = None\n\n")

def addNumSignatures():
    global setupFile

    try:
        numSignatures = assignInfo[NONE_FUNC_NAME][numSignaturesVarName].getAssignNode().right
    except:
        sys.exit("addNumSignatures in codegen.py:  could not obtain the number of signatures from the input .bv file.")

    outputString = numSignaturesVarName + " = " + str(numSignatures) + "\n\n"
    setupFile.write(outputString)

def addNumSigners():
    global setupFile

    try:
        numSigners = assignInfo[NONE_FUNC_NAME][numSignersVarName].getAssignNode().right
    except:
        return #this value isn't necessary for all schemes

    outputString = numSignersVarName + " = " + str(numSigners) + "\n\n"
    setupFile.write(outputString)

def addSecParamValue():
    global setupFile

    try:
        theSecParamValue = assignInfo[NONE_FUNC_NAME][secParamVarName].getAssignNode().right
    except:
        sys.exit("addSecParamValue in codegen.py:  couldn't obtain secparam value.  Make sure it's in the SDL file, but not in an explicitly defined function (it needs to be outside the functions.")

    outputString = secParamVarName + " = " + str(theSecParamValue) + "\n\n"
    setupFile.write(outputString)

def addSmallExpFunc():
    global setupFile

    outputString = "def SmallExp(bits=80):\n"
    outputString += "    return group.init(ZR, randomBits(bits))\n\n"

    setupFile.write(outputString)

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
        #outputString += "\treturn output\n"
        outputString += "    return output\n"
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
            #outputString += "\tglobal " + varName + "\n"
            outputString += "    global " + varName + "\n"

    outputString += "\n"

    outputFile.write(outputString)

def getInputVariablesList(functionName):
    inputVariables = None

    try:
        inputVariables = assignInfo[functionName][inputKeyword].getVarDeps()
    except:
        print(functionName)
        sys.exit("getInputVariablesList in codegen.py:  could not obtain function's input variables from getVarDeps() on VarInfo obj.")

    return inputVariables

def writeInitDictDefs(outputFile, functionName):
    global initDictDefsAlreadyMade

    if (functionName not in assignInfo):
        sys.exit("writeInitDictDefs in codegen.py:  function name parameter passed in is not in assignInfo.")

    outputString = ""

    for currentVarName in assignInfo[functionName]:
        if (assignInfo[functionName][currentVarName].getHasListIndexSymInLeftAssign() == False):
            continue

        if (currentVarName.find(LIST_INDEX_END_SYMBOL) != -1):
            continue

        #if (currentVarName not in inputOutputVars):
            #continue

        if (currentVarName.count(LIST_INDEX_SYMBOL) == 1):
            currentVarNameSplit = currentVarName.split(LIST_INDEX_SYMBOL)
            if (currentVarNameSplit[1].isdigit()):
                currentVarName = currentVarNameSplit[0]

        if (currentVarName not in varNamesToFuncs_Assign):
            sys.exit("writeInitDictDefs in codegen.py:  current variable name in loop is not in varNamesToFuncs_Assign.")

        if (functionName != varNamesToFuncs_Assign[currentVarName][0]):
            continue

        #outputString += "\t" + currentVarName + " = {}\n"

        if (currentVarName not in initDictDefsAlreadyMade):
            outputString += "    " + currentVarName + " = {}\n"
            initDictDefsAlreadyMade.append(currentVarName)

    if (len(outputString) > 0):
        outputString += "\n"
        outputFile.write(outputString)

def writeFunctionDecl_Python(outputFile, functionName, toWriteGlobalVarDecls, retainGlobals):
    global initDictDefsAlreadyMade

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

    initDictDefsAlreadyMade = []
    writeInitDictDefs(outputFile, functionName)

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
    global returnValues, CPP_funcBodyLines

    outputVariables = getOutputVariablesList(functionName)

    if (len(outputVariables) > 1):
        sys.exit("writeFunctionEnd_CPP in codegen.py:  number of output variables obtained from getOutputVariables List is greater than one (unsupported).")

    if (len(outputVariables) == 0):
        return

    returnValues[functionName] = str(outputVariables[0])
    #outputFile.write("\treturn " + outputKeyword + ";\n}\n\n")
    #CPP_funcBodyLines += "\treturn " + outputKeyword + ";\n}\n\n"
    CPP_funcBodyLines += "    return " + outputKeyword + ";\n}\n\n"

    outputFile.write(CPP_varTypesLines)
    #outputFile.write("\n")
    outputFile.write(CPP_funcBodyLines)

def writeFunctionEnd(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionEnd_Python(transformFile, functionName, True)
    elif (currentFuncName == decOutFunctionName):
        writeFunctionEnd_CPP(decOutFile, functionName)
        #writeFunctionEnd_Python(decOutFile, functionName, True)
    else:
        writeFunctionEnd_Python(setupFile, functionName, False)

def isFuncCall(binNode):
    if (binNode.type == ops.FUNC):
        return True

    return False

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
    if ( (binNode.type == ops.FOR) or (binNode.type == ops.FORALL) or (binNode.type == ops.FORINNER) ):
        return True

    return False

def isIfStmtEnd(binNode):
    if ( (binNode.type == ops.END) and (binNode.left.attr == IF_BRANCH_HEADER) ):
        return True

    return False

def isForLoopEnd(binNode):
    if (binNode.type == ops.END):
        if ( (binNode.left.attr == FOR_LOOP_HEADER) or (binNode.left.attr == FORALL_LOOP_HEADER) or (binNode.left.attr == FOR_LOOP_INNER_HEADER) ):
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

    return nameToReturn.replace("?","",1) #in case we're directly accessing a list element (e.g., S[k-1])

def getLambdaReplacementsString(lambdaReplacements, includeLoopVar, loopVarName):
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
        #if ( (counter == 0) and (includeFirstLambdaVar == False) ):
            #continue
        if ( (includeLoopVar == False) and (reverseDict[counter] == loopVarName) ):
            continue
        retString += reverseDict[counter]
        retString += ", "

    return retString

def writeLamFuncToUserFuncsFile(lambdaReplacements, startVal, dotProdObj, forInt, lambdaLoopVar):
    global userFuncsFile

    userFuncsOutputString = ""
    userFuncsOutputString += "def "
    userFuncsOutputString += currentLambdaFuncName
    userFuncsOutputString += "("
    lambdaReplacementOutputString = getLambdaReplacementsString(lambdaReplacements, False, lambdaLoopVar)
    userFuncsOutputString += lambdaLoopVar + ", " 
    if (forInt == False):
        userFuncsOutputString += startVal + ", "
    userFuncsOutputString += lambdaReplacementOutputString
    userFuncsOutputString = userFuncsOutputString[0:(len(userFuncsOutputString) - len(", "))]
    #userFuncsOutputString += "):\n\t"
    userFuncsOutputString += "):\n    "
    #userFuncsOutputString += userGlobalsFuncName + "()\n\t"
    userFuncsOutputString += userGlobalsFuncName + "()\n    "
    if (forInt == False):
        userFuncsOutputString += lambdaLoopVar + " = " + getStringFunctionName + "("
        #userFuncsOutputString += startVal + "[" + lambdaLoopVar + "])\n\t"
        userFuncsOutputString += startVal + "[" + lambdaLoopVar + "])\n    "
    userFuncsOutputString += "return " + getAssignStmtAsString(dotProdObj.getBinaryNode().right, None, None, None, False)
    userFuncsOutputString += "\n\n"

    userFuncsFile.write(userFuncsOutputString)

def processDotProdAsNonInt(dotProdObj, currentLambdaFuncName, lambdaReplacements):
    global userFuncsFile

    startVal = dotProdObj.getStartVal()
    startValSplit = startVal.split(LIST_INDEX_SYMBOL)
    startVal = startValSplit[0]

    lambdaLoopVar = dotProdObj.getLoopVar()

    userFuncsOutputString = ""
    #userFuncsOutputString += "def " + getStringFunctionName + "(" + getStringFunctionName + argSuffix + "):\n\t"
    userFuncsOutputString += "def " + getStringFunctionName + "(" + getStringFunctionName + argSuffix + "):\n    "
    #userFuncsOutputString += userGlobalsFuncName + "()\n\t"
    userFuncsOutputString += userGlobalsFuncName + "()\n    "
    userFuncsOutputString += "return " + getStringFunctionName + argSuffix + ".getAttribute()\n\n"
    userFuncsFile.write(userFuncsOutputString)

    writeLamFuncToUserFuncsFile(lambdaReplacements, startVal, dotProdObj, False, lambdaLoopVar)

    dotProdOutputString = ""
    dotProdOutputString += "dotprod2(range(0, "
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getEndVal()))
    dotProdOutputString += "), "
    dotProdOutputString += currentLambdaFuncName + ", " + startVal + ", "
    lambdaReplacementOutputString = getLambdaReplacementsString(lambdaReplacements, False, lambdaLoopVar)
    dotProdOutputString += lambdaReplacementOutputString
    dotProdOutputString = dotProdOutputString[0:(len(dotProdOutputString) - len(", "))]
    dotProdOutputString += ")"

    return dotProdOutputString

def processDotProdAsInt(dotProdObj, currentLambdaFuncName, lambdaReplacements):
    lambdaLoopVar = dotProdObj.getLoopVar()

    writeLamFuncToUserFuncsFile(lambdaReplacements, str(dotProdObj.getStartVal()), dotProdObj, True, lambdaLoopVar)

    dotProdOutputString = "dotprod2(range("
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getStartVal()))
    dotProdOutputString += ","
    dotProdOutputString += replacePoundsWithBrackets(str(dotProdObj.getEndVal()))
    dotProdOutputString += "), "
    dotProdOutputString += currentLambdaFuncName
    dotProdOutputString += ", "
    lambdaReplacementOutputString = getLambdaReplacementsString(lambdaReplacements, False, lambdaLoopVar)
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
    #elif (node.type == ops.NON_EQ_TST):
        #leftSide = 
    elif ( (node.type == ops.LIST) ): #or ( (node.type == ops.EXPAND) and (variableType == types.list) ) ):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  encountered node of type ops.LIST, but variableName parameter passed in is of type None.")
        listOutputString = ""
        #listOutputString += ";\n"
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
            #userFuncsOutputString += "\t" + userGlobalsFuncName + "();\n"
            userFuncsOutputString += "    " + userGlobalsFuncName + "();\n"
            #userFuncsOutputString += "\treturn;\n}\n\n"
            userFuncsOutputString += "    return;\n}\n\n"
            userFuncsCPPFile.write(userFuncsOutputString)
        return funcOutputString
    elif (node.type == ops.EXPAND):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  ops.EXPAND node encountered, but variableName is set to None.")
        return getCPPAsstStringForExpand(node, variableName, replacementsDict)

    sys.exit("getAssignStmtAsString_CPP in codegen.py:  unsupported node type detected.")

def getCPPAsstStringForExpand(node, variableName, replacementsDict):
    global CPP_varTypesLines

    outputString = ""
    outputString += "\n"

    for listNode in node.listNodes:
        listNodeName = applyReplacementsDict(replacementsDict, listNode)
        listNodeName = replacePoundsWithBrackets(listNodeName)
        listNodeType = getFinalVarType(listNodeName, currentFuncName)
        if (listNodeType == types.NO_TYPE):
            sys.exit("getCPPAsstStringForExpand in codegen.py:  could not obtain one of the types for the variable names included in the expand node.")
        outputString += writeCurrentNumTabsToString()

        #CPP_varTypesLines += "\t" + makeTypeReplacementsForCPP(listNodeType) + " " + listNodeName + ";\n"
        CPP_varTypesLines += "    " + makeTypeReplacementsForCPP(listNodeType) + " " + listNodeName + ";\n"
        outputString += listNodeName + " = "

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
    elif ( (node.type == ops.ATTR) and (str(node.attr) == smallExp) ):
        return "SmallExp(80)"
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

    elif (node.type == ops.NON_EQ_TST):
        leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        return "( (" + leftString + ") != (" + rightString + ") )"


    #elif (node.type == ops.CONCAT):
        #leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #return "(" + leftString + ", " + rightString + ")"
        #return leftString + ", " + rightString


    #elif (node.type == ops.OR):
        #leftString = getAssignStmtAsString(node.left, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #rightString = getAssignStmtAsString(node.right, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
        #return "(" + leftString + " or " + rightString + ")"
    elif (node.type == ops.STRCONCAT):
        strconcatOutputString = "("
        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode, replacementsDict, dotProdObj, lambdaReplacements, forOutput)
            strconcatOutputString += listNodeAsString + " + "
        strconcatOutputString = strconcatOutputString[0:(len(strconcatOutputString) - len(" + "))]
        strconcatOutputString += ")"
        return strconcatOutputString
    elif (node.type == ops.CONCAT):
        concatOutputString = "("
        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode, replacementsDict, dotProdObj, lambdaReplacements, forOutput)          
            concatOutputString += listNodeAsString + ", "
        concatOutputString = concatOutputString[0:(len(concatOutputString) - len(", "))]
        concatOutputString += ")"
        return concatOutputString
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
        if (nodeName == INIT_FUNC_NAME):
            if ( (len(node.listNodes) == 1) and (node.listNodes[0] == strArgName) ):
                return "\"\""
            else:
                return "1"
        elif (nodeName == ISMEMBER_FUNC_NAME):
            funcOutputString = groupObjName + "." + nodeName + "("
        elif (nodeName == INTEGER_FUNC_NAME):
            funcOutputString = "int("
        else:
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
            #userFuncsOutputString += "\t" + userGlobalsFuncName + "()\n"
            userFuncsOutputString += "    " + userGlobalsFuncName + "()\n"
            #userFuncsOutputString += "\treturn\n\n"
            userFuncsOutputString += "    return\n\n"
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

    (funcName, varInfoObj) = getVarNameEntryFromAssignInfo(assignInfo, varName)
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
    global CPP_varTypesLines, CPP_funcBodyLines

    variableName = getFullVarName(binNode.left, False)

    if (variableName == inputKeyword):
        return

    outputString_Types = ""
    outputString_Body = ""

    if (binNode.right.type != ops.LIST):
        outputString_Body += writeCurrentNumTabsToString()

    #writeCurrentNumTabsIn(outputFile)

    if ( (variableName.find(LIST_INDEX_SYMBOL) == -1) and (binNode.right.type != ops.EXPAND) ):
        variableType = getFinalVarType(variableName, currentFuncName)
        #outputString += makeTypeReplacementsForCPP(variableType) + " "
        #outputString_Types += "\t" + makeTypeReplacementsForCPP(variableType) + " "
        outputString_Types += "    " + makeTypeReplacementsForCPP(variableType) + " "

    variableName = replacePoundsWithBrackets(variableName)

    if (binNode.right.type != ops.EXPAND):
        outputString_Types += variableName + ";\n"

    if ( (binNode.right.type != ops.EXPAND) and (binNode.right.type != ops.LIST) ):
        outputString_Body += variableName

    if ( (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
        outputString_Body += " = "

    outputString_Body += getAssignStmtAsString_CPP(binNode.right, None, variableName)
    if ( (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
        outputString_Body += ";\n"
    #outputFile.write(outputString)

    CPP_varTypesLines += outputString_Types
    CPP_funcBodyLines += outputString_Body

def writeAssignStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    if (str(binNode) == RETURN_STATEMENT):
        outputFile.write("return\n")
        return

    outputString = ""
    dotProdObj = None
    lambdaReplacements = None

    if ( (binNode.right.type == ops.ON) and (binNode.right.left.type == ops.PROD) ):
        (dotProdObj, lambdaReplacements) = writeLambdaFuncAssignStmt(outputFile, binNode)
        #writeCurrentNumTabsIn(outputFile)

    variableName = replacePoundsWithBrackets(getFullVarName(binNode.left, False))

    if (variableName == outputKeyword):
        if ( (str(binNode) == "output := False") or (str(binNode) == "output := false") ):
            falseOutputString = "output = False\n"
            falseOutputString += writeCurrentNumTabsToString()
            falseOutputString += "return output\n"
            outputFile.write(falseOutputString)
            return

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
        #userFuncsOutputString += "\t" + userGlobalsFuncName + "()\n"
        userFuncsOutputString += "    " + userGlobalsFuncName + "()\n"
        #userFuncsOutputString += "\treturn\n\n"
        userFuncsOutputString += "    return\n\n"
        userFuncsFile.write(userFuncsOutputString)

def writeErrorFunc_CPP(outputFile, binNode):
    global userFuncsCPPFile, userFuncsList_CPP, CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()

    outputString += errorFuncName + "("
    userErrorFuncArg_WithApostrophes = getAssignStmtAsString_CPP(binNode.attr, None, None)
    lenErrorArg_WithApostrophes = len(userErrorFuncArg_WithApostrophes)
    if (userErrorFuncArg_WithApostrophes[0] == "'"):
        userErrorFuncArg_WithApostrophes = "\"" + userErrorFuncArg_WithApostrophes[1:lenErrorArg_WithApostrophes]
    if (userErrorFuncArg_WithApostrophes[lenErrorArg_WithApostrophes - 1] == "'"):
        userErrorFuncArg_WithApostrophes = userErrorFuncArg_WithApostrophes[0:(lenErrorArg_WithApostrophes -1)] + "\""
    outputString += userErrorFuncArg_WithApostrophes
    outputString += ");\n"

    outputString += writeCurrentNumTabsToString()

    outputString += "return \"\";\n"
    CPP_funcBodyLines += outputString

    if (errorFuncName not in userFuncsList_CPP):
        userFuncsList_CPP.append(errorFuncName)
        userFuncsOutputString = ""
        userFuncsOutputString += "void " + errorFuncName + "("
        userFuncsOutputString += makeTypeReplacementsForCPP(errorFuncArgString_CPPType) + " "
        userFuncsOutputString += errorFuncArgString + ")\n"
        userFuncsOutputString += "{\n"
        #userFuncsOutputString += "\t" + userGlobalsFuncName + "();\n"
        #userFuncsOutputString += "\tcout << " + errorFuncArgString + " << endl;\n"
        userFuncsOutputString += "    cout << " + errorFuncArgString + " << endl;\n"
        #userFuncsOutputString += "\treturn;\n"
        userFuncsOutputString += "    return;\n"
        userFuncsOutputString += "}\n\n"
        userFuncsCPPFile.write(userFuncsOutputString)

def writeElseStmt_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    #writeCurrentNumTabsIn(outputFile)
    outputString = ""
    outputString += writeCurrentNumTabsToString()
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

    #outputFile.write(outputString)
    CPP_funcBodyLines += outputString

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
    global CPP_funcBodyLines

    #writeCurrentNumTabsIn(outputFile)
    outputString = ""
    outputString += writeCurrentNumTabsToString()

    outputString += "if ( "
    outputString += getAssignStmtAsString_CPP(binNode.left, None, None)
    outputString += " )\n"
    outputString += writeCurrentNumTabsToString()
    outputString += "{\n"

    #outputFile.write(outputString)

    CPP_funcBodyLines += outputString

def writeIfStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)
    outputString = ""

    outputString += "if ( "
    outputString += getAssignStmtAsString(binNode.left, None, None, None, False)
    outputString += " ):\n"

    outputFile.write(outputString)

def writeForLoopDecl_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    #writeCurrentNumTabsIn(outputFile)

    outputString = ""
    outputString += writeCurrentNumTabsToString()

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
        #outputString += writeCurrentNumTabsToString() + "\t"
        outputString += writeCurrentNumTabsToString() + "    "
        outputString += currentLoopIncVarName + " = " + currentLoopVariableName + KeysListSuffix_CPP + "[" + currentLoopIncVarName + TempLoopVar_CPP + "];\n"
    else:
        sys.exit("writeForLoopDecl_CPP in codegen.py:  encounted node that is neither type ops.FOR nor ops.FORALL (unsupported).")

    #outputFile.write(outputString)
    CPP_funcBodyLines += outputString

def writeForLoopDecl_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    if ( (binNode.type == ops.FOR) or (binNode.type == ops.FORINNER) ):
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

def executeAddToListPython(binNode):
    global setupFile

    listNodes = None

    try:
        listNodes = binNode.listNodes
    except:
        sys.exit("executeAddToListPythonn in codegen.py:  could not obtain binary node's list nodes; must be 2 of them (list, data item to add).")

    if (len(listNodes) != 2):
        sys.exit("executeAddToListPython in codegen.py:  number of binary node's list nodes isn't 2; this must be the case (list, data item to add to it).")

    outputString = listNodes[0] + ".append(" + listNodes[1] + ")\n"
    setupFile.write(outputString)

def writeFuncCall(binNode):
    global setupFile

    writeCurrentNumTabsIn(setupFile)

    outputString = ""

    if (str(binNode.attr) == ADD_TO_LIST):
        executeAddToListPython(binNode)
        return

    outputString += binNode.attr + "("

    listNodes = None

    try:
        listNodes = binNode.listNodes
    except:
        sys.exit("writeFuncCall in codegen.py:  couldn't obtain listNodes for func call binary node; make sure that even if passing no arguments to function, you put \"None\" in the parentheses.")

    if (listNodes[0] != "None"):
        for listNode in listNodes:
            outputString += listNode + ", "
        lenString = len(outputString)
        outputString = outputString[0:(lenString - 2)]

    outputString += ")\n"

    setupFile.write(outputString)

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
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    #outputFile.write(outputString)

    CPP_funcBodyLines += outputString

def writeForLoopEnd(binNode):
    if (currentFuncName == decOutFunctionName):
        writeForLoopEnd_CPP(decOutFile, binNode)

def writeIfStmtEnd(binNode):
    if (currentFuncName == decOutFunctionName):
        writeIfStmtEnd_CPP(decOutFile, binNode)

def writeIfStmtEnd_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    #outputFile.write(outputString)
    CPP_funcBodyLines += outputString

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

    if ( (varName != secParamVarName) and (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
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

    if ( (astNode.type == ops.BEGIN) and (astNode.left.attr == FOR_LOOP_INNER_HEADER) ):
        return True

    if ( (astNode.type == ops.BEGIN) and (astNode.left.attr == IF_BRANCH_HEADER) ):
        return True

    return False

def writeSDLToFiles(astNodes):
    global currentFuncName, numTabsIn, setupFile, transformFile, lineNoBeingProcessed
    global CPP_varTypesLines, CPP_funcBodyLines

    for astNode in astNodes:
        lineNoBeingProcessed += 1
        processedAsFunctionStart = False

        if (isFunctionStart(astNode) == True):
            currentFuncName = getFuncNameFromBinNode(astNode)
            writeFunctionDecl(currentFuncName)
            CPP_varTypesLines = ""
            CPP_funcBodyLines = ""
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
        elif (isFuncCall(astNode) == True):
            writeFuncCall(astNode)
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
    #outputString += "\tglobal " + groupObjName + "\n"
    outputString += "    global " + groupObjName + "\n"
    #outputString += "\t" + groupObjName + " = PairingGroup(" + groupArg + ")\n\n"
    outputString += "    " + groupObjName + " = PairingGroup(" + groupArg + ")\n\n"

    return outputString

def writeFuncsCalledFromMain(functionOrder, argsToFirstFunc):
    outputString = ""

    if ( (type(functionOrder) is not list) or (len(functionOrder) == 0) ):
        sys.exit("writeFuncsCalledFromMain in codegen.py:  functionOrder parameter passed in is invalid.")

    counter = 0
    for funcName in functionOrder:
        if ( (type(funcName) is not str) or (len(funcName) == 0) ):
            sys.exit("writeFuncsCalledFromMain in codegen.py:  one of the entries in functionOrder is invalid.")
        #outputString += "\t"
        outputString += "    "
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
        #outputString += "\t" + lineForSetupMain + "\n"
        outputString += "    " + lineForSetupMain + "\n"

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
        #outputString += "\tf_" + currentVariableName + " = open('" + currentVariableName + charmPickleExt + "', 'wb')\n"
        outputString += "    f_" + currentVariableName + " = open('" + currentVariableName + charmPickleExt + "', 'wb')\n"
        #outputString += "\tpick_" + currentVariableName + " = " + objectToBytesFuncName + "(" + lastFuncOutputVar + ", " + groupObjName + ")\n"
        outputString += "    pick_" + currentVariableName + " = " + objectToBytesFuncName + "(" + lastFuncOutputVar + ", " + groupObjName + ")\n"
        #outputString += "\tf_" + currentVariableName + ".write(pick_" + currentVariableName + ")\n"
        outputString += "    f_" + currentVariableName + ".write(pick_" + currentVariableName + ")\n"
        #outputString += "\tf_" + currentVariableName + ".close()\n\n"
        outputString += "    f_" + currentVariableName + ".close()\n\n"

    #outputString += "\t" + serializeKeysName + " = {'" + keygenSecVar + "':" + keygenBlindingExponent + ", '" + keygenPubVar[0] + "':" + serializePubKey + "}\n"
    outputString += "    " + serializeKeysName + " = {'" + keygenSecVar + "':" + keygenBlindingExponent + ", '" + keygenPubVar[0] + "':" + serializePubKey + "}\n"
    #outputString += "\t" + serializeFuncName + "('" + serializeKeysName + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + serializeKeysName + "))\n\n"
    outputString += "    " + serializeFuncName + "('" + serializeKeysName + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + serializeKeysName + "))\n\n"

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
        #outputString += "\t" + varToUnpickle + unpickleFileSuffix + " = open('" + fileNameForThisVar + "', 'rb').read()\n"
        outputString += "    " + varToUnpickle + unpickleFileSuffix + " = open('" + fileNameForThisVar + "', 'rb').read()\n"
        #outputString += "\t" + varToUnpickle + " = " + bytesToObjectFuncName + "(" + varToUnpickle + unpickleFileSuffix + ", " + groupObjName + ")\n\n"
        outputString += "    " + varToUnpickle + " = " + bytesToObjectFuncName + "(" + varToUnpickle + unpickleFileSuffix + ", " + groupObjName + ")\n\n"
        #outputString += "\t" + varToUnpickle + unpickleFileSuffix + ".close()\n\n"

    #outputString += "\n"

    (outputFromFuncsCalledFromMain, lastFuncNameWrittenToMain) = writeFuncsCalledFromMain(transformFunctionOrder, argsToFirstTransformFunc)
    outputString += outputFromFuncsCalledFromMain
    outputString += "\n"

    varsToPickle = getOutputVariablesList(transformFunctionName)
    for varToPickle in varsToPickle:
        #outputString += "\t" + serializeFuncName + "('" + varToPickle + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + varToPickle + "))\n"
        outputString += "    " + serializeFuncName + "('" + varToPickle + "_" + schemeName + "_" + serializeExt + "', " + serializeObjectOutFuncName + "(" + groupObjName + ", " + varToPickle + "))\n"

    transformFile.write(outputString)

def writeMainFuncOfDecOut():
    global decOutFile

    outputString = ""
    outputString += CPP_Main_Line + "\n"
    outputString += "{\n"
    #outputString += "\t" + PairingGroupClassName_CPP + " " + groupObjName + "(" + SecurityParameter_CPP + ");\n\n"
    outputString += "    " + PairingGroupClassName_CPP + " " + groupObjName + "(" + SecurityParameter_CPP + ");\n\n"

    #outputString += "\t" + charmDictType + " dict;\n"
    outputString += "    " + charmDictType + " dict;\n"

    secretKeyType = getFinalVarType(keygenBlindingExponent, keygenFuncName)

    #outputString += "\t" + makeTypeReplacementsForCPP(secretKeyType) + " " + keygenBlindingExponent + ";\n"
    outputString += "    " + makeTypeReplacementsForCPP(secretKeyType) + " " + keygenBlindingExponent + ";\n"

    #outputString += "\t" + serializePubKeyType + " " + serializePubKey_DecOut + ";\n\n"
    outputString += "    " + serializePubKeyType + " " + serializePubKey_DecOut + ";\n\n"

    #outputString += "\t" + "Element T0, T1, T2;\n"
    outputString += "    " + "Element T0, T1, T2;\n"

    #outputString += "\t" + "dict.set(\"T0\", T0);\n"
    outputString += "    " + "dict.set(\"T0\", T0);\n"

    #outputString += "\t" + "dict.set(\"T1\", T1);\n"
    outputString += "    " + "dict.set(\"T1\", T1);\n"

    #outputString += "\t" + "dict.set(\"T2\", T2);\n\n"
    outputString += "    " + "dict.set(\"T2\", T2);\n\n"

    #outputString += "\t" + parseParCT_FuncName_DecOut + "(\""
    outputString += "    " + parseParCT_FuncName_DecOut + "(\""

    transformOutputVar = getOutputVariablesList(transformFunctionName)
    if (len(transformOutputVar) != 1):
        sys.exit("writeMainFuncOfDecOut in codegen.py:  getOutputVariablesList(transformFunctionName) returned list of length != 1.")
 
    outputString += transformOutputVar[0] + "_" + schemeName + "_" + serializeExt + "\", dict);\n"
    #outputString += "\t" + parseKeys_FuncName_DecOut + "(\""
    outputString += "    " + parseKeys_FuncName_DecOut + "(\""
    outputString += serializeKeysName + "_" + schemeName + "_" + serializeExt + "\", "
    outputString += keygenBlindingExponent + ", " + serializePubKey_DecOut + ");\n\n"

    decOutOutputVars = getOutputVariablesList(decOutFunctionName)
    if (len(decOutOutputVars) != 1):
        sys.exit("writeMainFuncOfDecOut in codegen.py:  getOutputVariablesList(decOutFunctionName) returned a list that is not of length one.")

    varTypeOfDecOut_Output = getFinalVarType(decOutOutputVars[0], decOutFunctionName)
    if (varTypeOfDecOut_Output == types.NO_TYPE):
        sys.exit("writeMainFuncOfDecOut in codegen.py:  could not obtain the type of decout's output variable.")

    #outputString += "\t" + makeTypeReplacementsForCPP(varTypeOfDecOut_Output) + " " + decOutOutputVars[0] + " = " + decOutFunctionName
    outputString += "    " + makeTypeReplacementsForCPP(varTypeOfDecOut_Output) + " " + decOutOutputVars[0] + " = " + decOutFunctionName
    outputString += "(" + groupObjName + ", dict, " + keygenBlindingExponent + ", " + serializePubKey_DecOut
    outputString += ");\n\n"
    #outputString += "\tcout << " + decOutOutputVars[0] + " << endl;\n\n"
    outputString += "    cout << " + decOutOutputVars[0] + " << endl;\n\n"
    #outputString += "\treturn 0;\n"
    outputString += "    return 0;\n"
    outputString += "}\n"

    decOutFile.write(outputString)

def writeMainFuncOfDecOut_Python():
    global decOutFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()
    (outputFromFuncsCalledFromMain, lastFuncNameWrittenToMain) = writeFuncsCalledFromMain(decOutFunctionOrder, argsToFirstDecOutFunc)
    outputString += outputFromFuncsCalledFromMain

    decOutFile.write(outputString)

def writeMainFunc_IgnoreCloudSourcing():
    global setupFile

    outputString = "def main():\n"
    outputString += "    global group\n    group = PairingGroup(" + secParamVarName + ")\n\n"
    outputString += "if __name__ == '__main__':\n"
    outputString += "    main()\n\n"
    setupFile.write(outputString)

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
        if ( (varName != secParamVarName) and (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
            globalVarNames.append(varName)

def addGetGlobalsToUserFuncs():
    global userFuncsFile, userFuncsCPPFile

    outputString = ""

    outputString += "def " + userGlobalsFuncName + "():\n"
    #outputString += "\tglobal " + groupObjName + "UserFuncs\n\n"
    outputString += "    global " + groupObjName + "UserFuncs\n\n"
    #outputString += "\tif (" + groupObjName + "UserFuncs == None):\n"
    outputString += "    if (" + groupObjName + "UserFuncs == None):\n"
    #outputString += "\t\t" + groupObjName + "UserFuncs = PairingGroup(" + groupArg + ")\n"
    outputString += "        " + groupObjName + "UserFuncs = PairingGroup(" + groupArg + ")\n"

    userFuncsFile.write(outputString)

    outputString = ""
    outputString += "void " + userGlobalsFuncName + "()\n"
    outputString += "{\n"
    #outputString += "\tif (" + groupObjName + "UserFuncs == NULL)\n"
    outputString += "    if (" + groupObjName + "UserFuncs == NULL)\n"
    #outputString += "\t{\n"
    outputString += "    {\n"
    #outputString += "\t\t" + PairingGroupClassName_CPP + " " + groupObjName + "UserFuncs(" + SecurityParameter_CPP + ");\n"
    outputString += "        " + PairingGroupClassName_CPP + " " + groupObjName + "UserFuncs(" + SecurityParameter_CPP + ");\n"
    #outputString += "\t}\n"
    outputString += "    }\n"
    outputString += "}\n"

    #userFuncsCPPFile.write(outputString)

def generateMakefile():
    if (ignoreCloudSourcing == False):
        makefile_FileObject = open(makefileFolderName + makefileFileName, 'w')
    else:
        makefile_FileObject = open("/tmp/" + makefileFileName, 'w')

    outputString = ""
    outputString += "SDL_SRC := decOutOutsourcing_" + schemeName + "\n"
    outputString += "NAME    := " + decOutObjFileName + "\n\n"

    makefileTemplateLines = open(makefileTemplateFileName, 'r').readlines()
    for line in makefileTemplateLines:
        outputString += line

    makefile_FileObject.write(outputString)
    makefile_FileObject.close()

def main(SDL_Scheme, ignoreCloudSourcingArg, nonCloudSourcingFileNameArg=None):
    global setupFile, transformFile, decOutFile, userFuncsFile, assignInfo, varNamesToFuncs_All
    global varNamesToFuncs_Assign, inputOutputVars, userFuncsCPPFile, functionNameOrder
    global blindingFactors_NonLists, blindingFactors_Lists, ignoreCloudSourcing
    global nonCloudSourcingFileName

    ignoreCloudSourcing = ignoreCloudSourcingArg
    if (nonCloudSourcingFileNameArg != None):
        nonCloudSourcingFileName = nonCloudSourcingFileNameArg

    if ( (type(SDL_Scheme) is not str) or (len(SDL_Scheme) == 0) ):
        sys.exit("codegen.py:  sys.argv[1] argument (file name for SDL scheme) passed in was invalid.")

    if (ignoreCloudSourcing == False):
        (blindingFactors_NonLists, blindingFactors_Lists) = keygen(SDL_Scheme)
    else:
        parseFile2(SDL_Scheme, False, True)

    #printLinesOfCode()
    #print(blindingFactors_NonLists)
    #print(blindingFactors_Lists)
    #sys.exit("test")

    astNodes = getAstNodes()
    assignInfo = getAssignInfo()
    inputOutputVars = getInputOutputVars()
    functionNameOrder = getFunctionNameOrder()
    varNamesToFuncs_All = getVarNamesToFuncs_All()
    varNamesToFuncs_Assign = getVarNamesToFuncs_Assign()

    if ( (type(setupFileName) is not str) or (len(setupFileName) <= len(pySuffix) ) or (setupFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with setupFileName in config.py.")

    if ( (type(transformFileName) is not str) or (len(transformFileName) <= len(pySuffix) ) or (transformFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with transformFileName in config.py.")

    if ( (type(decOutFileName) is not str) or (len(decOutFileName) <= len(cppSuffix) ) or (decOutFileName.endswith(cppSuffix) == False) ):
        sys.exit("codegen.py:  problem with decOutFileName in config.py.")

    setupFile = open(setupFileName, 'w')

    if (ignoreCloudSourcing == False):
        transformFile = open(transformFileName, 'w')
    else:
        transformFile = open("/tmp/" + transformFileName, 'w')

    if (ignoreCloudSourcing == False):
        decOutFile = open(decOutFolderName + decOutFileName, 'w')
    else:
        decOutFile = open("/tmp/" + decOutFileName, 'w')

    if (ignoreCloudSourcing == False):
        userFuncsFile = open(userFuncsFileName, 'w')
    else:
        userFuncsFile = open("/tmp/" + userFuncsFileName, 'w')

    if (ignoreCloudSourcing == False):
        userFuncsCPPFile = open(decOutFolderName + userFuncsCPPFileName, 'w')
    else:
        userFuncsCPPFile = open("/tmp/" + userFuncsCPPFileName, 'w')

    getGlobalVarNames()

    addImportLines()
    addGroupObjGlobalVar()
    addNumSignatures()
    addNumSigners()
    addSecParamValue()

    #if (ignoreCloudSourcing == True):
        #setupFile.write("bodyKey = 'Body'\n\n")

    writeSDLToFiles(astNodes)

    addSmallExpFunc()

    if (ignoreCloudSourcing == False):
        writeMainFuncs()
    else:
        writeMainFunc_IgnoreCloudSourcing()

    addGetGlobalsToUserFuncs()

    setupFile.close()
    transformFile.close()
    decOutFile.close()
    userFuncsFile.close()
    userFuncsCPPFile.close()

    if (ignoreCloudSourcing == False):
        generateMakefile()

    if (ignoreCloudSourcing != False):
        os.system("mv " + setupFileName + " " + nonCloudSourcingFileName)

if __name__ == "__main__":
    #global ignoreCloudSourcing

    lenSysArgv = len(sys.argv)

    if ( (lenSysArgv == 1) or (lenSysArgv > 3) ):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of SDL file] [OPTIONAL:  if second argument passed, codegen does not run CloudSourcing]")

    if ( (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of SDL file] [OPTIONAL:  if second argument passed, codegen does not run CloudSourcing]")

    if (lenSysArgv == 2):
        main(sys.argv[1], False)
    elif (lenSysArgv == 3):
        main(sys.argv[1], True, sys.argv[2])
    else:
        sys.exit("error in system logic in first main method.")

    parseLinesOfCode(getLinesOfCode(), True, True)
    #os.system("cp userFuncsPermanent.py userFuncs.py")
    #printLinesOfCode()
    #sys.exit("test")

    if (ignoreCloudSourcing == False):
        writeLinesOfCodeToFile(outputSDLFileName)
    #print("io vars:  ", getInputOutputVars())
    lll = getFinalVarType("gl#0", "setup")
    #print(str(lll))
    #print("Function Name Order:  ", functionNameOrder)
