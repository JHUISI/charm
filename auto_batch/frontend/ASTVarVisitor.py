import ast, con, sys
from ASTParser import *
from Variable import Variable
from StringName import StringName
from SubscriptName import SubscriptName
from StringValue import StringValue
from IntegerValue import IntegerValue
from FloatValue import FloatValue
from HashValue import HashValue
from RandomValue import RandomValue
from LambdaValue import LambdaValue
from DotProdValue import DotProdValue
from DictValue import DictValue

class ASTVarVisitor(ast.NodeVisitor):
	def __init__(self, myASTParser):
		if (myASTParser == None):
			sys.exit("ASTVarVisitor->init:  myASTParser passed in is of None type.")

		self.varAssignments = []
		self.myASTParser = myASTParser

	def buildStringName(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildStringName:  node passed in is of None type.")

		stringName = self.myASTParser.getStringNameFromNode(node)
		if (stringName == None):
			sys.exit("ASTVarVisitor->buildStringName:  string name returned from myASTParser->getStringNameFromNode is of None type.")

		if (type(stringName) is not str):
			sys.exit("ASTVarVisitor->buildStringName:  string name returned from myASTParser->getStringNameFromNode is not of type str.")

		if (len(stringName) == 0):
			sys.exit("ASTVarVisitor->buildStringName:  string name returned from myASTParser->getStringNameFromNode is of length zero.")

		stringNameToAdd = StringName()
		stringNameToAdd.setName(stringName)

		return stringNameToAdd

	def buildStringValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildStringValue:  node passed in is of None type.")

		stringValue = self.myASTParser.getStringValueFromNode(node)
		if (stringValue == None):
			sys.exit("ASTVarVisitor->buildStringValue:  string value returned from myASTParser->getStringValueFromNode is of None type.")

		if (type(stringValue) is not str):
			sys.exit("ASTVarVisitor->buildStringValue:  string value returned from myASTParser->getStringValueFromNode is not of type str.")

		if (len(stringValue) == 0):
			sys.exit("ASTVarVisitor->buildStringValue:  string value returned from myASTParser->getStringValueFromNode is of length zero.")

		stringValueToAdd = StringValue()
		stringValueToAdd.setValue(stringValue)

		return stringValueToAdd

	def buildSubscriptName(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildSubscriptName:  node passed in is of None type.")

		valueAsStringName = self.myASTParser.getSubscriptValueAsStringName(node)
		if ( (valueAsStringName == None) or (type(valueAsStringName).__name__ != con.stringName) ):
			sys.exit("ASTVarVisitor->buildSubscriptName:  problem with value returned from myASTParser->getSubscriptValueAsStringName.")

		slice = self.myASTParser.getSubscriptSlice(node)
		if (slice == None):
			sys.exit("ASTVarVisitor->buildSubscriptName:  value returned from myASTParser->getSubscriptSlice is of None type.")

		subscriptNameToAdd = SubscriptName()
		subscriptNameToAdd.setValue(valueAsStringName)
		subscriptNameToAdd.setSlice(slice)

		return subscriptNameToAdd

	def buildIntValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildIntValue:  node passed in is of None type.")

		intValue = self.myASTParser.getIntValueFromNode(node)
		if (intValue == None):
			sys.exit("ASTVarVisitor->buildIntValue:  int value returned from myASTParser->getIntValueFromNode is of None type.")

		if (type(intValue) is not int):
			sys.exit("ASTVarVisitor->buildIntValue:  int value returned from myASTParser->getIntValueFromNode is not of type int.")

		intValueToAdd = IntegerValue()
		intValueToAdd.setValue(intValue)

		return intValueToAdd

	def buildFloatValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildFloatValue:  node passed in is of None type.")

		floatValue = self.myASTParser.getFloatValueFromNode(node)
		if (floatValue == None):
			sys.exit("ASTVarVisitor->buildFloatValue:  float value returned from myASTParser->getFloatValueFromNode is of None type.")

		if (type(floatValue) is not float):
			sys.exit("ASTVarVisitor->buildFloatValue:  float value returned from myASTParser->getFloatValueFromNode is not of type float.")

		floatValueToAdd = FloatValue()
		floatValueToAdd.setValue(floatValue)

		return floatValueToAdd

	def getHashGroupType(self, hashArgsList):
		if (hashArgsList == None):
			sys.exit("ASTVarVisitor->getHashGroupType:  arguments list passed in is of None type.")

		if (len(hashArgsList) == 0):
			sys.exit("ASTVarVisitor->getHashGroupType:  arguments list passed in is empty.")

		hashGroupType = None

		for hashArg in hashArgsList:
			if hashArg in con.groupTypes:
				if (hashGroupType != None):
					sys.exit("ASTVarVisitor->getHashGroupType:  found more than one argument that represents group type.")

				hashGroupType = hashArg

		if (hashGroupType == None):
			sys.exit("ASTVarVisitor->getHashGroupType:  could not locate a group type from the arguments list.")

		return hashGroupType

	def buildHashValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildHashValue:  node passed in is of None type.")

		hashArgsList = self.myASTParser.getCallArgsList(node)
		if (hashArgsList == None):
			sys.exit("ASTVarVisitor->buildHashValue:  value returned from getCallArgsList is of None type.")

		hashGroupType = self.getHashGroupType(hashArgsList)
		if (hashGroupType == None):
			sys.exit("ASTVarVisitor->buildHashValue:  value returned from getHashGroupType is of None type.")

		hashArgsList.remove(hashGroupType)

		hashValueToAdd = HashValue()
		hashValueToAdd.setArgsList(hashArgsList)
		hashValueToAdd.setGroupType(hashGroupType)

		return hashValueToAdd

	def buildRandomValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildRandomValue:  node passed in is of None type.")

		randomArgsList = self.myASTParser.getCallArgsList(node)
		if (randomArgsList == None):
			groupType = con.ZR
		else:
			if (len(randomArgsList) != 1):
				sys.exit("ASTVarVisitor->buildRandomValue:  length of argument list returned from getCallArgsList is greater than one.")

			if (randomArgsList[0] not in con.groupTypes):
				sys.exit("ASTVarVisitor->buildRandomValue:  the argument returned from getCallArgsList is not a group type that is supported.")

			groupType = randomArgsList[0]

		randomValueToAdd = RandomValue()
		randomValueToAdd.setGroupType(groupType)

		return randomValueToAdd

	def buildDotProdValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildDotProdValue:  node passed in is of None type.")

		dotProdArgsList = self.myASTParser.getCallArgsList(node)
		if ( (dotProdArgsList == None) or (type(dotProdArgsList) is not list) or (len(dotProdArgsList) < 4) ):
			sys.exit("ASTVarVisitor->buildDotProdValue:  return value from getCallArgsList does not meet the proper criteria.")

		dotProdValueToAdd = DotProdValue()
		dotProdValueToAdd.setNumProds(dotProdArgsList[2])
		dotProdValueToAdd.setFuncName(dotProdArgsList[3])

		if (len(dotProdArgsList) == 4):
			return dotProdValueToAdd

		lenList = len(dotProdArgsList)
		funcArgsList = []
		numFuncArgs = lenList - 4

		for index in range(0, numFuncArgs):
			funcArgsList.append(dotProdArgsList[index + 4])

		if (len(funcArgsList) == 0):
			sys.exit("ASTVarVisitor->buildDotProdValue:  could not extract the function arguments from the dot product.")

		dotProdValueToAdd.setArgsList(funcArgsList)

		return dotProdValueToAdd

	def buildCallValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildCallValue:  node passed in is of None type.")

		callType = self.myASTParser.getCallType(node)
		if (callType == None):
			return
			#sys.exit("ASTVarVisitor->buildCallValue:  return value of myASTParser->getCallType is of None type.")

		if (callType == con.hashType):
			hashValueToAdd = self.buildHashValue(node)
			if (hashValueToAdd == None):
				sys.exit("ASTVarVisitor->buildCallValue:  return value of buildHashValue is of None type.")

			return hashValueToAdd
		if (callType == con.randomType):
			randomValueToAdd = self.buildRandomValue(node)
			if (randomValueToAdd == None):
				sys.exit("ASTVarVisitor->buildCallValue:  return value of buildRandomValue is of None type.")

			return randomValueToAdd

		if (callType == con.dotProdType):
			dotProdValueToAdd = self.buildDotProdValue(node)
			if (dotProdValueToAdd == None):
				sys.exit("ASTVarVisitor->buildCallValue:  return value of buildDotProdValue is of None type.")

			return dotProdValueToAdd

		return None

	def buildLambdaValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildLambdaValue:  node passed in is of None type.")

		isHashCall = self.myASTParser.isLambdaAHashCall(node)
		if ( (isHashCall != True) and (isHashCall != False) ):
			sys.exit("ASTVarVisitor->buildLambdaValue:  return value from isLambdaAHashCall is neither True nor False.")

		if (isHashCall == True):
			hashNode = self.myASTParser.getHashNodeFromLambda(node)
			if (hashNode == None):
				sys.exit("ASTVarVisitor->buildLambdaValue:  return node from getHashNodeFromLambda is of None type.")

			hashValue = self.buildHashValue(hashNode)
			if (hashValue == None):
				sys.exit("ASTVarVisitor->buildLambdaValue:  return value from buildHashValue is of None type.")

			return hashValue

		lambdaArgsList = self.myASTParser.getLambdaArgsList(node)
		if (lambdaArgsList == None):
			sys.exit("ASTVarVisitor->buildLambdaValue:  list returned from getLambdaArgsList is of None type.")

		if (len(lambdaArgsList) == 0):
			sys.exit("ASTVarVisitor->buildLambdaValue:  list returned from getLambdaArgsList is of length zero.")

		for arg in lambdaArgsList:
			if (type(arg) is not str):
				sys.exit("ASTVarVisitor->buildLambdaValue:  one of the arguments returned from getLambdaArgsList is not of type " + con.strTypePython)

		lambdaExpression = self.myASTParser.getLambdaExpression(node, lambdaArgsList)
		if (lambdaExpression == None):
			sys.exit("ASTVarVisitor->buildLambdaValue:  expression returned from getLambdaExpression is of None type.")

		if (len(lambdaExpression) == 0):
			sys.exit("ASTVarVisitor->buildLambdaValue:  expression returned from getLambdaExpression if of length zero.")

		if (type(lambdaExpression) is not str):
			sys.exit("ASTVarVisitor->buildLambdaValue:  expression returned from getLambdaExpression is not of type " + con.strTypePython)

		returnLambdaValue = LambdaValue()
		returnLambdaValue.setArgList(lambdaArgsList)
		returnLambdaValue.setExpression(lambdaExpression)
		return returnLambdaValue

	def buildDictValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildDictValue:  node passed in is of None type.")

		dictKeys = self.myASTParser.getDictKeys(node)
		if ( (dictKeys == None) or (type(dictKeys).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictKeys.")

		dictValues = self.myASTParser.getDictValues(node)
		if ( (dictValues == None) or (type(dictValues).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictValues.")

		returnDictValue = DictValue()
		returnDictValue.setKeys(dictKeys)
		returnDictValue.setValues(dictValues)

		return returnDictValue

	def processAssignment(self, leftSideNode, rightSideNode):
		if (leftSideNode == None):
			sys.exit("ASTVarVisitor->processAssignment:  left side node passed in is of None type.")

		if (rightSideNode == None):
			sys.exit("ASTVarVisitor->processAssignment:  right side node passed in is of None type.")

		leftNodeType = self.myASTParser.getNodeType(leftSideNode)
		rightNodeType = self.myASTParser.getNodeType(rightSideNode)

		variableToAdd = Variable()

		if (leftNodeType == str):
			stringNameToAdd = self.buildStringName(leftSideNode)
			if (stringNameToAdd == None):
				sys.exit("ASTVarVisitor->processAssignment:  return value of buildStringName is of None type.")

			variableToAdd.setName(stringNameToAdd)

		if (leftNodeType == con.subscriptTypeAST):
			subscriptNameToAdd = self.buildSubscriptName(leftSideNode)
			if (subscriptNameToAdd == None):
				sys.exit("ASTVarVisitor->processAssignment:  return value of buildSubscriptName is of None type.")

			variableToAdd.setName(subscriptNameToAdd)

		if (rightNodeType == str):
			stringValueToAdd = self.buildStringValue(rightSideNode)
			if (stringValueToAdd == None):
				sys.exit("ASTVarVisitor->processAssignment:  return value of buildStringValue is of None type.")

			variableToAdd.setValue(stringValueToAdd)

		if (rightNodeType == int):
			intValueToAdd = self.buildIntValue(rightSideNode)
			if (intValueToAdd == None):
				sys.exit("ASTVarVisitor->processAssignment:  return value of buildIntValue is of None type.")

			variableToAdd.setValue(intValueToAdd)

		if (rightNodeType == float):
			floatValueToAdd = self.buildFloatValue(rightSideNode)
			if (floatValueToAdd == None):
				sys.exit("ASTVarVisitor->processAssignment:  return value of buildFloatValue is of None type.")

			variableToAdd.setValue(floatValueToAdd)

		if (rightNodeType == con.callTypeAST):
			callValueToAdd = self.buildCallValue(rightSideNode)
			if (callValueToAdd != None):
				variableToAdd.setValue(callValueToAdd)

		if (rightNodeType == con.lambdaType):
			lambdaValueToAdd = self.buildLambdaValue(rightSideNode)
			if (lambdaValueToAdd != None):
				variableToAdd.setValue(lambdaValueToAdd)

		if (rightNodeType == con.dictTypeAST):
			dictValueToAdd = self.buildDictValue(rightSideNode)
			if (dictValueToAdd != None):
				variableToAdd.setValue(dictValueToAdd)

		if ( (variableToAdd.getName() != None) and (variableToAdd.getValue() != None) ):
			leftLineNo = self.myASTParser.getLineNumberOfNode(leftSideNode)
			rightLineNo = self.myASTParser.getLineNumberOfNode(rightSideNode)

			variableToAdd.getName().setLineNo(leftLineNo)
			variableToAdd.getValue().setLineNo(rightLineNo)
			self.varAssignments.append(variableToAdd)

	def visit_Assign(self, node):
		leftSideNode = self.myASTParser.getAssignLeftSideNode(node)
		if (leftSideNode == None):
			sys.exit("ASTVarVisitor->visit_Assign:  left side of assignment node is of None type.")

		isLeftSideATuple = self.myASTParser.isNodeATuple(leftSideNode)

		rightSideNode = self.myASTParser.getAssignRightSideNode(node)
		if (rightSideNode == None):
			sys.exit("ASTVarVisitor->visit_Assign:  right side of assignment node is of None type.")

		isRightSideATuple = self.myASTParser.isNodeATuple(rightSideNode)

		if ( (isLeftSideATuple == False) and (isRightSideATuple == False) ):
			self.processAssignment(leftSideNode, rightSideNode)
			return

		leftSideList = None
		rightSideList = None

		if (isLeftSideATuple == True):
			leftSideList = self.myASTParser.getTupleNodesList(leftSideNode)
			if (leftSideList == None):
				sys.exit("ASTVarVisitor->visit_Assign:  could not obtain the tuple list of the left side of the assignment equation.")

		if (isRightSideATuple == True):
			rightSideList = self.myASTParser.getTupleNodesList(rightSideNode)
			if (rightSideList == None):
				sys.exit("ASTVarVisitor->visit_Assign:  could not obtain the tuple list of the right side of the assignment equation.")

		if (isLeftSideATuple == False):
			for tupleNode in rightSideList:
				self.processAssignment(leftSideNode, tupleNode)
			return

		if (isRightSideATuple == False):
			for tupleNode in leftSideList:
				self.processAssignment(tupleNode, rightSideNode)
			return

		for leftTupleNode, rightTupleNode in zip(leftSideList, rightSideList):
			self.processAssignment(leftTupleNode, rightTupleNode)

	def getVarAssignDict(self):
		if (len(self.varAssignments) == 0):
			return None

		return self.varAssignments
