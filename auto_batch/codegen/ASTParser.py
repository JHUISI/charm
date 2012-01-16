import ast, con, copy, sys
from StringName import StringName
from StringValue import StringValue
from IntegerValue import IntegerValue
from FloatValue import FloatValue
from FunctionArgMap import FunctionArgMap
from CallValue import CallValue
from SubscriptName import SubscriptName
from VariableNamesValue import VariableNamesValue

def getPrimaryNameOfNameObject(nameObject):
	if ( (nameObject == None) or (type(nameObject).__name__ not in con.variableNameTypes) ):
		sys.exit("ASTParser->getPrimaryNameOfNameObject:  problem with name object passed in to function.")

	nameType = type(nameObject).__name__

	if (nameType == con.stringName):
		return nameObject.getStringVarName()
	elif (nameType == con.subscriptName):
		return nameObject.getValue().getStringVarName()
	else:
		sys.exit("ASTParser->getPrimaryNameOfNameObject:  this function does not include logic for all of the supported Name types.")

def getStringListOfStructItems(struct):
	if ( (struct == None) or (len(struct) == 0) ):
		sys.exit("ASTParser->getStringListOfStructItems:  problem with structure passed in.")

	stringList = []

	for key in struct:
		if (key == None):
			sys.exit("ASTParser->getStringListOfStructItems:  one of the keys of the structure passed in is of None type.")

		try:
			stringRepOfKey = key.getStringVarName()
		except:
			sys.exit("ASTParser->getStringListOfStructItems:  problem when running the getStringVarName() method on one of the keys of the structure passed in.")

		if ( (stringRepOfKey == None) or (type(stringRepOfKey).__name__ != con.strTypePython) or (len(stringRepOfKey) == 0) ):
			sys.exit("ASTParser->getStringListOfStructItems:  problem with value returned from getStringVarName() on one of the keys.")

		stringList.append(stringRepOfKey)

	if (len(stringList) == 0):
		sys.exit("ASTParser->getStringListOfStructItems:  could not extract the string representations of any of the keys of the structure passed in.")

	return stringList

def getValueOfLastLine(dict):
	if ( (dict == None) or (len(dict) == 0) ):
		sys.exit("ASTParser->getValueOfLastLine:  problem with dictionary passed in.")

	keys = list(dict.keys())
	keys.sort()
	lenKeys = len(keys)
	return dict[keys[lenKeys-1]]

class GetLineNosOfNodeType(ast.NodeVisitor):
	def __init__(self, nodeType):
		self.lineNos = []
		self.nodeType = nodeType

	def generic_visit(self, node):
		if (type(node).__name__ == self.nodeType):
			currentLineNo = node.lineno
			if (currentLineNo not in self.lineNos):
				self.lineNos.append(currentLineNo)

		ast.NodeVisitor.generic_visit(self, node)

	def getLineNos(self):
		return self.lineNos

class ASTGetGlobalDeclVars(ast.NodeVisitor):
	def __init__(self):
		self.globalDeclVars = []
		self.myASTParser = ASTParser()
		if ( (self.myASTParser == None) or (type(self.myASTParser).__name__ != con.ASTParser) ):
			sys.exit("ASTParser->ASTGetGlobalDeclVars->__init__:  could not obtain an ASTParser object.")

	def visit_Global(self, node):
		try:
			namesList = node.names
		except:
			sys.exit("ASTParser->ASTGetGlobalDeclVars->visit_Global:  could not obtain global names list.")

		for name in namesList:
			stringNameToAdd = StringName()
			stringNameToAdd.setName(name)
			lineNumber = self.myASTParser.getLineNumberOfNode(node)
			stringNameToAdd.setLineNo(lineNumber)
			self.globalDeclVars.append(copy.deepcopy(stringNameToAdd))
			del stringNameToAdd

	def getGlobalDecVars(self):
		if (len(self.globalDeclVars) == 0):
			return None

		return self.globalDeclVars

class ASTGetVariableNames(ast.NodeVisitor):
	def __init__(self):
		self.varNamesAsStringNameList = []
		self.varNamesAsStrings = []
		self.varNamesValue = None
		self.myASTParser = ASTParser()

	def visit_Name(self, node):
		try:
			nodeName = node.id
		except:
			sys.exit("ASTParser->ASTGetVariableNames->visit_Name:  could not obtain the name of the node.")

		if (nodeName in con.reservedWords):
			return

		if (nodeName in self.varNamesAsStrings):
			return

		varNameAsStringName = StringName()
		varNameAsStringName.setName(nodeName)
		varNameAsStringName.setLineNo(self.myASTParser.getLineNumberOfNode(node))

		self.varNamesAsStringNameList.append(varNameAsStringName)
		self.varNamesAsStrings.append(nodeName)

	def getVarNamesValue(self):
		if (len(self.varNamesAsStringNameList) == 0):
			return None

		retValue = VariableNamesValue()
		retValue.setVarNamesList(self.varNamesAsStringNameList)

		return retValue

class GetLastLineOfFunction(ast.NodeVisitor):
	def __init__(self):
		self.lastLine = 0

	def generic_visit(self, node):
		try:
			if (node.lineno > self.lastLine):
				self.lastLine = node.lineno
		except:
			pass
		ast.NodeVisitor.generic_visit(self, node)

	def getLastLine(self):
		if (self.lastLine == 0):
			sys.exit("ASTParser->GetLastLineOfFunction->getLastLine:  could not extract the last line of the function node passed in.")

		return self.lastLine

class ASTImportNodeLineNoVisitor(ast.NodeVisitor):
	def __init__(self):
		self.lineNos = []

	def visit_ImportFrom(self, node):
		self.lineNos.append(node.lineno)

	def visit_Import(self, node):
		self.lineNos.append(node.lineno)

	def getLineNos(self):
		if (len(self.lineNos) == 0):
			return None

		return self.lineNos

class ASTReturnNodeVisitor(ast.NodeVisitor):
	def __init__(self):
		self.returnNodeList = []

	def visit_Return(self, node):
		self.returnNodeList.append(node)

	def getReturnNodeList(self):
		if (len(self.returnNodeList) == 0):
			return None

		return self.returnNodeList

class ASTVariableNamesVisitor(ast.NodeVisitor):
	def __init__(self):
		self.variableNames = []
		self.myASTParser = ASTParser()
		if ( (self.myASTParser == None) or (type(self.myASTParser).__name__ != con.ASTParser) ):
			sys.exit("ASTVariableNamesVisitor->__init__:  problem with value returned from ASTParser().")

	def visit_Subscript(self, node):
		subscriptObject = self.myASTParser.buildSubscriptObjectFromNode(node)
		if ( (subscriptObject == None) or (type(subscriptObject).__name__ != con.subscriptName) ):
			sys.exit("ASTVariableNamesVisitor->visit_Subscript:  problem with value returned from ASTParser->buildSubscriptObjectFromNode.")

		self.variableNames.append(subscriptObject)

	def visit_Name(self, node):
		variableObject = self.myASTParser.buildObjectFromNode(node)
		if (variableObject == None):
			sys.exit("ASTVariableNamesVisitor->visit_Name:  problem with value returned from ASTParser->buildObjectFromNode.")

		self.variableNames.append(variableObject)

	def getVariableNames(self):
		if (len(self.variableNames) == 0):
			return None

		return self.variableNames

'''
class ASTFuncArgMapsVisitor(ast.NodeVisitor):
	def __init__(self, functionArgNames, lenFunctionArgDefaults):
		if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the function argument names passed in.")

		if ( (lenFunctionArgDefaults == None) or (type(lenFunctionArgDefaults).__name__ != con.dictTypePython) or (len(lenFunctionArgDefaults) == 0) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the length of function argument defaults dictionary.")

		self.myASTParser = ASTParser()
		if ( (self.myASTParser == None) or (type(self.myASTParser).__name__ != con.ASTParser) ):
			sys.exit("ASTFuncArgMapsVisitor->__init__:  problem with the value returned from ASTParser().")

		self.functionArgNames = functionArgNames
		self.lenFunctionArgDefaults = lenFunctionArgDefaults
		self.functionArgMappings = []

	def getDestFuncName(self, node):
		if ( (node == None) or (type(node).__name__ != con.callTypeAST) ):
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with node passed in to function.")

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

		#if (funcValueName != con.self):
			#return None

		try:
			funcAttrName = node.func.attr
		except:
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  could not obtain the function's attribute name from the node passed in.")

		funcAttrNameObject = self.myASTParser.buildStringName(node, funcAttrName)
		if ( (funcAttrNameObject == None) or (type(funcAttrNameObject).__name__ != con.stringName) ):
			sys.exit("ASTFuncArgMapsVisitor->getDestFuncName:  problem with value returned from ASTParser->buildStringName for function attribute name.")

		return funcAttrNameObject

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
			#sys.exit("ASTFuncArgMapsVisitor->visit_Call:  " + destFuncName + " is not in the function argument names object passed in.")

		destArgNames = self.functionArgNames[destFuncName.getStringVarName()]

		callerArgList = self.myASTParser.getCallArgList(node)

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
'''

class ASTFunctionArgNames(ast.NodeVisitor):
	def __init__(self):
		self.myASTParser = ASTParser()
		if ( (self.myASTParser == None) or (type(self.myASTParser).__name__ != con.ASTParser) ):
			sys.exit("ASTParser->ASTFunctionArgNames->__init__:  problem with value returned from ASTParser constructor.")

		self.functionArgNames = {}
		self.lenFunctionArgDefaults = {}

	def visit_FunctionDef(self, node):
		try:
			nodeName = node.name
		except:
			sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not obtain the name of the function.")

		try:
			argList = node.args.args
		except:
			sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not obtain the arguments list for function " + nodeName)

		if (len(argList) == 0):
			self.functionArgNames[nodeName] = None
			return

		argNamesList = []

		for argItr in argList:
			try:
				argToAdd = argItr.arg
			except:
				sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not extract one of the argument names of function " + nodeName)

			if (argToAdd != con.self):
				argToAddStringName = self.myASTParser.buildStringName(node, argToAdd)
				argNamesList.append(argToAddStringName)

		self.functionArgNames[nodeName] = argNamesList

		try:
			lenDefaultArgs = len(node.args.defaults)
		except:
			sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not obtain the length of the default argument array.")

		self.lenFunctionArgDefaults[nodeName] = lenDefaultArgs

	def getFunctionArgNames(self):
		if (len(self.functionArgNames) == 0):
			return None

		return self.functionArgNames

	def getLenFunctionArgDefaults(self):
		if (len(self.lenFunctionArgDefaults) == 0):
			return None

		return self.lenFunctionArgDefaults

class ASTFunctionNamesVisitor(ast.NodeVisitor):
	def __init__(self):
		self.functionNames = {}

	def visit_FunctionDef(self, node):
		try:
			nodeName = node.name
		except:
			sys.exit("ASTParser->ASTFunctionNamesVisitor->visit_FunctionDef:  could not obtain the name of the function.")

		self.functionNames[nodeName] = node

	def getFunctionNames(self):
		if (len(self.functionNames) == 0):
			return None

		return self.functionNames

class ASTEquationVisitor(ast.NodeVisitor):
	def __init__(self):
		self.equations = {}

	def visit_Compare(self, node):
		loopCounter = 0
		for childNode in ast.iter_child_nodes(node):
			if ( (loopCounter == 1) and (ast.dump(childNode) == con.equals) ):
				self.equations[node.lineno] = node
			loopCounter += 1
			if (loopCounter > 1):
				break

	def getLastEquation(self):
		if (len(self.equations) == 0):
			return None

		return getValueOfLastLine(self.equations)

class ASTFunctionVisitor(ast.NodeVisitor):
	def __init__(self, functionName):
		if (len(functionName) == 0):
			sys.exit("ASTParser->ASTFunctionVisitor->init:  function named passed in is of length zero.")

		self.functionName = functionName
		self.functionNodes = []

	def visit_FunctionDef(self, node):
		if (node.name == self.functionName):
			self.functionNodes.append(node)

	def getFunctionNodes(self):
		if (len(self.functionNodes) == 0):
			return None

		return self.functionNodes

class ASTParser:
	def __init__(self):
		self.baseNode = None
		self.sourceLinesList = None

	def getASTNodeFromFile(self, fileName):
		if (len(fileName) == 0):
			sys.exit("ASTParser->getASTNodeFromFile:  file name passed in has a length of zero.")

		try:
			self.sourceLinesList = open(fileName, 'r').readlines()
		except:
			sys.exit("ASTParser->getASTNodeFromFile:  error when running \"open\" system call on the file name passed in.")

		if (len(self.sourceLinesList) == 0):
			sys.exit("ASTParser->getASTNodeFromFile:  retrieved zero lines of source code from file name passed in.")

		sourceLines = ""
		for line in self.sourceLinesList:
			sourceLines += line

		try:
			returnNode = ast.parse(sourceLines)
		except:
			sys.exit("ASTParser->getASTNodeFromFile:  error when running \"ast.parse\" on the source-code lines of the file name passed in.")

		return returnNode

	def getImportLineNos(self, rootNode):
		if (rootNode == None):
			sys.exit("ASTParser->getImportLineNos:  node passed in is of None type.")

		importLineNoObj = ASTImportNodeLineNoVisitor()
		importLineNoObj.visit(rootNode)
		return importLineNoObj.getLineNos()

	def getPrimaryNameOfNameObject(self, nameObject):
		return getPrimaryNameOfNameObject(nameObject)

	def getStringListOfStructItems(self, struct):
		return getStringListOfStructItems(struct)

	def getStartOrEndLineOfBlock(self, codeLines, lineInfo, lineNumber, numTabsOnVerifyLine, getStartLine, minLine, maxLine):

		while (True):
			if (getStartLine == True):
				lineNumber -= 1
			else:
				lineNumber += 1

			if ( (lineNumber <= minLine) or (lineNumber >= maxLine) ):
				return lineNumber

			if (lineNumber not in lineInfo):
				continue

			numTabsOnThisLine = lineInfo[lineNumber].getNumIndentTabs()
			if ( (numTabsOnThisLine) != (numTabsOnVerifyLine + 1) ):
				continue

			lineOfCode = codeLines[lineNumber - 1].lstrip().rstrip()
			if ( (lineOfCode.startswith('elif ') == True) or (lineOfCode.startswith('else:') == True) ):
				continue

			return lineNumber

	def getStartEndLineCheckBlocks(self, codeLines, lineInfo, startLine, endLine, numTabsOnVerifyLine):
		lineNoInList = startLine - 2
		endLineNoInList = endLine - 1

		withinIfBranch = False

		retList = []

		while (lineNoInList <= (endLineNoInList - 1)):
			lineNoInList += 1

			lineOfCode = codeLines[lineNoInList].lstrip().rstrip()
			if (lineOfCode == 'return False'):
				startLineOfCheckBlock = self.getStartOrEndLineOfBlock(codeLines, lineInfo, lineNoInList + 1, numTabsOnVerifyLine, True, startLine, endLine)
				endLineOfCheckBlock = self.getStartOrEndLineOfBlock(codeLines, lineInfo, lineNoInList + 1, numTabsOnVerifyLine, False, startLine, endLine)
				endLineOfCheckBlock -= 1
				retList.append((startLineOfCheckBlock, endLineOfCheckBlock))

		if (len(retList) == 0):
			return None

		return retList

	def getFuncNameFromCallNode(self, node):
		if ( (node == None) or (type(node).__name__ != con.callTypeAST) ):
			sys.exit("ASTParser->getFuncNameFromCallNode:  problem with node passed in to function.")

		try:
			funcName = node.func.id
		except:
			funcName = None

		if (funcName != None):
			funcNameObject = self.buildStringName(node, funcName)
			if ( (funcNameObject == None) or (type(funcNameObject).__name__ != con.stringName) ):
				sys.exit("ASTParser->getFuncNameFromCallNode:  problem with value returned from ASTParser->buildStringName for function name.")

			return (funcNameObject, None)

		try:
			funcValueName = node.func.value.id
		except:
			print("ASTParser->getFuncNameFromCallNode:  could not obtain any information about the call represented by the node passed in.  THIS SHOULD BE FIXED.")
			funcValueName = None

		try:
			funcAttrName = node.func.attr
		except:
			sys.exit("ASTParser->getFuncNameFromCallNode:  could not obtain the function's attribute name from the node passed in.")

		funcValueNameObject = None

		if (funcValueName != None):
			funcValueNameObject = self.buildStringName(node, funcValueName)
			if ( (funcValueNameObject == None) or (type(funcValueNameObject).__name__ != con.stringName) ):
				sys.exit("ASTParser->getFuncNameFromCallNode:  problem with value returned from buildStringName for function value name.")

		funcAttrNameObject = self.buildStringName(node, funcAttrName)
		if ( (funcAttrNameObject == None) or (type(funcAttrNameObject).__name__ != con.stringName) ):
			sys.exit("ASTParser->getFuncNameFromCallNode:  problem with value returned from buildStringName for function attribute name.")

		return (funcValueNameObject, funcAttrNameObject)

	def getLineNumberOfNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getLineNumberOfNode:  node passed in is of None type.")

		try:
			lineNo = node.lineno
		except:
			sys.exit("ASTParser->getLineNumberOfNode:  could not obtain the line number of the node passed in.")

		if (type(lineNo) is not int):
			sys.exit("ASTParser->getLineNumberOfNode:  line number obtained from node is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("ASTParser->getLineNumberOfNode:  line number obtained from node is less than one.")

		return lineNo

	def getFunctionNames(self, node):
		if (node == None):
			sys.exit("ASTParser->getFunctionNames:  node passed in is of None type.")

		myFuncNamesVisitor = ASTFunctionNamesVisitor()
		myFuncNamesVisitor.visit(node)
		return myFuncNamesVisitor.getFunctionNames()

	def getFunctionArgNamesAndDefaultLen(self, node):
		if (node == None):
			sys.exit("ASTParser->getFunctionArgNamesAndDefaultLen:  node passed in is of None type.")

		myFuncArgNamesVisitor = ASTFunctionArgNames()
		myFuncArgNamesVisitor.visit(node)
		return (myFuncArgNamesVisitor.getFunctionArgNames(), myFuncArgNamesVisitor.getLenFunctionArgDefaults())

	'''
	def getFunctionArgMappings(self, funcNode, functionArgNames, lenFunctionArgDefaults):
		if (funcNode == None):
			sys.exit("ASTParser->getFunctionArgMappings:  function node passed in is of None type.")

		if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
			sys.exit("ASTParser->getFunctionArgMappings:  problem with the function argument names passed in.")

		if ( (lenFunctionArgDefaults == None) or (type(lenFunctionArgDefaults).__name__ != con.dictTypePython) or (len(lenFunctionArgDefaults) == 0) ):
			sys.exit("ASTParser->getFunctionArgMappings:  problem with length of function default arguments parameter passed in.")

		myFuncArgMapsVisitor = ASTFuncArgMapsVisitor(functionArgNames, lenFunctionArgDefaults)
		myFuncArgMapsVisitor.visit(funcNode)
		return myFuncArgMapsVisitor.getFunctionArgMappings()
	'''

	def removeVarsFromListWithStringName(self, varList, varName):
		if ( (varList == None) or (type(varList).__name__ != con.listTypePython) or (len(varList) == 0) ):
			sys.exit("ASTParser->removeVarsFromListWithName:  problem with the variable list passed in.")

		if ( (varName == None) or (type(varName).__name__ != con.strTypePython) or (len(varName) == 0) ):
			sys.exit("ASTParser->removeVarsFromListWithName:  problem with the variable name passed in.")

		returnVarList = []

		for varEntry in varList:
			if (type(varEntry).__name__ != con.stringName):
				returnVarList.append(copy.deepcopy(varEntry))
				continue

			varEntryName = varEntry.getName()

			if (varEntryName != varName):
				returnVarList.append(copy.deepcopy(varEntry))

		del varList
		return returnVarList

	def getAllVariableNames(self, node):
		if (node == None):
			sys.exit("ASTParser->getAllVariableNames:  node passed in is of None type.")

		varNamesVisitor = ASTVariableNamesVisitor()
		varNamesVisitor.visit(node)
		variableNames = varNamesVisitor.getVariableNames()

		return variableNames

	def getReturnNodeList(self, funcNode):
		if (funcNode == None):
			sys.exit("ASTParser->getReturnNodeList:  function node passed in is of None type.")

		retNodeVisitor = ASTReturnNodeVisitor()
		retNodeVisitor.visit(funcNode)
		return retNodeVisitor.getReturnNodeList()

	def getOperandNodeOfUnaryOp(self, node):
		if ( (node == None) or (type(node).__name__ != con.unaryOpTypeAST) ):
			sys.exit("ASTParser->getOperandNodeOfUnaryOp:  problem with node passed in to function.")

		try:
			retNode = node.operand
		except:
			sys.exit("ASTParser->getOperandNodeOfUnaryOp:  could not extract operand node of the node passed in to the function.")

		return retNode

	def getLeftNodeOfBinOp(self, node):
		if ( (node == None) or (type(node).__name__ != con.binOpTypeAST) ):
			sys.exit("ASTParser->getLeftNodeOfBinOp:  problem with node passed in to function.")

		try:
			retNode = node.left
		except:
			sys.exit("ASTParser->getLeftNodeOfBinOp:  could not extract left node of the node passed in to the function.")

		return retNode

	def getRightNodeOfBinOp(self, node):
		if ( (node == None) or (type(node).__name__ != con.binOpTypeAST) ):
			sys.exit("ASTParser->getRightNodeOfBinOp:  problem with node passed in to function.")

		try:
			retNode = node.right
		except:
			sys.exit("ASTParser->getRightNodeOfBinOp:  could not extract right node of the node passed in to the function.")

		return retNode

	def getOpTypeOfBinOp(self, node):
		if ( (node == None) or (type(node).__name__ != con.binOpTypeAST) ):
			sys.exit("ASTParser->getOpTypeOfBinOp:  problem with the node passed in to the function.")

		retType = self.getOpTypeOfOp(node)

		if ( (retType == None) or (type(retType).__name__ != con.strTypePython) or (retType not in con.opTypesAST) ):
			sys.exit("ASTParser->getOpTypeOfBinOp:  problem with value returned from getOpTypeOfOp.")

		return retType

	def getOpTypeOfUnaryOp(self, node):
		if ( (node == None) or (type(node).__name__ != con.unaryOpTypeAST) ):
			sys.exit("ASTParser->getOpTypeOfUnaryOp:  problem with node passed in to function.")

		retType = self.getOpTypeOfOp(node)

		if ( (retType == None) or (type(retType).__name__ != con.strTypePython) or (retType not in con.unaryOpTypesAST) ):
			sys.exit("ASTParser->getOpTypeOfUnaryOp:  problem with value returned from getOpTypeOfOp.")

		return retType

	def getOpTypeOfOp(self, node):
		if (node == None):
			sys.exit("ASTParser->getOpTypeOfOp:  node passed in is of None type.")

		try:
			retType = type(node.op).__name__
		except:
			sys.exit("ASTParser->getOpTypeOfOp:  could not extract the type of the op node of the node passed in to the function.")

		return retType

	def getDictKeyNodes(self, node):
		if ( (node == None) or (type(node).__name__ != con.dictTypeAST) ):
			sys.exit("ASTParser->getDictKeyNodes:  problem with node passed in to function.")

		try:
			keyNodes = node.keys
		except:
			sys.exit("ASTParser->getDictKeyNodes:  could not extract dictionary key nodes from node passed in to function.")

		return keyNodes

	def getDictKeys(self, node):
		if (node == None):
			sys.exit("ASTParser->getDictKeys:  node passed in is of None type.")

		if (type(node).__name__ != con.dictTypeAST):
			sys.exit("ASTParser->getDictKeys:  node passed in is not of type " + con.dictTypeAST)

		try:
			dictKeys = node.keys
		except:
			sys.exit("ASTParser->getDictKeys:  could not obtain the keys list from the node passed in.")

		returnKeysList = []

		for key in dictKeys:
			keyObject = self.buildObjectFromNode(key)
			if (keyObject == None):
				sys.exit("ASTParser->getDictKeys:  return value from buildObjectFromNode is of None type.")

			returnKeysList.append(keyObject)

		if (len(returnKeysList) == 0):
			sys.exit("ASTParser->getDictKeys:  could not extract any of the keys from the node passed in.")

		return returnKeysList

	def getDictValueNodes(self, node):
		if ( (node == None) or (type(node).__name__ != con.dictTypeAST) ):
			sys.exit("ASTParser->getDictValueNodes:  problem with node passed in to function.")

		try:
			valueNodes = node.values
		except:
			sys.exit("ASTParser->getDictValueNodes:  could not extract the dictionary value nodes from the node passed in to the function.")

		return valueNodes

	def getDictValues(self, node):
		if (node == None):
			sys.exit("ASTParser->getDictValues:  node passed in is of None type.")

		if (type(node).__name__ != con.dictTypeAST):
			sys.exit("ASTParser->getDictValues:  node passed in is not of type " + con.dictTypeAST)

		try:
			dictValues = node.values
		except:
			sys.exit("ASTParser->getDictValues:  could not obtain the values list from the node passed in.")

		returnValuesList = []

		for value in dictValues:
			valueObject = self.buildObjectFromNode(value)
			if (valueObject == None):
				sys.exit("ASTParser->getDictValues:  return value from buildObjectFromNode is of None type.")

			returnValuesList.append(valueObject)

		if (len(returnValuesList) == 0):
			sys.exit("ASTParser->getDictValues:  could not extract any of the values from the node passed in.")

		return returnValuesList

	def getCallType(self, node):
		if (node == None):
			sys.exit("ASTParser->getCallType:  node passed in is of None type.")

		callType = None

		try:
			callType = node.func.id
		except:
			pass

		if (callType == con.dotProdType):
			return con.dotProdType

		try:
			callType = node.func.attr
		except:
			pass

		if (callType in con.hashTypesCharm):
			return con.hashType
		if (callType == con.randomType):
			return con.randomType
		if (callType == con.initType):
			return con.initType

		return None

	def getHashNodeFromLambda(self, node):
		if (node == None):
			sys.exit("ASTParser->getHashNodeFromLambda:  node passed in is of None type.")

		try:
			returnNode = node.body
		except:
			sys.exit("ASTParser->getHashNodeFromLambda:  could not obtain the \"body\" node of the node passed in.")

		return returnNode

	def isLambdaAHashCall(self, node):
		if (node == None):
			sys.exit("ASTParser->isLambdaAHashCall:  node passed in is of None type.")

		try:
			funcAttr = node.body.func.attr
		except:
			return False

		if (funcAttr in con.hashTypesCharm):
			return True

		return False

	def getLambdaArgOrder(self, argName, lambdaArgs):
		if ( (argName == None) or (len(argName) == 0) or (type(argName) is not str) or (lambdaArgs == None) or (len(lambdaArgs) == 0) or (type(lambdaArgs) is not list) ):
			sys.exit("ASTParser->getLambdaArgOrder:  problem with inputs to function.")

		lenLambdaArgs = len(lambdaArgs)

		for index in range(0, lenLambdaArgs):
			lambdaArgInLoop = lambdaArgs[index]
			if ( (lambdaArgInLoop == None) or (type(lambdaArgInLoop).__name__ != con.stringName) ):
				sys.exit("ASTParser->getLambdaArgOrder:  problem with one of the Lambda arguments.")

			lambdaArgNameAsStr = lambdaArgInLoop.getStringVarName()
			if ( (lambdaArgNameAsStr == None) or (type(lambdaArgNameAsStr).__name__ != con.strTypePython) or (len(lambdaArgNameAsStr) == 0) ):
				sys.exit("ASTParser->getLambdaArgOrder:  problem with value returned from getStringVarName() on one of the Lambda arguments.")

			if (argName == lambdaArgNameAsStr):
				return index

		sys.exit("ASTParser->getLambdaArgOrder:  could not find a match for " + argName + " in the Lambda argument names.")

	def lambdaExpressionRecursion(self, node, lambdaArgs):
		if ( (node == None) or (lambdaArgs == None) or (len(lambdaArgs) == 0) ):
			sys.exit("ASTParser->lambdaExpressionRecursion:  problem with inputs to function.")

		try:
			fields = node._fields
		except:
			fields = None

		if (fields != None):
			if (fields == con.mathOp):
				left = self.lambdaExpressionRecursion(node.left, lambdaArgs)
				right = self.lambdaExpressionRecursion(node.right, lambdaArgs)
				op = self.lambdaExpressionRecursion(node.op, lambdaArgs)
				return left + " " + op + " " + right
			if (fields == con.subscriptFields):
				try:
					argName = node.value.id
				except:
					argName = None

				if (argName != None):
					argOrder = self.getLambdaArgOrder(argName, lambdaArgs)
					return con.lambdaArgBegin + str(argOrder) + con.lambdaArgEnd

		try:
			nameType = type(node).__name__
		except:
			sys.exit("ASTParser->lambdaExpressionRecursion:  could not obtain the name type of a node.")

		if (nameType == con.expTypeAST):
			return "^"
		if (nameType == con.multTypeAST):
			return "*"
		if (nameType == con.subTypeAST):
			return "-"
		if (nameType == con.addTypeAST):
			return "+"
		if (nameType == con.divTypeAST):
			return "/"

		sys.exit("ASTParser->lambdaExpressionRecursion:  could not identify this element of the lambda expression.")

	def getLambdaExpression(self, node, lambdaArgs):
		if (node == None):
			sys.exit("ASTParser->getLambdaExpression:  node passed in is of None type.")

		if (lambdaArgs == None):
			sys.exit("ASTParser->getLambdaExpression:  lambda arguments passed in are of None type.")

		if (len(lambdaArgs) == 0):
			sys.exit("ASTParser->getLambdaExpression:  lambda arguments are of length zero.")

		for arg in lambdaArgs:
			if ( (arg == None) or (type(arg).__name__ != con.stringName) ):
				sys.exit("ASTParser->getLambdaExpression:  problem with one of the lambda arguments passed in.")

		try:
			lambdaBody = node.body
		except:
			sys.exit("ASTParser->getLambdaExpression:  could not obtain the body of the node passed in.")

		expression = self.lambdaExpressionRecursion(lambdaBody, lambdaArgs)
		if (expression == None):
			sys.exit("ASTParser->getLambdaExpression:  expression returned from lambdaExpressionRecursion if of None type.")

		if (len(expression) == 0):
			sys.exit("ASTParser->getLambdaExpression:  expression returned from lambdaExpressionRecursion is of length zero.")

		if (type(expression) is not str):
			sys.exit("ASTParser->getLambdaExpression:  expression returned from lambdaExpressRecursion is not of type " + con.strTypePython)

		returnLambdaExpression = self.buildStringValue(node, expression)
		if ( (returnLambdaExpression == None) or (type(returnLambdaExpression).__name__ != con.stringValue) ):
			sys.exit("ASTParser->getLambdaExpression:  problem with value returned from self.buildStringValue.")

		return returnLambdaExpression

	def getLambdaArgNodeList(self, node):
		if ( (node == None) or (type(node).__name__ != con.lambdaType) ):
			sys.exit("ASTParser->getLambdaArgNodeList:  problem with node passed in to function.")

		try:
			argNodeList = node.args.args
		except:
			sys.exit("ASTParser->getLambdaArgNodeList:  could not extract the arguments node list from the node passed in to the function.")

		return argNodeList

	def getLambdaArgList(self, node):
		if (node == None):
			sys.exit("ASTParser->getLambdaArgList:  node passed in is of None type.")

		try:
			argList = node.args.args
		except:
			sys.exit("ASTParser->getLambdaArgList:  could not obtain the arguments list of the node passed in.")

		returnArgList = []

		for argNode in argList:
			try:
				arg = argNode.arg
			except:
				sys.exit("ASTParser->getLambdaArgList:  could not obtain one of the arguments of the node passed in.")

			if (arg == None):
				sys.exit("ASTParser->getLambdaArgList:  one of the arguments of the node passed in is of None type.")

			if (type(arg) is not str):
				sys.exit("ASTParser->getLambdaArgList:  one of the arguments of the node passed in is not of " + con.strTypePython + " type.")

			argStringName = self.buildStringName(node, arg)
			if ( (argStringName == None) or (type(argStringName).__name__ != con.stringName) ):
				sys.exit("ASTParser->getLambdaArgList:  problem with value returned from self.buildStringName.")

			returnArgList.append(argStringName)

		if (len(returnArgList) == 0):
			sys.exit("ASTParser->getLambdaArgList:  could not obtain any of the arguments of the node passed in.")

		return returnArgList

	def getArgNodeList(self, node):
		if (node == None):
			sys.exit("ASTParser->getArgNodeList:  node passed in is of None type.")

		try:
			argNodeList = node.args
		except:
			sys.exit("ASTParser->getArgNodeList:  could not extract the arguments node list from the node passed in.")

		return argNodeList

	def getCallArgList(self, node):
		if (node == None):
			sys.exit("ASTParser->getCallArgList:  node passed in is of None type.")

		try:
			argList = node.args
		except:
			sys.exit("ASTParser->getCallArgList:  could not obtain the arguments list of the node passed in.")

		returnArgList = []

		for callArgNode in argList:
			nodeObject = self.buildObjectFromNode(callArgNode)
			if (nodeObject != None):
				returnArgList.append(nodeObject)

			#nameOfNode = self.getNameOfNode(callArgNode)
			#if (nameOfNode != None):
				#returnArgList.append(nameOfNode)

		if (len(returnArgList) == 0):
			return None

		return returnArgList

	def getNameOfNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getNameOfNode:  node passed in is of None type.")

		try:
			nodeType = type(node).__name__
		except:
			sys.exit("ASTParser->getNameOfNode:  could not obtain the type of the node passed in.")

		if (nodeType == con.strOnlyTypeAST):
			return self.getStrOnly(node)
		if (nodeType == con.nameOnlyTypeAST):
			return self.getNameOnly(node)
		if (nodeType == con.numTypeAST):
			return self.getNumOnly(node)
		if (nodeType == con.subscriptTypeAST):
			return self.getSubscriptOnly(node)

		return None

	def getNumOnly(self, node):
		if (node == None):
			sys.exit("ASTParser->getNumOnly:  node passed in is of None type.")

		if (type(node).__name__ != con.numTypeAST):
			sys.exit("ASTParser->getNumOnly:  type of node passed in is not " + con.numTypeAST)

		try:
			returnNum = node.n
		except:
			sys.exit("ASTParser->getNumOnly:  could not obtain \"n\" parameter of node passed in.")

		return returnNum

	def getNameOnly(self, node):
		if (node == None):
			sys.exit("ASTParser->getNameOnly:  node passed in is of None type.")

		if (type(node).__name__ != con.nameOnlyTypeAST):
			sys.exit("ASTParser->getNameOnly:  type of node passed in is not " + con.nameOnlyTypeAST)

		try:
			returnName = node.id
		except:
			sys.exit("ASTParser->getNameOnly:  could not obtain \"id\" parameter of node passed in.")

		return returnName

	def getStrOnly(self, node):
		if (node == None):
			sys.exit("ASTParser->getStrOnly:  node passed in is of None type.")

		if (type(node).__name__ != con.strOnlyTypeAST):
			sys.exit("ASTParser->getStrOnly:  type of node passed in is not " + con.strOnlyTypeAST)

		try:
			returnStr = node.s
		except:
			sys.exit("ASTParser->getStrOnly:  could not obtain \"s\" parameter of node passed in.")

		return returnStr

	def getSubscriptOnly(self, node):
		if (node == None):
			sys.exit("ASTParser->getSubscriptOnly:  node passed in is of None type.")

		if (type(node).__name__ != con.subscriptTypeAST):
			sys.exit("ASTParser->getSubscriptOnly:  type of node passed in is not " + con.subscriptTypeAST)

		valueName = self.getNameOfNode(node.value)
		if (valueName == None):
			sys.exit("ASTParser->getSubscriptOnly:  could not obtain the value name of the node passed in.")

		sliceValueName = self.getNameOfNode(node.slice.value)
		if (sliceValueName == None):
			sys.exit("ASTParser->getSubscriptOnly:  could not obtain the slice value name of the node passed in.")

		return valueName + "[" + sliceValueName + "]"

	def buildStringName(self, node, name):
		if ( (node == None) or (name == None) or (type(name).__name__ != con.strTypePython) or (len(name) == 0) ):
			sys.exit("ASTParser->buildStringName:  problem with input parameters passed in.")

		returnStringName = StringName()
		returnStringName.setName(name)

		lineNo = self.getLineNumberOfNode(node)
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("ASTParser->buildStringName:  could not extract the line number of the node passed in.")

		returnStringName.setLineNo(lineNo)

		return returnStringName

	def buildStringValue(self, node, name):
		if ( (node == None) or (name == None) or (type(name).__name__ != con.strTypePython) or (len(name) == 0) ):
			sys.exit("ASTParser->buildStringValue:  problem with input parameters passed in.")

		returnStringValue = StringValue()
		returnStringValue.setValue(name)

		lineNo = self.getLineNumberOfNode(node)
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("ASTParser->buildStringValue:  could not extract the line number of the node passed in.")

		returnStringValue.setLineNo(lineNo)

		return returnStringValue

	def getSubscriptValueAsStringName(self, node):
		if (node == None):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  node passed in is of None type.")

		if (type(node).__name__ != con.subscriptTypeAST):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  type of node passed in is not " + con.subscriptTypeAST)

		valueName = self.getNameOfNode(node.value)
		if (valueName == None):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  could not obtain the value name of the node passed in.")

		if (type(valueName).__name__ != con.strTypePython):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  value name returned from getNameOfNode is not of type " + con.strTypePython)

		returnStringName = self.buildStringName(node, valueName)
		if ( (returnStringName == None) or (type(returnStringName).__name__ != con.stringName) ):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  problem with value returned from buildStringName.")

		return returnStringName

	def buildSubscriptObjectFromNode(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->buildSubscriptObjectFromNode:  problem with node passed in.")

		subscriptValue = self.getSubscriptValueAsStringName(node)
		if ( (subscriptValue == None) or (type(subscriptValue).__name__ != con.stringName) ):
			sys.exit("ASTParser->buildSubscriptObjectFromNode:  problem with value returned from getSubscriptValueAsStringName.")

		subscriptSlice = self.getSubscriptSlice(node)
		if (subscriptSlice == None):
			sys.exit("ASTParser->buildSubscriptObjectFromNode:  value returned from getSubscriptSlice is of None type.")

		returnSubscriptObject = SubscriptName()
		returnSubscriptObject.setValue(subscriptValue)
		returnSubscriptObject.setSlice(subscriptSlice)
		returnSubscriptObject.setLineNo(node.lineno)
		return returnSubscriptObject

	'''
	def buildCallObjectFromNode(self, node):
		if ( (node == None) or (type(node).__name__ != con.callTypeAST) ):
			sys.exit("ASTParser->buildCallObjectFromNode:  problem with node passed in.")

		argList = self.getCallArgList(node)

		try:
			funcName = node.func.id
		except:
			funcName = None

		if (funcName != None):
			returnCallObject = CallValue()

			funcNameStringNameObj = self.buildStringName(node, funcName)

			returnCallObject.setFuncName(funcNameStringNameObj)
			returnCallObject.setArgList(argList)
			returnCallObject.setLineNo(node.lineno)
			return returnCallObject

		try:
			funcValueName = node.func.value.id
		except:
			sys.exit("ASTParser->buildCallObjectFromNode:  could not extract any information about the call of the node passed in.")

		try:
			funcAttrName = node.func.attr
		except:
			sys.exit("ASTParser->buildCallObjectFromNode:  could not extract attribute name of call from the node passed in.")

		returnCallObject = CallValue()

		funcValueNameStringNameObj = self.buildStringName(node, funcValueName)
		funcAttrNameStringNameObj = self.buildStringName(node, funcAttrName)

		returnCallObject.setFuncName(funcValueNameStringNameObj)
		returnCallObject.setAttrName(funcAttrNameStringNameObj)
		returnCallObject.setArgList(argList)
		returnCallObject.setLineNo(node.lineno)
		return returnCallObject
	'''

	def buildObjectFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->buildObjectFromNode:  node passed in is of None type.")

		try:
			nodeName = self.getNameOfNode(node)
		except:
			sys.exit("ASTParser->buildObjectFromNode:  call to getNameOfNode failed.")

		try:
			nodeType = type(node).__name__
		except:
			sys.exit("ASTParser->buildObjectFromNode:  could not obtain the type of the node passed in.")

		if (nodeType == con.nameOnlyTypeAST):
			returnObject = StringName()
			returnObject.setName(nodeName)
			returnObject.setLineNo(node.lineno)
			return returnObject

		if (nodeType == con.strOnlyTypeAST):
			returnObject = StringValue()
			returnObject.setValue(nodeName)
			returnObject.setLineNo(node.lineno)
			return returnObject

		if (nodeType == con.numTypeAST):
			if (type(nodeName).__name__ == con.intTypePython):
				returnObject = IntegerValue()
				returnObject.setValue(nodeName)
				returnObject.setLineNo(node.lineno)
				return returnObject
			if (type(nodeName).__name__ == con.floatTypePython):
				returnObject = FloatValue()
				returnObject.setValue(nodeName)
				returnObject.setLineNo(node.lineno)
				return returnObject

		if (nodeType == con.callTypeAST):
			returnObject = self.buildCallObjectFromNode(node)
			if ( (returnObject == None) or (type(returnObject).__name__ != con.callValue) ):
				sys.exit("ASTParser->buildObjectFromNode:  problem with the value returned from buildCallObjectFromNode.")

			return returnObject

		if (nodeType == con.subscriptTypeAST):
			returnObject = self.buildSubscriptObjectFromNode(node)
			if ( (returnObject == None) or (type(returnObject).__name__ != con.subscriptName) ):
				sys.exit("ASTParser->buildObjectFromNode:  problem with the value returned from buildSubscriptObjectFromNode.")

			return returnObject

		sys.exit("ASTParser->buildObjectFromNode:  type of node is not currently supported.")

	def getSubscriptSliceTypeAsStringName(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptSliceTypeAsStringName:  problem with node passed in.")

		retStringName = StringName()

		typeIsValue = True

		try:
			dummyVariable = node.slice.value
		except:
			typeIsValue = False

		if (typeIsValue == True):
			retStringName.setName(con.sliceType_Value)
			return retStringName

		typeIsLowerUpperStep = True

		try:
			dummyVariable = node.slice.lower
		except:
			typeIsLowerUperStep = False

		try:
			dummyVariable = node.slice.upper
		except:
			typeIsLowerUpperStep = False

		try:
			dummyVariable = node.slice.step
		except:
			typeIsLowerUpperStep = False

		if (typeIsLowerUpperStep == True):
			retStringName.setName(con.sliceType_LowerUpperStep)
			return retStringName

		sys.exit("ASTParser->getSubscriptSliceTypeAsStringName:  slice component of node passed in is not one of the supported types.")

	'''
	def buildSliceValueObjForSubscript(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->buildSliceValueObjForSubscript:  problem with node passed in.")

		sliceTypeStringName = self.getSubscriptSliceTypeAsStringName(node)
		if ( (sliceTypeStringName == None) or (type(sliceTypeStringName).__name__ != con.stringName) ):
			sys.exit("ASTVarVisitor->buildSliceValueObjForSubscript:  problem with value returned from getSubscriptSliceTypeAsStringName.")

		sliceType = sliceTypeStringName.getStringVarName()

		if ( (sliceType == None) or (type(sliceType).__name__ != con.strTypePython) or (sliceType not in con.sliceTypes) ):
			sys.exit("ASTVarVisitor->buildSliceValueObjForSubscript:  problem with string representation of value returned from getSubscriptSliceType.")

		sliceValueObj = SliceValue()

		if (sliceType == con.sliceType_Value):
			sliceNode_Value = self.getSubscriptSliceNode_Value(node)
			processedSliceNode_Value = self.processNode(sliceNode_Value)
			sliceValueObj.setSliceType(sliceTypeStringName)
			sliceValueObj.setValue(processedSliceNode_Value)
		elif (sliceType == con.sliceType_LowerUpperStep):
			foundAtLeastOne = False

			sliceNode_Lower = self.myASTParser.getSubscriptSliceNode_Lower(node)
			if (sliceNode_Lower != None):
				foundAtLeastOne = True
				processedSliceNode_Lower = self.processNode(sliceNode_Lower)
				sliceValueObj.setLower(processedSliceNode_Lower)

			sliceNode_Upper = self.myASTParser.getSubscriptSliceNode_Upper(node)
			if (sliceNode_Upper != None):
				foundAtLeastOne = True
				processedSliceNode_Upper = self.processNode(sliceNode_Upper)
				sliceValueObj.setUpper(processedSliceNode_Upper)

			sliceNode_Step = self.myASTParser.getSubscriptSliceNode_Step(node)
			if (sliceNode_Step != None):
				foundAtLeastOne = True
				processedSliceNode_Step = self.processNode(sliceNode_Step)
				sliceValueObj.setStep(processedSliceNode_Step)

			if (foundAtLeastOne == False):
				sys.exit("ASTVarVisitor->buildSubscriptName:  slice type was returned as lower/upper/step, but none of those three nodes was a non-None type.")

			sliceValueObj.setSliceType(sliceTypeStringName)

		else:
			sys.exit("ASTVarVisitor->buildSubscriptName:  value obtained for slice type is not one of the supported types.")
	'''

	def getSubscriptValueNode(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptValueNode:  problem with node passed in to function.")

		try:
			retNode = node.value
		except:
			sys.exit("ASTParser->getSubscriptValueNode:  could not extract value node from subscript node passed in to function.")

		#if ( (type(retNode).__name__ != con.nameOnlyTypeAST) and (type(retNode).__name__ != con.callTypeAST) ):
			#sys.exit("ASTParser->getSubscriptValueNode:  value node extracted is neither of type " + con.nameOnlyTypeAST + " nor of type " + con.callTypeAST + ".")

		return retNode

	def getSubscriptSliceNode_Value(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptSliceNode_Value:  problem with node passed in to function.")

		try:
			retNode = node.slice.value
		except:
			sys.exit("ASTParser->getSubscriptSliceNode_Value:  could not extract slice value node from the subscript node passed in.")

		return retNode

	def getSubscriptSliceNode_Lower(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptSliceNode_Lower:  problem with node passed in to function.")

		try:
			retNode = node.slice.lower
		except:
			sys.exit("ASTParser->getSubscriptSliceNode_Lower:  could not extract slice lower node from the subscript node passed in.")

		return retNode

	def getSubscriptSliceNode_Upper(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptSliceNode_Upper:  problem with node passed in to function.")

		try:
			retNode = node.slice.upper
		except:
			sys.exit("ASTParser->getSubscriptSliceNode_Upper:  could not extract slice upper node from the subscript node passed in.")

		return retNode

	def getSubscriptSliceNode_Step(self, node):
		if ( (node == None) or (type(node).__name__ != con.subscriptTypeAST) ):
			sys.exit("ASTParser->getSubscriptSliceNode_Step:  problem with node passed in to function.")

		try:
			retNode = node.slice.step
		except:
			sys.exit("ASTParser->getSubscriptSliceNode_Step:  could not extract slice step node from the subscript node passed in.")

		return retNode

	def getSubscriptSlice(self, node):
		if (node == None):
			sys.exit("ASTParser->getSubscriptSlice:  node passed in is of None type.")

		if (type(node).__name__ != con.subscriptTypeAST):
			sys.exit("ASTParser->getSubscriptSlice:  type of node passed in is not " + con.subscriptTypeAST)

		sliceObject = self.buildObjectFromNode(node.slice.value)
		if (sliceObject == None):
			sys.exit("ASTParser->getSubscriptSlice:  problem with value returned from buildObjectFromNode.")

		return sliceObject

	def getBaseNode(self):
		return self.baseNode

	def setBaseNode(self, node):
		if (node == None):
			sys.exit("ASTParser->setBaseNode:  node passed in is of None type.")

		self.baseNode = node

	def getForLoopIterNode(self, node):
		if ( (node == None) or (type(node).__name__ != con.forLoopTypeAST) ):
			sys.exit("ASTParser->getForLoopIterNode:  problem with node passed in to function.")

		try:
			forLoopIterNode = node.iter
		except:
			sys.exit("ASTParser->getForLoopIterNode:  could not extract iter node from for loop node passed in.")

		return forLoopIterNode

	def getTargetNameOfForLoopAsStringName(self, node):
		if ( (node == None) or (type(node).__name__ != con.forLoopTypeAST) ):
			sys.exit("ASTParser->getTargetNameOfForLoopAsStringName:  problem with node passed in.")

		try:
			forLoopTargetName = node.target.id
		except:
			sys.exit("ASTParser->getTargetNameOfForLoopAsStringName:  could not extract the target name of the for loop node passed in.")

		targetNameAsStringName = StringName()
		targetNameAsStringName.setName(forLoopTargetName)
		lineNo = self.getLineNumberOfNode(node)
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("ASTParser->getTargetNameOfForLoopAsStringName:  problem with value returned from self.getLineNumberOfNode.")

		targetNameAsStringName.setLineNo(lineNo)
		return targetNameAsStringName

	def getAssignLeftSideNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getAssignLeftSideNode:  node passed in is of None type.")

		try:
			returnNode = node.targets[0]
		except:
			sys.exit("ASTParser->getAssignLeftSideNode:  node passed in does not have the \"targets[0]\" child.")

		return returnNode

	def getAssignRightSideNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getAssignRightSideNode:  node passed in is of None type.")

		try:
			returnNode = node.value
		except:
			sys.exit("ASTParser->getAssignRightSideNode:  node passed in does not have the \"value\" child.")

		return returnNode

	def isNodeATuple(self, node):
		if (node == None):
			sys.exit("ASTParser->isNodeATuple:  node passed in is of None type.")

		'''
		try:
			nodeFields = node._fields
		except:
			sys.exit("ASTParser->isNodeATuple:  cannot obtain the node's fields.")

		if (len(nodeFields) == 0):
			sys.exit("ASTParser->isNodeATuple:  the fields list of the node passed in has a length of zero.")

		if (nodeFields[0] == con.tupleAST):
			return True

		return False
		'''

		nodeType = self.getNodeType(node)

		if (nodeType == con.tupleTypeAST):
			return True

		return False

	def getTupleNodesList(self, node):
		if (node == None):
			sys.exit("ASTParser->getTupleNodesList:  node passed in is of None type.")

		isTuple = self.isNodeATuple(node)
		if (isTuple == False):
			sys.exit("ASTParser->getTupleNodesList:  node passed in is not a tuple.")

		try:
			returnList = node.elts
		except:
			sys.exit("ASTParser->getTupleNodesList:  could not obtain tuple nodes of the node passed in.")

		if (len(returnList) == 0):
			sys.exit("ASTParser->getTupleNodesList:  list of tuple nodes extracted from node passed in was of length zero.")

		return returnList

	def getFunctionNode(self, node, functionName):
		if (node == None):
			sys.exit("ASTParser->getFunctionNode:  node passed in is of None type.")

		if (len(functionName) == 0):
			sys.exit("ASTParser->getFunctionNode:  function name passed in is of length zero.")

		functionVisitor = ASTFunctionVisitor(functionName)
		functionVisitor.visit(node)
		return functionVisitor.getFunctionNodes()

	def getLastEquation(self, node):
		if (node == None):
			sys.exit("ASTParser->getLastEquation:  node passed in is of None type.")

		equationVisitor = ASTEquationVisitor()
		equationVisitor.visit(node)
		return equationVisitor.getLastEquation()

	def getSourceLineOfNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getSourceLineOfNode:  node passed in is of None type.")

		if (self.sourceLinesList == None):
			sys.exit("ASTParser->getSourceLineOfNode:  self.sourceLinesList is of None type.")

		if (len(self.sourceLinesList) == 0):
			sys.exit("ASTParser->getSourceLineOfNode:  self.sourceLinesList has length zero.")

		try:
			lineNo = node.lineno
		except:
			sys.exit("ASTParser->getSourceLineOfNode:  could not obtain line number of the node passed in.")

		lenSourceLines = len(self.sourceLinesList)

		if (lineNo >= lenSourceLines):
			sys.exit("ASTParser->getSourceLineOfNode:  line number of node passed in exceeds the number of lines in self.sourceLinesList.")

		return self.sourceLinesList[lineNo-1]

	def getNodeType(self, node):
		if (node == None):
			sys.exit("ASTParser->getNodeType:  node passed in is of None type.")

		try:
			nameType = type(node).__name__
		except:
			sys.exit("ASTParser->getNodeType:  could not obtain the name type from the node passed in.")

		#if (nameType in con.strTypeAST):
			#return con.strTypePython

		if (nameType == con.nameOnlyTypeAST):
			return con.nameOnlyTypeAST

		if (nameType == con.strOnlyTypeAST):
			return con.strOnlyTypeAST

		if (nameType == con.numTypeAST):
			try:
				nodeNumType = type(node.n)
			except:
				sys.exit("ASTParser->getNodeType:  could not obtain the type of the number node.")

			if (nodeNumType == int):
				return con.intTypePython
			if (nodeNumType == float):
				return con.floatTypePython

		if (nameType == con.callTypeAST):
			return con.callTypeAST

		if (nameType == con.lambdaTypeAST):
			return con.lambdaTypeAST

		if (nameType == con.subscriptTypeAST):
			return con.subscriptTypeAST

		if (nameType == con.dictTypeAST):
			return con.dictTypeAST

		if (nameType == con.binOpTypeAST):
			return con.binOpTypeAST

		if (nameType == con.unaryOpTypeAST):
			return con.unaryOpTypeAST

		if (nameType == con.tupleTypeAST):
			return con.tupleTypeAST

		if (nameType == con.listTypeAST):
			return con.listTypeAST

		return None

	def getStringNameFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getStringNameFromNode:  node passed in is of None type.")

		try:
			stringName = node.id
		except:
			sys.exit("ASTParser->getStringNameFromNode:  could not obtain the \"id\" filed of the node passed in.")

		if (len(stringName) == 0):
			sys.exit("ASTParser->getStringNameFromNode:  string obtained from node is of length zero.")

		return stringName

	def getStringValueFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getStringValueFromNode:  node passed in is of None type.")

		try:
			stringValue = node.s
		except:
			sys.exit("ASTParser->getStringValueFromNode:  could not obtain the \"s\" field of the node passed in.")

		#if (len(stringValue) == 0):
			#sys.exit("ASTParser->getStringValueFromNode:  string obtained from node is of length zero.")

		return stringValue

	def getIntValueFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getIntValueFromNode:  node passed in is of None type.")

		try:
			intValue = node.n
		except:
			sys.exit("ASTParser->getIntValueFromNode:  could not obtain the \"n\" field of the node passed in.")

		return intValue

	def getFloatValueFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getFloatValueFromNode:  node passed in is of None type.")

		try:
			floatValue = node.n
		except:
			sys.exit("ASTParser->getFloatValueFromNode:  could not obtain the \"n\" field of the node passed in.")

		return floatValue

	def buildVarNamesValueFromNode(self, node):
		if (node == None):
			sys.exit("ASTParser->buildVarNamesValueFromNode:  node passed in is of None type.")

		getVarNamesObj = ASTGetVariableNames()
		getVarNamesObj.visit(node)
		varNamesValue = getVarNamesObj.getVarNamesValue()

		return varNamesValue
