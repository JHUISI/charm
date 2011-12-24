import con, sys
from ASTParser import *
from ASTVarVisitor import *

def ensureSpacesBtwnTokens_CodeGen(lineOfCode):
	if ( (lineOfCode == None) or (type(lineOfCode).__name__ != con.strTypePython) or (len(lineOfCode) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->ensureSpacesBtwnTokens_CodeGen:  problem with line of code parameter passed in.")

	if (lineOfCode == '\n'):
		return lineOfCode

	lenOfLine = len(lineOfCode)
	if (lineOfCode[lenOfLine - 1] == '\n'):
		lineOfCode = lineOfCode[0:(lenOfLine-1)]
	
	L_index = 1
	R_index = 1
	withinApostrophes = False

	while (True):
		checkForSpace = False
		if ( (lineOfCode[R_index] == '\'') or (lineOfCode[R_index] == '\"') ):
			if (withinApostrophes == True):
				withinApostrophes = False
			else:
				withinApostrophes = True
		if (withinApostrophes == True):
			pass
		elif (lineOfCode[R_index] in ['^', '+', '(', ')', '{', '}', '-', ',', '[', ']']):
			currChars = lineOfCode[R_index]
			L_index = R_index
			checkForSpace = True			
		elif ( (lineOfCode[R_index] == 'e') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
			currChars = lineOfCode[R_index]
			L_index = R_index
			checkForSpace = True
		elif (lineOfCode[R_index] in ['>', '<', ':', '!', '=']):
			if (lineOfCode[R_index+1] == '='):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '&'):
			if (lineOfCode[R_index+1] == '&'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '/'):
			if (lineOfCode[R_index+1] == '/'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '|'):
			if (lineOfCode[R_index+1] == '|'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '*'):
			if (lineOfCode[R_index+1] == '*'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == 'H'):
			if (lineOfCode[R_index+1] == '('):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		elif (lineOfCode[R_index] == 'e'):
			if ( (lineOfCode[R_index+1] == '(') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		if (checkForSpace == True):
			if ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 3
			elif ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] == ' ') ):
				lenOfLine = len(lineOfCode)
				if (L_index == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index:lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] == ' ') ):
				R_index += 2
		else:
			R_index += 1

		lenOfLine = len(lineOfCode)

		if (R_index == (lenOfLine - 1)):
			if (lineOfCode[R_index] == ']'):
				lineOfCode = lineOfCode[0:R_index] + ' ]'
				break
			elif (lineOfCode[R_index] == ')'):
				lineOfCode = lineOfCode[0:R_index] + ' )'
				break			
			elif (lineOfCode[R_index] == ':'):
				lineOfCode = lineOfCode[0:R_index] + ' :'
				break

		if (R_index >= (lenOfLine - 1)):
			break

	lenOfLine = len(lineOfCode)
	if ( (lineOfCode[0] == '(' ) and (lineOfCode[1] != ' ') ):
		lineOfCode = '( ' + lineOfCode[1:lenOfLine]
	if ( (lineOfCode[lenOfLine-1] == ')' ) and (lineOfCode[lenOfLine-2] != ' ') ):
		lineOfCode = lineOfCode[0:(lenOfLine-1)] + ' )'

	lineOfCode = ' ' + lineOfCode + ' '

	return lineOfCode

def ensureSpacesBtwnTokens_Parser(lineOfCode):
	if ( (lineOfCode == None) or (type(lineOfCode).__name__ != con.strTypePython) or (len(lineOfCode) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->ensureSpacesBtwnTokens_Parser:  problem with line of code parameter passed in.")

	L_index = 1
	R_index = 1
	while (True):
		checkForSpace = False
		if (lineOfCode[R_index] in ['^', '+', '(', ')', '{', '}', '-', ',']):
			currChars = lineOfCode[R_index]
			L_index = R_index
			checkForSpace = True
		elif (lineOfCode[R_index] in ['>', '<', ':', '!', '=']):
			if (lineOfCode[R_index+1] == '='):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '&'):
			if (lineOfCode[R_index+1] == '&'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '/'):
			if (lineOfCode[R_index+1] == '/'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '|'):
			if (lineOfCode[R_index+1] == '|'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '*'):
			if (lineOfCode[R_index+1] == '*'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == 'H'):
			if (lineOfCode[R_index+1] == '('):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		elif (lineOfCode[R_index] == 'e'):
			if (lineOfCode[R_index+1] == '('):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		if (checkForSpace == True):
			if ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 3
			elif ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] == ' ') ):
				lenOfLine = len(lineOfCode)
				if (L_index == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index:lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] == ' ') ):
				R_index += 2
		else:
			R_index += 1

		lenOfLine = len(lineOfCode)
		if (R_index >= (lenOfLine - 1)):
			break

	return lineOfCode

def getFunctionArgsAsStrings(functionArgNames, funcName):
	if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  problem with function argument names dictionary parameter passed in.")

	if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (funcName not in functionArgNames) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  problem with function name parameter passed in.")

	argsAsStringNames = functionArgNames[funcName]
	if ( (argsAsStringNames == None) or (type(argsAsStringNames).__name__ != con.listTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  problem with list of argument names represented as StringName objects.")

	if (len(argsAsStringNames) == 0):
		return None

	argsAsStringsList = []

	for argStringName in argsAsStringNames:
		if ( (argStringName == None) or (type(argStringName).__name__ != con.stringName) ):
			sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  problem with one of the stringName objects in the argument list.")

		argAsString = argStringName.getStringVarName()
		if ( (argAsString == None) or (type(argAsString).__name__ != con.strTypePython) or (len(argAsString) == 0) ):
			sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  problem with the return value of getStringVarName on one of the argument stringName objects.")

		argsAsStringsList.append(argAsString)

	if (len(argsAsStringsList) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgsAsStrings:  could not extract any of the argument names as strings.")

	return argsAsStringsList

def removeLeftParanSpaces(line):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->removeLeftParanSpaces:  problem with line parameter passed in.")

	nextLParanIndex = line.find(con.lParan)

	while (nextLParanIndex != -1):
		if ( (nextLParanIndex > 0) and (line[nextLParanIndex - 1] == con.space) ):
			lenOfLine = len(line)
			line = line[0:(nextLParanIndex - 1)] + line[nextLParanIndex:lenOfLine]
			nextLParanIndex = line.find(con.lParan, nextLParanIndex)
		else:
			nextLParanIndex = line.find(con.lParan, (nextLParanIndex + 1))

	return line

def writeFunctionFromCodeToString(sourceCodeLines, startLineNo, endLineNo, extraTabsPerLine, removeSelf=False):
	if ( (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with source code lines parameter passed in.")

	if ( (startLineNo == None) or (type(startLineNo).__name__ != con.intTypePython) or (startLineNo < 1) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with start line number parameter passed in.")

	if ( (endLineNo == None) or (type(endLineNo).__name__ != con.intTypePython) or (endLineNo < startLineNo) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with end line number parameter passed in.")

	if ( (extraTabsPerLine == None) or (type(extraTabsPerLine).__name__ != con.intTypePython) or (extraTabsPerLine < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with extra tabs per line parameter passed in.")

	indentationList = []
	extractedLines = getLinesFromSourceCodeWithinRange(sourceCodeLines, startLineNo, endLineNo, indentationList)
	if ( (extractedLines == None) or (type(extractedLines).__name__ != con.listTypePython) or (len(extractedLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with value returned from getLinesFromSourceCodeWithinRange.")

	outputString = ""

	numSpacesFirstLine = indentationList[0]
	if ( (numSpacesFirstLine == None) or (type(numSpacesFirstLine).__name__ != con.intTypePython) or (numSpacesFirstLine < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with value returned from getNumIndentedSpaces on first line.")

	numTabsFirstLine = determineNumTabsFromSpaces(numSpacesFirstLine)
	if ( (numTabsFirstLine == None) or (type(numTabsFirstLine).__name__ != con.intTypePython) or (numTabsFirstLine < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->writeFunctionFromCodeToString:  problem with value returned from determineNumTabsFromSpaces on first line.")

	outputString += getStringOfTabs(extraTabsPerLine)
	firstLine = extractedLines[0].lstrip().rstrip()
	firstLine = ensureSpacesBtwnTokens_CodeGen(firstLine)
	if (removeSelf == True):
		firstLine = firstLine.replace(con.selfFuncArgString, con.space)

	firstLine = firstLine.lstrip()
	firstLine = removeLeftParanSpaces(firstLine)
	outputString += firstLine
	outputString += "\n"

	lenExtractedLines = len(extractedLines)

	for index in range(1, lenExtractedLines):
		numSpaces = indentationList[index]
		numTabs = determineNumTabsFromSpaces(numSpaces)
		numTabsForThisLine = numTabs - numTabsFirstLine
		line = extractedLines[index].lstrip().rstrip()
		outputString += getStringOfTabs(extraTabsPerLine + numTabsForThisLine)
		outputString += line
		outputString += "\n"

	outputString += "\n"
	return outputString

def getStringOfTabs(numTabs):
	if ( (numTabs == None) or (type(numTabs).__name__ != con.intTypePython) or (numTabs < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getStringOfTabs:  problem with the number of tabs passed in.")

	outputString = ""

	for tab in range(0, numTabs):
		outputString += "\t"

	return outputString

def determineNumTabsFromSpaces(numSpaces):
	if ( (numSpaces == None) or (type(numSpaces).__name__ != con.intTypePython) or (numSpaces < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->determineNumTabsFromSpaces:  problem with number of spaces parameter passed in.")

	if ( (numSpaces % con.numSpacesPerTab) != 0):
		sys.exit("Parser_CodeGen_Toolbox->determineNumTabsFromSpaces:  number of spaces passed in is not a multiple of the number of spaces per tab (" + con.numSpacesPerTab + ")")

	return (int(numSpaces / con.numSpacesPerTab))

def getFirstLastLineNosOfFuncList(funcList, rootNode):
	if ( (funcList == None) or (type(funcList).__name__ != con.listTypePython) or (len(funcList) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFirstLastLineNosOfFuncList:  problem with function list parameter passed in.")

	if (rootNode == None):
		sys.exit("Parser_CodeGen_Toolbox->getFirstLastLineNosOfFuncList:  root node passed in is of None type.")

	firstLastLinePairs = []

	for funcName in funcList:
		if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (len(funcName) == 0) ):
			sys.exit("Parser_CodeGen_Toolbox->getFirstLastLineNosOfFuncList:  problem with one of the function names in the function list parameter passed in.")

		currentFirstLastLinePair = getFuncFirstLastLineNos(funcName, rootNode)

		firstLastLinePairs.append(currentFirstLastLinePair)

	if (len(firstLastLinePairs) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getFirstLastLineNosOfFuncList:  could not extract any first/last line number pairs.")

	return firstLastLinePairs

def getFuncFirstLastLineNos(funcName, rootNode):
	if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (len(funcName) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  problem with function name parameter passed in.")

	if (rootNode == None):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  root node passed in is of None type.")

	myASTParser = ASTParser()
	if (myASTParser == None):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  could not obtain ASTParser object.")

	funcNodeList = myASTParser.getFunctionNode(rootNode, funcName)
	if (funcNodeList == None):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  could not locate a function with name " + funcName)
	if (len(funcNodeList) > 1):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  located more than one function with the name " + funcName)

	funcNode = funcNodeList[0]

	firstLine = myASTParser.getLineNumberOfNode(funcNode)
	if ( (firstLine == None) or (type(firstLine).__name__ != con.intTypePython) or (firstLine < 1) ):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  problem with first line number returned from ASTParser->getLineNumberOfNode.")

	lastLineVisitor = GetLastLineOfFunction()
	lastLineVisitor.visit(funcNode)
	lastLine = lastLineVisitor.getLastLine()

	if ( (lastLine == None) or (type(lastLine).__name__ != con.intTypePython) or (lastLine < firstLine) ):
		sys.exit("Parser_CodeGen_Toolbox->getFuncFirstLastLineNos:  problem with last line returned from GetLastLineOfFunction->getLastLine.")

	return (firstLine, lastLine)

def buildCallListOfFunc(functionArgMappings, funcName, callList, funcsVisitedSoFar):
	if ( (functionArgMappings == None) or (type(functionArgMappings).__name__ != con.dictTypePython) or (len(functionArgMappings) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with function argument mappings parameter passed in.")

	if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (funcName not in functionArgMappings) ):
		sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with the function name parameter passed in.")

	if ( (callList == None) or (type(callList).__name__ != con.listTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with the call list parameter passed in.")

	if ( (funcsVisitedSoFar == None) or (type(funcsVisitedSoFar).__name__ != con.listTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with the list of functions visited so far.")

	if (funcName in funcsVisitedSoFar):
		return

	funcsCalledWithinFunc = functionArgMappings[funcName]
	if ( (funcsCalledWithinFunc == None) or (type(funcsCalledWithinFunc).__name__ != con.listTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with function list extracted from function argument mappings for function " + funcName)

	funcsVisitedSoFar.append(funcName)

	if (len(funcsCalledWithinFunc) == 0):
		return

	for funcCalledWithin in funcsCalledWithinFunc:
		if ( (funcCalledWithin == None) or (type(funcCalledWithin).__name__ != con.functionArgMap) ):
			sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with function argument map extracted from list of function " + funcName)

		funcCalledWithinName = funcCalledWithin.getDestFuncName().getStringVarName()
		if ( (funcCalledWithinName == None) or (type(funcCalledWithinName).__name__ != con.strTypePython) or (len(funcCalledWithinName) == 0) ):
			sys.exit("Parser_CodeGen_Toolbox->buildCallListOfFunc:  problem with the name of one of the functions called from within " + funcName)

		if funcCalledWithinName not in callList:
			callList.append(funcCalledWithinName)

		buildCallListOfFunc(functionArgMappings, funcCalledWithinName, callList, funcsVisitedSoFar)

def isLineOnlyWhiteSpace(line):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->isLineOnlyWhiteSpace:  problem with line parameter passed in.")

	if (len(line) == 0):
		return True

	line = line.lstrip().rstrip()
	if (line == ""):
		return True
	return False

def isPreviousCharAlpha(line, currIndex):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->isPreviousCharAlpha:  problem with line parameter passed in.")

	if ( (currIndex == None) or (type(currIndex).__name__ != con.intTypePython) or (currIndex < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->isPreviousCharAlpha:  problem with current index parameter passed in.")

	if (currIndex == 0):
		return False
	
	if (line[currIndex - 1].isalpha() == True):
		return True
	
	return False

def getNumIndentedSpaces(line):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getNumIndentedSpaces:  problem with line parameter passed in.")

	lenOfLine = len(line)
	for index in range(0, lenOfLine):
		if (line[index] != con.space):
			break

	return index

def getLinesFromSourceCodeWithinRange(lines, startLine, endLine, indentationList):
	if ( (lines == None) or (type(lines).__name__ != con.listTypePython) or (len(lines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCodeWithinRange:  problem with lines parameter passed in.")

	if ( (startLine == None) or (type(startLine).__name__ != con.intTypePython) or (startLine < 1) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCodeWithinRange:  problem with the start line parameter passed in.")

	if ( (endLine == None) or (type(endLine).__name__ != con.intTypePython) or (endLine < startLine) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCodeWithinRange:  problem with the end line parameter passed in.")

	if ( (indentationList == None) or (type(indentationList).__name__ != con.listTypePython) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCodeWithinRange:  problem with the indentation list passed in.")

	retLines = []
	lineCounter = 1

	for line in lines:
		if (lineCounter > endLine):
			if (len(retLines) == 0):
				return None
			return retLines
		if (lineCounter >= startLine):
			numIndentedSpaces = getNumIndentedSpaces(line)
			tempLine = line.lstrip().rstrip()
			retLines.append(tempLine)
			indentationList.append(numIndentedSpaces)
		lineCounter += 1

def getLineNosOfValueType(varAssignments, valueType):
	if ( (varAssignments == None) or (type(varAssignments).__name__ != con.dictTypePython) or (len(varAssignments) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLineNosOfValueType:  problem with the variable assignments dictionary passed in.")

	if ( (valueType == None) or (type(valueType).__name__ != con.strTypePython) or (len(valueType) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLineNosOfValueType:  problem with the value type passed in.")

	lineNos = []

	for funcName in varAssignments:
		funcAssignments = varAssignments[funcName]
		for assignment in funcAssignments:
			value = assignment.getValue()
			if (type(value).__name__ == valueType):
				lineNos.append(value.getLineNo())

	if (len(lineNos) == 0):
		return None

	return lineNos

def getFunctionArgMappings(functionNames, functionArgNames, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problem with the function names passed in.")

	if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problem with the function argument names passed in.")

	if (myASTParser == None):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  myASTParser passed in is of None type.")

	functionArgMappings = {}

	for funcName in functionNames:
		funcArgMapList = myASTParser.getFunctionArgMappings(functionNames[funcName], functionArgNames)
		if ( (funcArgMapList == None) or (type(funcArgMapList).__name__ != con.listTypePython) ):
			sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problems with value returned from myASTParser->getFunctionArgMappings.")

		functionArgMappings[funcName] = funcArgMapList

	if (len(functionArgMappings) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  could not obtain any function argument mappings at all.")

	return functionArgMappings

def getVarAssignments(rootNode, functionNames, myASTParser):
	if (rootNode == None):
		sys.exit("Parser_CodeGen_Toolbox->getVarAssignments:  root node passed in is of None type.")

	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getVarAssignments:  problem with the function names passed in.")

	if (myASTParser == None):
		sys.exit("Parser_CodeGen_Toolbox->getVarAssignments:  myASTParser passed in is of None type.")

	varAssignments = {}

	for funcName in functionNames:
		myVarVisitor = ASTVarVisitor(myASTParser)
		myVarVisitor.visit(functionNames[funcName])
		varAssignments[funcName] = copy.deepcopy(myVarVisitor.getVarAssignDict())
		del myVarVisitor

	if (len(varAssignments) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getVarAssigments:  could not find any variable assignments.")

	return varAssignments

def getAllVariableNamesFromVerifyEq(verifyEqNode, myASTParser):
	if ( (verifyEqNode == None) or (myASTParser == None) ):
		sys.exit("Parser_CodeGen_Toolbox->getAllVariableNamesFromVerifyEq:  problem with the variables passed in to the function.")

	varsVerifyEq = myASTParser.getAllVariableNames(verifyEqNode)
	if ( (varsVerifyEq == None) or (type(varsVerifyEq).__name__ != con.listTypePython) or (len(varsVerifyEq) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getAllVariableNamesFromVerifyEq:  problem with value returned from ASTParser->getAllVariableNames.")

	varsVerifyEq = myASTParser.removeVarsFromListWithStringName(varsVerifyEq, con.pair)
	if ( (varsVerifyEq == None) or (type(varsVerifyEq).__name__ != con.listTypePython) or (len(varsVerifyEq) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getAllVariableNamesFromVerifyEq:  problem with value returned from ASTParser->removeVarsFromListWithName.")

	return varsVerifyEq

def getReturnNodes(functionNames, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getReturnNodes:  problem with the function names dictionary passed in.")

	if ( (myASTParser == None) or (type(myASTParser).__name__ != con.ASTParser) ):
		sys.exit("Parser_CodeGen_Toolbox->getReturnNodes:  problem with the AST parser passed in.")

	returnNodes = {}

	for funcName in functionNames:
		returnNodes[funcName] = myASTParser.getReturnNodeList(functionNames[funcName])

	if (len(returnNodes) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getReturnNodes:  could not obtain any return nodes for the function names/nodes passed in.")

	return returnNodes

def getStringNameIntegerValue(varAssignments, stringNameOfVariable, nameOfFunction):
	if ( (varAssignments == None) or (type(varAssignments).__name__ != con.dictTypePython) or (len(varAssignments) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  problem with the variable assignments dictionary passed in.")

	if ( (stringNameOfVariable == None) or (type(stringNameOfVariable).__name__ != con.strTypePython) or (len(stringNameOfVariable) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  problem with the variable name passed in.")

	if ( (nameOfFunction == None) or (type(nameOfFunction).__name__ != con.strTypePython) or (len(nameOfFunction) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  problem with the function name passed in.")

	if (nameOfFunction not in varAssignments):
		sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  could not find a function named " + nameOfFunction + " in the varAssignments dictionary passed in.")

	functionVariables = varAssignments[nameOfFunction]
	if ( (functionVariables == None) or (type(functionVariables).__name__ != con.listTypePython) or (len(functionVariables) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  problem with the list of variables obtained from varAssignments for the " + nameOfFunction + " function.")

	for var in functionVariables:
		if (type(var).__name__ != con.variable):
			sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  one of the entries in varAssignments is not of type " + con.variable)

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

	return None

	#sys.exit("Parser_CodeGen_Toolbox->getStringNameIntegerValue:  could not find a variable named " + stringNameOfVariable + " in the " + nameOfFunction + " function.")

def cleanVerifyEq(origVerifyEq):
	if (len(origVerifyEq) == 0):
		sys.exit("Parser_CodeGen_Toolbox->cleanVerifyEq:  original verification equation passed in is of length zero.")

	cleanVerifyEq = origVerifyEq.lstrip().rstrip().rstrip(':').replace('pair', 'e').replace('**', '^').replace(' = ', ' := ')
	cleanVerifyEq = removeSubstringFromEnd(cleanVerifyEq, 'if ', con.left)
	cleanVerifyEq = removeSubstringFromEnd(cleanVerifyEq, 'return ', con.left)
	cleanVerifyEq = "verify := { " + cleanVerifyEq + " }"
	return cleanVerifyEq

def removeSubstringFromEnd(fullString, removeSubstring, leftOrRight):
	if (len(fullString) == 0):
		sys.exit("Parser_CodeGen_Toolbox->removeSubstringFromEnd:  full string passed in is of length zero.")

	if (len(removeSubstring) == 0):
		sys.exit("Parser_CodeGen_Toolbox->removeSubstringFromEnd:  remove substring passed in is of length zero.")

	if ( (leftOrRight != con.left) and (leftOrRight != con.right) ):
		sys.exit("Parser_CodeGen_Toolbox->removeSubstringFromEnd:  leftOrRight parameter passed in was neither con.left nor con.right.")

	lenFullString = len(fullString)
	lenRemoveSubstring = len(removeSubstring)

	if (lenRemoveSubstring >= lenFullString):
		sys.exit("Parser_CodeGen_Toolbox->removeSubstringFromEnd:  length of remove substring is greater than or equal to the length of the full string.")

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
