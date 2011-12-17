import ast, con, sys
from StringName import StringName
from StringValue import StringValue
from IntegerValue import IntegerValue
from FloatValue import FloatValue

def getValueOfLastLine(dict):
	if (len(dict) == 0):
		return None

	keys = list(dict.keys())
	keys.sort()
	lenKeys = len(keys)
	return dict[keys[lenKeys-1]]

def getCallArgsList(node):
	if (node == None):
		sys.exit("ASTParser->getCallArgsList:  node passed in is of None type.")

	try:
		argsList = node.args
	except:
		sys.exit("ASTParser->getCallArgsList:  could not obtain the arguments list of the node passed in.")

	returnArgsList = []

	for callArgNode in argsList:
		nameOfNode = getNameOfNode(callArgNode)
		if (nameOfNode != None):
			returnArgsList.append(nameOfNode)

	if (len(returnArgsList) == 0):
		return None

	return returnArgsList

class ASTFuncArgMapsVisitor(ast.NodeVisitor):
	def __init__(self):
		self.functionArgMappings = {}

	def visit_Call(self, node):
		try:
			destFuncName = node.func.id
		except:
			sys.exit("ASTFuncArgMapsVisitor->visit_Call:  could not obtain the name of the destination function.")

		pass

	def getFunctionArgMappings(self):
		return self.functionArgMappings

class ASTFunctionArgNames(ast.NodeVisitor):
	def __init__(self):
		self.functionArgNames = {}

	def visit_FunctionDef(self, node):
		try:
			nodeName = node.name
		except:
			sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not obtain the name of the function.")

		try:
			argsList = node.args.args
		except:
			sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not obtain the arguments list for function " + nodeName)

		if (len(argsList) == 0):
			self.functionArgNames[nodeName] = None
			return

		argNamesList = []

		for argItr in argsList:
			try:
				argNamesList.append(argItr.arg)
			except:
				sys.exit("ASTParser->ASTFunctionArgNames->visit_FunctionDef:  could not extract one of the argument names of function " + nodeName)

		self.functionArgNames[nodeName] = argNamesList

	def getFunctionArgNames(self):
		if (len(self.functionArgNames) == 0):
			return None

		return self.functionArgNames

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

	def getFunctionArgNames(self, node):
		if (node == None):
			sys.exit("ASTParser->getFunctionArgNames:  node passed in is of None type.")

		myFuncArgNamesVisitor = ASTFunctionArgNames()
		myFuncArgNamesVisitor.visit(node)
		return myFuncArgNamesVisitor.getFunctionArgNames()

	def getFunctionArgMappings(self, funcNode, functionArgNames):
		if (funcNode == None):
			sys.exit("ASTParser->getFunctionArgMappings:  function node passed in is of None type.")

		if ( (functionArgNames == None) or (type(functionArgNames).__name__ != con.dictTypePython) or (len(functionArgNames) == 0) ):
			sys.exit("ASTParser->getFunctionArgMappings:  problem with the function argument names passed in.")

		myFuncArgMapsVisitor = ASTFuncArgMapsVisitor()
		myFuncArgMapsVisitor.visit(funcNode)
		return myFuncArgMapsVisitor.getFunctionArgMappings()

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

		try:
			argOrder = lambdaArgs.index(argName)
		except:
			sys.exit("ASTParser->getLambdaArgOrder:  the argument name passed in is not in the argument list passed in.")

		return argOrder

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
			if (type(arg) is not str):
				sys.exit("ASTParser->getLambdaExpression:  one of the lambda arguments passed in is not of type " + con.strTypePython)

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

		return expression

	def getLambdaArgsList(self, node):
		if (node == None):
			sys.exit("ASTParser->getLambdaArgsList:  node passed in is of None type.")

		try:
			argsList = node.args.args
		except:
			sys.exit("ASTParser->getLambdaArgsList:  could not obtain the arguments list of the node passed in.")

		returnArgsList = []

		for argNode in argsList:
			try:
				arg = argNode.arg
			except:
				sys.exit("ASTParser->getLambdaArgsList:  could not obtain one of the arguments of the node passed in.")

			if (arg == None):
				sys.exit("ASTParser->getLambdaArgsList:  one of the arguments of the node passed in is of None type.")

			if (type(arg) is not str):
				sys.exit("ASTParser->getLambdaArgsList:  one of the arguments of the node passed in is not of " + con.strTypePython + " type.")

			returnArgsList.append(arg)

		if (len(returnArgsList) == 0):
			sys.exit("ASTParser->getLambdaArgsList:  could not obtain any of the arguments of the node passed in.")

		return returnArgsList

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
		if ( (node == None) or (name == None) or (type(name).__name__ != con.strTypePython) ):
			sys.exit("ASTParser->buildStringName:  problem with input parameter passed in.")

		returnStringName = StringName()
		returnStringName.setName(name)
		returnStringName.setLineNo(node.lineno)

		return returnStringName

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

		returnStringName = self.buildStringName(node, name)
		if ( (returnStringName == None) or (type(returnStringName).__name__ != con.stringName) ):
			sys.exit("ASTParser->getSubscriptValueAsStringName:  problem with value returned from buildStringName.")

		return returnStringName

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

		sys.exit("ASTParser->buildObjectFromNode:  type of node is not currently supported.")

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

		try:
			nodeFields = node._fields
		except:
			sys.exit("ASTParser->isNodeATuple:  cannot obtain the node's fields.")

		if (len(nodeFields) == 0):
			sys.exit("ASTParser->isNodeATuple:  the fields list of the node passed in has a length of zero.")

		if (nodeFields[0] == con.tupleAST):
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

		if (nameType in con.strTypeAST):
			return str

		if (nameType == con.numTypeAST):
			try:
				nodeNumType = type(node.n)
			except:
				sys.exit("ASTParser->getNodeType:  could not obtain the type of the number node.")

			if (nodeNumType == int):
				return int
			if (nodeNumType == float):
				return float

		if (nameType == con.callTypeAST):
			return con.callTypeAST

		if (nameType == con.lambdaType):
			return con.lambdaType

		if (nameType == con.subscriptTypeAST):
			return con.subscriptTypeAST

		if (nameType == con.dictTypeAST):
			return con.dictTypeAST

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

		if (len(stringValue) == 0):
			sys.exit("ASTParser->getStringValueFromNode:  string obtained from node is of length zero.")

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
