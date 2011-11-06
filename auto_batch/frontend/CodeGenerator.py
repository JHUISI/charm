#TODO:  get ensurespacesbetweentokens in here, run every
#line of verify through it
#then go through and replace each variable name with the
#right variable in the verify dict

'''
Requirements:

- The definition line for the verify function in the 
Charm code for the scheme must be on one line.  For example,

def verify(pk, sig, M):

This must all be on one line.
'''

import ast, os, sys, copy

numSignaturesEndValInCode = 'N'
numSignersEndValInCode = 'numSigners'
numSignaturesEndVal = 'N'
numSignersEndVal = 'l'
pythonDictRep = 'dict'
multipleSubscriptIndicatorChar = '$'
finalEqLineString = 'Final version => '
dotProdPrefix = 'dot'
computeLineVarsNoSubscripts = 'Variable_List_No_Subscripts'
computeLineVars = 'Variable_List'
computeLineIndex = 'Index_Variable'
computeLineExp = 'Expression'
computeLineStartValue = 'Start_Value'
computeLineEndValue = 'End_Value'
computeLineRange = 'Range'
nameOfVerifyFunc = 'verify'
argsRepInAST = 'args'
argRepInAST = 'arg'
selfRepInAST = 'self'
idRepInAST = 'id'
lambdaRepInAST = 'Lambda'
callRepInAST = 'Call'
funcRepInAST = 'func'
sigNumKey = 'Signature_Number'
bodyKey = 'Body'
individualTemplate = '/Users/matt/Documents/charm/auto_batch/frontend/IndividualVerifyTemplate.py'
batchTemplate = '/Users/matt/Documents/charm/auto_batch/frontend/BatchVerifyTemplate.py'
equalityOperator = 'Eq()'
printPrefix = 'print('
commentPrefix = '#'
dictBeginChar = '['
lParan = '('
space = ' '
numSpacesPerTab = 4
pairFuncNames = ['pairing', 'PairingGroup']
selfDump = 'self.dump('
selfDumpLen = len(selfDump)
batchVerifierPythonFile = '/Users/matt/Documents/charm/auto_batch/batchverify.py'
batchVerifierOutputFile = '/Users/matt/Documents/charm/auto_batch/frontend/batchVerifierOutput'
finalBatchEqTag = 'Final batch eq'
numBitsOfSecurity = 80
deltasGroupType = 'ZR'
batchEqRemoveVars = ['e', '(', 'j', '1', 'prod', '{', '}', 'N', ':=', '^', ',', 'on', ')', '==', '*', 'i', 'l']
dotProdSymbol = '_'
deltaString = 'delta'
deltasString = 'deltas'
deltaDotProdString = 'delta_j'
idRepInAST = 'id'
eltsRepInAST = 'elts'
numRepInAST = 'n'
sliceRepInAST = 'slice'
unknownType = 'Unknown'
reservedWords = ['prod', 'group', 'G1', 'G2', 'GT', 'dotprod', 'range', 'lam_func', 'ZR', 'self', 'for', 'in', 'while', 'if', 'pass']
reservedSymbols = ['(', ')', '{', '}', ':=', '=', '-', '*', '^', '/', ',', '==', ':', '[', ']' ]
numSpacesPerTab = 4
commentChar = '#'
indentedBlockStartLineNo = 'startLineNo'
indentedBlockEndLineNo = 'endLineNo'
indentedBlockVars = 'Variable_Names'
computeLineString = 'Compute:  '
dotProdAssignSymbol = ' := '

class ImportFromVisitor(ast.NodeVisitor):
	def __init__(self):
		self.lineNos = []

	def visit_ImportFrom(self, node):
		self.lineNos.append(node.lineno)

	def getImportFromLineNos(self):
		if (len(self.lineNos) == 0):
			return 0

		return self.lineNos

class GetLastLineOfFunction(ast.NodeVisitor):
	def __init__(self):
		self.lastLine = 0

	'''
	def checkNextNode(self, node):
		print(node.lineno)
		if (node.lineno > self.lastLine):
			self.lastLine = node.lineno
	'''

	'''
	def visit_Module(self, node):
		self.checkNextNode(node)

	def visit_Interactive(self, node):
		self.checkNextNode(node)

	def visit_Expression(self, node):
		self.checkNextNode(node)

	#def visit_Assign(self, node):
		#self.checkNextNode(node)
	'''

	def generic_visit(self, node):
		#print(node._fields)
		try:
			if (node.lineno > self.lastLine):
				self.lastLine = node.lineno
		except:
			pass
		ast.NodeVisitor.generic_visit(self, node)

	def getLastLine(self):
		return self.lastLine

class BuildAssignMap(ast.NodeVisitor):
	def __init__(self):
		self.assignMap = {}
		
	def getName(self, node):
		if (idRepInAST in node._fields):
			name = node.id
			if name in reservedWords:
				return unknownType
			else:
				return name
		else:
			return unknownType

	def getAllIDs(self, node, allIDs):
		name = self.getName(node)
		if ( (name != unknownType) and (node.id not in allIDs) ):
			allIDs.append(node.id)
			return

		for childNode in ast.iter_child_nodes(node):
			self.getAllIDs(childNode, allIDs)
		
	def buildNameDictEntry(self, node):
		targetName = self.getName(node)
		if (targetName == unknownType):
			return
		if (targetName not in self.assignMap):
			self.assignMap[targetName] = {}		
		return targetName
		
	def buildValuesDictEntries(self, node, targetName):
		allIDs = []
		self.getAllIDs(node, allIDs)
		return allIDs

	def visit_Assign(self, node):
		if (eltsRepInAST in node.targets[0]._fields):
			for eltsTargetIndex in range(0, len(node.targets[0].elts)):
				targetName = self.buildNameDictEntry(node.targets[0].elts[eltsTargetIndex])
				if (targetName == unknownType):
					return
				allIDs = self.buildValuesDictEntries(node.value.elts[eltsTargetIndex], targetName)
				self.assignMap[targetName][node.lineno] = allIDs
		elif (idRepInAST in node.targets[0]._fields):
			targetName = self.buildNameDictEntry(node.targets[0])
			if (targetName == unknownType):
				return
			allIDs = self.buildValuesDictEntries(node.value, targetName)
			self.assignMap[targetName][node.lineno] = allIDs
		elif (sliceRepInAST in node.targets[0]._fields):
			targetName = self.buildNameDictEntry(node.targets[0].value)
			if (targetName == unknownType):
				return
			#print(targetName)
			#print(node.targets[0].slice._fields)
			#print(ast.dump(node))
			
			allIDs = self.buildValuesDictEntries(node.value, targetName)
			self.assignMap[targetName][node.lineno] = allIDs




		else:
			print(node.targets[0]._fields)
		#print(self.assignMap)
		
	def getAssignMap(self):
		if (len(self.assignMap) == 0):
			return {}
		
		return self.assignMap

class PrereqAssignVisitor(ast.NodeVisitor):
	def __init__(self):
		self.prereqAssignLineNos = []

	def visit_Assign(self, node):
		if (ast.dump(node.targets[0]).startswith('Name(')):
			if (idRepInAST in node.targets[0]._fields):
				if (type(node.value).__name__ == lambdaRepInAST):
					self.prereqAssignLineNos.append(node.lineno)
				elif (type(node.value).__name__ == callRepInAST):
					if (funcRepInAST in node.value._fields):
						if (idRepInAST in node.value.func._fields):
							if (node.value.func.id in pairFuncNames):
								self.prereqAssignLineNos.insert(0, node.lineno)

	def getPrereqAssignLineNos(self):
		return self.prereqAssignLineNos

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

def isPreviousCharAlpha(line, currIndex):
	if (currIndex == 0):
		return False
	
	if (line[currIndex - 1].isalpha() == True):
		return True
	
	return False


def isNextCharAlpha(line, currIndex):
	lastCharIndex = len(line) - 1
	if (currIndex == lastCharIndex):
		return False
	
	if (line[currIndex + 1].isalpha() == True):
		return True
	
	return False


def isLineOnlyWhiteSpace(line):
	line = line.lstrip().rstrip()
	if (line == ""):
		return True
	return False

def getVerifyEqNode(verifyFuncNode):
	astEqVisitor = ASTEqCompareVisitor()
	astEqVisitor.visit(verifyFuncNode)
	return astEqVisitor.getLastEqOpFromVerify()

def getRootASTNode(lines):
	code = ""
	for line in lines:
		code += line
	return ast.parse(code)

def getVerifyFuncNode(astNode):
	astVerifyVisitor = ASTVerifyFuncVisitor()
	astVerifyVisitor.visit(astNode)
	return astVerifyVisitor.getVerifyFuncFromASTVisitor()

def getVerifyFuncArgs(verifyFuncNode):
	verifyFuncArgs = []
	if (argsRepInAST not in verifyFuncNode._fields):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")
	if (argsRepInAST not in verifyFuncNode.args._fields):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")

	numArgs = len(verifyFuncNode.args.args)
	for index in range(0, numArgs):
		if (argRepInAST not in verifyFuncNode.args.args[index]._fields):
			sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")
		if (verifyFuncNode.args.args[index].arg != selfRepInAST):
			verifyFuncArgs.append(verifyFuncNode.args.args[index].arg)

	if (len(verifyFuncArgs) <= 0):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")

	return verifyFuncArgs

def removeLastCharNewline(buf):
	lenOfBuf = len(buf)
	lastChar = lenOfBuf - 1
	if (buf[lastChar] == 10):
		buf = buf[0:lastChar]

	return buf

def getNumIndentedSpaces(line):
	lenOfLine = len(line)
	for index in range(0, lenOfLine):
		if (line[index] != space):
			break

	#print(line)

	#if (index == 0):
		#sys.exit("Error:  one of the lines in the verify() function is not preceded by a space.")

	return index

def getLinesFromSourceCode(lines, startLine, endLine, indentationList):
	retLines = []
	lineCounter = 1

	for line in lines:
		if (lineCounter > endLine):
			return retLines
		if (lineCounter >= startLine):
			numIndentedSpaces = getNumIndentedSpaces(line)
			tempLine = line.lstrip().rstrip()
			if ( (not tempLine.startswith(printPrefix)) and (not tempLine.startswith(commentPrefix)) ):
				#print(tempLine)
				retLines.append(tempLine)
				indentationList.append(numIndentedSpaces)
		lineCounter += 1

def ensureSpacesBtwnTokens(lineOfCode):
	if (lineOfCode == '\n'):
		return lineOfCode
	
	L_index = 1
	R_index = 1
	withinApostrophes = False

	while (True):
		checkForSpace = False
		if (lineOfCode[R_index] == '\''):
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
			
			
				
		#elif ( (lineOfCode[R_index] == '[') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
			#currChars = lineOfCode[R_index]
			#L_index = R_index
			#checkForSpace = True

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

		#CHEAP HACK!!!!  THIS MUST BE FIXED
		if (R_index == (lenOfLine - 1)):
			if (lineOfCode[R_index] == ']'):
				lineOfCode = lineOfCode[0:R_index] + ' ]'
				break
			elif (lineOfCode[R_index] == ')'):
				lineOfCode = lineOfCode[0:R_index] + ' )'
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

def removeLeftParanSpaces(line):
	nextLParanIndex = line.find(lParan)

	while (nextLParanIndex != -1):
		if ( (nextLParanIndex > 0) and (line[nextLParanIndex - 1] == space) ):
			lenOfLine = len(line)
			line = line[0:(nextLParanIndex - 1)] + line[nextLParanIndex:lenOfLine]
			nextLParanIndex = line.find(lParan, nextLParanIndex)
		else:
			nextLParanIndex = line.find(lParan, (nextLParanIndex + 1))

	return line

def determineNumTabs(numSpaces):
	if ( (numSpaces % numSpacesPerTab) != 0):
		sys.exit("Error:  Python cryptosystem did not use proper number of spaces per tab.")

	return (int(numSpaces / numSpacesPerTab))

def getImportFromLines(rootNode, codeLines):
	importVisitor = ImportFromVisitor()
	importVisitor.visit(rootNode)
	importLineNos = importVisitor.getImportFromLineNos()

	indentationList = []
	importFromLines = []

	for lineNo in importLineNos:
		importLineList = getLinesFromSourceCode(codeLines, lineNo, lineNo, indentationList)
		importFromLines.append(importLineList[0])

	if (len(importFromLines) == 0):
		return 0

	return importFromLines

def removeSelfDump(line):
	selfDumpIndex = line.find(selfDump)
	if (selfDumpIndex == -1):
		return line

	lenOfLine = len(line)
	line = line[0:selfDumpIndex] + line[(selfDumpIndex + selfDumpLen + 1):lenOfLine]
	line = line.rstrip(')')
	return line

def cleanFinalBatchEq(finalBatchEq):
	#print(finalBatchEq)
	finalBatchEq = finalBatchEq.lstrip(finalBatchEqTag).lstrip(':').lstrip()
	
	
	finalBatchEq = ensureSpacesBtwnTokens(finalBatchEq)
	
	#finalBatchEq = finalBatchEq.rstrip()
	
	#print(finalBatchEq)
	
	return finalBatchEq
	
	#print(finalBatchEq)

def addDeltasAndArgSigIndexMap(batchOutputString):
	batchOutputString += "\n\t" + deltasString + " = {}\n\n"
	batchOutputString += "\tfor sigIndex in range(1, (numSigs+1)):\n"
	batchOutputString += "\t\t" + deltasString + ".append(prng_bits(" + deltasGroupType + ", " + str(numBitsOfSecurity) + "))\n\n"

	'''
	batchOutputString += "\t\tfor arg in verifyFuncArgs:\n"
	batchOutputString += "\t\t\tif (sigNumKey in verifyArgsDict[sigIndex][arg]):\n"
	batchOutputString += "\t\t\t\targSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])\n"
	batchOutputString += "\t\t\telse:\n"
	batchOutputString += "\t\t\t\targSigIndexMap[arg] = sigIndex\n\n"
	'''
		
	return batchOutputString

def addIfElse(batchOutputString, finalBatchEq):
	finalBatchEq = finalBatchEq.rstrip()
	batchOutputString += "\tif " + finalBatchEq
	batchOutputString += " :\n"
	batchOutputString += "\t\tpass\n"
	batchOutputString += "\telse:\n"
	batchOutputString += "\t\tprint(\"Batch signature verification failed.\\n\")"
	return batchOutputString

def getBatchEqVars(finalBatchEq):
	batchEqVars = finalBatchEq.split()
	for removeVar in batchEqRemoveVars:
		while (batchEqVars.count(removeVar) > 0):
			batchEqVars.remove(removeVar)

	'''
	for varIndex in range(0, len(batchEqVars)):
		batchEqVars[varIndex] = batchEqVars[varIndex].rstrip(dotProdSuffix)
	'''
	
	for dupVar in batchEqVars:
		while (batchEqVars.count(dupVar) > 1):
			batchEqVars.remove(dupVar)
			
	if (batchEqVars.count(deltaString) == 1):
		batchEqVars.remove(deltaString)
	
	if (batchEqVars.count(deltaDotProdString) == 1):
		batchEqVars.remove(deltaDotProdString)

	return batchEqVars

def getBatchEqDotProdVars(batchEqVars):
	batchEqDotProdVars = []
	
	for varIndex in range(0, len(batchEqVars)):
		dotProdSymbolIndex = batchEqVars[varIndex].find(dotProdSymbol)
		if (dotProdSymbolIndex != -1):
			batchEqDotProdVars.append(batchEqVars[varIndex][0:dotProdSymbolIndex])
	return batchEqDotProdVars

'''
def removeDupsFromList(list):
	for listIndex in range(0, len(list)):
		while ()
'''

def getIndentedBlockIndex(listOfIndentedBlocks, lineNo):
	for counter in range(0, len(listOfIndentedBlocks)):
		indentedBlock = listOfIndentedBlocks[counter]
		startLineNo = indentedBlock[indentedBlockStartLineNo]
		endLineNo = indentedBlock[indentedBlockEndLineNo]
		if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
			#print(counter)
			return counter
		
	return -1

def addIndentedBlockDataToDotProdVars(indentedBlock, varsNeededForDotProds, lineNosNeededForDotProds, lastAssignLine):
	startLineNo = indentedBlock[indentedBlockStartLineNo]
	endLineNo = indentedBlock[indentedBlockEndLineNo]
	
	if ( (startLineNo - 1) > lastAssignLine):
		return
	
	for lineIndex in range( (startLineNo - 1) , (endLineNo + 1)):
		if lineIndex not in lineNosNeededForDotProds:
			lineNosNeededForDotProds.append(lineIndex)
			
	namesOfVarsInBlock = indentedBlock[indentedBlockVars]
	for nameOfVarsInBlock in namesOfVarsInBlock:
		if nameOfVarsInBlock not in varsNeededForDotProds:
			varsNeededForDotProds.append(nameOfVarsInBlock)

def getLastLineAssignOfVarGroup(varGroup, assignMap):
	#print(assignMap)
	#print(varGroup)
	
	lastLineNo = 0
	for varName in varGroup:
		for lineNo in assignMap[varName]:
			if (lineNo > lastLineNo):
				lastLineNo = lineNo

	#print(lastLineNo)				
	return lastLineNo

def getLastLineOfControlBlock(lastLine, listOfIndentedBlocks):
	#print(listOfIndentedBlocks)
	for indentedBlock in listOfIndentedBlocks:
		startLineNo = indentedBlock[indentedBlockStartLineNo] - 1
		endLineNo = indentedBlock[indentedBlockEndLineNo]
		if ( (lastLine >= startLineNo) and (lastLine <= endLineNo) ):
			return endLineNo
		
	return lastLine

def getLinesForDotProd_OneVar(dotProdVarName, assignMap, listOfIndentedBlocks, lineNosNeededForDotProds):
	varsNeededForDotProds = []
	varsNeededForDotProds.append(dotProdVarName)

	lastAssignLine = 0
	
	lineNos = list(assignMap[dotProdVarName].keys())
	for lineNo in lineNos:
		if (lineNo > lastAssignLine):
			lastAssignLine = lineNo
		for varName in assignMap[dotProdVarName][lineNo]:
			if varName not in varsNeededForDotProds:
				varsNeededForDotProds.append(varName)

	tempVarsToAdd = []
					
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			lineNos = list(assignMap[varNeededForDotProds].keys())
			for lineNo in lineNos:
				indentedBlockIndex = getIndentedBlockIndex(listOfIndentedBlocks, lineNo)
				if (indentedBlockIndex != -1):
					addIndentedBlockDataToDotProdVars(listOfIndentedBlocks[indentedBlockIndex], varsNeededForDotProds, lineNosNeededForDotProds, lastAssignLine)
	
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			nextLines = list(assignMap[varNeededForDotProds].keys())
			for nextLine in nextLines:
				if ( (nextLine not in lineNosNeededForDotProds) and (nextLine <= lastAssignLine) ):
					lineNosNeededForDotProds.append(nextLine)

	return lineNosNeededForDotProds

def getLinesForDotProds(batchEqDotProdVars, assignMap, pythonCodeLines, listOfIndentedBlocks):
	varsNeededForDotProds = []
	lineNosNeededForDotProds = []
	linesForDotProds = []

	#print(assignMap)
	
	for batchEqVarName in batchEqDotProdVars:
		lineNosNeededForDotProds = getLinesForDotProd_OneVar(batchEqVarName, assignMap, listOfIndentedBlocks, lineNosNeededForDotProds)
		
	'''	
		varsNeededForDotProds.append(batchEqVarName)
		lineNos = list(assignMap[batchEqVarName].keys())
		#print(lineNos)
		for lineNo in lineNos:
			#print(lineNo)
			for varName in assignMap[batchEqVarName][lineNo]:
				if varName not in varsNeededForDotProds:
					varsNeededForDotProds.append(varName)

	tempVarsToAdd = []
					
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			lineNos = list(assignMap[varNeededForDotProds].keys())
			for lineNo in lineNos:
				indentedBlockIndex = getIndentedBlockIndex(listOfIndentedBlocks, lineNo)
				if (indentedBlockIndex != -1):
					addIndentedBlockDataToDotProdVars(listOfIndentedBlocks[indentedBlockIndex], varsNeededForDotProds, lineNosNeededForDotProds)
					
	
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			nextLines = list(assignMap[varNeededForDotProds].keys())
			for nextLine in nextLines:
				if nextLine not in lineNosNeededForDotProds:
					lineNosNeededForDotProds.append(nextLine)

	'''
		
	lineNosNeededForDotProds.sort()
	
	lastLineAssignOfVarGroup = getLastLineAssignOfVarGroup(batchEqDotProdVars, assignMap)
	
	lastLineOfControlBlock = getLastLineOfControlBlock(lastLineAssignOfVarGroup, listOfIndentedBlocks)

	totalNumOfLines = len(lineNosNeededForDotProds)
	
	for lineNo in range(0, totalNumOfLines):
		if (lineNosNeededForDotProds[lineNo] > lastLineOfControlBlock):
			break
		
	if (lineNo < (totalNumOfLines - 1) ):
		for lineIndex in range(lineNo, totalNumOfLines):
			lineNosNeededForDotProds.remove(lineNosNeededForDotProds[lineIndex])

	'''
	for lineNoNeededForDotProds in lineNosNeededForDotProds:
		if (lineNoNeededForDotProds > lastLineOfControlBlock):
			lineNosNeededForDotProds.remove()
	'''



	#print(lastLineOfControlBlock)
	
	#print(lastLineAssignOfVarGroup)
	
	#print(lineNosNeededForDotProds)
	#print(varsNeededForDotProds)

	#dfdfd
				
	#lineNosNeededForDotProds.sort()
	#print(lineNosNeededForDotProds)
		
		#print(nextLines)
		#print(assignMap)
		#pass
	
	#print(batchEqDotProdVars)
	#print(assignMap)
	
	return lineNosNeededForDotProds

def determineNumSpacesBeforeText(line):
	if (line[0] != ' '):
		return 0
	
	numSpaces = 0
	
	for index in range(0, len(line)):
		if (line[index] == ' '):
			numSpaces += 1
		else:
			return numSpaces
			
	return numSpaces

def getVarsOfLine(linesOfCode, lineNo):
	line = linesOfCode[lineNo - 1]
	line = line.lstrip().rstrip().rstrip('\n')
	if ( (line.startswith(commentChar)) or (line == "") ):
		return []
	line = ensureSpacesBtwnTokens(line)

	vars = []
	
	for token in line.split():
		if ( (token not in reservedSymbols) and (token not in reservedWords) and (token.isdigit() == False) ):
			vars.append(token)

	#print(vars)			
	return vars

def buildMapOfControlFlow(pythonCodeLines, funcDefLineNo, endLineNo):
	withinIndentedBlock = False
	indentedBlockPairs = []
	
	for lineIndex in range(0, len(pythonCodeLines)):
		realLineNo = lineIndex + 1
		lineWithNoSpaces = pythonCodeLines[lineIndex].lstrip().rstrip()
		
		if (realLineNo < funcDefLineNo):
			continue
		elif (realLineNo > endLineNo):
			break
		elif (realLineNo == funcDefLineNo):
			baseNumSpacesBeforeText = determineNumSpacesBeforeText(pythonCodeLines[lineIndex]) + numSpacesPerTab
		elif ( (lineWithNoSpaces.startswith(commentChar)) or (lineWithNoSpaces == "") ):
			continue
		else:
			numSpacesBeforeText = determineNumSpacesBeforeText(pythonCodeLines[lineIndex])
			if (withinIndentedBlock == True):
				if (numSpacesBeforeText == baseNumSpacesBeforeText):
					withinIndentedBlock = False
					indentedBlockPairs.append(realLineNo - 1)
			else:
				if (numSpacesBeforeText == (baseNumSpacesBeforeText + numSpacesPerTab) ):
					withinIndentedBlock = True
					indentedBlockPairs.append(realLineNo)
					
	if ( (len(indentedBlockPairs) % 2) == 1):
		indentedBlockPairs.append(endLineNo)
		
	listOfIndentedBlocks = []
	indentedBlockDict = {}
	numIndentedBlocks = int(len(indentedBlockPairs) / 2)
	
	for indentedBlockIndex in range(0, numIndentedBlocks):
		indentedBlockDict[indentedBlockStartLineNo] = indentedBlockPairs[indentedBlockIndex * 2]
		indentedStart = indentedBlockDict[indentedBlockStartLineNo]
		indentedBlockDict[indentedBlockEndLineNo] = indentedBlockPairs[(indentedBlockIndex * 2) + 1]
		indentedEnd = indentedBlockDict[indentedBlockEndLineNo]
		varsInBlock = []
		for indentedLineNo in range( (indentedStart - 1), (indentedEnd + 1) ):
			varsOfLine = getVarsOfLine(pythonCodeLines, indentedLineNo)
			if (varsOfLine != []):
				for varOfLine in varsOfLine:
					if varOfLine not in varsInBlock:
						varsInBlock.append(varOfLine)
		indentedBlockDict[indentedBlockVars] = varsInBlock
		listOfIndentedBlocks.append(copy.deepcopy(indentedBlockDict))
		
	#print(listOfIndentedBlocks)
	return listOfIndentedBlocks

def getComputeLineVars(exp):
	varList = []
	
	exp = ensureSpacesBtwnTokens(exp)
	for token in exp.split():
		if ( (token not in reservedWords) and (token not in reservedSymbols) and (token not in varList) ):
			varList.append(token)
			
	return varList
		
def getComputeLineInfo(batchVerifierOutput):
	computeLineInfo = {}
	
	for line in batchVerifierOutput:
		if (line.startswith(computeLineString)):
			line = line.lstrip(computeLineString)
			line = line.replace(multipleSubscriptIndicatorChar, '')
			dotProdLine = line.split(dotProdAssignSymbol, 1)
			key = dotProdLine[0]
			initValue = dotProdLine[1].rstrip('\n')
			computeLineInfo[key] = {}
			tempString = initValue.split(dotProdAssignSymbol)
			tempStringIndexVar = tempString[0].split('{')
			computeLineInfo[key][computeLineIndex] = tempStringIndexVar[1]
			tempString = tempString[1].split('}')
			#print(tempString)
			tempStringStartEndVals = tempString[0].split(',')
			computeLineInfo[key][computeLineStartValue] = tempStringStartEndVals[0]
			computeLineInfo[key][computeLineEndValue] = tempStringStartEndVals[1]
			
			computeLineInfo[key][computeLineRange] = str(computeLineInfo[key][computeLineIndex]) + str(computeLineInfo[key][computeLineStartValue]) + str(computeLineInfo[key][computeLineEndValue])
			
			tempString = tempString[1].split(' on ')
			#print(tempString[1].rstrip(')'))
			tempStringExp = tempString[1]
			lenTempStringExp = len(tempStringExp)
			computeLineInfo[key][computeLineExp] = tempStringExp[0:(lenTempStringExp - 1)]
			
			computeLineInfo[key][computeLineVars] = getComputeLineVars( computeLineInfo[key][computeLineExp] )

			varNames = computeLineInfo[key][computeLineVars]
			varNamesNoSubscripts = []
			
			for varName in varNames:
				varNameSplit = varName.split(dotProdSymbol)
				varNamesNoSubscripts.append(varNameSplit[0])

			computeLineInfo[key][computeLineVarsNoSubscripts] = varNamesNoSubscripts						
			#print(exp)
			#print(dotProdLine)

	#print(computeLineInfo)
	return computeLineInfo

def doesVarNeedList(varName, verifyFuncArgs):
	if ( (varName == 'i') or (varName == 'j') ):
		return False
	
	if (varName in verifyFuncArgs):
		return False
	
	if ( (varName.startswith(dotProdPrefix)) and (len(varName) == 4)):
		return False
	
	return True

def addListDeclarations(batchOutputString, computeLineInfo, verifyFuncArgs, declaredLists):
	listVars = []
	dotProdListNames = []

	#print(computeLineInfo)
	
	batchOutputString += "\n"
	
	for key in computeLineInfo:
		if key not in dotProdListNames:
			dotProdListNames.append(key)
		for varIndex in range(0, len(computeLineInfo[key][computeLineVars])):
			varName = computeLineInfo[key][computeLineVars][varIndex]
			varNameNoSubscript = computeLineInfo[key][computeLineVarsNoSubscripts][varIndex]
			if (varNameNoSubscript.startswith(deltaString) == True):
				continue
			
			needsList = doesVarNeedList(varNameNoSubscript, verifyFuncArgs)
			if (needsList == True):
				if varName not in listVars:
					listVars.append(varName)
					
	for listVar in listVars:
		listVarSplit = listVar.split(dotProdSymbol)
		listVarName = listVarSplit[0]
		listVarSuffixes = listVarSplit[1]
		suffixes = ""
		for listVarSuffix in listVarSuffixes:
			suffixes += listVarSuffix
			batchOutputString += "\t" + listVarName + suffixes + " = {}\n"
			declaredListEntry = listVarName + "_" + suffixes
			if declaredListEntry not in declaredLists:
				declaredLists.append(declaredListEntry)

	for dotProdListName in dotProdListNames:
		batchOutputString += "\t" + dotProdListName + " = {}\n"
		if dotProdListName not in declaredLists:
			declaredLists.append(dotProdListName) #IS THIS A PROBLEM?

	#batchOutputString += "\n"

	declaredLists.append(deltasString)

	#print(dotProdListNames)

	return batchOutputString

def getOuterDotProds(batchVerifierOutput):
	outerDotProds = []

	for line in batchVerifierOutput:
		if (line.startswith(finalEqLineString)):
			break
		
	line = ensureSpacesBtwnTokens(line)
	
	line = line.split()
	
	for token in line:
		if ( (token.startswith(dotProdPrefix)) and (len(token) == 4) ):
			if (token not in outerDotProds):
				outerDotProds.append(token)
	
	return outerDotProds



#def addDotProdLoops(batchOutputString, computeLineInfo, outerDotProds, assignMap, pythonCodeLines, listOfIndentedBlocks):

def cleanVarsForDotProds(varsForDotProds):
	if (varsForDotProds.count(deltaString) > 0):
		varsForDotProds.remove(deltaString)
	
	varsToRemove = []
	
	for var in varsForDotProds:
		if ( (var.startswith(dotProdPrefix)) and (len(var) == 4) ):
			varsToRemove.append(var)
			
	for var in varsToRemove:
		varsForDotProds.remove(var)

def getListNameFromDeclaredLists(listName):
	if (listName.count("_") == 0):
		return listName
	
	listName = listName.split("_")
	return listName[0]

def getSuffixesFromDeclaredLists(listName):
	if (listName.count("_") == 0):
		return None
	
	listName = listName.split("_")
	return listName[1]

def writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, linesForDotProds, baseNumTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar, dotProdListName):
	#print(declaredLists)
	
	for lineNo in linesForDotProds:
		line = pythonCodeLines[lineNo - 1]
		if (line.lstrip().rstrip().startswith(commentChar) == True):
			continue
		if (line.lstrip().rstrip() == ""):
			continue		
		numSpacesBeforeText = determineNumSpacesBeforeText(line)
		numTabsBeforeText = determineNumTabs(numSpacesBeforeText)
		extraTabsNeeded = numTabsBeforeText - numTabsBeforeVerify - 1		
		line = ensureSpacesBtwnTokens(line)
		
		
		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):				
				indexOfCharAfterArg = line.index(argWithSpaces) + len(argWithSpaces)
				if (indexOfCharAfterArg < len(line)):
					charAfterArg = line[indexOfCharAfterArg]
				else:
					charAfterArg = ''
				replacementString = " verifyArgsDict[argSigIndexMap[\'" + arg + "\']][\'" + arg + "\'][bodyKey]"
				if (charAfterArg == dictBeginChar):
					line = line.replace(argWithSpaces + '[', replacementString + '[', 1)
				else:
					line = line.replace(argWithSpaces, replacementString + ' ', 1)		
					
		for listName in declaredLists:
			listName = getListNameFromDeclaredLists(listName)
			listWithSpaces = ' ' + listName + ' '
			numListMatches = line.count(listWithSpaces)
			replacementString = listName + indexVar + "[" + indexVar + "] "
			for countIndex in range(0, numListMatches):
				line = line.replace(listWithSpaces, replacementString, 1)
					
		line = line.lstrip().rstrip()
		line = removeLeftParanSpaces(line)		
		line = removeSelfDump(line)
		numTabs = baseNumTabs + extraTabsNeeded		
		for tabNumber in range(0, numTabs):
			batchOutputString += "\t"
		batchOutputString += line + "\n"

	for tabNumber in range(0, numTabs):
		batchOutputString += "\t"
		
	batchOutputString += dotProdListName + "[" + indexVar + "] = \n"

	batchOutputString += "\n"

	print(computeLineInfo[dotProdListName][computeLineExp])
		
	return batchOutputString

def addTabsToFile(file, numTabsToAdd):
	for tab in range(0, numTabsToAdd):
		file += "\t"
	
	return file

def setUpVerifyFuncArgs(batchOutputString, numTabs):
	batchOutputString = addTabsToFile(batchOutputString, numTabs)
	batchOutputString += "for arg in verifyFuncArgs:\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 1)
	batchOutputString += "if (sigNumKey in verifyArgsDict[sigIndex][arg]):\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 2)
	batchOutputString += "argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 1)
	batchOutputString += "else:\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 2)
	batchOutputString += "argSigIndexMap[arg] = sigIndex\n\n"
		
	return batchOutputString

def addDotProdLoopRecursive(batchOutputString, computeLineInfo, dotProdList, assignMap, pythonCodeLines, listOfIndentedBlock, numTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, parentIndexVar):
	for key in dotProdList:
		dotProdRange = key
	
	indexVar = dotProdRange[0]
	startVal = int(dotProdRange[1])
	startVal = startVal - 1
	startVal = str(startVal)
	endVal = dotProdRange[2]

	#print(numTabs + 1)

	for tab in range(0, numTabs):
		batchOutputString += "\t"

	#for myNewVar in range(0, 10):
	'''
	for n in range(2, 10):
		pass
		batchOutputString += "\t"
	'''

	endValInCode = endVal

	if (endVal == numSignaturesEndVal):
		endValInCode = numSignaturesEndValInCode
	elif (endVal == numSignersEndVal):
		endValInCode = numSignersEndValInCode
		
	batchOutputString += "for " + indexVar + " in range(" + startVal + ", " + endValInCode + "):\n"
	if (endValInCode == numSignaturesEndValInCode):
		batchOutputString = setUpVerifyFuncArgs(batchOutputString, numTabs + 1)


	for child in dotProdList[dotProdRange]:
		if type(child).__name__ == pythonDictRep:
			batchOutputString = addDotProdLoopRecursive(batchOutputString, computeLineInfo, child, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabs + 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar)

	#batchOutputString += "\n " + str(numTabs)
	
	for child in dotProdList[dotProdRange]:
		if ( (type(child).__name__ != pythonDictRep) and (child.startswith(dotProdPrefix)) and (len(child) == 4) ):
			#print(child)
			varsForDotProds = computeLineInfo[child][computeLineVarsNoSubscripts]
			#print(varsForDotProds)
			cleanVarsForDotProds(varsForDotProds)
			#print(varsForDotProds)
			linesForDotProds = getLinesForDotProds(varsForDotProds, assignMap, pythonCodeLines, listOfIndentedBlocks)
			batchOutputString = writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, linesForDotProds, numTabs + 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar, child)

			
			#print(linesForDotProds)
			if (parentIndexVar != None):
				parentAndChildIndices = indexVar + parentIndexVar
				for declaredList in declaredLists:
					if (parentAndChildIndices == getSuffixesFromDeclaredLists(declaredList) ):
						for numTab in range(0, numTabs):
							batchOutputString += "\t"
						listNameFromDL = getListNameFromDeclaredLists(declaredList)
						batchOutputString += listNameFromDL + parentAndChildIndices + "[" + parentIndexVar + "] = copy.deepcopy(" + listNameFromDL + indexVar + ")\n"


	return batchOutputString

def addDotProdLoops(batchOutputString, computeLineInfo, dotProdLoopOrder, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabsBeforeVerify, verifyFuncArgs, declaredLists):
	#batchOutputString += "\ttest\n"
	
	#print(dotProdLoopOrder)
	
	for outerDotProd in dotProdLoopOrder:
		#print(outerDotProd)
		batchOutputString = addDotProdLoopRecursive(batchOutputString, computeLineInfo, outerDotProd, assignMap, pythonCodeLines, listOfIndentedBlocks, 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, None)
		batchOutputString += "\n"
	
	return batchOutputString

def getDotProdListIndex(dotProdList, range):
	childCounter = 0
	
	for child in dotProdList:
		if type(child).__name__ == pythonDictRep:
			for key in child:
				if (key == range):
					return childCounter
					
		childCounter += 1
		
	return -1
					

def dotProdLoopRecursive(computeLineInfo, outerDotProd, dotProdList):
	'''
	if (outerDotProd not in dotProdDict):
		dotProdDict[outerDotProd] = {}
	'''
	
	range = computeLineInfo[outerDotProd][computeLineRange]
	
	#if (range not in dotProdList):

	#rangeKeyExists = False

	'''	
	for child in dotProdList:
		if child == range:
			rangeKeyExists = True
			break
	'''

	dotProdListIndex = getDotProdListIndex(dotProdList, range)
		
	if (dotProdListIndex == -1):
		newDictEntry = {}
		dotProdList.append(newDictEntry)
		newDictEntry[range] = []
		newDictEntry[range].append(outerDotProd)
	else:
		dotProdList[dotProdListIndex][range].append(outerDotProd)
	
	for varName in computeLineInfo[outerDotProd][computeLineVarsNoSubscripts]:
		if ( (varName.startswith(dotProdPrefix)) and (len(varName) ==  4) ):
			#dotProdDict[outerDotProd][varName] = {}
			#dotProdLoopRecursive(computeLineInfo, varName, dotProdDict[outerDotProd])
			
			dotProdListIndex = getDotProdListIndex(dotProdList, range)
			
			dotProdLoopRecursive(computeLineInfo, varName, dotProdList[dotProdListIndex][range])

def getDotProdLoopOrder(computeLineInfo, outerDotProds, dotProdLoopOrder):
	#dotProdLoopOrder = {}

	for outerDotProd in outerDotProds:
		dotProdLoopRecursive(computeLineInfo, outerDotProd, dotProdLoopOrder)
			
	return dotProdLoopOrder

def printList(dict):
	for key in dict:
		if (type(key).__name__ == 'dict'):
			print(key)
			for child in key:
				print(key)
				print(key[child])
			print("\n")
		else:
			print(key)
		#print(key)
		#print(dict[key])
		print("\n")

def addNumSigsSignersDefs(batchOutputString, pythonCodeLines):
	foundNumSignatures = False
	foundNumSigners = False
	
	for line in pythonCodeLines:
		if (line.lstrip().startswith(numSignaturesEndValInCode + " = ") == True):
			batchOutputString += "\t" + line.lstrip().rstrip() + "\n"
			foundNumSignatures = True
		elif (line.lstrip().startswith(numSignersEndValInCode + " = ") == True):
			batchOutputString += "\t" + line.lstrip().rstrip() + "\n"
			foundNumSigners = True
			
		if ( (foundNumSignatures == True) and (foundNumSigners == True) ):
			break

	return batchOutputString

if __name__ == '__main__':
	if ( (len(sys.argv) != 6) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python Code_Generator.py \n [individual verification output filename] \n [batch verification output filename] \n [filename of Python code for signature scheme] \n [filename of pickled Python dictionary with verify function arguments] \n [filename of .bv file that will be input for the batch verifier] \n")

	individualVerArg = sys.argv[1]
	batchVerArg = sys.argv[2]
	pythonCodeArg = sys.argv[3]
	verifyParamFilesArg = sys.argv[4]
	batchVerifierInputFile = sys.argv[5]

	#os.system("cp " + individualTemplate + " " + individualVerArg)
	#os.system("cp " + batchTemplate + " " + batchVerArg)

	individualVerFile = open(individualVerArg, 'w')
	batchVerFile = open(batchVerArg, 'w')

	pythonCodeLines = open(pythonCodeArg, 'r').readlines()

	pythonCodeNode = getRootASTNode(pythonCodeLines)
	
	
	importFromLines = getImportFromLines(pythonCodeNode, pythonCodeLines)
	for importFromLine in importFromLines:			
		#individualOutputString += "\t" + str(importFromLine) + "\n"
		individualVerFile.write(importFromLine)
		individualVerFile.write("\n")
		batchVerFile.write(importFromLine)
		batchVerFile.write("\n")

	individualTemplateLines = open(individualTemplate, 'r').readlines()
	batchTemplateLines = open(batchTemplate, 'r').readlines()

	for line in individualTemplateLines:
		individualVerFile.write(line)
		
	for line in batchTemplateLines:
		batchVerFile.write(line)
	
	verifyFuncNode = getVerifyFuncNode(pythonCodeNode)
	verifyFuncArgs = getVerifyFuncArgs(verifyFuncNode)
	#print(verifyFuncArgs)

	verifyEqNode = getVerifyEqNode(verifyFuncNode)
	if (verifyEqNode == 0):
		sys.exit("Could not locate the verify equation within the \"verify\" function")


	#buildMapOfControlFlow(pythonCodeLines, verifyFuncNode.lineno, (verifyEqNode.lineno - 1))


	lastLineVisitor = GetLastLineOfFunction()
	lastLineVisitor.visit(verifyFuncNode)
	lastLineOfVerifyFunc = lastLineVisitor.getLastLine()
	#print(lastLineOfVerifyFunc)

	individualOutputString = ""
	batchOutputString = ""

	individualOutputString += "\n"
	batchOutputString += "\n"

	indentationList = []

	verifyFuncLine = getLinesFromSourceCode(pythonCodeLines, verifyFuncNode.lineno, verifyFuncNode.lineno, indentationList)
	#print(verifyFuncLine)
	#numSpacesOnVerifyFuncLine = getNumIndentedSpaces(indentationList[0])
	#print(numSpacesOnVerifyFuncLine)
	numTabsOnVerifyFuncLine = determineNumTabs(indentationList[0])
	#print(numTabsOnVerifyFuncLine)

	#individualOutputString += "\tfrom charm.engine.util import *\n"


	prereqVisitor = PrereqAssignVisitor()
	prereqVisitor.visit(pythonCodeNode)
	prereqAssignLineNos = prereqVisitor.getPrereqAssignLineNos()

	indentationList = []

	if (len(prereqAssignLineNos) > 0):
		for prereqLineNo in prereqAssignLineNos:
			prereqLine = getLinesFromSourceCode(pythonCodeLines, prereqLineNo, prereqLineNo, indentationList)
			individualOutputString += "\t" + str(prereqLine[0]) + "\n"
			batchOutputString += "\t" + str(prereqLine[0]) + "\n"

	batchOutputString = addNumSigsSignersDefs(batchOutputString, pythonCodeLines)

	indentationList = []

	verifyLines = getLinesFromSourceCode(pythonCodeLines, (verifyFuncNode.lineno + 1), verifyEqNode.lineno, indentationList)

	lineNumber = -1

	individualOutputString += "\n\tfor sigIndex in range(1, (numSigs+1)):\n"
	individualOutputString += "\t\tfor arg in verifyFuncArgs:\n"
	individualOutputString += "\t\t\tif (sigNumKey in verifyArgsDict[sigIndex][arg]):\n"
	individualOutputString += "\t\t\t\targSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])\n"
	individualOutputString += "\t\t\telse:\n"
	individualOutputString += "\t\t\t\targSigIndexMap[arg] = sigIndex\n"

	for line in verifyLines:
		lineNumber += 1
		if (isLineOnlyWhiteSpace(line) == True):
			continue
		line = ensureSpacesBtwnTokens(line)
		#print(line)
		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):
				#print(argWithSpaces)
				indexOfCharAfterArg = line.index(argWithSpaces) + len(argWithSpaces)
				if (indexOfCharAfterArg < len(line)):
					charAfterArg = line[indexOfCharAfterArg]
				else:
					charAfterArg = ''
				replacementString = " verifyArgsDict[argSigIndexMap[\'" + arg + "\']][\'" + arg + "\'][bodyKey]"
				if (charAfterArg == dictBeginChar):
					line = line.replace(argWithSpaces + '[', replacementString + '[', 1)
				else:
					line = line.replace(argWithSpaces, replacementString + ' ', 1)
				#print(line)
				#print("\n\n")
		#print(line)
		line = line.lstrip().rstrip()
		#print(line)
		line = removeLeftParanSpaces(line)
		#print(line)
		#print("\n\n")
		line = removeSelfDump(line)
		numTabs = determineNumTabs(indentationList[lineNumber]) - numTabsOnVerifyFuncLine
		numTabs += 1
		for tabNumber in range(0, numTabs):
			individualOutputString += "\t"
		individualOutputString += line + "\n"

	individualOutputString += "\t\t\tpass\n"
	individualOutputString += "\t\telse:\n"
	individualOutputString += "\t\t\tprint(\"Verification of signature \" + str(sigIndex) + \" failed.\\n\")\n"

	#os.system("python " + batchVerifierPythonFile + " " + batchVerifierInputFile + " > " + batchVerifierOutputFile)
	batchVerifierOutput = open(batchVerifierOutputFile, 'r').readlines()
	for line in batchVerifierOutput:
		if (line.startswith(finalBatchEqTag) == True):
			finalBatchEq = line
			break

	finalBatchEq = cleanFinalBatchEq(finalBatchEq)
	
	batchEqVars = getBatchEqVars(finalBatchEq)
	batchEqDotProdVars = getBatchEqDotProdVars(batchEqVars)
	
	#print(batchEqVars)
	#print(batchEqDotProdVars)
	
	assignMapVar = BuildAssignMap()
	assignMapVar.visit(verifyFuncNode)
	assignMap = assignMapVar.getAssignMap()

	listOfIndentedBlocks = buildMapOfControlFlow(pythonCodeLines, verifyFuncNode.lineno, (verifyEqNode.lineno - 1))
	#print(listOfIndentedBlocks)
	
	#linesForDotProds = getLinesForDotProds(batchEqDotProdVars, assignMap, pythonCodeLines, listOfIndentedBlocks)

	#print(linesForDotProds)



	#linesForDotProds = getLinesForDotProds(['sig'], assignMap, pythonCodeLines, listOfIndentedBlocks)

	#print(linesForDotProds)



	#print(linesForDotProds)
	
	#dotProdCodeBlock = formDotProdCodeBlock(pythonCodeLines, linesForDotProds)
	
	'''
	for key in assignMap:
		print(key)
		print(assignMap[key])
		print("\n")
	'''
	
	#print(batchEqVars)
    
	#print(finalBatchEq.split())

	computeLineInfo = getComputeLineInfo(batchVerifierOutput)

	#print(computeLineInfo)
	
	outerDotProds = getOuterDotProds(batchVerifierOutput)

	dotProdLoopOrder = []
	
	dotProdLoopOrder = getDotProdLoopOrder(computeLineInfo, outerDotProds, dotProdLoopOrder)
	
	#printList(dotProdLoopOrder)

	#print(outerDotProds)

	declaredLists = []

	batchOutputString = addListDeclarations(batchOutputString, computeLineInfo, verifyFuncArgs, declaredLists)
	
	#print(declaredLists)

	batchOutputString = addDeltasAndArgSigIndexMap(batchOutputString)

	#numTabsBeforeVerify = determineNumTabsBeforeVerify()
	
	batchOutputString = addDotProdLoops(batchOutputString, computeLineInfo, dotProdLoopOrder, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabsOnVerifyFuncLine, verifyFuncArgs, declaredLists)

	#print(computeLineInfo)
	
	#batchOutputString = addDeltas(batchOutputString)
	
	#batchOutputString = addIfElse(batchOutputString, finalBatchEq)

	individualVerFile.write(individualOutputString)
	batchVerFile.write(batchOutputString)

	individualVerFile.close()
	batchVerFile.close()

	#os.system("python " + individualVerArg)
	#os.system("python " + batchVerArg)
