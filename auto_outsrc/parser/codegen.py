from keygen import *
from config import *
import sys

assignInfo = None
setupFile = None
transformFile = None
decOutFile = None
currentFuncName = NONE_FUNC_NAME
numTabsIn = 1
returnValues = {}

def writeCurrentNumTabsIn(outputFile):
    outputString = ""

    for numTabs in range(0, numTabsIn):
        outputString += "\t"

    outputFile.write(outputString)

def addImportLines():
    global setupFile, transformFile, decOutFile

def addGlobalVars():
    global setupFile, transformFile

    if ( (type(groupObjName) is not str) or (len(groupObjName) == 0) ):
        sys.exit("addGlobalVars in codegen.py:  groupObjName in config.py is invalid.")

    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(groupObjName)
    if ( (possibleFuncName != None) or (possibleVarInfoObj != None) ):
        sys.exit("addGlobalVars in codegen.py:  groupObjName in config.py is also the name of a variable in the cryptoscheme (not allowed).")

    outputString = groupObjName + " = None\n\n"

    setupFile.write(outputString)
    transformFile.write(outputString) 

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
        print("writeFunctionEnd_Python in codegen.py:  could not obtain function's output variables from getVarDeps() on VarInfo obj.")
        print("This is most likely the decrypt function.  This should be fixed in transform.")
        return

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

def writeFunctionDecl_Python(outputFile, functionName):
    outputString = ""

    inputVariables = None

    try:
        inputVariables = assignInfo[functionName][inputKeyword].getVarDeps()
    except:
        print("writeFunctionDecl_Python in codegen.py:  could not obtain function's input variables from getVarDeps() on VarInfo obj.")
        print("This is most likely the decrypt function.  This should be fixed in transform.")
        return

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

def writeFunctionDecl_CPP(outputFile, functionName):
    pass

def writeFunctionDecl(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionDecl_Python(transformFile, functionName)
    elif (currentFuncName == decOutFunctionName):
        writeFunctionDecl_CPP(decOutFile, functionName)
    else:
        writeFunctionDecl_Python(setupFile, functionName)

def writeFunctionEnd(functionName):
    global setupFile, transformFile, decOutFile

    if (currentFuncName == transformFunctionName):
        writeFunctionEnd_Python(transformFile, functionName)
    elif (currentFuncName == decOutFunctionName):
        writeFunctionEnd_CPP(decOutFile, functionName)
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

def getAssignStmtAsString(node):
    if (type(node) is str):
        return node
    elif ( (node.type == ops.ATTR) or (node.type == ops.TYPE) ):
        strNameToReturn = replacePoundsWithBrackets(str(node.attr))
        return strNameToReturn
    elif (node.type == ops.ADD):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return "(" + leftString + " + " + rightString + ")"
    elif (node.type == ops.SUB):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return "(" + leftString + " - " + rightString + ")"
    elif (node.type == ops.MUL):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return "(" + leftString + " * " + rightString + ")"
    elif (node.type == ops.DIV):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return "(" + leftString + " / " + rightString + ")"
    elif (node.type == ops.EXP):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return "(" + leftString + " ** " + rightString + ")"
    elif (node.type == ops.LIST):
        listOutputString = "["
        for listNode in node.listNodes:
            listNodeAsString = getAssignStmtAsString(listNode)
            listOutputString += listNodeAsString + ", "
        listOutputString = listOutputString[0:(len(listOutputString) - len(", "))]
        listOutputString += "]"
        return listOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString(node.left)
        randomOutputString = groupObjName + ".random(" + randomGroupType + ")"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString(node.left)
        hashGroupType = getAssignStmtAsString(node.right)
        hashOutputString = groupObjName + ".hash(" + hashMessage + ", " + hashGroupType + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString(node.left)
        pairRightSide = getAssignStmtAsString(node.right)
        pairOutputString = "pair(" + pairLeftSide + ", " + pairRightSide + ")"
        return pairOutputString
    elif (node.type == ops.FUNC):
        funcOutputString = node.attr + "("
        for listNodeInFunc in node.listNodes:
            funcOutputString += listNodeInFunc + ", "
        funcOutputString = funcOutputString[0:(len(funcOutputString) - len(", "))]
        funcOutputString += ")"
        return funcOutputString

    return "" #replace with sys.exit

def writeAssignStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""
    outputString += replacePoundsWithBrackets(str(binNode.left.attr))
    outputString += " = "

    outputString += getAssignStmtAsString(binNode.right)
    
    outputString += "\n"
    outputFile.write(outputString)

def writeAssignStmt(binNode):
    if (currentFuncName == transformFunctionName):
        writeAssignStmt_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeAssignStmt_CPP(decOutFile, binNode)
    else:
        writeAssignStmt_Python(setupFile, binNode)

def writeForLoopDecl_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""

    outputString += "for "
    outputString += getAssignStmtAsString(binNode.left.left)
    outputString += " in range("
    outputString += getAssignStmtAsString(binNode.left.right)
    outputString += ", "
    outputString += getAssignStmtAsString(binNode.right)
    outputString += "):\n"

    outputFile.write(outputString)

def writeForLoopDecl(binNode):
    if (currentFuncName == transformFunctionName):
        writeForLoopDecl_Python(transformFile, binNode)
    elif (currentFuncName == decOutFunctionName):
        writeForLoopDecl_CPP(decOutFile, binNode)
    else:
        writeForLoopDecl_Python(setupFile, binNode)

def writeSDLToFiles(astNodes):
    global currentFuncName, numTabsIn

    for astNode in astNodes:
        if (isFunctionStart(astNode) == True):
            currentFuncName = getFuncNameFromBinNode(astNode)
            writeFunctionDecl(currentFuncName)
        elif (isFunctionEnd(astNode) == True):
            writeFunctionEnd(currentFuncName)
            currentFuncName = NONE_FUNC_NAME

        if (currentFuncName == NONE_FUNC_NAME):
            continue

        if (isForLoopStart(astNode) == True):
            writeForLoopDecl(astNode)
            numTabsIn += 1
        elif (isForLoopEnd(astNode) == True):
            numTabsIn -= 1
        elif (isAssignStmt(astNode) == True):
            writeAssignStmt(astNode)

def getStringOfFirstSetupFuncArgs():
    if (type(argsToFirstSetupFunc) is not list):
        sys.exit("getStringOfFirstSetupFuncArgs in codegen.py:  argsToFirstSetupFunc is not of type list.")

    if (len(argsToFirstSetupFunc) == 0):
        return ""

    outputString = ""

    for argName in argsToFirstSetupFunc:
        try:
            argNameAsStr = str(argName)
        except:
            sys.exit("getStringOfFirstSetupFuncArgs in codegen.py:  could not convert one of the argument names to a string.")

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

def writeMainFuncOfSetup():
    global setupFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"

    outputString += writeGroupObjToMain()

    if ( (type(setupFunctionOrder) is not list) or (len(setupFunctionOrder) == 0) ):
        sys.exit("writeMainFuncOfSetup in codegen.py:  setupFunctionOrder from config.py is invalid.")

    counter = 0
    for setupFunc in setupFunctionOrder:
        if ( (type(setupFunc) is not str) or (len(setupFunc) == 0) ):
            sys.exit("writeMainFuncOfSetup in codegen.py:  one of the entries in setupFunctionOrder from config.py is invalid.")
        outputString += "\t"
        if (setupFunc not in returnValues):
            sys.exit("writeMainFuncOfSetup in codegen.py:  current function name in setupFunctionOrder is not in return values.")
        if (len(returnValues[setupFunc]) > 0):
            outputString += returnValues[setupFunc] + " = "
        outputString += setupFunc + "("
        if (counter == 0):
            outputString += getStringOfFirstSetupFuncArgs()
        else:
            outputString += getStringOfInputArgsToFunc(setupFunc)
        outputString += ")\n"
        counter += 1

    setupFile.write(outputString)

def writeMainFuncOfTransform():
    global transformFile

    outputString = ""
    outputString += "if __name__ == \"__main__\":\n"
    outputString += writeGroupObjToMain()

    transformFile.write(outputString)

def writeMainFuncOfDecOut():
    return

def writeMainFuncs():
    writeMainFuncOfSetup()
    writeMainFuncOfTransform()
    writeMainFuncOfDecOut()

def main(SDL_Scheme):
    global setupFile, transformFile, decOutFile, assignInfo

    if ( (type(SDL_Scheme) is not str) or (len(SDL_Scheme) == 0) ):
        sys.exit("codegen.py:  sys.argv[1] argument (file name for SDL scheme) passed in was invalid.")

    keygen(SDL_Scheme)
    #printLinesOfCode()
    astNodes = getAstNodes()
    assignInfo = getAssignInfo()

    if ( (type(setupFileName) is not str) or (len(setupFileName) <= len(pySuffix) ) or (setupFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with setupFileName in config.py.")

    if ( (type(transformFileName) is not str) or (len(transformFileName) <= len(pySuffix) ) or (transformFileName.endswith(pySuffix) == False) ):
        sys.exit("codegen.py:  problem with transformFileName in config.py.")

    if ( (type(decOutFileName) is not str) or (len(decOutFileName) <= len(cppSuffix) ) or (decOutFileName.endswith(cppSuffix) == False) ):
        sys.exit("codegen.py:  problem with decOutFileName in config.py.")

    setupFile = open(setupFileName, 'w')
    transformFile = open(transformFileName, 'w')
    decOutFile = open(decOutFileName, 'w')

    addImportLines()
    addGlobalVars()
    writeSDLToFiles(astNodes)
    writeMainFuncs()

    setupFile.close()
    transformFile.close()
    decOutFile.close()

if __name__ == "__main__":
    main(sys.argv[1])
