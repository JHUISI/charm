import sys, os

sys.path.extend(['../../', '../../sdlparser'])

from SDLParser import *

#ORIGINAL_LOOP_VAR_NAME = "originalLoopVarName"
GET_STRING_SUFFIX = "GetStringSuffix"
reservedVarNameNumber = 0
RESERVED_VAR_NAME = "resVarName"

def hasPairingsSomewhereRecursive(astNode, pairingsList):
    if (astNode.left != None):
        hasPairingsSomewhereRecursive(astNode.left, pairingsList)

    if (astNode.right != None):
        hasPairingsSomewhereRecursive(astNode.right, pairingsList)

    if (astNode.type == ops.PAIR):
        pairingsList.append(astNode)

def hasPairingsSomewhere(astNode):
    pairingsList = []
    hasPairingsSomewhereRecursive(astNode, pairingsList)
    if (len(pairingsList) == 0):
        return False

    return True

def hasPairingsMixedWithNonExpCalcsRecursive(astNode, listOfAttrNodes):
    if ( (astNode.left != None) and (astNode.left.type != ops.PAIR) ):
        hasPairingsMixedWithNonExpCalcsRecursive(astNode.left, listOfAttrNodes)

    if ( (astNode.right != None) and (astNode.right.type != ops.PAIR) ):
        hasPairingsMixedWithNonExpCalcsRecursive(astNode.right, listOfAttrNodes)

    if (astNode.type == ops.ATTR):
        listOfAttrNodes.append(astNode)

def hasPairingsMixedWithNonExpCalcs(astNode):
    if (astNode.type != ops.EQ):
        return False

    if (hasPairingsSomewhere(astNode) == False):
        return False

    astNodeValue = astNode.right

    if (astNodeValue.type == ops.PAIR): #only one pairing
        return False

    if (astNodeValue.type == ops.EXP): #only one exponentiation
        return False

    listOfAttrNodes = []
    hasPairingsMixedWithNonExpCalcsRecursive(astNodeValue, listOfAttrNodes)
    if (len(listOfAttrNodes) == 0): #no attr nodes, so nothing is mixed in (unsupported)
        return False

    return True

def isUsingOurReservedVarNames(astNode):
    if (astNode.type != ops.EQ):
        return False

    varName = str(astNode.left)

    if (varName.startswith(RESERVED_VAR_NAME) == True):
        return True

    #if (varName.startswith(ORIGINAL_LOOP_VAR_NAME) == True):
        #return True

    return False

def fixPairingsMixedWithNonExpCalcs(astNode, outputFile):
    global reservedVarNameNumber

    outputFile.write(str(astNode) + "\n")

def isDotProdLoopStartResultOfPruneFunc(assignInfo, lineNo, varName):
    listIndexPos = varName.find(LIST_INDEX_SYMBOL)
    if (listIndexPos != -1):
        varName = varName[0:listIndexPos]

    funcName = getFuncNameFromLineNo(lineNo)
    if (varName not in assignInfo[funcName]):
        #sys.exit("isDotProdLoopStartResultOfPruneFunc in SDLPreProcessor.py:  couldn't find variabe in assignInfo.")
        return False

    varInfoObj = assignInfo[funcName][varName]
    return varInfoObj.getIsResultOfPruneFunc()

def expandDotProdIntoForLoop(assignInfo, astNode, lineNo, outputFile):
    global reservedVarNameNumber

    outputString = ""
    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber)

    dotProdType = getVarTypeInfoRecursive(astNode.right.right)

    if (dotProdType == types.G1):
        outputString += " := init(G1)\n"
    elif (dotProdType == types.G2):
        outputString += " := init(G2)\n"
    elif (dotProdType == types.GT):
        outputString += " := init(GT)\n"
    elif (dotProdType == types.ZR):
        outputString += " := init(ZR)\n"
    else:
        outputString += " := init(1)\n"
    outputString += "BEGIN :: for\n"
    outputString += "for{"

    loopVar = astNode.right.left.left.left
    loopStart = astNode.right.left.left.right
    loopEnd = astNode.right.left.right

    loopVarFromPrune = isDotProdLoopStartResultOfPruneFunc(assignInfo, lineNo, str(loopStart))

    outputString += str(loopVar) + " := "
    if (loopVarFromPrune == True):
        outputString += "0, "
    else:
        outputString += str(loopStart) + ", "
    outputString += str(loopEnd) + "}\n"

    if (loopVarFromPrune == True):
        if (str(loopStart).find(LIST_INDEX_SYMBOL) != -1):
            listIndexPos = str(loopStart).find(LIST_INDEX_SYMBOL)
            loopStartNoListEntry = str(loopStart)[0:listIndexPos]
        else:
            loopStartNoListEntry = str(loopStart)
        #outputString += ORIGINAL_LOOP_VAR_NAME + " := " + str(loopVar) + "\n"
        outputString += str(loopVar) + GET_STRING_SUFFIX + " := GetString(" + loopStartNoListEntry + LIST_INDEX_SYMBOL + str(loopVar) + ")\n"


    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber + 1) + " := "
    #outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + " * "

    if (loopVarFromPrune == True):
        outputString += str(astNode.right.right).replace(LIST_INDEX_SYMBOL + str(loopVar), LIST_INDEX_SYMBOL + str(loopVar) + GET_STRING_SUFFIX) + "\n"
    else:
        outputString += str(astNode.right.right) + "\n"

    #if (loopVarFromPrune == True):
        #outputString += str(loopVar) + " := " + ORIGINAL_LOOP_VAR_NAME + "\n"

    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + " := " + RESERVED_VAR_NAME + str(reservedVarNameNumber) + " * " + RESERVED_VAR_NAME + str(reservedVarNameNumber + 1) + "\n"

    outputString += "END :: for\n"

    outputString += str(astNode.left) + " := "
    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + "\n"

    doNotIncludeInTransformList.append(RESERVED_VAR_NAME + str(reservedVarNameNumber))

    reservedVarNameNumber += 2
    outputFile.write(outputString)

def SDLPreProcessor_main(inputFileName, outputFileName):
    try:
        outputFile = open(outputFileName, 'w')
    except:
        sys.exit("SDLPreProcessor_main in SDLPreProcessor.py:  could not open output file name passed in.")

    parseFile2(inputFileName, False, True)
    assignInfo = getAssignInfo()
    astNodes = getAstNodes()

    lineNo = 0

    for astNode in astNodes:
        lineNo += 1
        if (isUsingOurReservedVarNames(astNode) == True):
            print(astNode)
            sys.exit("SDLPreProcessor_main in SDLPreProcessor.py:  one of the ops.EQ assignments is using a variable name on the left that begins with one of our reserved variable name strings.")
        elif (astNode.type == ops.NONE):
            outputFile.write("\n")
        elif ( (astNode.right != None) and (astNode.right.type == ops.ON) ):
            expandDotProdIntoForLoop(assignInfo, astNode, lineNo, outputFile)
        elif (hasPairingsMixedWithNonExpCalcs(astNode) == True):
            fixPairingsMixedWithNonExpCalcs(astNode, outputFile)
        else:
            outputFile.write(str(astNode) + "\n")

    outputFile.close()

if __name__ == "__main__":
    lenSysArgv = len(sys.argv)

    if ( (lenSysArgv != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of input SDL file] [name of output SDL file].")

    SDLPreProcessor_main(sys.argv[1], sys.argv[2])
