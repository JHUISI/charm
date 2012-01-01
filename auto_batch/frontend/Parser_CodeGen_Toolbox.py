import con, copy, sys
from ASTParser import *
from ASTVarVisitor import *
from LineInfo import LineInfo
from StringName import StringName
from StringValue import StringValue

'''
def getLineNosPerVar(varAssignments):
	if ( (varAssignments == None) or (type(varAssignments).
'''

def getGlobalDeclVars(node):
	if (node == None):
		sys.exit("Parser_CodeGen_Toolbox->getGlobalDeclVars:  node passed in is of None type.")

	myASTGlobalVisitor = ASTGetGlobalDeclVars()
	myASTGlobalVisitor.visit(node)
	return myASTGlobalVisitor.getGlobalDecVars()

class ASTFuncArgMapsVisitor(ast.NodeVisitor):
	def __init__(self, functionArgNames, lenFunctionArgDefaults):
		if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the function argument names passed in.")

		if ( (lenFunctionArgDefaults == None) or (type(lenFunctionArgDefaults).__name__ != con.dictTypePython) or (len(lenFunctionArgDefaults) == 0) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the length of function argument defaults dictionary.")

		self.myASTParser = ASTParser()
		if ( (self.myASTParser == None) or (type(self.myASTParser).__name__ != con.ASTParser) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the value returned from ASTParser().")

		self.myASTVarVisitor = ASTVarVisitor(self.myASTParser)
		if ( (self.myASTVarVisitor == None) or (type(self.myASTVarVisitor).__name__ != con.ASTVarVisitor) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with value returned from ASTVarVisitor().")

		self.functionArgNames = functionArgNames
		self.lenFunctionArgDefaults = lenFunctionArgDefaults
		self.functionArgMappings = []

	def getDestFuncName(self, node):
		if ( (node == None) or (type(node).__name__ != con.callTypeAST) ):
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with node passed in to function.")

		(funcValueNameObject, funcAttrNameObject) = self.myASTParser.getFuncNameFromCallNode(node)
		if (funcAttrNameObject == None):
			destFuncName = funcValueNameObject
		else:
			destFuncName = funcAttrNameObject

		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.stringName) ):
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with value returned from ASTParser->getFuncNameFromCallNode.")

		return destFuncName

		'''
		try:
			destFuncName = node.func.id
		except:
			destFuncName = None

		if (destFuncName != None):
			destFuncNameObject = self.myASTParser.buildStringName(node, destFuncName)
			if ( (destFuncNameObject == None) or (type(destFuncNameObject).__name__ != con.stringName) ):
				sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with value returned from ASTParser->buildStringName for destination function name.")

			return destFuncNameObject

		try:
			funcValueName = node.func.value.id
		except:
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  could not obtain any information about the call represented by the node passed in.")

		try:
			funcAttrName = node.func.attr
		except:
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  could not obtain the function's attribute name from the node passed in.")

		funcAttrNameObject = self.myASTParser.buildStringName(node, funcAttrName)
		if ( (funcAttrNameObject == None) or (type(funcAttrNameObject).__name__ != con.stringName) ):
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with value returned from ASTParser->buildStringName for function attribute name.")

		return funcAttrNameObject
		'''

	def throwErrorOnUnequalCallLists(self, lenCallerArgs, lenDestArgs, destFuncName):
		if ( (lenCallerArgs == None) or (type(lenCallerArgs).__name__ != con.intTypePython) or (lenCallerArgs < 0) ):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  problem with length of caller arguments passed in.")

		if ( (lenDestArgs == None) or (type(lenDestArgs).__name__ != con.intTypePython) or (lenDestArgs < 0) ):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  problem with length of destination arguments passed in.")

		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.strTypePython) or (len(destFuncName) == 0) ):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  problem with destination function name passed in.")

		if ( (destFuncName not in self.functionArgNames) or (destFuncName not in self.lenFunctionArgDefaults) ):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  destination function name passed in is not in the function argument names dictionary OR length of function default arguments dictionary.")

		diffInNumArgs = lenDestArgs - lenCallerArgs
		if (diffInNumArgs < 0):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  number of caller arguments exceeds number of destination arguments.")

		numDefaultArgsInDest = self.lenFunctionArgDefaults[destFuncName]
		if (numDefaultArgsInDest < 0):
			sys.exit("ASTFuncArgMapsVisitor->throwErrorOnUnequalCallLists:  number of default arguments for destination function name passed in is less than zero.")

		if (diffInNumArgs > numDefaultArgsInDest):
			return True

		return False

	def visit_Call(self, node):
		destFuncName = self.getDestFuncName(node)
		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.stringName) ):
			sys.exit("ASTFuncArgMapsVisitor->visit_Call:  problem with value returned from self.getDestFuncName.")

		if (destFuncName.getStringVarName() not in self.functionArgNames):
			return

		destArgNames = self.functionArgNames[destFuncName.getStringVarName()]

		callerArgList = self.myASTVarVisitor.getArgNodeList(node)

		if ( (callerArgList == None) and (len(destArgNames) == 0) ):
			funcArgMapObject = FunctionArgMap()
			funcArgMapObject.setDestFuncName(destFuncName)
			funcArgMapObject.setLineNo(node.lineno)
			self.functionArgMappings.append(copy.deepcopy(funcArgMapObject))
			return

		if (len(callerArgList) != len(destArgNames) ):
			throwError = self.throwErrorOnUnequalCallLists(len(callerArgList), len(destArgNames), destFuncName.getStringVarName())
			if (throwError == True):
				sys.exit("ASTFuncArgMapsVisitor->visit_Call:  length of caller and destination arguments lists are not equal.")

		funcArgMapObject = FunctionArgMap()
		funcArgMapObject.setDestFuncName(destFuncName)

		if (len(callerArgList) != 0):
			funcArgMapObject.setCallerArgList(callerArgList)
			funcArgMapObject.setDestArgList(destArgNames)

		funcArgMapObject.setLineNo(node.lineno)

		self.functionArgMappings.append(copy.deepcopy(funcArgMapObject))

	def getFunctionArgMappings(self):
		return self.functionArgMappings

def getFunctionArgMappings_OneFunction(funcNode, functionArgNames, lenFunctionArgDefaults):
	if (funcNode == None):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings_OneFunction:  function node passed in is of None type.")

	if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings_OneFunction:  problem with the function argument names passed in.")

	if ( (lenFunctionArgDefaults == None) or (type(lenFunctionArgDefaults).__name__ != con.dictTypePython) or (len(lenFunctionArgDefaults) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings_OneFunction:  problem with length of function default arguments parameter passed in.")

	myFuncArgMapsVisitor = ASTFuncArgMapsVisitor(functionArgNames, lenFunctionArgDefaults)
	myFuncArgMapsVisitor.visit(funcNode)
	return myFuncArgMapsVisitor.getFunctionArgMappings()

def getLineNoOfFirstFunction(functionNames, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLineNoOfFirstFunction:  problem with function names parameter passed in.")

	if (myASTParser == None):
		sys.exit("Parser_CodeGen_Toolbox->getLineNoOfFirstFunction:  problem with ASTParser parameter passed in.")

	firstLineNo = sys.maxsize

	for funcNameAsString in functionNames:
		funcNode = functionNames[funcNameAsString]
		if (funcNode == None):
			sys.exit("Parser_CodeGen_Toolbox->getLineNoOfFirstFunction:  one of the function nodes extracted from the function names parameter passed in is of None type.")

		currentLineNo = myASTParser.getLineNumberOfNode(funcNode)
		if ( (currentLineNo == None) or (type(currentLineNo).__name__ != con.intTypePython) or (currentLineNo < 1) ):
			sys.exit("Parser_CodeGen_Toolbox->getLineNoOfFirstFunction:  problem with one of the line numbers obtained of the function nodes.")

		if (currentLineNo < firstLineNo):
			firstLineNo = currentLineNo

	if (firstLineNo == sys.maxsize):
		sys.exit("Parser_CodeGen_Toolbox->getLineNoOfFirstFunction:  could not obtain the first line number from the function names parameter passed in.")

	return firstLineNo

def searchForLoopNameInLoopList(loopNameToSearchFor, loopList):
	if (loopList == None):
		return False

	if ( (loopNameToSearchFor == None) or (type(loopNameToSearchFor).__name__ != con.strTypePython) or (isStringALoopName(loopNameToSearchFor) == False) ):
		sys.exit("Parser_CodeGen_Toolbox->searchForLoopNameInLoopList:  problem with loop name to search for parameter passed in.")

	if ( (type(loopList).__name__ != con.listTypePython) or (len(loopList) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->searchForLoopNameInLoopList:  problem with loop list parameter passed in.")

	foundIt = False

	for loopStringName in loopList:
		if ( (loopStringName == None) or (type(loopStringName).__name__ != con.stringName) ):
			sys.exit("Parser_CodeGen_Toolbox->searchForLoopNameInLoopList:  problem with one of the loop string name objects extracted from the loop list parameter passed in.")

		loopAsString = loopStringName.getStringVarName()
		if ( (loopAsString == None) or (type(loopAsString).__name__ != con.strTypePython) or (isStringALoopName(loopAsString) == False) ):
			sys.exit("Parser_CodeGen_Toolbox->searchForLoopNameInLoopList:  problem with return value for getStringVarName called on one of the loops in the loop list passed in.")

		if (loopNameToSearchFor == loopAsString):
			if (foundIt == True):
				sys.exit("Parser_CodeGen_Toolbox->searchForLoopNameInLoopList:  found duplicate loop names in the loop list passed in that match the loop name to search for parameter passed in.")

			foundIt = True

	return foundIt

def getLoopNamesAsStringsFromLoopList(loopList):
	if (areAllLoopNamesValid(loopList) == False):
		sys.exit("Parser_CodeGen_Toolbox->getLoopNamesAsStringsFromLoopList:  loop list passed in failed the check of areAllLoopNamesValid.")

	retList = []

	for loop in loopList:
		retList.append(loop.getLoopName().getStringVarName())

	return retList

def checkLoopOrder(loopOrder):
	if ( (loopOrder == None) or (type(loopOrder).__name__ != con.listTypePython) or (len(loopOrder) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->checkLoopOrder:  problem with loop order parameter passed in.")

	for indexStringName in loopOrder:
		if ( (indexStringName == None) or (type(indexStringName).__name__ != con.stringName) ):
			sys.exit("Parser_CodeGen_Toolbox->checkLoopOrder:  problem with one of the indices in the loop order parameter passed in.")

		index = indexStringName.getStringVarName()

		if ( (index == None) or (type(index).__name__ != con.strTypePython) or (index not in con.loopIndexTypes) ):
			sys.exit("Parser_CodeGen_Toolbox->checkLoopOrder:  problem with string version of one of the indices in the loop order passed in.")

	return True

def getLoopOrderAsString(loopOrder):
	if (loopOrder == None):
		return None

	if ( (type(loopOrder).__name__ != con.listTypePython) or (len(loopOrder) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLoopOrderAsString:  problem with loopOrder parameter passed in.")

	loopOrderAsString = ""

	for loop in loopOrder:
		if ( (loop == None) or (type(loop).__name__ != con.stringName) ):
			sys.exit("Parser_CodeGen_Toolbox->getLoopOrderAsString:  problem with one of the loop " + con.stringName + " objects extracted from the loop order list.")

		loopIndexString = loop.getStringVarName()
		if ( (loopIndexString == None) or (type(loopIndexString).__name__ != con.strTypePython) or (loopIndexString not in con.loopIndexTypes) ):
			sys.exit("Parser_CodeGen_Toolbox->getLoopOrderAsString:  problem with the string representations of one of the loop indices in the loop order.")

		loopOrderAsString += loopIndexString

	if (len(loopOrderAsString) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getLoopOrderAsString:  could not extract the string representations of any of the loop indices in the loop order.")

	return loopOrderAsString

def getLoopInfoObjFromLoopName(loopList, loopName):
	if ( (loopList == None) or (type(loopList).__name__ != con.listTypePython) or (len(loopList) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLoopInfoObjFromLoopName:  problem with loop list passed in.")

	if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (len(loopName) == 0) or (isStringALoopName(loopName) == False) ):
		sys.exit("Parser_CodeGen_Toolbox->getLoopInfoObjFromLoopName:  problem with loop name passed in.")

	retLoop = None

	for loop in loopList:
		if (loop.getLoopName().getStringVarName() == loopName):
			if (retLoop != None):
				sys.exit("Parser_CodeGen_Toolbox->getLoopInfoObjFromLoopName:  found more than one loop info object with the same loop name (" + loopName + ").")
			retLoop = copy.deepcopy(loop)

	return retLoop

def returnOperationAsStringValue(opString):
	if ( (opString == None) or (type(opString).__name__ != con.strTypePython) or (len(opString) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->returnOperationAsStringValue:  problem with operation string passed in.")

	retOpString = None

	for opType in con.operationTypes:
		if (opString.startswith(opType) == True):
			if (retOpString != None):
				sys.exit("Parser_CodeGen_Toolbox->returnOperationAsStringValue:  found multiple operation types that fit the operation string passed in (" + opString + ").")
			retOpString = opType

	if (retOpString == None):
		return None

	retOpString_StringValue = StringValue()
	retOpString_StringValue.setValue(retOpString)
	return retOpString_StringValue

def getChildrenLoopsOfLoop(loop):
	if ( (loop == None) or (type(loop).__name__ != con.loopInfo) ):
		sys.exit("Parser_CodeGen_Toolbox->getChildrenLoopsOfLoop:  problem with loop passed in.")

	returnList = []

	childrenList = loop.getVarListWithSubscripts()
	for child in childrenList:
		childName = child.getStringVarName()
		if ( (childName == None) or (type(childName).__name__ != con.strTypePython) or (len(childName) == 0) ):
			sys.exit("Parser_CodeGen_Toolbox->getChildrenLoopsOfLoop:  problem with the string version of one of the child variable names.")

		if (isStringALoopName(childName) == True):
			returnList.append(childName)

	if (len(returnList) == 0):
		return None

	return returnList

def buildAbbreviatedLoopDict(loopList):
	if (areAllLoopNamesValid(loopList) == False):
		sys.exit("Parser_CodeGen_Toolbox->buildAbbreviatedLoopDict:  one of the loop names in the loop list passed in is invalid.")

	abbrLoopDict = {}

	for loop in loopList:
		loopName = loop.getLoopName().getStringVarName()
		startVal = loop.getStartValue().getValue()
		if ( (startVal == None) or (type(startVal).__name__ != con.intTypePython) or (startVal < 0) ):
			sys.exit("Parser_CodeGen_Toolbox->buildAbbreviatedLoopDict:  problem with start value extracted for one of the loops in the loop list passed in.")
		loopOverValue = loop.getLoopOverValue().getStringVarName()
		if ( (loopOverValue == None) or (type(loopOverValue).__name__ != con.strTypePython) or (loopOverValue not in con.loopTypes) ):
			sys.exit("Parser_CodeGen_Toolbox->buildAbbreviatedLoopDict:  problem with loop over value in one of the loops in the loop list passed in.")
		loopOperation = loop.getOperation().getStringVarName()
		if ( (loopOperation == None) or (type(loopOperation).__name__ != con.strTypePython) or (loopOperation not in con.operationTypes) ):
			sys.exit("Parser_CodeGen_Toolbox->buildAbbreviatedLoopDict:  problem with loop operation in one of the loops in the loop list passed in.")

		rangeStruct = []
		rangeStruct.append(startVal)
		rangeStruct.append(loopOverValue)
		rangeStruct.append(loopOperation)

		abbrLoopDict[loopName] = copy.deepcopy(rangeStruct)
		del rangeStruct

	if (len(abbrLoopDict) == 0):
		sys.exit("Parser_CodeGen_Toolbox->buildAbbreviatedLoopDict:  could not extract abbreviated loop form of any of the loops passed in.")

	return abbrLoopDict

def areAllLoopNamesValid(loopList):
	if ( (loopList == None) or (type(loopList).__name__ != con.listTypePython) or (len(loopList) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->areAllLoopNamesValid:  problem with loop list passed in.")

	for loop in loopList:
		if (type(loop).__name__ == con.loopInfo):
			loopName = loop.getLoopName().getStringVarName()
		elif (type(loop).__name__ == con.stringName):
			loopName = loop.getStringVarName()
		else:
			sys.exit("Parser_CodeGen_Toolbox->areAllLoopNamesValid:  type of the loops in the loop list passed in are not one of the supported types (" + con.loopInfo + ", " + con.stringName + ").")

		if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (len(loopName) == 0) ):
			sys.exit("Parser_CodeGen_Toolbox->areAllLoopNamesValid:  problem with one of the loop names in the list passed in.")

		isValidLoopName = isStringALoopName(loopName)
		if (isValidLoopName == False):
			return False

	return True

def isStringALoopName(strName):
	if ( (strName == None) or (type(strName).__name__ != con.strTypePython) or (len(strName) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->isStringALoopName:  problem with string name parameter passed in.")

	lenStr = len(strName)

	if (lenStr > con.maxStrLengthForLoopNames):
		return False

	foundPrefix = False

	for prefix in con.loopPrefixes:
		if (strName.startswith(prefix) == True):
			foundPrefix = True
			break

	return foundPrefix

def removeSubscriptsReturnStringNames(list):
	if ( (list == None) or (type(list).__name__ != con.listTypePython) or (len(list) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->removeSubscriptsReturnStringNames:  problem with list input parameter passed in.")

	returnList = []

	for varName in list:
		if ( (varName == None) or (type(varName).__name__ != con.strTypePython) or (len(varName) == 0) or (varName.count(con.loopIndicator) > 1) ):
			sys.exit("Parser_CodeGen_Toolbox->removeSubscriptsReturnStringNames:  problem with one of the variable names in the list input parameter passed in.")

		loopIndicatorIndex = varName.find(con.loopIndicator)
		if (loopIndicatorIndex == -1):
			finalString = varName
		else:
			finalString = varName[0:loopIndicatorIndex]

		finalStringName = StringName()
		finalStringName.setName(finalString)
		returnList.append(copy.deepcopy(finalStringName))
		del finalStringName

	if (len(returnList) == 0):
		sys.exit("Parser_CodeGen_Toolbox->removeSubscriptsReturnStringNames:  could not build any StringName objects for the names in the list passed in.")

	return returnList

def getVarNamesAsStringsFromLine(line):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getVarNamesAsStringsFromLine:  problem with line passed in.")

	line = line.lstrip().rstrip()

	if ( (line.startswith(con.commentChar) == True) or (len(line) == 0) ):
		return None

	line = ensureSpacesBtwnTokens_CodeGen(line)

	varList = []

	for token in line.split():
		if ( (token in con.reservedWords) or (token in con.reservedSymbols) or (token.isdigit() == True) ):
			continue

		if (token in varList):
			continue

		varList.append(token)

	if (len(varList) == 0):
		return None

	return varList

def getVarNamesAsStringNamesFromLine(line):
	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getVarNamesAsStringNamesFromLine:  problem with line passed in.")

	line = line.lstrip().rstrip()

	if ( (line.startswith(con.commentChar) == True) or (len(line) == 0) ):
		return None

	line = ensureSpacesBtwnTokens_CodeGen(line)

	varList = []
	namesAsStrings = []

	for token in line.split():
		if ( (token in con.reservedWords) or (token in con.reservedSymbols) or (token.isdigit() == True) ):
			continue

		if (token in namesAsStrings):
			continue

		namesAsStrings.append(token)

		nextStringNameObj = StringName()
		nextStringNameObj.setName(token)
		varList.append(copy.deepcopy(nextStringNameObj))
		del nextStringNameObj

	if (len(varList) == 0):
		return None

	return varList

def getLineInfoFromSourceCodeLines(sourceCodeLines, numSpacesPerTab):
	if ( (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLineInfoFromSourceCodeLines:  problem with source code lines passed in.")

	if ( (numSpacesPerTab == None) or (type(numSpacesPerTab).__name__ != con.intTypePython) or (numSpacesPerTab < 1) ):
		sys.exit("Parser_CodeGen_Toolbox->getLineInfoFromSourceCodeLines:  problem with the number of spaces per tab passed in.")

	lineNumber = 0
	lineInfoList = []
	
	for line in sourceCodeLines:
		lineNumber += 1

		if (isLineOnlyWhiteSpace(line) == True):
			continue

		nextLineInfoObj = LineInfo()
		nextLineInfoObj.setLineNo(lineNumber)
		numSpaces = getNumIndentedSpaces(line)
		if ( (numSpaces == None) or (type(numSpaces).__name__ != con.intTypePython) or (numSpaces < 0) ):
			sys.exit("Parser_CodeGen_Toolbox->getLineInfoFromSourceCodeLines:  problem with number of spaces extracted from one of the lines passed in.")
		nextLineInfoObj.setNumIndentSpaces(numSpaces, numSpacesPerTab)
		varNames = getVarNamesAsStringNamesFromLine(line)
		if (varNames != None):
			if ( (type(varNames).__name__ != con.listTypePython) or (len(varNames) == 0) ):
				sys.exit("Parser_CodeGen_Toolbox->getLineInfoFromSourceCodeLines:  problem with list returned from getVarNamesAsStringNamesFromLine.")
			nextLineInfoObj.setVarNames(varNames)

		lineInfoList.append(copy.deepcopy(nextLineInfoObj))
		del nextLineInfoObj

	if (len(lineInfoList) == 0):
		sys.exit("Parser_CodeGen_Toolbox->getLineInfoFromSourceCodeLines:  could not extract line information for any of the lines passed in.")

	return lineInfoList

def determineIfWithinQuotes(lineOfCode, R_index, withinQuotes, lastQuoteChar):
	if ( (lineOfCode == None) or (type(lineOfCode).__name__ != con.strTypePython) or (len(lineOfCode) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->determineIfWithinQuotes:  problem with line of code parameter passed in.")

	if ( (R_index == None) or (type(R_index).__name__ != con.intTypePython) or (R_index < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->determineIfWithinQuotes:  problem with right index number passed in.")

	if ( (withinQuotes != None) and (type(withinQuotes).__name__ != con.booleanType) ):
		sys.exit("Parser_CodeGen_Toolbox->determineIfWithinQuotes:  problem with parameter passed in that indicates whether we're within quotes or not.")

	if ( (lastQuoteChar != None) and (lastQuoteChar not in con.quoteCharTypes) ):
		sys.exit("Parser_CodeGen_Toolbox->determineIfWithinQuotes:  problem with last quote character passed in.")

	if (R_index == 0):
		if (lineOfCode[R_index] == con.singleQuote):
			return (True, con.singleQuote)
		if (lineOfCode[R_index] == con.doubleQuote):
			return (True, con.doubleQuote)
		return (False, None)

	if (lineOfCode[R_index - 1] == con.backSlash):
		return (withinQuotes, lastQuoteChar)

	if (lineOfCode[R_index] not in con.quoteCharTypes):
		return (withinQuotes, lastQuoteChar)

	currentQuoteChar = lineOfCode[R_index]

	if (withinQuotes == True):
		if (lastQuoteChar == con.singleQuote):
			if (currentQuoteChar == con.singleQuote):
				return (False, None)
			elif (currentQuoteChar == con.doubleQuote):
				return (withinQuotes, lastQuoteChar)
		elif (lastQuoteChar == con.doubleQuote):
			if (currentQuoteChar == con.singleQuote):
				return (withinQuotes, lastQuoteChar)
			elif (currentQuoteChar == con.doubleQuote):
				return (False, None)
	elif (withinQuotes == False):
		if (currentQuoteChar == con.singleQuote):
			return (True, con.singleQuote)
		elif (currentQuoteChar == con.doubleQuote):
			return (True, con.doubleQuote)

	sys.exit("Parser_CodeGen_Toolbox->determineIfWithinQuotes:  reached end of function without finding case for the input parameters passed in.")

def ensureSpacesBtwnTokens_CodeGen(lineOfCode):
	if ( (lineOfCode == None) or (type(lineOfCode).__name__ != con.strTypePython) or (len(lineOfCode) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->ensureSpacesBtwnTokens_CodeGen:  problem with line of code parameter passed in.")

	if (len(lineOfCode) < 3):
		return lineOfCode

	lenOfLine = len(lineOfCode)
	if (lineOfCode[lenOfLine - 1] == con.newLineChar):
		lineOfCode = lineOfCode[0:(lenOfLine-1)]
	
	L_index = 0
	R_index = 0
	withinQuotes = False
	lastQuoteChar = None

	while (True):
		checkForSpace = False
		(withinQuotes, lastQuoteChar) = determineIfWithinQuotes(lineOfCode, R_index, withinQuotes, lastQuoteChar)
		lenOfLine = len(lineOfCode)
		if (withinQuotes == True):
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
			if ( (R_index+1) <= (lenOfLine - 1) ) and (lineOfCode[R_index+1] == '='):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '&'):
			if ( (R_index+1) <= (lenOfLine-1) ) and (lineOfCode[R_index+1] == '&'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '/'):
			if ( (R_index+1) <= (lenOfLine - 1) ) and (lineOfCode[R_index+1] == '/'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '|'):
			if ( (R_index+1) <= (lenOfLine - 1) ) and (lineOfCode[R_index+1] == '|'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '*'):
			if ( (R_index+1) <= (lenOfLine - 1) ) and (lineOfCode[R_index+1] == '*'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == 'H'):
			if ( (R_index+1) <= (lenOfLine - 1) ) and (lineOfCode[R_index+1] == '('):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		elif (lineOfCode[R_index] == 'e'):
			if ( (R_index+1) <= (lenOfLine - 1) ) and ( (lineOfCode[R_index+1] == '(') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False

		if ( (checkForSpace == True) and (L_index == 0) ):
			if (lineOfCode[R_index+1] != con.space):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:(R_index+1)] + con.space + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:(R_index+1)] + con.space + lineOfCode[(R_index+1):lenOfLine]
				R_index += 2
			else:
				R_index += 1
		elif ( (checkForSpace == True) and (R_index == (len(lineOfCode)-1) ) ):
			if (lineOfCode[L_index-1] != con.space):
				lenOfLine = len(lineOfCode)
				if (L_index == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + con.space + lineOfCode[L_index]
				else:
					lineOfCode = lineOfCode[0:L_index] + con.space + lineOfCode[L_index:lenOfLine]
			break
		elif (checkForSpace == True):
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
		if (R_index >= lenOfLine):
			break

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

def writeFunctionFromCodeToString(sourceCodeLines, startLineNo, endLineNo, extraTabsPerLine, numSpacesPerTab, removeSelf=False):
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

	numTabsFirstLine = determineNumTabsFromSpaces(numSpacesFirstLine, numSpacesPerTab)
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
		numTabs = determineNumTabsFromSpaces(numSpaces, numSpacesPerTab)
		numTabsForThisLine = numTabs - numTabsFirstLine
		line = extractedLines[index].lstrip().rstrip()
		if ( (extraTabsPerLine + numTabsForThisLine) > 0):
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

def determineNumTabsFromSpaces(numSpaces, numSpacesPerTab):
	if ( (numSpaces == None) or (type(numSpaces).__name__ != con.intTypePython) or (numSpaces < 0) ):
		sys.exit("Parser_CodeGen_Toolbox->determineNumTabsFromSpaces:  problem with number of spaces parameter passed in.")

	if ( (numSpacesPerTab == None) or (type(numSpacesPerTab).__name__ != con.intTypePython) or (numSpacesPerTab < 1) ):
		sys.exit("Parser_CodeGen_Toolbox->determineNumTabsFromSpaces:  problem with number of spaces per tab passed in.")

	if ( (numSpaces % numSpacesPerTab) != 0):
		sys.exit("Parser_CodeGen_Toolbox->determineNumTabsFromSpaces:  number of spaces passed in (" + numSpaces + ") is not a multiple of the number of spaces per tab (" + numSpacesPerTab + ")")

	return (int(numSpaces / numSpacesPerTab))

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

def getFunctionArgMappings(functionNames, functionArgNames, lenFunctionArgDefaults, myASTParser):
	if ( (functionNames == None) or (type(functionNames).__name__ != con.dictTypePython) or (len(functionNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problem with the function names passed in.")

	if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problem with the function argument names passed in.")

	if ( (lenFunctionArgDefaults == None) or (type(lenFunctionArgDefaults).__name__ != con.dictTypePython) or (len(lenFunctionArgDefaults) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problem with the length of function argument defaults parameter passed in.")

	if (myASTParser == None):
		sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  myASTParser passed in is of None type.")

	functionArgMappings = {}

	for funcName in functionNames:
		funcArgMapList = getFunctionArgMappings_OneFunction(functionNames[funcName], functionArgNames, lenFunctionArgDefaults)
		if ( (funcArgMapList == None) or (type(funcArgMapList).__name__ != con.listTypePython) ):
			sys.exit("Parser_CodeGen_Toolbox->getFunctionArgMappings:  problems with value returned from getFunctionArgMappings_OneFunction.")

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

	myVarVisitor = ASTVarVisitor(myASTParser)
	myVarVisitor.visit(verifyEqNode)
	varsVerifyEq = copy.deepcopy(myVarVisitor.getVarNameDict())

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
