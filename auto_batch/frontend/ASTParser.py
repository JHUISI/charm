import ast, con, sys

def getValueOfLastLine(dict):
	if (len(dict) == 0):
		return None

	keys = list(dict.keys())
	keys.sort()
	lenKeys = len(keys)
	return dict[keys[lenKeys-1]]

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
			fieldsTuple = node._fields
		except:
			sys.exit("ASTParser->getNodeType:  could not obtain the \"._fields\" tuple from the node")

		if (fieldsTuple[0] == con.strTypeAST):
			return str
		if (fieldsTuple[0] == con.numTypeAST):
			try:
				nodeNumType = type(node.n)
			except:
				sys.exit("ASTParser->getNodeType:  could not obtain the type of the number node.")

			if (nodeNumType == int):
				return int
			if (nodeNumType == float):
				return float

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
