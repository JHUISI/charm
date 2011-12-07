import ast, con, sys

class ASTParser:
	def __init__(self):
		self.baseNode = None

	def getASTNodeFromFile(self, fileName):
		if (len(fileName) == 0):
			sys.exit("ASTParser->getASTNodeFromFile:  file name passed in has a length of zero.")

		try:
			sourceLinesList = open(fileName, 'r').readlines()
		except:
			sys.exit("ASTParser->getASTNodeFromFile:  error when running \"open\" system call on the file name passed in.")

		if (len(sourceLinesList) == 0):
			sys.exit("ASTParser->getASTNodeFromFile:  retrieved zero lines of source code from file name passed in.")

		sourceLines = ""
		for line in sourceLinesList:
			sourceLines += line

		try:
			returnNode = ast.parse(sourceLines)
		except:
			sys.exit("ASTParser->getASTNodeFromFile:  error when running \"ast.parse\" on the source-code lines of the file name passed in.")

		return returnNode

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

		if (nodeFields[0] == con.tuple):
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

	def getVerifyFuncNode(self, node):
		if (node == None):
			sys.exit("ASTParser->getVerifyFuncNode:  node passed in is of None type.")

		d
