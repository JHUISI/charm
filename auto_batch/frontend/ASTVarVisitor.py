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
from BinOpValue import BinOpValue
from InitValue import InitValue

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

		sliceNode = self.myASTParser.getSubscriptSliceNode(node)
		if (sliceNode == None):
			sys.exit("ASTVarVisitor->buildSubscriptName:  problem with value returned from myASTParser->getSubscriptSliceNode.")

		#slice = self.myASTParser.getSubscriptSlice(node)
		#if (slice == None):
			#sys.exit("ASTVarVisitor->buildSubscriptName:  value returned from myASTParser->getSubscriptSlice is of None type.")

		subscriptNameToAdd = SubscriptName()
		subscriptNameToAdd.setValue(valueAsStringName)
		#subscriptNameToAdd.setSlice(slice)
		subscriptNameToAdd.setSlice(self.processNode(sliceNode))

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

	def getHashGroupType(self, hashArgList):
		if (hashArgList == None):
			sys.exit("ASTVarVisitor->getHashGroupType:  arguments list passed in is of None type.")

		if (len(hashArgList) == 0):
			sys.exit("ASTVarVisitor->getHashGroupType:  arguments list passed in is empty.")

		hashGroupType = None

		for hashArg in hashArgList:
			if (type(hashArg).__name__ != con.stringName):
				continue

			possibleGroupType = hashArg.getName()
			if (possibleGroupType in con.groupTypes):
				if (hashGroupType != None):
					sys.exit("ASTVarVisitor->getHashGroupType:  found more than one argument that represents group type.")

				hashGroupType = possibleGroupType

		if (hashGroupType == None):
			sys.exit("ASTVarVisitor->getHashGroupType:  could not locate a group type from the arguments list.")

		return hashGroupType

	def getArgNodeList(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->getArgNodeList:  node passed in is of None type.")

		argNodeList = self.myASTParser.getArgNodeList(node)
		if ( (argNodeList == None) or (type(argNodeList).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->getArgNodeList:  problem with value returned from ASTParser->getArgNodeList.")

		if (len(argNodeList) == 0):
			return None

		retArgNodeList = self.processEachArgNode(argNodeList)
		if ( (retArgNodeList == None) or (type(retArgNodeList).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->getArgNodeList:  problem with value returned from processEachArgNode.")

		return retArgNodeList

	def processEachArgNode(self, argNodeList):
		if ( (argNodeList == None) or (type(argNodeList).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->processEachArgNode:  problem with the arguments node list passed in to the function.")

		retArgNodeList = []

		for argNode in argNodeList:
			retArgNode = self.processNode(argNode)
			retArgNodeList.append(copy.deepcopy(retArgNode))

		return retArgNodeList

	def buildHashValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildHashValue:  node passed in is of None type.")

		hashArgList = self.getArgNodeList(node)
		if ( (hashArgList == None) or (type(hashArgList).__name__ != con.listTypePython) or (len(hashArgList) == 0) ):
			sys.exit("ASTVarVisitor->buildHashValue:  problem with value returned from getArgNodeList")

		#hashArgList = self.myASTParser.getCallArgList(node)
		#if (hashArgList == None):
			#sys.exit("ASTVarVisitor->buildHashValue:  value returned from getCallArgList is of None type.")

		hashGroupType = self.getHashGroupType(hashArgList)
		if (hashGroupType == None):
			sys.exit("ASTVarVisitor->buildHashValue:  value returned from getHashGroupType is of None type.")

		#hashArgList.remove(hashGroupType)

		hashValueToAdd = HashValue()
		hashValueToAdd.setArgList(hashArgList)
		hashValueToAdd.setGroupType(hashGroupType)

		return hashValueToAdd

	def buildRandomValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildRandomValue:  node passed in is of None type.")

		randomArgList = self.getArgNodeList(node)

		#randomArgList = self.myASTParser.getCallArgList(node)

		seed = None

		if (randomArgList == None):
			groupType = self.myASTParser.buildStringName(node, con.ZR)
			if ( (groupType == None) or (type(groupType).__name__ != con.stringName) ):
				sys.exit("ASTVarVisitor->buildRandomValue:  problem with value returned from buildStringName for a null arguments list.")

		else:
			if ( (len(randomArgList) > 2) or (type(randomArgList[0]).__name__ != con.stringName) ):
				sys.exit("ASTVarVisitor->buildRandomValue:  problem with the values returned from getArgNodeList.")

			if (randomArgList[0].getStringVarName() not in con.groupTypes):
				sys.exit("ASTVarVisitor->buildRandomValue:  the first argument returned from getArgNodeList is not a group type that is supported.")

			groupType = copy.deepcopy(randomArgList[0])

			if (len(randomArgList) == 2):
				seed = copy.deepcopy(randomArgList[1])

		randomValueToAdd = RandomValue()
		randomValueToAdd.setGroupType(groupType)
		if (seed != None):
			randomValueToAdd.setSeed(seed)

		return randomValueToAdd

	def buildInitValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildInitValue:  node passed in is of None type.")

		initArgList = self.getArgNodeList(node)

		value = None

		if ( (len(initArgList) == 0) or (len(initArgList) > 2) or (type(initArgList[0]).__name__ != con.stringName) ):
			sys.exit("ASTVarVisitor->buildInitValue:  problem with the value returned from getArgNodeList..")

		if (initArgList[0].getStringVarName() not in con.groupTypes):
			sys.exit("ASTVarVisitor->buildInitValue:  first argument returned from getArgNodeList is not a group type that is currently supported.")

		groupType = copy.deepcopy(initArgList[0])

		if (len(initArgList) == 2):
			value = copy.deepcopy(initArgList[1])

		initValueToAdd = InitValue()
		initValueToAdd.setGroupType(groupType)
		if (value != None):
			initValueToAdd.setValue(value)

		return initValueToAdd

	def buildDotProdValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildDotProdValue:  node passed in is of None type.")

		dotProdArgList = self.getArgNodeList(node)
		if ( (dotProdArgList == None) or (type(dotProdArgList).__name__ != con.listTypePython) or (len(dotProdArgList) < 4) ):
			sys.exit("ASTVarVisitor->buildDotProdValue:  return value from getArgNodeList does not meet the proper criteria.")

		#dotProdArgList = self.myASTParser.getCallArgList(node)
		#if ( (dotProdArgList == None) or (type(dotProdArgList) is not list) or (len(dotProdArgList) < 4) ):
			#sys.exit("ASTVarVisitor->buildDotProdValue:  return value from getCallArgList does not meet the proper criteria.")

		dotProdValueToAdd = DotProdValue()
		dotProdValueToAdd.setInitialValue(dotProdArgList[0])
		dotProdValueToAdd.setSkipValue(dotProdArgList[1])
		dotProdValueToAdd.setNumProds(dotProdArgList[2])
		dotProdValueToAdd.setFuncName(dotProdArgList[3])

		if (len(dotProdArgList) == 4):
			return dotProdValueToAdd

		lenList = len(dotProdArgList)
		funcArgList = []
		numFuncArgs = lenList - 4

		for index in range(0, numFuncArgs):
			funcArgList.append(dotProdArgList[index + 4])

		if (len(funcArgList) == 0):
			sys.exit("ASTVarVisitor->buildDotProdValue:  could not extract the function arguments from the dot product.")

		dotProdValueToAdd.setArgList(funcArgList)

		return dotProdValueToAdd

	def buildCallValue(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->buildCallValue:  node passed in is of None type.")

		callType = self.myASTParser.getCallType(node)
		#if (callType == None):
			#return
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

		if (callType == con.initType):
			initValueToAdd = self.buildInitValue(node)
			if (initValueToAdd == None):
				sys.exit("ASTVarVisitor->buildCallValue:  return value of buildInitValue is of None type.")

			return initValueToAdd

		if (callType == con.dotProdType):
			dotProdValueToAdd = self.buildDotProdValue(node)
			if (dotProdValueToAdd == None):
				sys.exit("ASTVarVisitor->buildCallValue:  return value of buildDotProdValue is of None type.")

			return dotProdValueToAdd

		#return None

		callValueToAdd = self.myASTParser.buildCallObjectFromNode(node)
		if ( (callValueToAdd == None) or (type(callValueToAdd).__name__ != con.callValue) ):
			sys.exit("ASTVarVisitor->buildCallValue:  problem with return value of buildCallObjectFromNode.")

		return callValueToAdd

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

		lambdaArgList = self.myASTParser.getLambdaArgList(node)
		if (lambdaArgList == None):
			sys.exit("ASTVarVisitor->buildLambdaValue:  list returned from getLambdaArgList is of None type.")

		if (len(lambdaArgList) == 0):
			sys.exit("ASTVarVisitor->buildLambdaValue:  list returned from getLambdaArgList is of length zero.")

		for arg in lambdaArgList:
			if ( (arg == None) or (type(arg).__name__ != con.stringName) ):
				sys.exit("ASTVarVisitor->buildLambdaValue:  problem with one of the arguments returned from getLambdaArgList.")

		lambdaExpression = self.myASTParser.getLambdaExpression(node, lambdaArgList)
		if (lambdaExpression == None):
			sys.exit("ASTVarVisitor->buildLambdaValue:  expression returned from getLambdaExpression is of None type.")

		if (type(lambdaExpression).__name__ != con.stringValue):
			sys.exit("ASTVarVisitor->buildLambdaValue:  expression returned from getLambdaExpression is not of type " + con.stringValue)

		returnLambdaValue = LambdaValue()
		returnLambdaValue.setArgList(lambdaArgList)
		returnLambdaValue.setExpression(lambdaExpression)
		return returnLambdaValue

	def buildDictValue(self, node):
		if ( (node == None) or (type(node).__name__ != con.dictTypeAST) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with node passed in to function.")

		dictKeyNodes = self.myASTParser.getDictKeyNodes(node)
		if ( (dictKeyNodes != None) and (type(dictKeyNodes).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictKeyNodes.")

		dictValueNodes = self.myASTParser.getDictValueNodes(node)
		if ( (dictValueNodes != None) and (type(dictValueNodes).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictValueNodes.")

		if ( len(dictKeyNodes) != len(dictValueNodes) ):
			sys.exit("ASTVarVisitor->buildDictValue:  extracted unequal numbers of keys and values.")

		#dictKeys = self.myASTParser.getDictKeys(node)
		#if ( (dictKeys == None) or (type(dictKeys).__name__ != con.listTypePython) ):
			#sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictKeys.")

		#dictValues = self.myASTParser.getDictValues(node)
		#if ( (dictValues == None) or (type(dictValues).__name__ != con.listTypePython) ):
			#sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from myASTParser->getDictValues.")

		processedKeys = self.processEachArgNode(dictKeyNodes)
		if ( (processedKeys != None) and (type(processedKeys).__name__ != con.listTypePython) ) or (len(dictKeyNodes) != len(processedKeys) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from processEachArgNode (keys).")

		processedValues = self.processEachArgNode(dictValueNodes)
		if ( (processedValues != None) and (type(processedValues).__name__ != con.listTypePython) ) or (len(dictValueNodes) != len(processedValues) ):
			sys.exit("ASTVarVisitor->buildDictValue:  problem with value returned from processEachArgNode (values).")

		returnDictValue = DictValue()
		returnDictValue.setKeys(processedKeys)
		returnDictValue.setValues(processedValues)

		return returnDictValue

	def buildBinOpValue(self, node):
		if ( (node == None) or (type(node).__name__ != con.binOpTypeAST) ):
			sys.exit("ASTVarVisitor->buildBinOpValue:  problem with node passed in to function.")

		leftNode = self.myASTParser.getLeftNodeOfBinOp(node)
		if (node == None):
			sys.exit("ASTVarVisitor->buildBinOpValue:  could not extract left node of the node passed in.")

		rightNode = self.myASTParser.getRightNodeOfBinOp(node)
		if (node == None):
			sys.exit("ASTVarVisitor->buildBinOpValue:  could not extract right node of the node passed in.")

		opType = self.myASTParser.getOpTypeOfBinOp(node)
		if (opType not in con.opTypesAST):
			sys.exit("ASTVarVisitor->buildBinOpValue:  op type extracted from node passed in is not one of the supported types.")

		processedLeftNode = self.processNode(leftNode)
		if (processedLeftNode == None):
			sys.exit("ASTVarVisitor->buildBinOpValue:  value returned from processNode (on left node) is of None type.")

		processedRightNode = self.processNode(rightNode)
		if (processedRightNode == None):
			sys.exit("ASTVarVisitor->buildBinOpValue:  value returned from processNode (on right node) is of None type.")

		returnBinOpValue = BinOpValue()
		returnBinOpValue.setLeft(processedLeftNode)
		returnBinOpValue.setRight(processedRightNode)
		returnBinOpValue.setOpType(opType)

		return returnBinOpValue

	def processNode(self, node):
		if (node == None):
			sys.exit("ASTVarVisitor->processNode:  node passed in is of None type.")

		nodeType = self.myASTParser.getNodeType(node)

		if (nodeType == con.nameOnlyTypeAST):
			stringNameToAdd = self.buildStringName(node)
			if (stringNameToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildStringName is of None type.")

			return stringNameToAdd

		if (nodeType == con.subscriptTypeAST):
			subscriptNameToAdd = self.buildSubscriptName(node)
			if (subscriptNameToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildSubscriptName is of None type.")

			return subscriptNameToAdd

		if (nodeType == con.strOnlyTypeAST):
			stringValueToAdd = self.buildStringValue(node)
			if (stringValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildStringValue is of None type.")

			return stringValueToAdd

		if (nodeType == con.intTypePython):
			intValueToAdd = self.buildIntValue(node)
			if (intValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildIntValue is of None type.")

			return intValueToAdd

		if (nodeType == con.floatTypePython):
			floatValueToAdd = self.buildFloatValue(node)
			if (floatValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildFloatValue is of None type.")

			return floatValueToAdd

		if (nodeType == con.callTypeAST):
			callValueToAdd = self.buildCallValue(node)
			if (callValueToAdd != None):
				return callValueToAdd

		if (nodeType == con.lambdaTypeAST):
			lambdaValueToAdd = self.buildLambdaValue(node)
			if (lambdaValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildLambdaValue is of None type.")

			return lambdaValueToAdd

		if (nodeType == con.dictTypeAST):
			dictValueToAdd = self.buildDictValue(node)
			if (dictValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildDictValue is of None type.")

			return dictValueToAdd

		if (nodeType == con.binOpTypeAST):
			binOpValueToAdd = self.buildBinOpValue(node)
			if (binOpValueToAdd == None):
				sys.exit("ASTVarVisitor->processNode:  return value of buildBinOpValue is of None type.")

			return binOpValueToAdd

		return None

	def processAssignment(self, leftSideNode, rightSideNode):
		if (leftSideNode == None):
			sys.exit("ASTVarVisitor->processAssignment:  left side node passed in is of None type.")

		if (rightSideNode == None):
			sys.exit("ASTVarVisitor->processAssignment:  right side node passed in is of None type.")

		variableToAdd = Variable()
		variableToAdd.setName(self.processNode(leftSideNode))
		variableToAdd.setValue(self.processNode(rightSideNode))

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

	def recursiveGroupTypeTraversal(self, varObj, funcName, functionArgMappings, returnNodes, groupTypeList):
		if ( (varObj == None) or (type(varObj).__name__ not in variableTypes) ):
			sys.exit("ASTVarVisitor->recursiveGroupTypeTraversal:  problem with varObj input parameter passed in.")

		if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (funcName not in functionArgMappings) ):
			sys.exit("ASTVarVisitor->recursiveGroupTypeTraversal:  problem with function name parameter passed in.")

		if ( (groupTypeList == None) or (type(groupTypeList).__name__ != con.listTypePython) or (len(groupTypeList) > 1) ):
			sys.exit("ASTVarVisitor->recursiveGroupTypeTraversal:  problem with the group type list parameter passed in.")

		try:
			retGroupType = varObj.getGroupType()
		except:
			retGroupType = None

		if (retGroupType != None):
			if (retGroupType not in con.groupTypes):
				sys.exit("ASTVarVisitor->recursiveGroupTypeTraversal:  group type extracted is not one of the supported types.")

			if (len(groupTypeList) == 0):
				groupTypeList.append(retGroupType)
			else:
				if (retGroupType != groupTypeList[0]):
					sys.exit("ASTVarVisitor->recursiveGroupTypeTraversal:  group type extracted is different from a previously extracted group type.")

		varType = type(varObj).__name__

		if (varType == con.binOpValue):
			nextVarObj = self.myASTParser.getLeftNodeOfBinOp(varObj)
			self.recursiveGroupTypeTraversal(nextVarObj, groupTypeList)

	def getVarObjFromSameFunction(self, varName, funcName, varAssignments):
		if ( (varName == None) or (type(varName).__name__ not in con.variableNameTypes) ):
			sys.exit("ASTVarVisitor->getVarObjFromSameFunction:  problem with the variable name parameter passed in.")

		if ( (varAssignments == None) or (type(varAssignments).__name__ != con.dictTypePython) or (len(varAssignments) == 0) ):
			sys.exit("ASTVarVisitor->getVarObjFromSameFunction:  problem with the variable assignments dictionary passed in.")

		if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (funcName not in varAssignments) ):
			sys.exit("ASTVarVisitor->getVarObjFromSameFunction:  problem with the function name parameter passed in.")

		varsForFuncName = varAssignments[funcName]
		if ( (varsForFuncName == None) or (type(varsForFuncName).__name__ != con.listTypePython) ):
			sys.exit("ASTVarVisitor->getVarObjFromSameFunction:  problem with the list from varAssignments corresponding to the function name passed in to the function.")

		lenVarsForFunc = len(varsForFuncName)

		if (lenVarsForFunc == 0):
			return None

		for index in range( (lenVarsForFunc - 1), -1, -1):
			currentVarObj = varsForFuncName[index]
			if (varName.getStringVarName() == currentVarObj.getName().getStringVarName() ):
				return currentVarObj

		return None

	def getVariableGroupType(self, varName, funcName, functionArgMappings, returnNodes, varAssignments):
		if ( (varName == None) or (type(varName).__name__ not in con.variableNameTypes) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with variable name parameter passed in.")

		if ( (functionArgMappings == None) or (type(functionArgMappings).__name__ != con.dictTypePython) or (len(functionArgMappings) == 0) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with the function argument mappings dictionary passed in.")

		if ( (varAssignments == None) or (type(varAssignments).__name__ != con.dictTypePython) or (len(varAssignments) == 0) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with the variable assignments dictionary passed in.")

		if ( (funcName == None) or (funcName not in varAssignments) or (funcName not in functionArgMappings) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with the function name passed in.")

		if ( (returnNodes == None) or (type(returnNodes).__name__ != con.dictTypePython) or (len(returnNodes) == 0) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with the return nodes dictionary passed in.")

		variableObject = self.getVarObjFromSameFunction(varName, funcName, varAssignments)
		if ( (variableObject != None) and (type(variableObject).__name__ != con.variable) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with the variable object returned from getVarObjFromSameFunction.")

		'''
		groupTypeList = self.recursiveGroupTypeTraversal(varObj, funcName, functionArgMappings, returnNodes, [])
		if ( (groupTypeList == None) or (type(groupTypeList).__name__ != con.listTypePython) or (len(groupTypeList) > 1) ):
			sys.exit("ASTVarVisitor->getVariableGroupType:  problem with value returned from recursiveGroupTypeTraversal.")

		if (len(groupTypeList) == 0):
			return None

		retGroupType = groupTypeList[0]

		if (retGroupType not in con.groupTypes):
			sys.exit("ASTVarVisitor->getVariableGroupType:  group type returned from recursiveGroupTypeTraversal is not one of the supported types.")

		return retGroupType
		'''
