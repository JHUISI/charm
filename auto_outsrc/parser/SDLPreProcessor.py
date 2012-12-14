import sys, os

sys.path.extend(['../../', '../../sdlparser'])

from SDLParser import *

reservedVarNameNumber = 0
RESERVED_VAR_NAME = "reservedVarName"

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

def isUsingOurReservedVarName(astNode):
    if (astNode.type != ops.EQ):
        return False

    varName = str(astNode.left)

    if (varName.startswith(RESERVED_VAR_NAME) == True):
        return True

    return False

def fixPairingsMixedWithNonExpCalcs(astNode, outputFile):
    global reservedVarNameNumber

    outputFile.write(str(astNode) + "\n")

def isVarResultOfPruneFunc(assignInfo, varName):
    ddddd

def expandDotProdIntoForLoop(assignInfo, astNode, outputFile):
    global reservedVarNameNumber

    outputString = ""
    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber)
    outputString += " := init(1)\n"
    outputString += "BEGIN :: for\n"
    outputString += "for{"

    loopVar = astNode.right.left.left.left
    loopStart = astNode.right.left.left.right
    loopEnd = astNode.right.left.right

    outputString += str(loopVar) + " := "
    outputString += str(loopStart) + ", "
    outputString += str(loopEnd) + "}\n"

    loopVarFromPrune = isDotProdLoopVarResultOfPruneFunc(assignInfo, loopVar)

    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + " := "
    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + " * "
    outputString += str(astNode.right.right) + "\n"
    outputString += "END :: for\n"

    outputString += str(astNode.left) + " := "
    outputString += RESERVED_VAR_NAME + str(reservedVarNameNumber) + "\n"

    reservedVarNameNumber += 1
    outputFile.write(outputString)

def SDLPreProcessor_main(inputFileName, outputFileName):
    try:
        outputFile = open(outputFileName, 'w')
    except:
        sys.exit("SDLPreProcessor_main in SDLPreProcessor.py:  could not open output file name passed in.")

    parseFile2(inputFileName, False, True)
    assignInfo = getAssignInfo()
    astNodes = getAstNodes()

    for astNode in astNodes:
        if (isUsingOurReservedVarName(astNode) == True):
            print(astNode)
            sys.exit("SDLPreProcessor_main in SDLPreProcessor.py:  one of the ops.EQ assignments is using a variable name on the left that begins with our reserved variable name string.")
        elif (astNode.type == ops.NONE):
            outputFile.write("\n")
        elif ( (astNode.right != None) and (astNode.right.type == ops.ON) ):
            expandDotProdIntoForLoop(assignInfo, astNode, outputFile)
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
