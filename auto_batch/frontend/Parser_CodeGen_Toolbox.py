import con, sys
from ASTParser import *
from ASTVarVisitor import *

def getFunctionArgMappings(functionNames, functionArgNames, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("AutoBatch_Parser->getFunctionArgMappings:  problem with the function names passed in.")

	if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
		sys.exit("AutoBatch_Parser->getFunctionArgMappings:  problem with the function argument names passed in.")

	if (myASTParser == None):
		sys.exit("AutoBatch_Parser->getFunctionArgMappings:  myASTParser passed in is of None type.")

	functionArgMappings = {}

	for funcName in functionNames:
		funcArgMapList = myASTParser.getFunctionArgMappings(functionNames[funcName], functionArgNames)
		if ( (funcArgMapList == None) or (type(funcArgMapList).__name__ != con.listTypePython) ):
			sys.exit("AutoBatch_Parser->getFunctionArgMappings:  problems with value returned from myASTParser->getFunctionArgMappings.")

		functionArgMappings[funcName] = funcArgMapList

	if (len(functionArgMappings) == 0):
		sys.exit("AutoBatch_Parser->getFunctionArgMappings:  could not obtain any function argument mappings at all.")

	return functionArgMappings

def getVarAssignments(rootNode, functionNames, myASTParser):
	if (rootNode == None):
		sys.exit("AutoBatch_Parser->getVarAssignments:  root node passed in is of None type.")

	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("AutoBatch_Parser->getVarAssignments:  problem with the function names passed in.")

	if (myASTParser == None):
		sys.exit("AutoBatch_Parser->getVarAssignments:  myASTParser passed in is of None type.")

	varAssignments = {}

	for funcName in functionNames:
		myVarVisitor = ASTVarVisitor(myASTParser)
		myVarVisitor.visit(functionNames[funcName])
		varAssignments[funcName] = copy.deepcopy(myVarVisitor.getVarAssignDict())
		del myVarVisitor

	if (len(varAssignments) == 0):
		sys.exit("AutoBatch_Parser->getVarAssigments:  could not find any variable assignments.")

	return varAssignments

def getAllVariableNamesFromVerifyEq(verifyEqNode, myASTParser):
	if ( (verifyEqNode == None) or (myASTParser == None) ):
		sys.exit("AutoBatch_Parser->getAllVariableNamesFromVerifyEq:  problem with the variables passed in to the function.")

	varsVerifyEq = myASTParser.getAllVariableNames(verifyEqNode)
	if ( (varsVerifyEq == None) or (type(varsVerifyEq).__name__ != con.listTypePython) or (len(varsVerifyEq) == 0) ):
		sys.exit("AutoBatch_Parser->getAllVariableNamesFromVerifyEq:  problem with value returned from ASTParser->getAllVariableNames.")

	varsVerifyEq = myASTParser.removeVarsFromListWithStringName(varsVerifyEq, con.pair)
	if ( (varsVerifyEq == None) or (type(varsVerifyEq).__name__ != con.listTypePython) or (len(varsVerifyEq) == 0) ):
		sys.exit("AutoBatch_Parser->getAllVariableNamesFromVerifyEq:  problem with value returned from ASTParser->removeVarsFromListWithName.")

	return varsVerifyEq

def getReturnNodes(functionNames, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("AutoBatch_Parser->getReturnNodes:  problem with the function names dictionary passed in.")

	if ( (myASTParser == None) or (type(myASTParser).__name__ != con.ASTParser) ):
		sys.exit("AutoBatch_Parser->getReturnNodes:  problem with the AST parser passed in.")

	returnNodes = {}

	for funcName in functionNames:
		returnNodes[funcName] = myASTParser.getReturnNodeList(functionNames[funcName])

	if (len(returnNodes) == 0):
		sys.exit("AutoBatch_Parser->getReturnNodes:  could not obtain any return nodes for the function names/nodes passed in.")

	return returnNodes

def getStringNameIntegerValue(varAssignments, stringNameOfVariable, nameOfFunction):
	if ( (varAssignments == None) or (type(varAssignments).__name__ != con.dictTypePython) or (len(varAssignments) == 0) ):
		sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  problem with the variable assignments dictionary passed in.")

	if ( (stringNameOfVariable == None) or (type(stringNameOfVariable).__name__ != con.strTypePython) or (len(stringNameOfVariable) == 0) ):
		sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  problem with the variable name passed in.")

	if ( (nameOfFunction == None) or (type(nameOfFunction).__name__ != con.strTypePython) or (len(nameOfFunction) == 0) ):
		sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  problem with the function name passed in.")

	if (nameOfFunction not in varAssignments):
		sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  could not find a function named " + nameOfFunction + " in the varAssignments dictionary passed in.")

	functionVariables = varAssignments[nameOfFunction]
	if ( (functionVariables == None) or (type(functionVariables).__name__ != con.listTypePython) or (len(functionVariables) == 0) ):
		sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  problem with the list of variables obtained from varAssignments for the " + nameOfFunction + " function.")

	for var in functionVariables:
		if (type(var).__name__ != con.variable):
			sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  one of the entries in varAssignments is not of type " + con.variable)

		varNameObj = var.getName()
		if (type(varNameObj).__name__ != con.stringName):
			continue

		varName = varNameObj.getName()
		if (varName != stringNameOfVariable):
			continue

		varValueObj = var.getValue()
		if (type(varValueObj).__name__ != con.integerValue):
			continue

		varValue = varValueObj.getValue()
		if ( (varValue == None) or (type(varValue).__name__ != con.intTypePython) ):
			continue

		return varValue

	sys.exit("AutoBatch_Parser->getStringNameIntegerValue:  could not find a variable named " + stringNameOfVariable + " in the " + nameOfFunction + " function.")

def cleanVerifyEq(origVerifyEq):
	if (len(origVerifyEq) == 0):
		sys.exit("AutoBatch_Parser->cleanVerifyEq:  original verification equation passed in is of length zero.")

	cleanVerifyEq = origVerifyEq.lstrip().rstrip().rstrip(':').replace('pair', 'e').replace('**', '^').replace(' = ', ' := ')
	cleanVerifyEq = removeSubstringFromEnd(cleanVerifyEq, 'if ', con.left)
	cleanVerifyEq = removeSubstringFromEnd(cleanVerifyEq, 'return ', con.left)
	cleanVerifyEq = "verify := { " + cleanVerifyEq + " }"
	return cleanVerifyEq

def removeSubstringFromEnd(fullString, removeSubstring, leftOrRight):
	if (len(fullString) == 0):
		sys.exit("AutoBatch_Parser->removeSubstringFromEnd:  full string passed in is of length zero.")

	if (len(removeSubstring) == 0):
		sys.exit("AutoBatch_Parser->removeSubstringFromEnd:  remove substring passed in is of length zero.")

	if ( (leftOrRight != con.left) and (leftOrRight != con.right) ):
		sys.exit("AutoBatch_Parser->removeSubstringFromEnd:  leftOrRight parameter passed in was neither con.left nor con.right.")

	lenFullString = len(fullString)
	lenRemoveSubstring = len(removeSubstring)

	if (lenRemoveSubstring >= lenFullString):
		sys.exit("AutoBatch_Parser->removeSubstringFromEnd:  length of remove substring is greater than or equal to the length of the full string.")

	if (leftOrRight == con.left):
		if (fullString.startswith(removeSubstring) == False):
			return fullString
		return fullString[lenRemoveSubstring:lenFullString]

	if (fullString.endswith(removeSubstring) == False):
		return fullString

	return fullString[0:(lenFullString - lenRemoveSubstring)]

def getLinesFromSourceCode(sourceCodeLines, lineNos):
	if ( (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  problem with source code lines passed in.")

	if ( (lineNos == None) or (type(lineNos).__name__ != con.listTypePython) or (len(lineNos) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  problem with line numbers passed in.")

	matchingLines = []

	lineNos = list(set(lineNos))
	lenLineNos = len(lineNos)
	lastLineNo = lineNos[lenLineNos - 1]

	lastSourceCodeLineNo = len(sourceCodeLines)

	if (lastLineNo > lastSourceCodeLineNo):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  one of the line numbers passed in exceeds the number of lines in the source code passed in.")

	for index in range(0, lenLineNos):
		nextMatchingLineNo = lineNos[index]
		nextMatchingLine = sourceCodeLines[nextMatchingLineNo - 1]
		matchingLines.append(nextMatchingLine)

	if (len(matchingLines) == 0):
		return None

	return matchingLines

def getImportLines(rootNode, sourceCodeLines):
	if ( (rootNode == None) or (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with one of the parameters passed in.")

	myASTParser = ASTParser()
	importLineNos = myASTParser.getImportLineNos(rootNode)
	if (importLineNos == None):
		return None

	if ( (type(importLineNos).__name__ != con.listTypePython) or (len(importLineNos) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with import line numbers returned from ASTParser->getImportLineNos.")

	importLines = getLinesFromSourceCode(sourceCodeLines, importLineNos)
	if ( (importLines == None) or (type(importLines).__name__ != con.listTypePython) or (len(importLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with import lines returned from getLinesFromSourceCode.")

	return importLines
