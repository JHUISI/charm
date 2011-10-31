'''
Requirements:  

- There must be one, and only one, function named "verify."  This function must 
be responsible for evaluating whether a signature is valid (i.e., signature
verification).

- In the "verify" function, the last equality operator (==) MUST be the equality
operator in the statement that conducts the actual verification test.  You can
have as many equality operators before that statement, but that statement must
contain the last equality operator in the "verify" function.  In addition, this
statement must be completely contained on one line in the source code.

- Variable names MUST be unique and consisent throughout the entire program, not just within 
a function.  For example, if you declare a variable named "g" in the keygen function,
then all variables that represent the same element in all other functions
throughout the program must be called "g".  This requires all variable names to be
unique and consistent.

- There must be a variable named "N" that represents the number
of messages/signatures for which this scheme will be applied in batch mode.
We will use the value for "N" that comes from the first time "N" is assigned
in the code, so make sure the value for "N" that is desired comes before
all other uses of "N" in the code.  "N" can be used freely after that.

- Same as above, but for "num_signers."  This variable must be the number
of signers in the signature scheme.  I plan on deducing this information from
the code in the future.

- There can only be one variable assignment per line.  For example, you
CANNOT have the following:
"x = 5, y = 6"
I intend to remove this prerequisite once we're further along.

- All hashes MUST be calculated using member functions named "hash" of 
objects.  This "hash" member function must take exactly two arguments.  The
first argument must be the variable being hashed.  The second argument must
be the group in which the variable is being hashed.  For example, 
"x = group.hash(M, G1)".

- All random number generations MUST be calculated using member functions
named "random" of objects.  This "random" member function must take exactly
one argument, the group type.  For example,
"x = group.random(G2)"

- If you return a value that is important to the cryptoscheme (e.g., a
hash), that value must be returned in a variable, NOT in a calculation
in the return statement itself.  For example, you CANNOT have the following:

return group.hash(M, G1) ** x

Instead, you must convert it to this:

hash = group.hash(M, G1) ** x
return hash

Make sure to keep the variable names consistent as well, so that if you 
refer to the signature elsewhere in the program (e.g., the verify function),
you refer to it as "sig" there as well.

The one exception to this rule is that if this program does not find a 
valid value for the signature, it tries to get the signature from the 
LAST return statement in a function named "sign".  If it can find
a valid signature there, it assumes that is the signature.  So, for
example, you could have the following:

def sign( . . . )
. . . .
. . . .
return group.hash(M, G1) ** x

Then this program would assume that group.hash(M, G1) ** x is the
signature.
'''

import ast, compiler, sys

nameOfVerifyFunc = 'verify'
equalityOperator = 'Eq()'
N_name = 'N'
numSignersName = 'num_signers'
numRepInAST = 'Num'
nameRepInAST = 'Name'
idRepInAST = 'id'
callRepInAST = 'Call'
funcRepInAST = 'func'
attrRepInAST = 'attr'
hashRepInAST = ['hash', 'H']
initRepInAST = 'init'
argsRepInAST = 'args'
argRepInAST = 'arg'
randomRepInAST = 'random'
subscriptRepInAST = 'Subscript'
tupleRepInAST = 'Tuple'
eltsRepInAST = 'elts'
typeKey = 'type'
groupType = 'groupType'
binOpRepInAST = 'BinOp'
leftNodeRepInAST = 'left'
opRepInAST = 'op'
rightNodeRepInAST = 'right'
expRepInAST = 'Pow'
multRepInAST = 'Mult'
dictRepInAST = 'Dict'
strRepInAST = 'Str'
strRepInBV = 'str'
valueRepInAST = 'value'
sliceRepInAST = 'slice'
indexRepInAST = 'Index'
lineNoRepInAST = 'lineno'
pairingName = 'pair'
input = 'input'
unknownType = 'Unknown'
otherType = 'other'
#noneType = 'None'
newSliceNameKey = 'NewSliceName'
hashBase = 'HashBase'
hashFunction = 'HashFunction'
tupleKey = 'Tuple'
varNamesKey = 'VariableNamesList'
lambdaFunction = 'LambdaFunction'
lambdaRepInAST = 'Lambda'
lambdaArgPlaceholder = 'lambdaArgPlaceholder'
lambdaArgBegin = 'LAMBDA_ARG_BEGIN'
lambdaArgEnd = 'LAMBDA_ARG_END'
dotProductFuncName = 'dotprod'
bodyRepInAST = 'body'
verifyEndPrecomputeString = '# END_PRECOMPUTE'
sRepInAST = 's'
G1 = 'G1'
G2 = 'G2'
GT = 'GT'

def getGroupType(astAssignDict, varName, dictKey = ""):
	try:
		lineNos = list(astAssignDict[varName].keys())
	except:
		return unknownType
			
	if (len(lineNos) == 0):
		return unknownType
	
	lineNos.sort()
	lineNos.reverse()
	lineNo = lineNos[0]

	if (dictKey == ""):
		try:
			return astAssignDict[varName][lineNo][groupType]
		except:
			return unknownType

	try:			
		return astAssignDict[varName][lineNo][dictRepInAST][dictKey][groupType]
	except:
		return unknownType

class ASTFindGroupTypes(ast.NodeVisitor):
	def __init__(self):
		self.groupTypes = {}

	def getGroupType(self, varName, dictKey = ""):
		try:
			lineNos = list(self.groupTypes[varName].keys())
		except:
			return unknownType
			
		if (len(lineNos) == 0):
			return unknownType
	
		lineNos.sort()
		lineNos.reverse()
		lineNo = lineNos[0]

		if (dictKey == ""):
			try:
				return self.groupTypes[varName][lineNo][groupType]
			except:
				return unknownType

		try:			
			return self.groupTypes[varName][lineNo][dictRepInAST][dictKey][groupType]
		except:
			return unknownType

	def getLambdaArgs(self, lambdaNode):
		lambdaArgs = []
		if (argsRepInAST in lambdaNode._fields):
			if (argsRepInAST in lambdaNode.args._fields):
				numLambdaArgs = len(lambdaNode.args.args) - 1
				for lambdaIndex in range(0, numLambdaArgs):
					if (argRepInAST in lambdaNode.args.args[lambdaIndex + 1]._fields):
						lambdaArgs.append(lambdaNode.args.args[lambdaIndex + 1].arg)
		return lambdaArgs

	def getLambdaArgOrderStatement(self, lambdaArgs, argName):
		lambdaArgOrder = -1
		try:
			lambdaArgOrder = lambdaArgs.index(argName)
		except:
			return ""

		return lambdaArgBegin + str(lambdaArgOrder) + lambdaArgEnd

	def getLambdaFuncExpression(self, node, lambdaArgs):
		#print(lambdaArgs)
		if (type(node).__name__ == binOpRepInAST):
			left = self.getLambdaFuncExpression(node.left, lambdaArgs)
			right = self.getLambdaFuncExpression(node.right, lambdaArgs)
			op = self.getLambdaFuncExpression(node.op, lambdaArgs)
			return left + " " + op + " " + right
		elif (type(node).__name__ == subscriptRepInAST):
			if (valueRepInAST in node._fields):
				if (idRepInAST in node.value._fields):
					return self.getLambdaArgOrderStatement(lambdaArgs, node.value.id)
			'''
			if (sliceRepInAST in node._fields):
				if (valueRepInAST in node.slice._fields):
					if (idRepInAST in node.slice.value._fields):
						retString += node.slice.value.id + "]"
						return retString
			'''
			return ""
		elif (type(node).__name__ == expRepInAST):
			return "^"
		elif (type(node).__name__ == multRepInAST):
			return "*"
		else:
			print(type(node).__name__)
			return ""

	def recordDotProductVariable(self, dotProdNode, variableName, dotProductVariableNames):
		dotProdString = "prod{ j := 1 , "

		if (argsRepInAST not in dotProdNode._fields):
			return

		numArgs = len(dotProdNode.args)
		if (numArgs < 5):
			return

		if (idRepInAST not in dotProdNode.args[2]._fields):
			return
				
		dotProdString += dotProdNode.args[2].id + " } on ( "

		if (idRepInAST not in dotProdNode.args[3]._fields):
			return

		funcName = dotProdNode.args[3].id

		if (funcName not in self.groupTypes):
			return

		lineNos = list(self.groupTypes[funcName].keys())
		lineNos.sort()
		lineNos.reverse()
		lineNo = lineNos[0]

		if (lambdaFunction not in self.groupTypes[funcName][lineNo]):
			return

		funcString = self.groupTypes[funcName][lineNo][lambdaFunction]

		numDotProdArgs = numArgs - 4
		if (numDotProdArgs < 1):
			return

		for dotProdArgIndex in range(4, numArgs):
			if (idRepInAST not in dotProdNode.args[dotProdArgIndex]._fields):
				return
			dotProductVariableNames.append(dotProdNode.args[dotProdArgIndex].id)

		#dotProductVariableNames = dotProdArgNames

		#print(dotProdArgNames)

		argStartIndex = funcString.find(lambdaArgBegin)
		while (argStartIndex != -1):
			argStartIndex += len(lambdaArgBegin)
			argEndIndex = funcString.find(lambdaArgEnd, argStartIndex)
			argNumber = int(funcString[argStartIndex:argEndIndex])
			#print(argNumber)
			stringToReplace = lambdaArgBegin + str(argNumber) + lambdaArgEnd
			#print(stringToReplace)
			replacementString = dotProductVariableNames[argNumber] + "_j"
			#print(replacementString)
			#print(funcString)
			#print("\n\n")
			funcString = funcString.replace(stringToReplace, replacementString)
			argStartIndex = funcString.find(lambdaArgBegin)

		dotProdString += funcString
		dotProdString += " )"

		#print(dotProdString)

		return dotProdString

	def recursiveNodeVisit(self, node):		
		if (type(node).__name__ == callRepInAST):			
			if (funcRepInAST in node._fields):
				#print(ast.dump(node))
				#print("\n")				
				if (attrRepInAST in node.func._fields):
					#print(ast.dump(node))					
					if (node.func.attr in hashRepInAST):						
						if (argsRepInAST in node._fields):							
							if (len(node.args) == 2):
								return node.args[1].id
					elif (node.func.attr in initRepInAST):
						if (argsRepInAST in node._fields):							
							if (len(node.args) >= 1):
								return node.args[0].id
					elif (node.func.attr == randomRepInAST):						
						if (argsRepInAST in node._fields):							
							if (len(node.args) == 1):
								return node.args[0].id

				elif (idRepInAST in node.func._fields):
					topLevelKey = node.func.id
					#print(topLevelKey)
					if (topLevelKey in self.groupTypes):
						#print(topLevelKey)
						lineNos = list(self.groupTypes[topLevelKey].keys())
						lineNos.sort()
						lineNos.reverse()
						lineNo = lineNos[0]
						if (hashFunction in self.groupTypes[topLevelKey][lineNo]):
							if (groupType in self.groupTypes[topLevelKey][lineNo][hashFunction]):
								return self.groupTypes[topLevelKey][lineNo][hashFunction][groupType]

					elif (topLevelKey == pairingName):
						if (argsRepInAST in node._fields):
							if (len(node.args) == 2):
								if (idRepInAST in node.args[0]._fields):
									groupTypeArg1 = self.getGroupType(node.args[0].id)
								if (valueRepInAST in node.args[1]._fields):
									if (idRepInAST in node.args[1].value._fields):
										idArg2 = node.args[1].value.id
										if (sliceRepInAST in node.args[1]._fields):
											if (valueRepInAST in node.args[1].slice._fields):
												if (sRepInAST in node.args[1].slice.value._fields):
													sliceArg2 = node.args[1].slice.value.s
													groupTypeArg2 = self.getGroupType(idArg2, sliceArg2)
													if ( (groupTypeArg1 == G1) and (groupTypeArg2 == G2) ):
														return GT



		elif (type(node).__name__ == binOpRepInAST):
			if (leftNodeRepInAST in node._fields):
				if (type(node.left).__name__ == nameRepInAST):
					retGroupType = self.getGroupType(node.left.id)
					if (retGroupType != unknownType):
						return retGroupType

		for childNode in ast.iter_child_nodes(node):
			retVal = self.recursiveNodeVisit(childNode)
			if (retVal != unknownType):
				return retVal
		
		return unknownType

	def visit_Assign(self, node):
		topLevelKey = ""

		if (ast.dump(node.targets[0]).startswith('Tuple(')):
			if (eltsRepInAST in node.targets[0]._fields):
				tupleObjects = node.targets[0].elts
				tupleNames = []
				for tupleObject in tupleObjects:
					if (idRepInAST in tupleObject._fields):
						tupleNames.append(tupleObject.id)
				if (valueRepInAST in node._fields):
					if (idRepInAST in node.value._fields):
						if (node.value.id in self.groupTypes):
							tupleGroupTypes = getTupleGroupTypes(self.groupTypes, node.value.id)
							if (len(tupleNames) == len(tupleGroupTypes) ):

								for tupleName,tupleGroupType in zip(tupleNames,tupleGroupTypes):



									self.groupTypes[tupleName] = {}
									self.groupTypes[tupleName][node.lineno] = {}



									self.groupTypes[tupleName][node.lineno][groupType] = tupleGroupType

		FIXME = False

		if (ast.dump(node.targets[0]).startswith('Subscript(')):
			if (valueRepInAST in node.targets[0]._fields):
				if (idRepInAST in node.targets[0].value._fields):
					topLevelKey = node.targets[0].value.id
					if (topLevelKey not in self.groupTypes):
						self.groupTypes[topLevelKey] = {}
					FIXME = True
					
		
		if ( (ast.dump(node.targets[0]).startswith('Name(')) or (FIXME == True)):			
			if (idRepInAST in node.targets[0]._fields):
				topLevelKey = node.targets[0].id
				if (topLevelKey not in self.groupTypes.keys()):
					self.groupTypes[topLevelKey] = {}
				if ( (topLevelKey == N_name) and (type(node.value).__name__ == numRepInAST) ):
					self.groupTypes[topLevelKey][node.lineno] = {valueRepInAST:node.value.n}
					return
				if ( (topLevelKey == numSignersName) and (type(node.value).__name__ == numRepInAST) ):
					self.groupTypes[topLevelKey][node.lineno] = {valueRepInAST:node.value.n}
					return
				FIXME = True
			if (FIXME == True):
				if (type(node.value).__name__ == dictRepInAST):
					keysList = node.value.keys
					if (len(keysList) > 0):
						self.groupTypes[topLevelKey][node.lineno] = {dictRepInAST:{}}
						for index in range(0,len(keysList)):
							if (type(node.value.keys[index]).__name__ == strRepInAST):
								newSliceName = topLevelKey + str(index)									
								if (type(node.value.values[index]).__name__ == nameRepInAST):
									self.groupTypes[topLevelKey][node.lineno][dictRepInAST][keysList[index].s] = {newSliceNameKey:newSliceName, valueRepInAST:node.value.values[index].id}
									retGroupType = self.getGroupType(node.value.values[index].id)
									if (retGroupType != unknownType):
										self.groupTypes[topLevelKey][node.lineno][dictRepInAST][keysList[index].s][groupType] = retGroupType
									else:
										retGroupType = self.recursiveNodeVisit(node)
										self.groupTypes[topLevelKey][node.lineno][dictRepInAST][keysList[index].s][groupType] = retGroupType
								else:
									retGroupType = self.recursiveNodeVisit(node)
									self.groupTypes[topLevelKey][node.lineno][dictRepInAST][keysList[index].s] = {newSliceNameKey:newSliceName, groupType:retGroupType}
					return
				if (type(node.value).__name__ == callRepInAST):
					if (funcRepInAST in node.value._fields):
						#print(ast.dump(node))
						if (attrRepInAST in node.value.func._fields):
							if (node.value.func.attr in hashRepInAST):
								if (argsRepInAST in node.value._fields):
									if (len(node.value.args) == 2):
										self.groupTypes[topLevelKey][node.lineno] = {hashBase:node.value.args[0].id, groupType:node.value.args[1].id}
										return

						elif (idRepInAST in node.value.func._fields):
							funcName = node.value.func.id
							if (funcName in self.groupTypes):
								lineNos = list(self.groupTypes[funcName].keys())
								lineNos.sort()
								lineNos.reverse()
								lineNo = lineNos[0]
								if (hashFunction in self.groupTypes[funcName][lineNo]):
									if (groupType in self.groupTypes[funcName][lineNo][hashFunction]):
										if (argsRepInAST in node.value._fields):
											numOfArgs = len(node.value.args)
											argConcatString = ""
											for argIndex in range(0, numOfArgs):
												#print(ast.dump(node))
												#print("\n")
												if (idRepInAST in node.value.args[argIndex]._fields):
													argConcatString += node.value.args[argIndex].id + " | "
												elif (sliceRepInAST in node.value.args[argIndex]._fields):
													print(ast.dump(node))
													#print("\n")
													if (type(node.value.args[argIndex].slice).__name__ == indexRepInAST):
														if (valueRepInAST in node.value.args[argIndex].slice._fields):
															if (type(node.value.args[argIndex].slice.value).__name__ == strRepInAST):
																print(ast.dump(node))
																print("\n")
																argConcatString += node.value.args[argIndex].slice.value.s + " | "


												#print(node.value.args[argIndex]._fields)

												elif (valueRepInAST in node.value.args[argIndex]._fields):
													#print(node.value.args[argIndex].value._fields)
													print("success")

											argConcatString = argConcatString.rstrip(" | ")
											self.groupTypes[topLevelKey][node.lineno] = {hashBase:argConcatString, groupType:self.groupTypes[funcName][lineNo][hashFunction][groupType]}
											return
							elif (funcName == dotProductFuncName):
								self.groupTypes[topLevelKey][node.lineno] = {}
								dotProductVariableNames = []
								self.groupTypes[topLevelKey][node.lineno][dotProductFuncName] = self.recordDotProductVariable(node.value, topLevelKey, dotProductVariableNames)
								self.groupTypes[topLevelKey][node.lineno][varNamesKey] = dotProductVariableNames
								return
				if (type(node.value).__name__ == lambdaRepInAST):
					#print(ast.dump(node))
					if (bodyRepInAST in node.value._fields):
						#print(ast.dump(node))
						if (funcRepInAST in node.value.body._fields):
							#print(ast.dump(node))
							if (attrRepInAST in node.value.body.func._fields):
								#print(node.value.body.func._fields)
								if (node.value.body.func.attr in hashRepInAST):
									if (argsRepInAST in node.value.body._fields):
										if (len(node.value.body.args) == 2):
											#print(node.value.body.args[0]._fields)
											if (idRepInAST in node.value.body.args[1]._fields):
												self.groupTypes[topLevelKey][node.lineno] = {}
												self.groupTypes[topLevelKey][node.lineno][hashFunction] = {}
												self.groupTypes[topLevelKey][node.lineno][hashFunction][groupType] = node.value.body.args[1].id
												return
												#pass
						#elif (binOpRepInAST in node.value.body._fields):
							#print(ast.dump(node))
						else:
							#print(type(node.value.body).__name__)
							self.groupTypes[topLevelKey][node.lineno] = {}
							lambdaArgs = self.getLambdaArgs(node.value)
							self.groupTypes[topLevelKey][node.lineno][lambdaFunction] = self.getLambdaFuncExpression(node.value.body, lambdaArgs)
							return

				if (type(node.value).__name__ == tupleRepInAST):
					if (eltsRepInAST in node.value._fields):
						#print(ast.dump(node))
						lenOfTupleItems = len(node.value.elts)
						self.groupTypes[topLevelKey][node.lineno] = {}
						self.groupTypes[topLevelKey][node.lineno][tupleKey] = {}
						self.groupTypes[topLevelKey][node.lineno][tupleKey][varNamesKey] = []
						self.groupTypes[topLevelKey][node.lineno][tupleKey][groupType] = []
						for tupleIndex in range(0, lenOfTupleItems):
							if (idRepInAST in node.value.elts[tupleIndex]._fields):
								tupleArgName = node.value.elts[tupleIndex].id
								self.groupTypes[topLevelKey][node.lineno][tupleKey][varNamesKey].append(tupleArgName)
								self.groupTypes[topLevelKey][node.lineno][tupleKey][groupType].append(self.getGroupType(tupleArgName))
						return

				if (type(node.value).__name__ == 'Subscript'):
					if (valueRepInAST in node.value._fields):
						if (idRepInAST in node.value.value._fields):
							dictEntryName = node.value.value.id
							if (sliceRepInAST in node.value._fields):
								if (valueRepInAST in node.value.slice._fields):
									#print(node.value.slice.value._fields)
									if (sRepInAST in node.value.slice.value._fields):
										dictEntrySlice = node.value.slice.value.s
										#print(dictEntrySlice)
										self.groupTypes[topLevelKey][node.lineno] = {}
										self.groupTypes[topLevelKey][node.lineno][groupType] = self.getGroupType(dictEntryName, dictEntrySlice)


						#print(node.value.elts)

						#print(node.value._fields)


				retGroupType = self.recursiveNodeVisit(node)
				if (retGroupType != unknownType):
					self.groupTypes[topLevelKey][node.lineno] = {groupType:retGroupType}
					return

	def getGroupTypesDict(self):
		if (len(self.groupTypes) < 1):
			return 0
		keys = list(self.groupTypes.keys())
		for key in keys:
			if (self.groupTypes[key] == {}):
				del self.groupTypes[key]
		return self.groupTypes

class ASTVerifyFuncVisitor(ast.NodeVisitor):
	def __init__(self):
		self.verifyFunc = []

	def visit_FunctionDef(self, node):
		if (node.name == nameOfVerifyFunc):
			self.verifyFunc.append(node)

	def getVerifyFuncFromASTVisitor(self):
		if (len(self.verifyFunc) == 1):
			return self.verifyFunc[0]
		else:
			return []

class ASTFindAllVariables(ast.NodeVisitor):
	def __init__(self):
		self.variables = {}

	def visit_Subscript(self, node):
		if (valueRepInAST in node._fields):
			if (type(node.value).__name__ == nameRepInAST):
				topLevelKey = node.value.id
				if (topLevelKey == pairingName):
					return
				if (topLevelKey not in self.variables.keys()):
					self.variables[topLevelKey] = {}
					index = 0
				else:
					index = self.getNextIndex(topLevelKey)
				if (sliceRepInAST in node._fields):
					if (type(node.slice).__name__ == indexRepInAST):
						if (valueRepInAST in node.slice._fields):
							if (type(node.slice.value).__name__ == strRepInAST):
								self.variables[topLevelKey][index] = {valueRepInAST:node.slice.value.s, lineNoRepInAST:node.lineno}

	def visit_Name(self, node):
		if (node.id == pairingName):
			return

		addToDict = True

		if (node.id in self.variables.keys()):
			for i in self.variables[node.id].keys():
				if (node.lineno == self.variables[node.id][i][lineNoRepInAST]):
					addToDict = False

		if (addToDict == True):
			if (node.id not in self.variables.keys()):
				self.variables[node.id] = {}

	def getNextIndex(self, topLevelKey):
		currIndices = list(self.variables[topLevelKey].keys())
		if (len(currIndices) == 0):
			return 0
		currIndices.sort()
		currIndices.reverse()
		lastIndex = currIndices[0]
		return (lastIndex + 1)

	def getVariableNames(self):
		if (len(self.variables) < 1):
			return 0
		return self.variables

class ASTEqCompareVisitor(ast.NodeVisitor):
	def __init__(self):
		self.eqCompareNodes = {}

	def visit_Compare(self, node):
		loopCounter = 0
		for childNode in ast.iter_child_nodes(node):
			if ( (loopCounter == 1) and (ast.dump(childNode) == equalityOperator) ):
				self.eqCompareNodes[node.lineno] = node
			loopCounter = loopCounter + 1
			if (loopCounter > 1):
				break

	def getLastEqOpFromVerify(self):
		if (len(self.eqCompareNodes) < 1):
			return 0
		lineNumsList = list(self.eqCompareNodes.keys())
		lineNumsList.sort()
		lineNumsList.reverse()
		return self.eqCompareNodes[lineNumsList[0]]

def getRootASTNode(lines):
	code = ""
	for line in lines:
		code += line
	return ast.parse(code)

def getVerifyFuncNode(astNode):
	astVerifyVisitor = ASTVerifyFuncVisitor()
	astVerifyVisitor.visit(astNode)
	return astVerifyVisitor.getVerifyFuncFromASTVisitor()

def getVerifyEqNode(verifyFuncNode):
	astEqVisitor = ASTEqCompareVisitor()
	astEqVisitor.visit(verifyFuncNode)
	return astEqVisitor.getLastEqOpFromVerify()

def getLineFromSourceCode(lines, lineNum):
	lineCounter = 1
	for line in lines:
		if (lineCounter == lineNum):
			return line
		else:
			lineCounter = lineCounter + 1

def cleanVerifyEq(origVerifyEq):
	cleanVerifyEq = origVerifyEq.lstrip().lstrip('if ').rstrip().rstrip(':').replace('pair', 'e').replace('**', '^')
	cleanVerifyEq = cleanVerifyEq.replace(' = ', ' := ')
	cleanVerifyEq = "verify := { " + cleanVerifyEq + " }"
	return cleanVerifyEq

def replaceDictVars(verifyEqLn, assignmentsDict, variableNames, variableTypes):
	for varName in variableNames:		
		if varName not in assignmentsDict.keys():
			continue
		linenums = list(assignmentsDict[varName].keys())
		if (len(linenums) == 0):
			continue
		linenums.sort()
		linenums.reverse()
		if (dictRepInAST not in assignmentsDict[varName][linenums[0]].keys()):
			continue	
		for sliceIndex in variableNames[varName]:
			origVarName = ""
			origVarName += varName
			origVarName += "['"
			sliceName = variableNames[varName][sliceIndex][valueRepInAST]
			origVarName += sliceName
			origVarName += "']"
			newVarName = assignmentsDict[varName][linenums[0]][dictRepInAST][sliceName][newSliceNameKey]			
			verifyEqLn = verifyEqLn.replace(origVarName, newVarName)
			if (varName in variableTypes.keys()):
				del variableTypes[varName]
			if (newVarName not in variableTypes.keys()):
				if (groupType in assignmentsDict[varName][linenums[0]][dictRepInAST][sliceName].keys()):
					variableTypes[newVarName] = assignmentsDict[varName][linenums[0]][dictRepInAST][sliceName][groupType]
				else:
					variableTypes[newVarName] = 0

	return verifyEqLn

def expandHashesInVerify(verifyEqLn, hashAssignmentsDict, variableNames, variableTypes, precomputeTypes, verifyEndPrecomputeLine, verifyFuncLineStart, verifyFuncLineEnd):
	for varName in variableNames:
		#print(varName)
		if varName not in hashAssignmentsDict.keys():
			continue
		linenums = list(hashAssignmentsDict[varName].keys())
		if (len(linenums) == 0):
			continue
		linenums.sort()
		linenums.reverse()
		if (hashBase not in hashAssignmentsDict[varName][linenums[0]].keys()):
			continue
		if ( (linenums[0] < verifyFuncLineStart) or (linenums[0] > verifyFuncLineEnd) ):
			continue

		hashExpansion = ""
		hashExpansion += " H("
		inputVariable = hashAssignmentsDict[varName][linenums[0]][hashBase]
		hashExpansion += inputVariable
		hashExpansion += ", "
		hashExpansion += hashAssignmentsDict[varName][linenums[0]][groupType]
		hashExpansion += ") "
		searchExpression = " " + varName + " "

		if (linenums[0] < verifyEndPrecomputeLine):
			precomputeTypes[varName] = hashExpansion
			variableTypes[varName] = hashAssignmentsDict[varName][linenums[0]][groupType]
			#print(varName)
		else:
			verifyEqLn = verifyEqLn.replace(searchExpression, hashExpansion)

		#if (varName in variableTypes.keys()):
			#del variableTypes[varName]
		if (inputVariable not in variableTypes.keys()):
			variableTypes[inputVariable] = 0

	#print(precomputeTypes)

	return verifyEqLn

def ensureSpacesBtwnTokens(lineOfCode):
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

def getType(variable, assignmentsDict):
	lineNos = list(assignmentsDict[variable].keys())
	lineNos.sort()
	lineNos.reverse()
	lastLineNo = lineNos[0]

	if (groupType in assignmentsDict[variable][lastLineNo].keys()):
		return assignmentsDict[variable][lastLineNo][groupType]
	else:
		return strRepInBV

def getVariableTypes(variableTypes, assignmentsDict):
	for variable in variableTypes:		
		if (variableTypes[variable] != 0):
			continue
		if (variable in assignmentsDict.keys()):
			variableTypes[variable] = getType(variable, assignmentsDict)
		else:
			variableTypes[variable] = strRepInBV

	return variableTypes

def writeBVFile(outputFileName, variableTypes, precomputeTypes, cleanVerifyEqLn):
	outputFile = open(outputFileName, 'w')

	outputString = ""
	outputString += "# bls batch inputs\n"
	outputString += "# variables\n"
	outputString += "N := "
	outputString += str(variableTypes[N_name])
	outputString += "\n"

	outputString += "numSigners := "
	outputString += str(variableTypes[numSignersName])
	outputString += "\n\n"

	outputString += "BEGIN :: types\n"

	for variable in variableTypes:
		if ( (variable == N_name) or (variable == numSignersName) ):
			continue
		outputString += variable
		outputString += " := "
		outputString += variableTypes[variable]
		outputString += "\n"

	outputString += "END :: types\n\n"

	outputString += "BEGIN :: precompute\n"

	for variable in precomputeTypes:
		outputString += variable
		outputString += " := "
		outputString += precomputeTypes[variable]
		outputString += "\n"

	outputString += "END :: precompute\n\n"

	outputString += "# verify equation\n"
	outputString += cleanVerifyEqLn
	outputString += "\n"

	outputFile.write(outputString)
	outputFile.close()

	#print(outputString)

def findVariable(astAssignDict, variableName):
	if (variableName not in astAssignDict.keys()):
		return unknownType
	
	lineNos = list(astAssignDict[variableName].keys())
	lineNos.sort()
	lineNo = lineNos[0]
	
	if (valueRepInAST not in astAssignDict[variableName][lineNo].keys()):
		return unknownType

	return astAssignDict[variableName][lineNo][valueRepInAST]

def getLineOfTextFromSource(lineString, linesOfCode, startLine, endLine):
	lineNo = 1

	for line in linesOfCode:
		if (lineNo < startLine):
			lineNo += 1
			continue
		if (lineNo > endLine):
			return 0
		if (lineString in line):
			return lineNo
		lineNo += 1

	return 0

def replaceDotProdVars(verifyEq, astAssignDict, variableNames, variableTypes):
	#print(verifyEq)
	#print(variableNames)

	varsToAdd = []
	varsToRemove = []

	#print(variableNames)

	for varName in variableNames:
		if (varName not in astAssignDict):
			continue
		lineNos = list(astAssignDict[varName].keys())
		lineNos.sort()
		lineNos.reverse()
		lineNo = lineNos[0]

		if (dotProductFuncName not in astAssignDict[varName][lineNo]):
			continue

		stringToBeReplaced = " " + varName + " "
		replacementString = " " + astAssignDict[varName][lineNo][dotProductFuncName] + " "
		verifyEq = verifyEq.replace(stringToBeReplaced, replacementString)

		#if (

		if (varNamesKey not in astAssignDict[varName][lineNo]):
			continue

		dotProdVarNames = astAssignDict[varName][lineNo][varNamesKey]
		#print(dotProdVarNames)

		#print(astAssignDict)

		for dotProdVarName in dotProdVarNames:
			variableTypes[dotProdVarName] = getGroupType(astAssignDict, dotProdVarName)
			varsToAdd.append(dotProdVarName)

		varsToRemove.append(varName)

		for dotProdVarName in astAssignDict[varName][lineNo][varNamesKey]:
			#print(dotProdVarName)
			pass

	for varName in varsToRemove:
		del variableNames[varName]

	for varName in varsToAdd:
		variableNames[varName] = {}

	#print(variableNames)		
		
	return verifyEq

def printDictionary(dict):
	for key in dict:
		print(key + ":\t" + str(dict[key]))
		print("\n")

def getTupleGroupTypes(astAssignDict, varName):
	if (varName not in astAssignDict):
		return []

	tupleGroupTypes = []

	lineNos = list(astAssignDict[varName].keys())
	lineNos.sort()
	lineNos.reverse()
	lineNo = lineNos[0]
	if (tupleKey not in astAssignDict[varName][lineNo]):
		return []

	if (groupType not in astAssignDict[varName][lineNo][tupleKey]):
		return []

	for groupTypeEntry in astAssignDict[varName][lineNo][tupleKey][groupType]:
		tupleGroupTypes.append(groupTypeEntry)

	return tupleGroupTypes

if __name__ == '__main__':
	if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python AST_Visitor.py [name of input file that runs the cryptosystem] [name of .bls output file]")

	pythonFile = sys.argv[1]
	outputFileName = sys.argv[2]

	sourceCodeLines = open(pythonFile, 'r').readlines()
	astNode = getRootASTNode(sourceCodeLines)

	verifyFuncNode = getVerifyFuncNode(astNode)
	if (verifyFuncNode == []):
		sys.exit("Could not locate a function with name \"verify\"")

	verifyEqNode = getVerifyEqNode(verifyFuncNode)
	if (verifyEqNode == 0):
		sys.exit("Could not locate the verify equation within the \"verify\" function")

	origVerifyEq = getLineFromSourceCode(sourceCodeLines, verifyEqNode.lineno)

	#print(origVerifyEq)

	cleanVerifyEqLn = cleanVerifyEq(origVerifyEq)

	#print(cleanVerifyEqLn)

	astAssignments = ASTFindGroupTypes()
	astAssignments.visit(astNode)
	astAssignDict = astAssignments.getGroupTypesDict()
	if (astAssignDict == 0):
		sys.exit("Could not properly parse the assignment statements in the code")

	variableNamesAST = ASTFindAllVariables()
	variableNamesAST.visit(verifyEqNode)
	variableNames = variableNamesAST.getVariableNames()
	if (variableNames == 0):
		sys.exit("Could not retrieve variable names from verify equation")

	variableTypes = {}
	precomputeTypes = {}

	for varName in variableNames:
		variableTypes[varName] = 0

	verifyFuncLineStart = verifyFuncNode.lineno
	verifyFuncLineEnd = verifyEqNode.lineno

	verifyEndPrecomputeLine = getLineOfTextFromSource(verifyEndPrecomputeString, sourceCodeLines, verifyFuncLineStart, verifyFuncLineEnd)

	cleanVerifyEqLn = replaceDictVars(cleanVerifyEqLn, astAssignDict, variableNames, variableTypes)
	cleanVerifyEqLn = ensureSpacesBtwnTokens(cleanVerifyEqLn)

	cleanVerifyEqLn = replaceDotProdVars(cleanVerifyEqLn, astAssignDict, variableNames, variableTypes)

	cleanVerifyEqLn = expandHashesInVerify(cleanVerifyEqLn, astAssignDict, variableNames, variableTypes, precomputeTypes, verifyEndPrecomputeLine, verifyFuncLineStart, verifyFuncLineEnd)



	#print(variableTypes)

	variableTypes = getVariableTypes(variableTypes, astAssignDict)

	#print(variableTypes)

	variableTypes[N_name] = findVariable(astAssignDict, N_name)
	variableTypes[numSignersName] = findVariable(astAssignDict, numSignersName)

	writeBVFile(outputFileName, variableTypes, precomputeTypes, cleanVerifyEqLn)

	#print("\n\n")
	#printDictionary(astAssignDict)
	#getTupleGroupTypes(astAssignDict, 'sk_tuple')
