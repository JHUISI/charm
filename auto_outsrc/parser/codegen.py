from keygen import *
from config import *
import sys

assignInfo = None
setupFile = None
transformFile = None
decOutFile = None
currentFuncName = NONE_FUNC_NAME
numTabsIn = 1

def writeCurrentNumTabsIn(outputFile):
    outputString = ""

    for numTabs in range(0, numTabsIn):
        outputString += "\t"

    outputFile.write(outputString)

def addImportLines():
    global setupFile, transformFile, decOutFile

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

    outputString += "\treturn "
    outputString += outputVariablesString
    outputString += "\n\n"

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
        #print(binNode)
        pass

def isForLoopEnd(binNode):
    return False

def writeForLoopEnd():
    return

def isAssignStmt(binNode):
    if (binNode.type == ops.EQ):
        return True

    return False

def getAssignStmtAsString(node):
    if (node.type == ops.ATTR):
        return node.attr
    elif (node.type == ops.ADD):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return leftString + " + " + rightString
    elif (node.type == ops.SUB):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return leftString + " - " + rightString
    elif (node.type == ops.MUL):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return leftString + " * " + rightString
    elif (node.type == ops.DIV):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return leftString + " / " + rightString
    elif (node.type == ops.EXP):
        leftString = getAssignStmtAsString(node.left)
        rightString = getAssignStmtAsString(node.right)
        return leftString + " ** " + rightString

    return "" #replace with sys.exit

def writeAssignStmt_Python(outputFile, binNode):
    writeCurrentNumTabsIn(outputFile)

    outputString = ""
    outputString += binNode.left.attr
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
            writeForLoopEnd()
            numTabsIn -= 1
        elif (isAssignStmt(astNode) == True):
            writeAssignStmt(astNode)

def main(SDL_Scheme):
    global setupFile, transformFile, decOutFile, assignInfo

    if ( (type(SDL_Scheme) is not str) or (len(SDL_Scheme) == 0) ):
        sys.exit("codegen.py:  sys.argv[1] argument (file name for SDL scheme) passed in was invalid.")

    keygen(SDL_Scheme)
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
    writeSDLToFiles(astNodes)

    setupFile.close()
    transformFile.close()
    decOutFile.close()

if __name__ == "__main__":
    main(sys.argv[1])
