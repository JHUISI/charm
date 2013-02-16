import sys, os

sys.path.extend(['../', '../sdlparser']) 

from SDLParser import *
from codegenConfig import *
import inlinePreprocessor as inlinePP

assignInfo = None
inputOutputVars = None
functionNameOrder = None
varNamesToFuncs_All = None
varNamesToFuncs_Assign = None
setupFile = None
userFuncsCPPFile = None
currentFuncName = NONE_FUNC_NAME
numTabsIn = 1
returnValues = {}
globalVarNames = []
lineNoBeingProcessed = 0
userFuncsList_CPP = []
CPP_varTypesLines = None
CPP_funcBodyLines = None

blindingFactors_NonLists = None
blindingFactors_Lists = None

currentFuncOutputVars = None
currentFuncNonOutputVars = None
SDLListVars = []
listVarsDeclaredInThisFunc = []
nonListVarsDeclaredInThisFunc = []
integerVars = []
starRef = ""# "*"
NOP_STATEMENT = "NOP"
INSERT_FUNC_NAME = ".insert("
UTIL_FUNC_NAME = "util"
DFA_UTIL_FUNC_NAME = "dfaUtil"
secretUtils = ['createPolicy', 'getAttributeList', 'calculateSharesDict', 'calculateSharesList', 'prune', 'getCoefficients', 'recoverCoefficientsDict', 'intersectionSubset']
secretUtilsWithGroup = ['calculateSharesDict', 'calculateSharesList', 'getCoefficients', 'recoverCoefficientsDict', 'intersectionSubset']
dfaUtils = ['hashToKey', 'accept', 'getAcceptState', 'getTransitions', 'getString']
# default unless specified otherwise by caller
transformOutputList = "transformOutputList" #None
preprocessTypes = Enum('listWithinListAssign', 'dotProductAssign', 'NoMatch')

varCount = 0


def preProcessCheck(binNode):
    global varCount
    listCheck = inlinePP.ListCheck(varCount)
    ASTVisitor(listCheck).preorder(binNode)
    if listCheck.isMatch():
        varCount = listCheck.getVarCount()
        getVarTypes()[TYPES_HEADER].update(listCheck.getNewVarTypes())
        #print("New types: ", getVarTypes()[TYPES_HEADER].keys())
        return (preprocessTypes.listWithinListAssign, listCheck.getNewNodes())
#    dotProdCheck = inlinePP.DotProdCheck(count)
#    ASTVisitor(dotProdCheck).preorder(binNode)
#    if dotProdCheck.isMatch():
#        return (preprocessTypes.dotProductAssign, dotProdCheck.getNewNodes())
    return (preprocessTypes.NoMatch, None)

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
    global setupFile

    cppImportLines = ""
    cppImportLines += "#include \"Charm.h\"\n"
    cppImportLines += "#include <iostream>\n"
    cppImportLines += "#include <sstream>\n"
    cppImportLines += "#include <string>\n"
    cppImportLines += "#include <list>\n"
    cppImportLines += "using namespace std;\n"
    #cppImportLines += "#define DEBUG  true\n"
    cppImportLines += "\n"

    setupFile.write(cppImportLines)

def addNumSignatures():
    global setupFile

    try:
        numSignatures = assignInfo[NONE_FUNC_NAME][numSignaturesVarName].getAssignNode().right
    except:
        return #sys.exit("addNumSignatures in codegen_CPP:  could not obtain number of signatures from SDL file.")

    setupFile.write("int " + str(numSignaturesVarName) + " = " + str(numSignatures) + ";\n\n")

def addNumSigners():
    global setupFile

    try:
        numSigners = assignInfo[NONE_FUNC_NAME][numSignersVarName].getAssignNode().right
    except:
        return #this value isn't necessary for all schemes

    setupFile.write("int " + str(numSignersVarName) + " = " + str(numSigners) + ";\n\n")

def addSecParam():
    global setupFile

    try:
        secParam = assignInfo[NONE_FUNC_NAME][secParamVarName].getAssignNode().right
    except:
        return #sys.exit("addSecParamin codegen_CPP:  couldn't obtain secparam number from SDL file.")

    setupFile.write("int " + str(secParamVarName) + " = " + str(secParam) + ";\n\n")

def addGlobalPairingGroupObject(groupParam):
    global setupFile

    setupFile.write("PairingGroup group(%s);\n\n" % groupParam) # TODO: make AES_SECURITY a command line parameter

def addBuiltinObjects():
    global setupFile
    
    bFuncs = set(getUsedBuiltinList()).intersection(secretUtils)
    # JAA: TODO is to add one for the DFA class in C++
    if len(bFuncs) > 0: setupFile.write("SecretUtil %s;\n\n" % UTIL_FUNC_NAME)
    
    dFuncs = set(getUsedBuiltinList()).intersection(dfaUtils)
    # JAA: TODO is to add one for the DFA class in C++
    if len(dFuncs) > 0: setupFile.write("DFA %s;\n\n" % DFA_UTIL_FUNC_NAME)
    

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

def getInputVariablesList(functionName):
    inputVariables = None

    try:
        inputVariables = assignInfo[functionName][inputKeyword].getVarDeps()
    except:
        sys.exit("getInputVariablesList in codegen.py:  could not obtain function's input variables from getVarDeps() on VarInfo obj.")

    return inputVariables

def makeTypeReplacementsForCPP(SDL_Type, isList=False):
    SDLTypeAsString = str(SDL_Type)

    if (SDLTypeAsString == "str"):
        return "string"
    if (SDLTypeAsString == "list"):
        return charmListType
    if (SDLTypeAsString == "pol"):
        return "Policy"
    if (SDLTypeAsString == "symmap"):
        return charmDictType
    if (SDLTypeAsString == "symmapZR"):
        return "CharmDictZR"    
    if (SDLTypeAsString == "listG1"):
        return "CharmListG1"
    if (SDLTypeAsString == "listG2"):
        return "CharmListG2"
    if (SDLTypeAsString == "listGT"):
        return "CharmListGT"
    if (SDLTypeAsString == "listZR"):
        return "CharmListZR"
    if (SDLTypeAsString == "listInt"):
        return "CharmListInt"
    if (SDLTypeAsString == "listStr"):
        return "CharmListStr"
    if (SDLTypeAsString == "metalistG1"):
        return "CharmMetaListG1"
    if (SDLTypeAsString == "metalistG2"):
        return "CharmMetaListG2"
    if (SDLTypeAsString == "metalistGT"):
        return "CharmMetaListGT"
    if (SDLTypeAsString == "metalistZR"):
        return "CharmMetaListZR"
    if (SDLTypeAsString == "metalistInt"):
        return "CharmMetaListInt"
    if (SDLTypeAsString == "metalist"):
        return "CharmMetaList"
    
    if ( (SDLTypeAsString == "G1") and (isList == True) ):
        return "CharmListG1"
    if ( (SDLTypeAsString == "G2") and (isList == True) ):
        return "CharmListG2"
    if ( (SDLTypeAsString == "GT") and (isList == True) ):
        return "CharmListGT"
    if ( (SDLTypeAsString == "ZR") and (isList == True) ):
        return "CharmListZR"

    return SDLTypeAsString

def getFinalVarType(varName, funcName, failSilently=False):
    return getVarTypeFromVarName(varName, funcName, failSilently)

def executeAddToListCPP(binNode):
    global CPP_funcBodyLines

    outputString = writeCurrentNumTabsToString()

    listNodes = None

    try:
        listNodes = binNode.listNodes
    except:
        sys.exit("executeAddToListCPP in codegen_CPP.py:  could not obtain binary node's list nodes; must be 2 of them (list, data item to add).")

    if (len(listNodes) != 2):
        sys.exit("executeAddToListCPP in codegen_CPP.py:  number of binary node's list nodes isn't 2; this must be the case (list, data item to add to it).")

    outputString += listNodes[0] + ".push_back(" + listNodes[1] + ");\n"

    CPP_funcBodyLines += outputString    

def writeFuncCall(binNode):
    global CPP_funcBodyLines

    outputString = writeCurrentNumTabsToString()

    if (str(binNode.attr) == ADD_TO_LIST):
        executeAddToListCPP(binNode)
        return

    outputString += binNode.attr + "("

    listNodes = None

    try:
        listNodes = binNode.listNodes
    except:
        sys.exit("writeFuncCall in codegen_CPP.py:  couldn't obtain listNodes for func call binary node; make sure that even if passing no arguments to function, you put \"None\" in the parentheses.")

    if (listNodes[0] != "None"):
        for listNode in listNodes:
            outputString += listNode + ", "
        lenString = len(outputString)
        outputString = outputString[0:(lenString - 2)]

    outputString += ");\n"

    CPP_funcBodyLines += outputString

def isFuncDeclVarAList(variableName, functionName):
    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(assignInfo, variableName)
    if (possibleVarInfoObj == None):
        return False

    assignNode = possibleVarInfoObj.getAssignNode()
    if (assignNode == None):
        return False

    assignNodeLeft = assignNode.left
    if (assignNodeLeft == None):
        return False

    if (str(assignNodeLeft).find(LIST_INDEX_SYMBOL) != -1):
        return True

    return False

# JAA:
def isFuncDeclVarAListAndSameType(variableName, functionName):
    (possibleFuncName, possibleVarInfoObj) = getVarNameEntryFromAssignInfo(assignInfo, variableName)
    if (possibleVarInfoObj == None):
        return False

    assignNode = possibleVarInfoObj.getAssignNode()
    if (assignNode == None):
        return False

    assignNodeLeft = assignNode.left
    if (assignNodeLeft == None):
        return False

    print("possibleVarInfoObj=", possibleVarInfoObj.getType())

    if (str(assignNodeLeft).find(LIST_INDEX_SYMBOL) != -1):
        return True

    return False


def writeFunctionDecl_CPP(outputFile, functionName):
    global currentFuncOutputVars, currentFuncNonOutputVars

    currentFuncOutputVars = []
    currentFuncNonOutputVars = []

    if (functionName in [verifyFuncName, membershipFuncName, batchVerifyFuncName, precheckFuncName]):
        outputString = "bool " + functionName + "("
    else:
        outputString = "void " + functionName + "("

    inputVariables = getInputVariablesList(functionName)
    outputVariables = getOutputVariablesList(functionName)

    for inputVariable in inputVariables:
        varIsAList = isFuncDeclVarAList(inputVariable, functionName)
        currentType = getFinalVarType(inputVariable, currentFuncName)
        if (currentType in [types.int]):
            outputString += makeTypeReplacementsForCPP(currentType) + " " + inputVariable + ", "
        else:
            outputString += makeTypeReplacementsForCPP(currentType, varIsAList) + " & " + inputVariable + ", "
        currentFuncOutputVars.append(inputVariable)
    
    # JAA: fix this to address user defined functions with one type
    for outputVariable in outputVariables:
        if (outputVariable in inputVariables):
            continue
        if ( (outputVariable != "True") and (outputVariable != "False") ):
            varIsAList = isFuncDeclVarAList(outputVariable, functionName)
            currentType = getFinalVarType(outputVariable, currentFuncName)
            if (currentType in [types.int]):
                outputString += makeTypeReplacementsForCPP(currentType) + " & " + outputVariable + ", "
            else:
                outputString += makeTypeReplacementsForCPP(currentType, varIsAList) + " & " + outputVariable + ", "
            currentFuncOutputVars.append(outputVariable)

    if ( (inputVariables != []) or (outputVariables != []) ):
        outputString = outputString[0:(len(outputString) - len(", "))]
    outputString += ")\n{\n"

    outputFile.write(outputString)

def writeFunctionDecl(functionName):
    global setupFile

    writeFunctionDecl_CPP(setupFile, functionName)

def writeFunctionEnd_CPP(outputFile, functionName):
    global returnValues, CPP_funcBodyLines

    if (functionName not in [verifyFuncName, membershipFuncName, batchVerifyFuncName, precheckFuncName]):
        CPP_funcBodyLines += "    return;\n}\n\n"
    elif (functionName == batchVerifyFuncName):
        CPP_funcBodyLines += "    return true;\n}\n\n"
    else:
        CPP_funcBodyLines += "}\n\n"

    outputFile.write(CPP_varTypesLines)
    outputFile.write(CPP_funcBodyLines)

def writeFunctionEnd(functionName):
    global setupFile

    writeFunctionEnd_CPP(setupFile, functionName)

def isFuncCall(binNode):
    if (binNode.type == ops.FUNC):
        return True

    return False

def isNOP(binNode):
    if (binNode.type == ops.NOP):
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

def replacePoundsWithBrackets(nameWithPounds, switchToInsert=False):
    if ( (type(nameWithPounds) is not str) or (len(nameWithPounds) == 0) ):
        sys.exit("replacePoundsWithBrackets in codegen.py:  problem with nameWithPounds parameter passed in.")

    nameSplit = nameWithPounds.split(LIST_INDEX_SYMBOL)
    if (len(nameSplit) == 1):
        return nameWithPounds

    nameToReturn = nameSplit[0]
    lenNameSplit = len(nameSplit)
    
    if switchToInsert:
        #print("DEBUG: JAA nameToReturn => ", nameToReturn)
        nums = nameSplit[1:]
        if len(nums) == 1:
            nameToReturn += ".insert(" + nums[0] + ", "
    else:
        for counter in range(0, (lenNameSplit - 1)):
            nameToReturn += "[" + nameSplit[counter + 1] + "]"

    return nameToReturn.replace("?","",1) #in case we're directly accessing list element (e.g., S[k-1])

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

def doesVarNeedStar(variable):
    variable = getRidOfAllListIndices(variable)

    return False

def writeMathStatement(leftSide, rightSide, opString):
    leftNeedsStar = doesVarNeedStar(leftSide)
    rightNeedsStar = doesVarNeedStar(rightSide)

    if ( (leftNeedsStar == True) and (rightNeedsStar == True) ):
        return groupObjName + "." + opString + "(*" + leftSide + ", *" + rightSide + ")"
    elif ( (leftNeedsStar == True) and (rightNeedsStar == False) ):
        return groupObjName + "." + opString + "(*" + leftSide + ", " + rightSide + ")"
    elif ( (leftNeedsStar == False) and (rightNeedsStar == True) ):
        return groupObjName + "." + opString + "(" + leftSide + ", *" + rightSide + ")"
    elif ( (leftNeedsStar == False) and (rightNeedsStar == False) ):
        return groupObjName + "." + opString + "(" + leftSide + ", " + rightSide + ")"

def processATTR_CPP(node, replacementsDict):
    returnString = processAttrOrTypeAssignStmt(node, replacementsDict)
    if (doesVarNeedStar(returnString)):
        return "*" + returnString
    else:
        return returnString

def getListOfAttrNamesFromConcatNode(node, replacementsDict, returnList):
    if (node.left.type not in [ops.ATTR, ops.CONCAT]):
        sys.exit("getListOfAttrNamesFromConcatNode in codegen_CPP.py in node.left:  concat nodes can only contain other concat nodes or attr nodes.")
    if (node.right.type not in [ops.ATTR, ops.CONCAT]):
        sys.exit("getListOfAttrNamesFromConcatNode in codegen_CPP.py in node.right:  concat nodes can only contain other concat nodes or attr nodes.")

    if (node.left.type == ops.CONCAT):
        getListOfAttrNamesFromConcatNode(node.left, replacementsDict, returnList)
    if (node.right.type == ops.CONCAT):
        getListOfAttrNamesFromConcatNode(node.right, replacementsDict, returnList)

    returnList.append(processATTR_CPP(node.left, replacementsDict))
    returnList.append(processATTR_CPP(node.right, replacementsDict))

def returnAllUpToLeftBrace(varName):
    leftBracePos = varName.find("[")
    if (leftBracePos == -1):
        return varName

    return varName[0:leftBracePos]

def areBothSidesStringVars(leftSide, rightSide):
    leftType = getFinalVarType(returnAllUpToLeftBrace(leftSide), currentFuncName, True)
    rightType = getFinalVarType(returnAllUpToLeftBrace(rightSide), currentFuncName, True)

    if (str(leftType) not in ["str", "listStr"]):
        return False

    if (str(rightType) not in ["str", "listStr"]):
        return False

    return True

def addGetTypeToAttrNode(inputString, variableType):
    #print("DEBUG: inputString=", inputString, ", variableType=", variableType)
    if (variableType == types.G1):
        return inputString + ".getG1()"

    if (variableType == types.G2):
        return inputString + ".getG2()"

    if (variableType == types.GT):
        return inputString + ".getGT()"

    if (variableType == types.ZR):
        return inputString + ".getZR()"
    
    if (variableType == types.symmapZR):
        return inputString

    if (variableType == types.list):
        return inputString + ".getList()"

    if (variableType in [types.str, types.int, types.listInt, types.listZR, types.listG1, types.listG2, types.listGT, types.metalistInt, types.metalistZR, types.metalistG1, types.metalistG2, types.metalistGT]):
        return inputString # + ".strPtr"
    
    print(variableType)
    print(inputString)
    
    sys.exit("addGetTypeToAttrNode in codegen_CPP.py:  variable type passed in is not one of the supported types.")

def exhaustSearchType(node, currentFuncName):
    if type(node) == str: return
    if Type(node) != ops.ATTR: return
    nodeParts = str(node).split(LIST_INDEX_SYMBOL)
    varName = nodeParts[0]
    _variableType = types.NO_TYPE
    if len(nodeParts) == 2: # pattern => var#ref1
        _rawType = searchForRawType(node, currentFuncName)
        #print("JAA-DEBUG2: rawType=", _rawType)
        if _rawType == types.NO_TYPE: _variableType = getFinalVarType(varName, currentFuncName)
        else: _variableType = _rawType
        #print("DEBUG: varName=", varName, ", type=", _variableType, ", currentFunc=", currentFuncName)
    elif len(nodeParts) == 3: # pattern => var#ref1#ref2
        _variableType = searchForRawType(node, currentFuncName)
    else: # last chance
        #print("DEBUG: exhaustSearchType -> handle case: ", node)
        _variableType = getVarTypeInfoRecursive(node) # getFinalVarType(str(node), currentFuncName)
        #print("DEBUG: getVarTypeInfoRecursive=", _variableType)
    #print("updated var type: ", _variableType, ", name: ", node, ", rawType=", getRawListTypes()) # JAA: added to find types in "insert" situations
    return _variableType

# TODO: this function needs refinement to handle all possible cases...
def searchForRawType(node, currentFuncName):
    name = str(node)
    if LIST_INDEX_END_SYMBOL in name:
        name = name[:-1]
    nodeParts = name.split(LIST_INDEX_SYMBOL)
    rawTypes = getRawListTypes()
    #print("rawTypes: ", rawTypes)
    key = nodeParts[0]
    typeDict = rawTypes.get(key)
    if typeDict != None:
        typeRef = typeDict[refType]
        typeInfo = typeDict[typeRef]
    else:
        return types.NO_TYPE
    if len(nodeParts) == 2:
        #print("2=typeInfo: ", typeInfo)
        return types[str(typeInfo)]
    elif len(nodeParts) == 3:
        lastKey = nodeParts[-1]
#        print("3=typeInfo: ", typeInfo, lastKey, name)
#        print("DEBUG: rawTypes=", rawTypes)
        if lastKey.isdigit() and type(typeInfo) == list and int(lastKey) < len(typeInfo): return typeInfo[ int(lastKey) ]
        elif type(typeInfo) == list: return typeInfo[0] # must be abstract reference
        else: return typeInfo # must be a concrete reference
    return types.NO_TYPE
    
def getCondStmtAsString_CPP(node, replacementsDict):
    if type(node) == str:
        return node
    
    if (node.type == ops.AND):
        leftSide = getCondStmtAsString_CPP(node.left, replacementsDict)
        rightSide = getCondStmtAsString_CPP(node.right, replacementsDict)
        return "( (" + leftSide + ") && (" + rightSide + ") )"
    elif (node.type == ops.EQ_TST):
        leftSide = getCondStmtAsString_CPP(node.left, replacementsDict)
        rightSide = getCondStmtAsString_CPP(node.right, replacementsDict)
        if (rightSide == "False"):
            rightSide = "false"
        elif (rightSide == "True"):
            rightSide = "true"
        if (areBothSidesStringVars(leftSide, rightSide) == True):
            return "( isEqual(" + leftSide + ", " + rightSide + ") )"
        else:
            return "( (" + leftSide + ") == (" + rightSide + ") )"
    elif (node.type == ops.NON_EQ_TST):
        leftSide = getCondStmtAsString_CPP(node.left, replacementsDict)
        rightSide = getCondStmtAsString_CPP(node.right, replacementsDict)
        if (rightSide == "False"):
            rightSide = "false"
        elif (rightSide == "True"):
            rightSide = "true"

        if (areBothSidesStringVars(leftSide, rightSide) == True):
            return "( isNotEqual(" + leftSide + ", " + rightSide + ") )"
        else:
            return "( (" + leftSide + ") != (" + rightSide + ") )"
    elif (node.type == ops.ATTR):
        returnString = processAttrOrTypeAssignStmt(node, replacementsDict)
        return returnString
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        variableTypeForFuncNode = getFinalVarType(nodeName, currentFuncName, True)
        
        variableName = nodeName
        if (nodeName == INIT_FUNC_NAME):
            return groupObjName + "." + INIT_FUNC_NAME + "(" + str(node.listNodes[0]) + "_t)"
        elif (nodeName == ISMEMBER_FUNC_NAME):
            funcOutputString = groupObjName + "." + nodeName + "("
        elif (nodeName == INTEGER_FUNC_NAME):
            funcOutputString = "int("
        elif (nodeName == STRING_TO_INT):
            funcOutputString = STRING_TO_INT + "(" + groupObjName + ", " 
        elif (nodeName in builtInTypes.keys()) and (nodeName in secretUtils):
            funcOutputString = UTIL_FUNC_NAME + "." + nodeName + "("
            if nodeName in secretUtilsWithGroup:
                funcOutputString += groupObjName + ", "
        elif (nodeName in builtInTypes.keys()) and (nodeName in dfaUtils):
            funcOutputString = DFA_UTIL_FUNC_NAME + "." + nodeName + "("
        else:
            funcOutputString = nodeName + "("
        
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getCondStmtAsString_CPP(listNodeInFunc, replacementsDict)
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
        
    return
    
def getAssignStmtAsString_CPP(node, replacementsDict, variableName, leftSideNameForInit=None):
    global userFuncsCPPFile, userFuncsList_CPP

    variableType = types.NO_TYPE
    
    if (variableName != None) and INSERT_FUNC_NAME not in variableName:
        variableType = getFinalVarType(variableName, currentFuncName)
    elif str(node).find(LIST_INDEX_SYMBOL) != -1:
        # in case it is being inserted, we want to find the type of the right variable name
        variableType = exhaustSearchType(node, currentFuncName)
        
    if (type(node) is str):
        return processStrAssignStmt(node, replacementsDict)

    elif ( (node.type == ops.ATTR) and (str(node.attr) == smallExp) ):
        return "SmallExp(80)"
    
    elif ( (node.type == ops.ATTR) or (node.type == ops.TYPE) ):
        returnString = processAttrOrTypeAssignStmt(node, replacementsDict)
        # JAA: added clause to look for direct references to lists and replace with the ".get<Type>()" extension
        if leftSideNameForInit != None and str(node).find(LIST_INDEX_SYMBOL) != -1: # if it appears on rhs of an assignment stmt
            varName2 = str(node).split(LIST_INDEX_SYMBOL)[0]
            varIsAList = isFuncDeclVarAList(varName2, currentFuncName)
            variableType = getVarTypeInfoRecursive(node)
            if varIsAList:
                varT = searchForRawType(node, currentFuncName)
                #print("varT=", varT, ", nodeName=", node)
                if varT in [types.listInt, types.listZR, types.listG1, types.listG2, types.listGT, types.metalistZR, types.metalistG1, types.metalistG2, types.metalistGT]:
                    pass
                else:
                    returnString = addGetTypeToAttrNode(returnString, variableType)
            else:
                pass # do nothing to returnString since the type is not embedded in a 'list'
        elif str(node).find(LIST_INDEX_SYMBOL) != -1 and variableName != None and INSERT_FUNC_NAME in variableName: # JAA: if list ref appears on rhs inside a "insert(" call. 
            returnString = addGetTypeToAttrNode(returnString, variableType) # getFinalVarType(str(node), currentFuncName) 
        if transformOutputList != None and (str(node).startswith(transformOutputList) == True):
            returnString = addGetTypeToAttrNode(returnString, variableType)

        if node.isNegated():
            returnString = returnString[1:] # remove the preceding "-" symbol
        returnThisString = returnString
        
        if node.isNegated() and not returnString.isdigit(): # now wrap in negate call.
            return groupObjName + ".neg" + "(" + returnThisString + ")"
        elif node.isNegated() and returnString.isdigit():
            return "-" + returnThisString
        else:
            return returnThisString

    elif (node.type == ops.ADD):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(leftSide, rightSide, "add")

    elif (node.type == ops.SUB):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(leftSide, rightSide, "sub")

    elif (node.type == ops.MUL):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(leftSide, rightSide, "mul")

    elif (node.type == ops.DIV):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(leftSide, rightSide, "div")

    elif (node.type == ops.EXP):
        leftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        rightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(leftSide, rightSide, "exp")  

    elif (node.type == ops.CONCAT):
        concatOutputString = "("
        for listNode in node.listNodes:
            concatOutputString += elementName + "(" + getAssignStmtAsString_CPP(listNode, replacementsDict, variableName, leftSideNameForInit) + ") + "
        concatOutputString = concatOutputString[0:(len(concatOutputString) - len(" + "))]
        concatOutputString += ")"
        return concatOutputString
    elif (node.type == ops.STRCONCAT):
        strconcatOutputString = "("
        for listNode in node.listNodes:
            if (doesVarNeedStar(listNode) == True):
                strconcatOutputString += "*" + getAssignStmtAsString_CPP(listNode, replacementsDict, variableName, leftSideNameForInit) + " + "
            else:
                strconcatOutputString += getAssignStmtAsString_CPP(listNode, replacementsDict, variableName, leftSideNameForInit) + " + "
        strconcatOutputString = strconcatOutputString[0:(len(strconcatOutputString) - len(" + "))]
        strconcatOutputString += ")"
        return strconcatOutputString

    elif ( (node.type == ops.LIST) ): #or ( (node.type == ops.EXPAND) and (variableType == types.list) ) ):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  encountered node of type ops.LIST, but variableName parameter passed in is of type None.")
        listOutputString = ""
        for listIndex, listNode in enumerate(node.listNodes):
            listOutputString += writeCurrentNumTabsToString()
# JAA: modified append to use insert instead
            listOutputString += variableName + ".insert("
            listNodeAsString = getAssignStmtAsString_CPP(listNode, replacementsDict, variableName, leftSideNameForInit)
            listOutputString += str(listIndex) + ", " + listNodeAsString + ");\n"
        return listOutputString
    elif ( (node.type == ops.SYMMAP) ): #or ( (node.type == ops.EXPAND) and (variableType == types.symmap) ) ):
        if (variableName == None):
            sys.exit("getAssignStmtAsString_CPP in codegen.py:  encountered node of type ops.SYMMAP, but variable name parameter passed in is of None type.")
        symmapOutputString = ""
        symmapOutputString += ";\n"
        for symmapNode in node.listNodes:
            symmapOutputString += writeCurrentNumTabsToString()
            symmapOutputString += variableName + ".set(\""
            symmapNodeAsString = getAssignStmtAsString_CPP(symmapNode, replacementsDict, variableName, leftSideNameForInit)
            symmapOutputString += "\":" + variableName + ");\n"
        return symmapOutputString
    elif (node.type == ops.RANDOM):
        randomGroupType = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        randomOutputString = groupObjName + ".random(" + randomGroupType + "_t)"
        return randomOutputString
    elif (node.type == ops.HASH):
        hashMessage = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        hashGroupType = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        hashOutputString = groupObjName + ".hashListTo" + (str(hashGroupType)).upper() + "(" + hashMessage + ")"
        return hashOutputString
    elif (node.type == ops.PAIR):
        pairLeftSide = getAssignStmtAsString_CPP(node.left, replacementsDict, variableName, leftSideNameForInit)
        pairRightSide = getAssignStmtAsString_CPP(node.right, replacementsDict, variableName, leftSideNameForInit)
        return writeMathStatement(pairLeftSide, pairRightSide, "pair")
    elif (node.type == ops.FUNC):
        nodeName = applyReplacementsDict(replacementsDict, getFullVarName(node, False))
        nodeName = replacePoundsWithBrackets(nodeName)
        variableTypeForFuncNode = getFinalVarType(variableName, currentFuncName, True)

        if (nodeName == INIT_FUNC_NAME):
            if variableName == None: 
                return
            elif (variableName.startswith(DOT_PROD_WORD) == True):
                return groupObjName + "." + INIT_FUNC_NAME + "(" + str(leftSideNameForInit) + ", 1)"
            elif (variableName.startswith(SUM_PROD_WORD) == True):
                return groupObjName + "." + INIT_FUNC_NAME + "(" + str(leftSideNameForInit) + ", 0)"
            elif (str(variableTypeForFuncNode) == "str"):
                return variableName + " = \"\""
            elif INSERT_FUNC_NAME in variableName and types[str(node.listNodes[0])] in standardTypes:
                return groupObjName + "." + INIT_FUNC_NAME + "(" + str(node.listNodes[0]) + "_t)"
            else:
                return "//"
        elif (nodeName == ISMEMBER_FUNC_NAME):
            funcOutputString = groupObjName + "." + nodeName + "("
        elif (nodeName == INTEGER_FUNC_NAME):
            funcOutputString = "int("
        elif (nodeName == STRING_TO_INT):
            funcOutputString = STRING_TO_INT + "(" + groupObjName + ", " 
        elif (nodeName == LEN_FUNC_NAME):
             if (len(node.listNodes) != 1):
                 sys.exit("getAssignStmtAsString_CPP in codegen_CPP.py:  len() function called, but either less than or more than one parameter was passed in (only one parameter can be passed in for len().")
             nameOfVarForLen = getAssignStmtAsString_CPP(node.listNodes[0], replacementsDict, variableName, leftSideNameForInit)
             return nameOfVarForLen + ".length()"
        elif (nodeName == STR_KEYS_FUNC_NAME):
             if (len(node.listNodes) != 1):
                 sys.exit("getAssignStmtAsString_CPP in codegen_CPP.py:  strkeys() function called, but either less than or more than one parameter was passed in (only one parameter can be passed in for strkeys().")
             nameOfVarForLen = getAssignStmtAsString_CPP(node.listNodes[0], replacementsDict, variableName, leftSideNameForInit)
             return nameOfVarForLen + ".strkeys()"
        elif (nodeName in builtInTypes.keys()) and (nodeName in secretUtils):
            funcOutputString = UTIL_FUNC_NAME + "." + nodeName + "("
            if nodeName in secretUtilsWithGroup:
                funcOutputString += groupObjName + ", "            
        elif (nodeName in builtInTypes.keys()) and (nodeName in dfaUtils):
            funcOutputString = DFA_UTIL_FUNC_NAME + "." + nodeName + "("
        else:
            funcOutputString = nodeName + "("
        
        for listNodeInFunc in node.listNodes:
            listNodeAsString = getAssignStmtAsString_CPP(listNodeInFunc, replacementsDict, variableName, leftSideNameForInit)
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
    
#    print("Current Node: ", node)
#    print("Type: ", node.type)
    assert False,"getAssignStmtAsString_CPP in codegen.py:  unsupported node type detected."
    return

def isVarInSDLListVars(varName):
    for listVar in SDLListVars:
        newListVarName = listVar
        listSymIndexPos = newListVarName.find(LIST_INDEX_SYMBOL)
        if (listSymIndexPos != -1):
            newListVarName = newListVarName[0:listSymIndexPos]
        if (varName == newListVarName):
            return True

    return False

def getCPPAsstStringForExpand(node, variableName, replacementsDict):
    global CPP_varTypesLines

    outputString = ""
    outputString += "\n"

    variableType = getFinalVarType(variableName, currentFuncName)
    counter = -1

    for listNode in node.listNodes:
        counter += 1
        listNodeName = applyReplacementsDict(replacementsDict, listNode)
        listNodeName = replacePoundsWithBrackets(listNodeName)
        listNodeType = getFinalVarType(listNodeName, currentFuncName)
        if (listNodeType == types.NO_TYPE):
            print("variable=", variableName)
            sys.exit("getCPPAsstStringForExpand in codegen.py:  could not obtain one of the types for the variable names included in the expand node.")
        outputString += writeCurrentNumTabsToString()

        if (isVarInSDLListVars(listNodeName) == True):
            CPP_varTypesLines += getVarDeclForListVar(listNodeName)
        else:
            #CPP_varTypesLines += "\t" + makeTypeReplacementsForCPP(listNodeType) + " " + listNodeName + ";\n"
            CPP_varTypesLines += "    " + makeTypeReplacementsForCPP(listNodeType) + " " + listNodeName + ";\n"

        outputString += listNodeName + " = "

        outputString += variableName + "[" + str(counter) + "]"

        if (variableType == types.list):
            outputString += "."
            if (isVarInSDLListVars(listNodeName) == True):
                if (listNodeType in [types.G1, types.listG1]): # TODO: JAA revisit
                    outputString += "getListG1()"
                elif (listNodeType == types.G2):
                    outputString += "getListG2()"
                elif (listNodeType == types.GT):
                    outputString += "getListGT()"
                elif (listNodeType == types.ZR):
                    outputString += "getListZR()"
                elif (listNodeType == types.list):
                    outputString += "getList()"
                elif (listNodeType in [types.str, types.listStr]):
                    outputString += "getListStr()"
                else:
                    print(node)
                    print(variableName)
                    print(listNodeName)
                    print(listNodeType)
                    sys.exit("getCPPAsstStringForExpand in codegen.py:  one of the types of the listNodes is not one of the supported types (G1, G2, GT, ZR, string or list types)")
            else:
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
                elif (listNodeType == types.listStr):
                    outputString += "getListStr()"
                elif (listNodeType == types.listInt):
                    outputString += "getListInt()"                    
                else:
                    print("listNodeType: ", listNodeType)
                    sys.exit("getCPPAsstStringForExpand in codegen.py:  one of the types of the listNodes is not one of the supported types (G1, G2, GT, ZR, or string), and is not a list.")

        outputString += ";\n"

    return outputString

def getVarDeclForListVar(variableName):
    listSymbolLoc = variableName.find(LIST_INDEX_SYMBOL)
    if (listSymbolLoc != -1):
        trueVarName = variableName[0:listSymbolLoc]
    else:
        trueVarName = variableName

    outputString_Types = ""

    listVarType = getFinalVarType(trueVarName, currentFuncName)

    if (listVarType == types.G1):
        outputString_Types += "    CharmListG1 " + trueVarName + ";\n"
    elif (listVarType == types.G2):
        outputString_Types += "    CharmListG2 " + trueVarName + ";\n"
    elif (listVarType == types.GT):
        outputString_Types += "    CharmListGT " + trueVarName + ";\n"
    elif (listVarType == types.ZR):
        outputString_Types += "    CharmListZR " + trueVarName + ";\n"
    elif (listVarType in [types.int, types.listInt]):
        outputString_Types += "    CharmListInt " + trueVarName + ";\n"
    elif (listVarType == types.list):
        outputString_Types += "    CharmList " + trueVarName + ";\n"
    elif (listVarType == types.pol):
        outputString_Types += "    Policy " + trueVarName + ";\n"        
    else:
        outputString_Types += "    NO TYPE FOUND FOR " + trueVarName + "\n"
        print("DEBUG: trueVarName=", trueVarName, ", type=", listVarType)

    return outputString_Types

def getRidOfAllListIndices(variableName):
    loc = variableName.find(LIST_INDEX_SYMBOL)
    if (loc == -1):
        return variableName

    loc = variableName.find(LIST_INDEX_SYMBOL)
    return variableName[0:loc]

def isInitCall(binNode):
    if ( (str(binNode).find(":= init(") != -1) or (str(binNode).find(":=init(") != -1) ):
        return True

    return False

# TODO: clean-up need for "*"
def writeAssignStmt_CPP(outputFile, binNode):
    global CPP_varTypesLines, CPP_funcBodyLines, setupFile, currentFuncNonOutputVars, SDLListVars, integerVars
    global listVarsDeclaredInThisFunc, nonListVarsDeclaredInThisFunc

    if (str(binNode) == RETURN_STATEMENT):
        CPP_funcBodyLines += writeCurrentNumTabsToString()
        CPP_funcBodyLines += "return;\n"
        return
    elif(str(binNode) == NOP_STATEMENT):
        CPP_funcBodyLines += "\t\t//NOP;\n"
        return
    
    variableName = getFullVarName(binNode.left, False)
    variableNameWOListIndices = getRidOfAllListIndices(getFullVarName(binNode.left, True))

    if (variableName == inputKeyword):
        return

    if ( (variableName.find(LIST_INDEX_SYMBOL) != -1) and (variableName not in SDLListVars) ):
        SDLListVars.append(variableName)

    if (variableName == outputKeyword):
        if ( (str(binNode) == "output := True") or (str(binNode) == "output := true") ):
            trueOutputString = writeCurrentNumTabsToString()
            trueOutputString += "return true;\n"
            CPP_funcBodyLines += trueOutputString
            return
        elif ( (str(binNode) == "output := False") or (str(binNode) == "output := false") ):
            falseOutputString = writeCurrentNumTabsToString()
            falseOutputString += "return false;\n"
            CPP_funcBodyLines += falseOutputString
            return
        else:
            return

    outputString_Types = ""
    outputString_Body = ""

    if (binNode.right.type != ops.LIST):
        outputString_Body += writeCurrentNumTabsToString()

    if (variableNameWOListIndices not in currentFuncOutputVars):
        if (variableNameWOListIndices not in currentFuncNonOutputVars):
            currentFuncNonOutputVars.append(variableNameWOListIndices)

    variableType = getFinalVarType(variableName, currentFuncName)

    if ( (variableName.find(LIST_INDEX_SYMBOL) == -1) and (binNode.right.type != ops.EXPAND) and (variableName not in nonListVarsDeclaredInThisFunc) ):
        if ( (variableName not in currentFuncOutputVars) and (variableType != types.int) ):
            outputString_Types += "    " + makeTypeReplacementsForCPP(variableType) + " " + starRef
        elif ( (variableName not in currentFuncOutputVars) and (variableType == types.int) ):
            outputString_Types += "    int "

    if ( (variableName in SDLListVars) and (variableNameWOListIndices not in currentFuncOutputVars) and (variableNameWOListIndices not in listVarsDeclaredInThisFunc) ):
        outputString_Types += getVarDeclForListVar(variableName)
        listVarsDeclaredInThisFunc.append(variableNameWOListIndices)

    if ( (binNode.right.type != ops.EXPAND) and (variableName not in currentFuncOutputVars) and (variableName not in SDLListVars) and (variableName not in nonListVarsDeclaredInThisFunc) ):
        if (variableType == types.int):
            outputString_Types += variableName + " = 0;\n"
        else:
            if (variableName.startswith(DOT_PROD_WORD) == True):
                outputString_Types += variableName + " = " + groupObjName + "." + INIT_FUNC_NAME + "(" + makeTypeReplacementsForCPP(variableType) + "_t, 1);\n"
            elif (variableName.startswith(SUM_PROD_WORD) == True):
                outputString_Types += variableName + " = " + groupObjName + "." + INIT_FUNC_NAME + "(" + makeTypeReplacementsForCPP(variableType) + "_t, 0);\n"
            elif variableType in [types.str, types.listStr, types.pol, types.list, types.listInt, types.listZR, types.listG1, types.listG2, types.listGT, types.metalist, types.metalistInt, types.metalistZR, types.metalistG1, types.metalistG2, types.metalistGT, types.symmapZR]:
                outputString_Types += variableName + ";\n"
            else:
                outputString_Types += variableName + " = " + groupObjName + "." + INIT_FUNC_NAME + "(" + makeTypeReplacementsForCPP(variableType) + "_t);\n"
        nonListVarsDeclaredInThisFunc.append(variableName)

    variableNamePounds = replacePoundsWithBrackets(variableName)
    variableLen = len(variableName.split(LIST_INDEX_SYMBOL))
    #print("DEBUG: variableNamePounds=", variableNamePounds, ", variableName=", variableName, ", variableLen=", variableLen)
    skipTheRest = False
    if (variableName != variableNamePounds) and variableLen < 3:
        variableNamePound = replacePoundsWithBrackets(variableName, True)
        #print("DEBUG: variableNamePound=", variableNamePound, ", variableName=", variableName)
        if(binNode.right.type != ops.LIST):
            rhsAssignment = getAssignStmtAsString_CPP(binNode.right, None, variableNamePound, None)
        else:
            rhsAssignment = getAssignStmtAsString_CPP(binNode.right, None, variableNamePound, None)
            #print("DEBUG: variableNamePound='", variableNamePound, "', rhsAssignment='", rhsAssignment, "'")
        outputString_Body += variableNamePound + rhsAssignment + ");\n"
        skipTheRest = True

    if not skipTheRest:    
        if ( (variableType == types.int) and (variableNamePounds not in integerVars) ):
            integerVars.append(variableNamePounds)
    
        leftSideNameForInit = None
        if ( (binNode.right.type != ops.EXPAND) and (binNode.right.type != ops.LIST) ):
            if ( (variableNamePounds in currentFuncOutputVars) or (variableName in SDLListVars) or (variableType == types.int) ):
                leftSideNameForInit = variableNamePounds
                if (isInitCall(binNode) == False):
                    outputString_Body += variableNamePounds  
            else:
                leftSideNameForInit = starRef + variableNamePounds
                if (isInitCall(binNode) == False):
                    outputString_Body += starRef + variableNamePounds        
            
        if ( (isInitCall(binNode) == False) and (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
            outputString_Body += " = "   
    
        outputString_Body += getAssignStmtAsString_CPP(binNode.right, None, variableNamePounds, leftSideNameForInit)
         
        if ( (binNode.right.type != ops.LIST) and (binNode.right.type != ops.SYMMAP) and (binNode.right.type != ops.EXPAND) ):
            outputString_Body += ";\n"
        
    CPP_varTypesLines += outputString_Types
    CPP_funcBodyLines += outputString_Body

def writeAssignStmt(binNode):
    global setupFile    
    print("DEBUG: ", binNode)
    # inline SDL assignment pre-processor
    resultPreType, binNodeList = preProcessCheck(binNode)
    if resultPreType == preprocessTypes.listWithinListAssign:
        for binNode2 in binNodeList:
            writeAssignStmt_CPP(setupFile, binNode2)            
    elif resultPreType == preprocessTypes.dotProductAssign:
        pass # TODO: writeAssignStmt on each element in the binNodeList
    else:
        writeAssignStmt_CPP(setupFile, binNode)

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
        userFuncsOutputString += "    cout << " + errorFuncArgString + " << endl;\n"
        userFuncsOutputString += "    return;\n"
        userFuncsOutputString += "}\n\n"
        userFuncsCPPFile.write(userFuncsOutputString)

def writeElseStmt_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"
    outputString += writeCurrentNumTabsToString()

    if (binNode.left == None):
        outputString += "else\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
    else:
        #print("DEBUG: condition=", binNode.left)
        outputString += "else if ( \n" 
        outputString += getCondStmtAsString_CPP(binNode.left, None) #getAssignStmtAsString_CPP(binNode.left, None, None)
        outputString += " )\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"

    CPP_funcBodyLines += outputString

def writeIfStmt_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    # JAA: fix this
    #print("DEBUG: condition=", binNode.left)
    outputString += "if ( "
    outputString += getCondStmtAsString_CPP(binNode.left, None)
    outputString += " )\n"
    outputString += writeCurrentNumTabsToString()
    outputString += "{\n"

    CPP_funcBodyLines += outputString

def writeForLoopDecl_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
        
    if ( (binNode.type == ops.FOR) or (binNode.type == ops.FORINNER) ):
        outputString += "for (int "
        currentLoopIncVarName = getAssignStmtAsString_CPP(binNode.left.left, None, None)
        outputString += currentLoopIncVarName + " = "
        outputString += getAssignStmtAsString_CPP(binNode.left.right, None, None)
        outputString += "; " + currentLoopIncVarName + " < "
        outputString += getAssignStmtAsString_CPP(binNode.right, None, None)
        outputString += "; " + currentLoopIncVarName + "++)\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
    elif (binNode.type == ops.FORALL): # JAA: fix this
        theVarTypes = getVarTypes()[currentFuncName]

        curLoopVarName = getAssignStmtAsString_CPP(binNode.left.right, None, None)
        varNameTypeObj = theVarTypes.get(curLoopVarName)
        if varNameTypeObj != None:
            if varNameTypeObj.getRefType() == types.str:
                outputString += "CharmListStr " + curLoopVarName + KeysListSuffix_CPP + " = " + curLoopVarName + ".strkeys();\n"
                curLoopIncVarType = "string"
            elif varNameTypeObj.getRefType() == types.int:
                outputString += "CharmListInt " + curLoopVarName + KeysListSuffix_CPP + " = " + curLoopVarName + ".keys();\n"
                curLoopIncVarType = "int"
            else:
                outputString += str(varNameTypeObj.getRefType()) + " " + curLoopVarName + ";\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "int " + curLoopVarName + ListLengthSuffix_CPP + " = " + curLoopVarName + ".length();\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "for (int "
        curLoopIncVarName = getAssignStmtAsString_CPP(binNode.left.left, None, None)
        outputString += curLoopIncVarName + TempLoopVar_CPP + " = 0; " + curLoopIncVarName + TempLoopVar_CPP + " < " + curLoopVarName + ListLengthSuffix_CPP + "; " + curLoopIncVarName + TempLoopVar_CPP + "++)\n"
        outputString += writeCurrentNumTabsToString()
        outputString += "{\n"
        #outputString += writeCurrentNumTabsToString() + "\t"
        outputString += writeCurrentNumTabsToString() + "    "
        outputString += curLoopIncVarType + " " + curLoopIncVarName + " = " + curLoopVarName + KeysListSuffix_CPP + "[" + curLoopIncVarName + TempLoopVar_CPP + "];\n"
    else:
        sys.exit("writeForLoopDecl_CPP in codegen.py:  encounted node that is neither type ops.FOR nor ops.FORALL (unsupported).")

    CPP_funcBodyLines += outputString

def writeErrorFunc(binNode):
    global setupFile

    writeErrorFunc_CPP(setupFile, binNode)

def writeElseStmtDecl(binNode):
    global setupFile

    writeElseStmt_CPP(setupFile, binNode)

def writeIfStmtDecl(binNode):
    global setupFile

    writeIfStmt_CPP(setupFile, binNode)

def writeForLoopEnd_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    CPP_funcBodyLines += outputString

def writeForLoopEnd(binNode):
    global setupFile

    writeForLoopEnd_CPP(setupFile, binNode)

def writeIfStmtEnd(binNode):
    global setupFile

    writeIfStmtEnd_CPP(setupFile, binNode)

def writeIfStmtEnd_CPP(outputFile, binNode):
    global CPP_funcBodyLines

    outputString = ""
    outputString += writeCurrentNumTabsToString()
    outputString += "}\n"

    CPP_funcBodyLines += outputString

def writeForLoopDecl(binNode):
    global setupFile

    writeForLoopDecl_CPP(setupFile, binNode)

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

    varName = getFullVarName(binNode.left, False)

    #if (varName.find(LIST_INDEX_SYMBOL) != -1):
        #sys.exit("addTypeDeclToGlobalVars in codegen.py:  variable name in types section has # sign in it.")

    varName = getVarNameWithoutIndices(binNode.left)

    if (varName not in varNamesToFuncs_Assign):
        return

    if ( (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
        globalVarNames.append(varName)

def writeGlobalVars_CPP(outputFile):
    return

def writeGlobalVars():
    writeGlobalVars_CPP(setupFile)

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
    global currentFuncName, numTabsIn, setupFile, lineNoBeingProcessed
    global CPP_varTypesLines, CPP_funcBodyLines, listVarsDeclaredInThisFunc, nonListVarsDeclaredInThisFunc

    for astNode in astNodes:
        lineNoBeingProcessed += 1
        processedAsFunctionStart = False

        if (isFunctionStart(astNode) == True):
            currentFuncName = getFuncNameFromBinNode(astNode)
            writeFunctionDecl(currentFuncName)
            CPP_varTypesLines = ""
            CPP_funcBodyLines = ""
            listVarsDeclaredInThisFunc = []
            nonListVarsDeclaredInThisFunc = []
            processedAsFunctionStart = True
        elif (isFunctionEnd(astNode) == True):
            writeFunctionEnd(currentFuncName)
            currentFuncName = NONE_FUNC_NAME
        elif (isTypesStart(astNode) == True):
            currentFuncName = TYPES_HEADER
        elif (isTypesEnd(astNode) == True):
            currentFuncName = NONE_FUNC_NAME

        if (currentFuncName == NONE_FUNC_NAME):
            continue

        if (currentFuncName == TYPES_HEADER):
            addTypeDeclToGlobalVars(astNode)
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
        elif (isNOP(astNode) == True):
            writeAssignStmt(astNode)
        else:
            print("BinNode: ", astNode)
            sys.exit("writeSDLToFiles in codegen.py:  unrecognized type of statement in SDL.")

def getStringOfFirstFuncArgs(argsToFirstFunc):
    if (type(argsToFirstFunc) is not list):
        sys.exit("getStringOfFirstFuncArgs in codegen_CPP.py:  argsToFirstFunc is not of type list.")

    if (len(argsToFirstFunc) == 0):
        return ""

    outputString = ""

    for argName in argsToFirstFunc:
        try:
            argNameAsStr = str(argName)
        except:
            sys.exit("getStringOfFirstFuncArgs in codegen_CPP.py:  could not convert one of the argument names to a string.")

        outputString += str(argName) + ", "

    lenOutputString = len(outputString)
    outputString = outputString[0:(lenOutputString - len(", "))]

    return outputString

def checkNumUserSuppliedArgs(userSuppliedArgs, funcName):
    try:
        inputVariables = assignInfo[funcName][inputKeyword].getVarDeps()
    except:
        sys.exit("checkNumUserSuppliedArgs in codegen_CPP.py:  could not obtain the input line for function currently being processed.")

    if (len(userSuppliedArgs) != len(inputVariables)):
        sys.exit("checkNumUserSuppliedArgs in codegen_CPP.py:  error in number of user-supplied args for function currently being processed.")

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

def writeMainFuncs():
    writeMainFuncOfSetup()

def getGlobalVarNames():
    global globalVarNames

    for varName in varNamesToFuncs_All:
        listForThisVar = varNamesToFuncs_All[varName]
        if (len(listForThisVar) == 0):
            sys.exit("getGlobalVarNames in codegen_CPP.py:  list extracted from varNamesToFuncs_All for current variable is empty.")

        if (len(listForThisVar) <= 1):
            continue
        if ( (varName not in globalVarNames) and (varName in varNamesToFuncs_Assign) and (varName != inputKeyword) and (varName != outputKeyword) and (varName not in inputOutputVars) ):
            globalVarNames.append(varName)

def addGetGlobalsToUserFuncs():
    global userFuncsCPPFile

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

def write_Main_Function():
    global setupFile

    outputString = "int main()\n{\n    return 0;\n}\n"
    setupFile.write(outputString)

def codegen_CPP_main(inputSDLScheme, outputFileName, groupParam='AES_SECURITY'):
    global setupFile, assignInfo, varNamesToFuncs_All
    global varNamesToFuncs_Assign, inputOutputVars, userFuncsCPPFile, functionNameOrder
    global blindingFactors_NonLists, blindingFactors_Lists

    parseFile2(inputSDLScheme, False, True)

    astNodes = getAstNodes()
    assignInfo = getAssignInfo()
    inputOutputVars = getInputOutputVars()
    functionNameOrder = getFunctionNameOrder()
    varNamesToFuncs_All = getVarNamesToFuncs_All()
    varNamesToFuncs_Assign = getVarNamesToFuncs_Assign()

    setupFile = open(outputFileName, 'w')
    userFuncsCPPFile = open("userFuncsCPPFile.h", 'w')

    getGlobalVarNames()
    addImportLines()
    addNumSignatures()
    addNumSigners()
    addSecParam()
    addGlobalPairingGroupObject(groupParam)
    addBuiltinObjects()
    writeSDLToFiles(astNodes)
    write_Main_Function()

    setupFile.close()
    userFuncsCPPFile.close()

if __name__ == "__main__":
    lenSysArgv = len(sys.argv)

    if (lenSysArgv != 3):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of input SDL file] [name of output C++ file]")

    if ( (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of input SDL file] [name of output C++ file]")

    codegen_CPP_main(sys.argv[1], sys.argv[2])
