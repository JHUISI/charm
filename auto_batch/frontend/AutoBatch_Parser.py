import con, copy, sys
from ASTParser import *
from ASTVarVisitor import ASTVarVisitor
from StringName import StringName
from Parser_CodeGen_Toolbox import *


#------------------------------

'''
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

				if (type(node.value).__name__ == dictRepInAST):
					keysList = node.value.keys
					if (len(keysList) > 0):
						self.groupTypes[topLevelKey][node.lineno] = {dictRepInAST:{}}
						for index in range(0,len(keysList)):
							if (type(node.value.keys[index]).__name__ == strRepInAST):
								newSliceName = topLevelKey + newSliceSymbol + str(index)									
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
'''

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


def writeBVFile(varAssignments, outputFileName):
	try:
		outputFile = open(outputFileName, 'w')
	except:
		sys.exit("AutoBatch_Parser->writeBVFile:  could not obtain a file named " + outputFileName + " for writing.")

	outputString = ""

	numSignatures = getStringNameIntegerValue(varAssignments, con.numSignatures, con.mainFuncName)
	if ( (numSignatures == None) or (type(numSignatures).__name__ != con.intTypePython) or (numSignatures < 1) ):
		sys.exit("AutoBatch_Parser->writeBVFile:  problem with the value returned from getNumSignatures.")

	outputString += "N = "
	outputString += str(numSignatures)
	outputString += "\n\n"

	outputString += "BEGIN :: types\n"

	try:
		outputFile.write(outputString)
		outputFile.close()
	except:
		sys.exit("AutoBatch_Parser->writeBVFile:  error when attempting to write to the " + outputFileName + " file and then close it.")

'''
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
'''

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


def main():
	if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + " [name of input file that runs the cryptosystem] [name of .bls output file]")

	inputFileName = sys.argv[1]
	outputFileName = sys.argv[2]

	if (len(inputFileName) == 0):
		sys.exit("AutoBatch_Parser->main:  input file name passed in is of length zero.")

	if (len(outputFileName) == 0):
		sys.exit("AutoBatch_Parser->main:  output file name passed in is of length zero.")

	myASTParser = ASTParser()
	rootNode = myASTParser.getASTNodeFromFile(inputFileName)
	if (rootNode == None):
		sys.exit("AutoBatch_Parser->main:  root node obtained from ASTParser->getASTNodeFromFile is of None type.")

	functionNames = myASTParser.getFunctionNames(rootNode)
	if (functionNames == None):
		sys.exit("AutoBatch_Parser->main:  function names obtained from ASTParser->getFunctionNames is of None type.")

	functionArgNames = myASTParser.getFunctionArgNames(rootNode)
	if (functionArgNames == None):
		sys.exit("AutoBatch_Parser->main:  function argument names obtained from ASTParser->getFunctionArgNames is of None type.")

	for funcName in con.funcNamesNotToTest:
		if (funcName in functionNames):
			del functionNames[funcName]
		if (funcName in functionArgNames):
			del functionArgNames[funcName]

	functionArgMappings = getFunctionArgMappings(functionNames, functionArgNames, myASTParser)
	if (functionArgMappings == None):
		sys.exit("AutoBatch_Parser->main:  mappings of variables passed between functions from getFunctionArgMappings is of None type.")

	returnNodes = getReturnNodes(functionNames, myASTParser)
	if ( (returnNodes == None) or (type(returnNodes).__name__ != con.dictTypePython) or (len(returnNodes) == 0) ):
		sys.exit("AutoBatch_Parser->main:  problem with value returned from getReturnNodes.")

	verifyFuncNodeList = myASTParser.getFunctionNode(rootNode, con.verifyFuncName)
	if (verifyFuncNodeList == None):
		sys.exit("AutoBatch_Parser->main:  could not locate a function with name " + con.verifyFuncName)
	if (len(verifyFuncNodeList) > 1):
		sys.exit("AutoBatch_Parser->main:  located more than one function with the name " + con.verifyFuncName)

	verifyFuncNode = verifyFuncNodeList[0]

	verifyEqNode = myASTParser.getLastEquation(verifyFuncNode)
	if (verifyEqNode == None):
		sys.exit("AutoBatch_Parser->main:  could not locate the verify equation within the " + con.verifyFuncName + " function.")

	origVerifyEq = myASTParser.getSourceLineOfNode(verifyEqNode)
	cleanVerifyEqLn = cleanVerifyEq(origVerifyEq)

	varsVerifyEq = getAllVariableNamesFromVerifyEq(verifyEqNode, myASTParser)
	if ( (varsVerifyEq == None) or (type(varsVerifyEq).__name__ != con.listTypePython) or (len(varsVerifyEq) == 0) ):
		sys.exit("AutoBatch_Parser->main:  problem with the value returned from getAllVariableNamesFromVerifyEq on the verify equation node.")

	varAssignments = getVarAssignments(rootNode, functionNames, myASTParser)
	if (varAssignments == None):
		sys.exit("AutoBatch_Parser->main:  getVarAssignments returned None when trying to get the variable assignments.")

	writeBVFile(varAssignments, outputFileName)


	DELETESTRING = StringName()
	DELETESTRING.setName("sig")
	DELETESTRING.setLineNo(30)

	DELETEME = ASTVarVisitor(myASTParser)
	deletethistoo = DELETEME.getVariableGroupType(DELETESTRING, "verify", functionArgMappings, functionArgNames, returnNodes, varAssignments)
	print(deletethistoo)


'''

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
'''

if __name__ == '__main__':
	main()
