import copy, os, sys
from ASTParser import *
from Parser_CodeGen_Toolbox import *
from LoopInfo import LoopInfo
from StringName import StringName
from PrecomputeVariable import PrecomputeVariable
from IntegerValue import IntegerValue
from Loop_Block_Toolbox import *
from OperationValue import OperationValue
from LoopBlock import LoopBlock
from FinalEqWithLoops import FinalEqWithLoops

batchEqLoopVars = {}
batchEqNotLoopVars = {}
batchEqVars = {}
batchVerFile = None
batchVerifierOutput = None
cachedCalcsToPassToDC = []
callListOfVerifyFuncs = None
checkBlocks = None
codeGenRanges = None

codeLinesFromBatcher = []

finalBatchEq = []
finalBatchEqWithLoops = []
functionArgMappings = None
functionArgNames = None
functionNames = None
globalVars = []
indentationListVerifyLines = None
individualVerFile = None
lineInfo = None
lineNoOfFirstFunction = None
lineNosPerVar = None
loopBlocksForCachedCalculations = []
loopBlocksForNonCachedCalculations = []
loopInfo = []
loopNamesOfFinalBatchEq = []
loopsOuterNumSignatures = []
loopsOuterNotNumSignatures = []
linePairsOfVerifyFuncs = None
listVars = {}
loopVarGroupTypes = {}
nonLoopCachedVars = []
numSpacesPerTab = None
numTabsOnVerifyLine = None
precomputeVars = []
pythonCodeLines = None
pythonCodeNode = None
sortVars = []

typeVars = {}

var_varDependencies = None
varAssignments = None
verifyEqNode = None
verifyFuncArgs = None
verifyFuncNode = None
verifyLines = None
verifyNumSignersLine = None
verifySigsFile = None
verifySigsFileName = None
verifySigsInitCall = None
verifyPrereqs = None

def cleanFinalBatchEq():
	global finalBatchEq

	numEqs = len(codeGenRanges)

	for index in range(0, numEqs):
		tempEq = finalBatchEq[index]
		tempEq = tempEq.replace(con.finalBatchEqString, '', 1)
		tempEq = tempEq.lstrip()
		tempEq = ensureSpacesBtwnTokens_CodeGen(tempEq)
		finalBatchEq[index] = tempEq

def getBatchEqVars():
	global batchEqVars

	numPasses = len(finalBatchEq)

	batchEqVars = {}

	for passNo in range(0, numPasses):
		getBatchEqVars_Ind(finalBatchEq[passNo], passNo)

def getBatchEqVars_Ind(finalBatchEq_Ind, codeGenSegNo):
	global batchEqVars

	batchEqVars[codeGenSegNo] = []

	batchEqVarsTemp = finalBatchEq_Ind.split()

	for removeString in con.batchEqRemoveStrings:
		while (batchEqVarsTemp.count(removeString) > 0):
			batchEqVarsTemp.remove(removeString)

	for dupVar in batchEqVarsTemp:
		while (batchEqVarsTemp.count(dupVar) > 1):
			batchEqVarsTemp.remove(dupVar)

	deltaVarsToRemove = []

	for deltaVar in batchEqVarsTemp:
		if ( (deltaVar == con.delta) or (deltaVar.startswith(con.delta + con.loopIndicator) == True) ):
			deltaVarsToRemove.append(deltaVar)

	for varToRemove in deltaVarsToRemove:
		batchEqVarsTemp.remove(varToRemove)

	#batchEqVars = []

	for batchEqVarName in batchEqVarsTemp:
		batchEqVarStringName = StringName()
		batchEqVarStringName.setName(batchEqVarName)
		batchEqVars[codeGenSegNo].append(copy.deepcopy(batchEqVarStringName))
		del batchEqVarStringName

def distillBatchEqVars():
	global batchEqLoopVars, batchEqNotLoopVars

	batchEqLoopVars = {}
	batchEqNotLoopVars = {}

	numPasses = len(batchEqVars)

	for index in range(0, numPasses):
		distillBatchEqVars_Ind(batchEqVars[index], index)

def distillBatchEqVars_Ind(batchEqVars_Ind, codeGenSegNo):
	global batchEqLoopVars, batchEqNotLoopVars

	batchEqLoopVars[codeGenSegNo] = []
	batchEqNotLoopVars[codeGenSegNo] = []

	for varName in batchEqVars_Ind:
		isThisALoopVar = varName.getStringVarName().find(con.loopIndicator)
		if (isThisALoopVar == -1):
			batchEqNotLoopVars[codeGenSegNo].append(copy.deepcopy(varName))
		else:
			batchEqLoopVars[codeGenSegNo].append(copy.deepcopy(varName))

def processComputeLine(line, passNo):
	global loopInfo

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) or (line.startswith(con.computeString) == False) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  problem with line passed in (" + line + ").")

	line = line.lstrip().rstrip()
	line = line.replace(con.computeString, '', 1)
	splitOnAssignment = line.split(con.batchVerifierOutputAssignment, 1)
	loopName = splitOnAssignment[0]
	fullExpression = splitOnAssignment[1].rstrip(con.newLineChar)
	if ( (fullExpression.count(con.dotDirector) == 1) and (fullExpression.count(con.sumDirector) == 0) ):
		splitExpression = fullExpression.split(con.dotDirector, 1)
	elif ( (fullExpression.count(con.dotDirector) == 0) and (fullExpression.count(con.sumDirector) == 1) ):
		splitExpression = fullExpression.split(con.sumDirector, 1)
	else:
		sys.exit("AutoBatch_CodeGen->processComputeLine:  compute line did not have only one " + con.dotDirector + " OR only one " + con.sumDirector + ".")

	loopDeclaration = splitExpression[0]
	initialExpression = splitExpression[1]

	if ( (loopDeclaration.count(',') != 1) or (loopDeclaration.count('}') != 1) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  loop declaration is improperly formatted.")

	commaLocation = loopDeclaration.find(',')
	rightCurlyBraceLocation = loopDeclaration.find('}')

	loopOverValue = loopDeclaration[(commaLocation + 1):rightCurlyBraceLocation].lstrip().rstrip()

	if (loopDeclaration.count(con.batchVerifierOutputAssignment) != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  loop declaration is improperly formatted (not only one " + con.batchVerifierOutputAssignment + " symbol).")

	splitLoopDecl = loopDeclaration.split(con.batchVerifierOutputAssignment, 1)
	indexVarExp = splitLoopDecl[0]
	startValExp = splitLoopDecl[1]

	if (indexVarExp.count('{') != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  index variable expression is improperly formatted (not only one \'{\' symbol.")

	leftCurlyBraceLocation = indexVarExp.find('{')
	indexVar = indexVarExp[(leftCurlyBraceLocation + 1):len(indexVarExp)]
	indexVar = indexVar.lstrip().rstrip()

	indexVarStringName = StringName()
	indexVarStringName.setName(indexVar)

	if (startValExp.count(',') != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  start value expression is improperly formatted (not only one \',\' symbol.")

	commaLocation = startValExp.find(',')

	startVal = startValExp[0:commaLocation]
	startVal = startVal.lstrip().rstrip()

	initialExpression = initialExpression.lstrip().rstrip()
	lenInitExp = len(initialExpression)
	if (initialExpression[lenInitExp-1] == ')'):
		initialExpression = initialExpression[0:(lenInitExp-1)]

	expression = initialExpression.lstrip().rstrip()

	varListWithSubscripts = getVarNamesAsStringNamesFromLine(expression)

	varListAsStrings = getVarNamesAsStringsFromLine(expression)

	hasMultipleEqChecks = False

	for varNameAsStringInLoop in varListAsStrings:
		if (varNameAsStringInLoop.find(con.eqChecksSuffix) != -1):
			hasMultipleEqChecks = True
			break

	loopOrder = getLoopOrder(varListAsStrings)
	varListNoSubscripts = removeSubscriptsReturnStringNames(varListAsStrings)

	operationStringValue = returnOperationAsStringValue(loopName)
	if ( (operationStringValue == None) or (type(operationStringValue).__name__ != con.stringValue) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  could not extract the operation value of one of the loops parsed from the batcher output.")

	myOperationValue = OperationValue()
	myOperationValue.setOperation(operationStringValue)

	loopNameStringName = StringName()
	loopNameStringName.setName(loopName)

	startValIntegerValue = IntegerValue()
	startValIntegerValue.setValue(int(startVal))

	loopOverValueStringName = StringName()
	loopOverValueStringName.setName(loopOverValue)

	expressionAsStringValue = StringValue()
	expressionAsStringValue.setValue(expression)

	nextLoopInfoObj = LoopInfo()
	nextLoopInfoObj.setLoopName(loopNameStringName)
	nextLoopInfoObj.setIndexVariable(indexVarStringName)
	nextLoopInfoObj.setStartValue(startValIntegerValue)
	nextLoopInfoObj.setLoopOverValue(loopOverValueStringName)
	nextLoopInfoObj.setOperation(myOperationValue)
	nextLoopInfoObj.setExpression(expressionAsStringValue)
	nextLoopInfoObj.setVarListWithSubscripts(varListWithSubscripts)
	nextLoopInfoObj.setVarListNoSubscripts(varListNoSubscripts)
	nextLoopInfoObj.setLoopOrder(loopOrder)
	nextLoopInfoObj.setCodeGenSegmentNo(passNo)
	nextLoopInfoObj.setHasMultipleEqChecks(hasMultipleEqChecks)

	loopInfo.append(copy.deepcopy(nextLoopInfoObj))

def processListLine(line):
	global listVars

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) or (line.startswith(con.listString) == False) ):
		sys.exit("AutoBatch_CodeGen->processListLine:  problem with line parameter passed to the function.")

	line = line.replace(con.listString, '', 1)
	line = line.lstrip().rstrip()
	lineSplit = line.split(con.listInString)
	varName = lineSplit[0].lstrip().rstrip()
	#if (varName in listVars):
		#sys.exit("AutoBatch_CodeGen->processListLine:  variable currently being processed (" + varName + ") is already included in the listVars data structure (duplicate).")

	loopTypes = lineSplit[1].lstrip().rstrip()

	#if (loopType not in con.loopTypes):
		#sys.exit("AutoBatch_CodeGen->processListLine:  one of the loop types extracted is not one of the supported loop types.")

	if ( (varName in listVars) and (listVars[varName] != loopTypes) ):
		sys.exit("CodeGen->processlistline:  duplicate varname, but mismatching loop type.")

	listVars[varName] = loopTypes

def processPrecomputeLine(line, passNo):
	global precomputeVars

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (line.startswith(con.precomputeString) == False) ):
		sys.exit("AutoBatch_CodeGen->processPrecomputeLine:  problem with line parameter passed in.")

	lenPrecomputeString = len(con.precomputeString)
	line = line[lenPrecomputeString:len(line)]
	line = line.lstrip().rstrip()
	if (line.startswith(con.deltaPrecomputeVarString) == True):
		return

	lineSplit = line.split(con.batchVerifierOutputAssignment)
	varName = lineSplit[0].lstrip().rstrip()
	expression = lineSplit[1].lstrip().rstrip()

	for precomputeVariable in precomputeVars:
		currentVariableName = precomputeVariable.getVarName().getStringVarName()
		if (varName == currentVariableName):
			sys.exit("AutoBatch_CodeGen->processPrecomputeLine:  found duplicate variable name for a precompute variable (" + varName + ").")

	varNameStringName = StringName()
	varNameStringName.setName(varName)

	nextPrecomputeVarObj = PrecomputeVariable()
	nextPrecomputeVarObj.setVarName(varNameStringName)
	nextPrecomputeVarObj.setExpression(expression)

	nextPrecomputeVarObj.setCodeGenSegmentNo(passNo)

	precomputeVars.append(copy.deepcopy(nextPrecomputeVarObj))

def processSortLine(line):
	global sortVars

	line = line.replace(con.sortString, '', 1)
	line = line.lstrip().rstrip()
	if (line.count(con.subscriptIndicator) != 1):
		sys.exit("processSortLine in codegen py file.")

	withExpandedSubscript = processTokenWithSubscriptIndicator(line)
	finalVersion = writeLinesToOutputString([withExpandedSubscript], None, 0, 0)
	finalVersion = finalVersion.lstrip().rstrip()

	if (finalVersion in sortVars):
		sys.exit("CodeGen->processSortLine:  found duplicate sort vars entry.")

	sortVars.append(finalVersion)

def processLoopLine(line, passNo):
	global loopVarGroupTypes

	if ( (line == None) or (type(line).__name__ != con.strTypePython) ):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  problem with line parameter passed in.")

	lineSplit = line.split(con.batchVerifierOutputAssignment)
	varName = lineSplit[0].lstrip().rstrip()
	groupType = lineSplit[1].lstrip().rstrip()

	isVarNameALoopName = isStringALoopName(varName)
	if (isVarNameALoopName == False):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  loop line passed in does not contain the name of a valid loop name.")

	if (varName in loopVarGroupTypes):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  found duplicate in loop variable names.")

	if (groupType not in con.groupTypes):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  group type ovar loop variable " + varName + " is not one of the supported types.")

	loopVarGroupTypes[varName] = groupType

def addImportLines():
	global batchVerFile, individualVerFile, verifySigsFile

	importLines = getImportLines(pythonCodeNode, copy.deepcopy(pythonCodeLines))
	if (importLines == None):
		return

	if ( (type(importLines).__name__ != con.listTypePython) or (len(importLines) == 0) ):
		sys.exit("AutoBatch_CodeGen->addImportLines:  problem with value returned from getImportLines.")

	for index in range(0, len(importLines)):
		batchVerFile.write(importLines[index].lstrip().rstrip() + "\n")
		individualVerFile.write(importLines[index].lstrip().rstrip() + "\n")
		verifySigsFile.write(importLines[index].lstrip().rstrip() + "\n")

	batchVerFile.write("import sys\n")
	individualVerFile.write("import sys\n")
	verifySigsFile.write("import sys\n\n")

def getGlobalVarsAsStringList():
	if (globalVars == None):
		return None

	if ( (type(globalVars).__name__ != con.listTypePython) or (len(globalVars) == 0) ):
		sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with globalVars global variable.")

	retList = []

	for var in globalVars:
		if ( (var == None) or (type(var).__name__ != con.stringName) ):
			sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with one of the StringName objects in the globalVars global variable.")

		varAsString = var.getStringVarName()
		if ( (varAsString == None) or (type(varAsString).__name__ != con.strTypePython) or (len(varAsString) == 0) ):
			sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with string representation of one of the StringName objects in the globalVars global variable.")

		if (varAsString == con.group):
			continue

		retList.append(varAsString)

	return retList

def getGlobalVarsHeaderString():
	globalVarsAsStringList = getGlobalVarsAsStringList()

	retString = ""

	for var in globalVarsAsStringList:
		retString += var + " = None\n"

	lenRetString = len(retString)

	return retString[0:(lenRetString - 8)]

def getGlobalVarsAssignString():
	globalVarsAsStringList = getGlobalVarsAsStringList()

	retString = ""

	for var in globalVarsAsStringList:
		retString += var + ", "

	lenRetString = len(retString)

	return retString[0:(lenRetString - 2)]

def addCommonHeaderLines():
	global batchVerFile, individualVerFile, verifySigsFile

	batchOutputString = ""
	indOutputString = ""
	verifyOutputString = ""

	batchOutputString += "from toolbox.pairinggroup import *\n"
	batchOutputString += "from " + verifySigsFileName + " import verifySigsRecursive\n\n"
	batchOutputString += con.group + " = None\n"

	indOutputString += "\n" + con.group + " = None\n"

	verifyOutputString += con.group + " = None\n"

	globalVarsString = getGlobalVarsHeaderString()
	if (globalVarsString != None):
		if ( (type(globalVarsString).__name__ == con.strTypePython) and (len(globalVarsString) > 0) ):
			#sys.exit("AutoBatch_CodeGen->addCommonHeaderLines:  problem with value returned from getGlobalVarsHeaderString.")
			batchOutputString += globalVarsString + " = None\n"
			indOutputString += globalVarsString + " = None\n"
			verifyOutputString += globalVarsString + " = None\n"

	batchOutputString += "bodyKey = \'Body\'\n\n"

	verifyOutputString += "bodyKey = \'Body\'\n\n"

	batchOutputString += "def prng_bits(bits=80):\n"
	batchOutputString += "\treturn " + con.group + ".init(ZR, randomBits(bits))\n\n"

	indOutputString += "bodyKey = \'Body\'\n\n"

	verifyOutputString += "\n"

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)
	verifySigsFile.write(verifyOutputString)

def writeNumSignersLine(outputFile):
	lineNosToWriteToFile = getAllLineNosThatImpactVarList([con.numSigners], con.verifyFuncName, lineNosPerVar, var_varDependencies)
	if (lineNosToWriteToFile != None):
		writeLinesToFile(lineNosToWriteToFile, 0, outputFile)
		return

	numSignersNum = getStringNameIntegerValue(varAssignments, con.numSigners, con.mainFuncName)

	if (numSignersNum != None):
		outputFile.write("\t" + con.numSigners + " = " + str(numSignersNum) + "\n")

def writeNumEqChecksLine(outputFile):
	lineNosToWriteToFile = getAllLineNosThatImpactVarList([con.numEqChecks], con.verifyFuncName, lineNosPerVar, var_varDependencies)
	if (lineNosToWriteToFile != None):
		writeLinesToFile(lineNosToWriteToFile, 0, outputFile)
		return

	numEqChecksNum = getStringNameIntegerValue(varAssignments, con.numEqChecks, con.mainFuncName)

	if (numEqChecksNum != None):
		outputFile.write("\t" + con.numEqChecks + " = " + str(numEqChecksNum) + "\n")

def addTemplateLines():
	global batchVerFile, individualVerFile

	batchOutputString = ""
	indOutputString = ""

	#batchOutputString += "def run_Batch_Sorted(verifyArgsDict, " + con.group + "ObjParam, verifyFuncArgs):\n"
	#batchOutputString += "\tglobal " + con.group + "\n"

	#indOutputString += "def run_Ind(verifyArgsDict, " + con.group + "ObjParam, verifyFuncArgs):\n"
	#indOutputString += "\tglobal " + con.group + "\n"

	globalsString = getGlobalVarsAssignString()
	#if (globalsString != None):
		#if ( (type(globalsString).__name__ == con.strTypePython) and (len(globalsString) > 0) ):
			#sys.exit("AutoBatch_CodeGen->addTemplateLines:  problem with return value from getGlobalVarsHeaderString.")
			#batchOutputString += "\tglobal " + globalsString + "\n"
			#indOutputString += "\tglobal " + globalsString + "\n"

	#batchOutputString += "\t" + con.group + " = " + con.group + "ObjParam\n\n"
	#batchOutputString += "\t" + con.numSignatures + " = len(verifyArgsDict)\n"
	#batchOutputString += "\t" + con.numSignaturesIndex + " = 0\n"

	#batchVerFile.write(batchOutputString)
	batchOutputString = ""
	#writeNumSignersLine(batchVerFile)
	#writeNumEqChecksLine(batchVerFile)

	batchOutputString += "\n\tBig " + con.delta + "[" + con.numSignatures + "];\n"
	batchOutputString += "\tbig t;\n\n"

	batchOutputString += "\tfor (int " + con.numSignaturesIndex + " = 0; " + con.numSignaturesIndex + " < " + con.numSignatures + "; " + con.numSignaturesIndex + "++)\n"

	batchOutputString += "\t{\n"
	batchOutputString += "\t\tSmallExp(t, " + con.delta + "[" + con.numSignaturesIndex + "]);\n"
	batchOutputString += "\t}\n\n"

	#batchOutputString += "\t" + con.deltaDictName + " = {}\n"
	#batchOutputString += "\tfor " + con.numSignaturesIndex + " in range(0, " + con.numSignatures + "):\n"
	#batchOutputString += "\t\t" + con.deltaDictName + "[" + con.numSignaturesIndex + "] = prng_bits(80)\n\n"
	#batchOutputString += "\t" + con.numSignaturesIndex + " = 0\n\n"
	#batchOutputString += "\tincorrectIndices = []\n"

	#indOutputString += "\t" + con.group + " = " + con.group + "ObjParam\n\n"
	#indOutputString += "\t" + con.numSignatures + " = len(verifyArgsDict)\n"
	#indOutputString += "\t" + con.numSignaturesIndex + " = 0\n"

	individualVerFile.write(indOutputString)
	indOutputString = ""
	#writeNumSignersLine(individualVerFile)
	#writeNumEqChecksLine(individualVerFile)

	#indOutputString += "\tincorrectIndices = []\n"

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)

def addPrerequisites():
	global batchVerFile, individualVerFile

	prereqLineNos = getLineNosOfNodeType(pythonCodeNode, con.lambdaTypeAST)
	if (len(prereqLineNos) == 0):
		return

	if ( (type(prereqLineNos).__name__ != con.listTypePython) or (len(prereqLineNos) == 0) ):
		sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with value returned from getLineNosOfValueType.")

	prereqLines = getLinesFromSourceCode(copy.deepcopy(pythonCodeLines), prereqLineNos)
	if ( (prereqLines == None) or (type(prereqLines).__name__ != con.listTypePython) or (len(prereqLines) == 0) ):
		sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with value returned from getLinesFromSourceCode.")

	outputString = ""

	for line in prereqLines:
		if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
			sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with one of the lines returned from getLinesFromSourceCode.")

		outputString += "\t" + line.lstrip().rstrip()
		outputString += "\n"

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)

	global verifyPrereqs
	verifyPrereqs = outputString

def getInitArgString():
	if (con.initFuncName not in functionArgNames):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  init function is not included in the function arguments names structure.")

	if (functionArgNames[con.initFuncName] == None):
		return ""

	initArgListAsStrings = getFunctionArgsAsStrings(functionArgNames, con.initFuncName)
	if ( (initArgListAsStrings == None) or (type(initArgListAsStrings).__name__ != con.listTypePython) or (len(initArgListAsStrings) == 0) ):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  problem with value returned from getFunctionArgsAsStrings.")

	if (len(initArgListAsStrings) > 1):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  number of arguments passed to __init__ function is greater than one; this is not currently supported.")

	onlyArg = initArgListAsStrings[0]

	if (onlyArg.startswith(con.group) == False):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  the argument passed to the __init__ function does not start with \"" + con.group + "\"; this is not currently supported.")

	return con.group

def addCallToInit():
	if (con.initFuncName not in functionNames):
		sys.exit("AutoBatch_CodeGen->addCallToInit:  init function is not included in the function names dictionary.")

	global batchVerFile, individualVerFile, verifySigsInitCall

	batchOutputString = ""
	indOutputString = ""

	initArgString = getInitArgString()

	batchOutputString += "\t__init__(" + initArgString + ")\n\n"
	indOutputString += "\t__init__(" + initArgString + ")\n"

	verifySigsInitCall = batchOutputString

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)

def addSigLoop():
	global batchVerFile, individualVerFile

	outputString = ""

	outputString += "\n"

	for currentVarName in typeVars:
		outputString += "\t" + typeVars[currentVarName] + " " + currentVarName + ";\n"

	#outputString += "\n\tfor " + con.numSignaturesIndex + " in range(0, " + con.numSignatures + "):\n"

	outputString += "\n\tfor (int " + con.numSignaturesIndex + " = 0; " + con.numSignaturesIndex + " < " + con.numSignatures + "; " + con.numSignaturesIndex + "++)\n"
	outputString += "\t{\n"

	#batchVerFile.write(outputString)
	individualVerFile.write(outputString)

def addGroupMembershipChecks():
	global batchVerFile, individualVerFile

	outputString = ""
	outputString += "\t\t#for arg in verifyFuncArgs:\n"
	outputString += "\t\t\t#if (group.ismember(verifyArgsDict[" + con.numSignaturesIndex + "][arg][bodyKey]) == False):\n"
	outputString += "\t\t\t\t#sys.exit(\"ALERT:  Group membership check failed!!!!\\n\")\n\n"

	outputString += "\t\tpass\n\n"

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)

	if ( (checkBlocks != None) and (len(codeGenRanges) == 1) ):
		for checkBlock in checkBlocks:
			startLineCheckBlock = checkBlock[0]
			endLineCheckBlock = checkBlock[1]
			lineNoList = createListFromRange(startLineCheckBlock, endLineCheckBlock)
			varNamesInCheckBlock = getVarNamesFromLineInfoObj(lineNoList, lineInfo)
			lineNosNeededForCheckBlock = getAllLineNosThatImpactVarList(varNamesInCheckBlock, con.verifyFuncName, lineNosPerVar, var_varDependencies)
			combineListsNoDups(lineNoList, lineNosNeededForCheckBlock)
			lineNoList.sort()
			writeLinesToFile(lineNoList, 1, batchVerFile)
			batchVerFile.write("\n")

	outputString = ""
	outputString += "\t" + con.numSignaturesIndex + " = 0\n"
	outputString += "\tstartSigNum = 0\n"
	outputString += "\tendSigNum = " + con.numSignatures + "\n\n"

	batchVerFile.write(outputString)

def writeLinesToOutputString(lines, indentationListParam, baseNumTabs, numExtraTabs):
	if ( (lines == None) or (type(lines).__name__ != con.listTypePython) or (len(lines) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with lines parameter passed in.")

	if ( (baseNumTabs == None) or (type(baseNumTabs).__name__ != con.intTypePython) or (baseNumTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with base number of tabs parameter passed in.")

	if ( (numExtraTabs == None) or (type(numExtraTabs).__name__ != con.intTypePython) or (numExtraTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with extra number of tabs passed in.")

	outputString = ""
	lineNumber = -1

	numTabsOnPreviousLine = 9999

	for line in lines:
		lineNumber += 1
		if (isLineOnlyWhiteSpace(line) == True):
			continue
		line = ensureSpacesBtwnTokens_CodeGen(line)

		if (line.lstrip().rstrip() == 'return False'):
			line = "incorrectIndices.append(" + con.numSignaturesIndex + ")"

		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):
				indexOfCharAfterArg = line.index(argWithSpaces) + len(argWithSpaces)
				if (indexOfCharAfterArg < len(line)):
					charAfterArg = line[indexOfCharAfterArg]
				else:
					charAfterArg = ''
				replacementString = " verifyArgsDict[" + con.numSignaturesIndex + "][\'" + arg + "\'][bodyKey]"
				if (charAfterArg == con.dictBeginChar):
					line = line.replace(argWithSpaces + '[', replacementString + '[', 1)
				else:
					line = line.replace(argWithSpaces, replacementString + ' ', 1)
		line = line.lstrip().rstrip()
		line = removeSpaceBeforeChar(line, con.lParan)

		line = removeSpaceBeforeChar(line, '=')

		line = removeSpaceAfterChar(line, '-')

		line = line.replace(con.subscriptTerminator, '')

		line = line.replace(con.selfFuncCallString, con.space)
		if (indentationListParam != None):
			numTabs = determineNumTabsFromSpaces(indentationListParam[lineNumber], numSpacesPerTab) - baseNumTabs
		else:
			numTabs = 0

		numTabs += numExtraTabs

		numTabsOnPreviousLine = numTabs

		outputString += getStringOfTabs(numTabs)
		outputString += line + "\n"

		outputString = addPassToPythonLoops(line, outputString, (numTabs+1))

	if (len(outputString) == 0):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  could not form any lines for the output string.")

	return outputString

def processHashesForCPP(line):
	splitValue = None

	if (line.count("group.hash (") == 1):
		splitValue = "group.hash ("

	if (splitValue == None):
		return line

	splitLine = line.split(splitValue)

	#['h = ', 'M, G1)']

	varName = splitLine[0].split('=')[0].lstrip().rstrip()
	argName = splitLine[1].split(',')[0].lstrip().rstrip()

	line = "HASH(" + varName + ", " + argName + ")"

	return line

def writeBodyOfInd():
	global individualVerFile

	#print(verifyLines)

	#individualOutputString = writeLinesToOutputString(verifyLines, indentationListVerifyLines, numTabsOnVerifyLine, 1)
	#if ( (individualOutputString == None) or (type(individualOutputString).__name__ != con.strTypePython) or (len(individualOutputString) == 0) ):
		#sys.exit("AutoBatch_CodeGen->writeBodyOfInd:  problem with value returned from writeLinesToOutputString.")

	individualOutputString = ""

	for line in verifyLines:
		line = ensureSpacesBtwnTokens_CodeGen(line)

		for arg in verifyFuncArgs:
			line = line.replace(arg, arg+"[z]")

		line = processHashesForCPP(line)

		line = line.lstrip().rstrip()

		if (line.endswith(':') == True):
			line = line.rstrip(':')
		else:
			line += ";"

		line = line.replace('\'', '"')

		individualOutputString += "\t\t" + line + "\n"

	individualOutputString += "\t\t{\n"
	individualOutputString += "\t\t\tcout << \"Signature verified!\" << endl;\n"
	individualOutputString += "\t\t}\n"
	individualOutputString += "\t\telse\n"
	individualOutputString += "\t\t{\n"
	individualOutputString += "\t\t\tcout << \"Signature failed!\" << endl;\n"
	individualOutputString += "\t\t}\n"
	individualOutputString += "\t}\n"
	individualOutputString += "}\n"

	'''
	for line in codeLinesFromBatcher:
		line = line.replace("_z", "[z]")
		individualOutputString += "\t\t" + line + "\n"

	individualOutputString += "\t\t\tpass\n"
	individualOutputString += "\t\telse:\n"
	individualOutputString += "\t\t\tif " + con.numSignaturesIndex + " not in incorrectIndices:\n"
	individualOutputString += "\t\t\t\tincorrectIndices.append(" + con.numSignaturesIndex + ")\n\n"

	individualOutputString += "\treturn incorrectIndices\n"
	'''

	individualVerFile.write(individualOutputString)

def addFunctionsThatVerifyCalls():
	global batchVerFile, individualVerFile, verifySigsFile

	outputString = ""
	linePairsOfVerifyFuncs.sort()

	for linePair in linePairsOfVerifyFuncs:
		functionString = writeFunctionFromCodeToString(copy.deepcopy(pythonCodeLines), linePair[0], linePair[1], 0, numSpacesPerTab, True)
		if ( (functionString == None) or (type(functionString).__name__ != con.strTypePython) or (len(functionString) == 0) ):
			sys.exit("AutoBatch_CodeGen->addFunctionsThatVerifyCalls:  problem with function string returned from writeFunctionFromCodeToString.")

		outputString += functionString

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)
	verifySigsFile.write(outputString)

def getLoopNamesOfFinalBatchEq():
	global loopNamesOfFinalBatchEq

	loopNamesOfFinalBatchEq = {}

	numPasses = len(finalBatchEqWithLoops)

	for index in range(0, numPasses):
		getLoopNamesOfFinalBatchEq_Ind(finalBatchEqWithLoops[index], index)

def getLoopNamesOfFinalBatchEq_Ind(finalBatchEqWithLoops_Ind, codeGenSegNo):
	global loopNamesOfFinalBatchEq

	loopNamesOfFinalBatchEq[codeGenSegNo] = []

	batchEqWithLoopsCopy = finalBatchEqWithLoops_Ind.getEquation().replace(con.finalBatchEqWithLoopsString, '', 1)

	tempList = getVarNamesAsStringNamesFromLine(batchEqWithLoopsCopy)

	for possibleLoopName in tempList:
		nameAsString = possibleLoopName.getStringVarName()
		isValidLoopName = isStringALoopName(nameAsString)
		if (isValidLoopName == False):
			continue
		loopNamesOfFinalBatchEq[codeGenSegNo].append(copy.deepcopy(possibleLoopName))

	del tempList

def getLoopOrder(varListAsStrings):
	if ( (varListAsStrings == None) or (type(varListAsStrings).__name__ != con.listTypePython) or (len(varListAsStrings) == 0) ):
		sys.exit("AutoBatch_CodeGen->getLoopOrder:  problem with variable list parameter passed in.")

	loopOrder = []
	maxListSize = 0
	maxList = []

	for varName in varListAsStrings:
		if ( (varName == None) or (type(varName).__name__ != con.strTypePython) or (len(varName) == 0) ):
			sys.exit("AutoBach_CodeGen->getLoopOrder:  problem with one of the variable names within the list parameter passed in.")

		if (varName.find(con.loopIndicator) == -1):
			continue

		if (varName.count(con.loopIndicator) > 1):
			sys.exit("AutoBatch_CodeGen->getLoopOrder:  variable name contains more than one loop indicator symbol (" + con.loopIndicator + ").")

		currentList = []

		loopIndicatorIndex = varName.find(con.loopIndicator)
		subscriptIndicesStringSpaces = varName[(loopIndicatorIndex + 1):len(varName)]
		subscriptIndicesString = subscriptIndicesStringSpaces.lstrip().rstrip()
		splitString = subscriptIndicesString.split(con.loopIndicesSeparator)

		for indString in splitString:
			currentList.append(indString)

		currentSize = len(currentList)

		if (currentSize < maxListSize):
			continue

		if (currentSize == maxListSize):
			if (currentList != maxList):
				sys.exit("AutoBatch_CodeGen->getLoopOrder:  multiple lists of same size contain different loop orders.")
			else:
				continue

		maxList = copy.deepcopy(currentList)
		maxListSize = len(maxList)

	for loopNameEntry in maxList:
		loopNameEntryAsStringName = StringName()
		loopNameEntryAsStringName.setName(loopNameEntry)
		loopOrder.append(copy.deepcopy(loopNameEntryAsStringName))
		del loopNameEntryAsStringName

	return loopOrder

def distillLoopsWRTNumSignatures():
	global loopsOuterNumSignatures, loopsOuterNotNumSignatures

	loopsOuterNumSignatures = []
	loopsOuterNotNumSignatures = []

	loopsAddedToOuterNumSigs = []
	loopsToAddToOuterNumSigs = []

	for loop in loopInfo:
		loopNameToAdd = StringName()
		loopNameToAdd.setName(loop.getLoopName().getStringVarName())

		loopOrder = loop.getLoopOrder()
		outerIndexStringName = loopOrder[0]
		outerIndex = outerIndexStringName.getStringVarName()
		if (outerIndex not in con.loopIndexTypes):
			sys.exit("AutoBatch_CodeGen->distillLoopsWRTNumSignatures:  outer loop index extracted from one of the loops in loopInfo is not one of the supported loop index types.")
		if (outerIndex != con.numSignaturesIndex):
			continue

		loopsOuterNumSignatures.append(copy.deepcopy(loop))

		loopsAddedToOuterNumSigs.append(loop.getLoopName().getStringVarName())

		childListAsStrings = getStringNameListAsStringsNoDups(loop.getVarListNoSubscripts())

		for childLoopName in childListAsStrings:
			if (isStringALoopName(childLoopName) == True):
				if childLoopName not in loopsToAddToOuterNumSigs:
					loopsToAddToOuterNumSigs.append(childLoopName)

		del loopNameToAdd

	for loop in loopInfo:
		currentLoopNameAsString = loop.getLoopName().getStringVarName()
		if (currentLoopNameAsString in loopsAddedToOuterNumSigs):
			continue

		if (currentLoopNameAsString in loopsToAddToOuterNumSigs):
			loopsOuterNumSignatures.append(copy.deepcopy(loop))
		else:
			loopsOuterNotNumSignatures.append(copy.deepcopy(loop))


def writeLinesToFile(lineNosToWriteToFile, numBaseTabs, outputFile):
	indentationListParam = []
	sourceLinesToWriteToFile = getSourceCodeLinesFromLineList(copy.deepcopy(pythonCodeLines), lineNosToWriteToFile, indentationListParam)
	batchOutputString = writeLinesToOutputString(sourceLinesToWriteToFile, indentationListParam, numTabsOnVerifyLine, numBaseTabs)
	outputFile.write(batchOutputString)

def writeOneBlockToFile(block, numBaseTabs, outputFile, forCachedCalcs):
	if ( (block == None) or (type(block).__name__ != con.loopBlock) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with block parameter passed in.")

	if ( (numBaseTabs == None) or (type(numBaseTabs).__name__ != con.intTypePython) or (numBaseTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with number of base tabs parameter passed in.")

	blockStartValue = block.getStartValue().getValue()
	blockIndexVariable = block.getIndexVariable().getStringVarName()
	blockLoopOverValue = block.getLoopOverValue().getStringVarName()

	if ( (blockStartValue == None) or (type(blockStartValue).__name__ != con.intTypePython) or (blockStartValue < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the start value of the block parameter passed in.")

	if ( (blockIndexVariable == None) or (type(blockIndexVariable).__name__ != con.strTypePython) or (blockIndexVariable not in con.loopIndexTypes) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the index variable of the block parameter passed in.")

	if ( (blockLoopOverValue == None) or (type(blockLoopOverValue).__name__ != con.strTypePython) or (blockLoopOverValue not in con.loopTypes) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the loop over value of the block parameter passed in.")

	loopsToCalculate = []

	blockLoopsWithVarsToCalc = block.getLoopsWithVarsToCalculate()
	if (blockLoopsWithVarsToCalc != None):
		blockLoopsWithVarsAsStrings = getStringNameListAsStringsNoDups(blockLoopsWithVarsToCalc)

		for blockLoopVarString in blockLoopsWithVarsAsStrings:
			loopsToCalculate.append(blockLoopVarString)

	blockLoopsToCalc = block.getLoopsToCalculate()
	if (blockLoopsToCalc != None):
		blockLoopsAsStrings = getStringNameListAsStringsNoDups(blockLoopsToCalc)
		for blockLoopString in blockLoopsAsStrings:
			loopsToCalculate.append(blockLoopString)

	blockOperationString = block.getOperation().getOperationSymbol()

	outputString = ""

	if (forCachedCalcs == False):
		for loopToCalc in loopsToCalculate:
			loopNameForInit = loopToCalc
			loopGroupTypeForInit = loopVarGroupTypes[loopToCalc]
			loopInitValueForInit = str(getInitValueOfLoop(loopInfo, loopToCalc))

			outputString += getStringOfTabs(numBaseTabs)
			outputString += loopNameForInit + "_loopVal = group.init(" + loopGroupTypeForInit + ", " + loopInitValueForInit + ")\n"

	outputString += getStringOfTabs(numBaseTabs)
	if ( (forCachedCalcs == False) and (blockLoopOverValue == con.numSignatures) ):
		outputString += "for " + blockIndexVariable + " in range(startSigNum, endSigNum):\n"
	else:
		outputString += "for " + blockIndexVariable + " in range(" + str(blockStartValue) + ", " + blockLoopOverValue + "):\n"

	outputFile.write(outputString)
	outputString = ""

	childrenList = block.getChildrenList()
	if (childrenList != None):
		for childBlock in childrenList:
			if ( (childBlock == None) or (type(childBlock).__name__ != con.loopBlock) ):
				sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with one of the child blocks from the block parameter passed in.")

			writeOneBlockToFile(childBlock, (numBaseTabs + 1), outputFile, False)

	if (blockLoopsWithVarsToCalc != None):
		variablesToCalculateAsStrings = getVariablesOfLoopsAsStrings(loopInfo, blockLoopsWithVarsAsStrings)

		removeListEntriesFromAnotherList(nonLoopCachedVars, variablesToCalculateAsStrings)

		lineNosToWriteToFile = getAllLineNosThatImpactVarList(variablesToCalculateAsStrings, con.verifyFuncName, lineNosPerVar, var_varDependencies)
		if (lineNosToWriteToFile != None):
			writeLinesToFile(lineNosToWriteToFile, numBaseTabs, outputFile)

	outputFile.write("\n")

	multipleEqChecksAlready = False
	eqChecksThisLoop = False
	loopsWithMultipleEqChecks = getListOfLoopsWithMultipleEqChecks(loopInfo)

	for loopToCalculate in loopsToCalculate:
		eqChecksThisLoop = doesThisLoopHaveMultipleEqChecks(loopInfo, loopToCalculate)

		if (eqChecksThisLoop == False):
			writeOneLoopCalculation(loopToCalculate, blockOperationString, (numBaseTabs + 1), forCachedCalcs, outputFile)
		elif (multipleEqChecksAlready == False):
			multipleEqChecksAlready = True
			outputString = writeEqChecksDictDefs(loopsWithMultipleEqChecks, (numBaseTabs + 1))
			outputFile.write(outputString)
			(outputString, indexVariable_EqChecks) = writeMultipleEqChecksForLoop(loopToCalculate, (numBaseTabs + 1))
			outputFile.write(outputString)
			writeOneLoopCalculation(loopToCalculate, blockOperationString, (numBaseTabs + 2), forCachedCalcs, outputFile, indexVariable_EqChecks)
		else:
			(outputString, indexVariable_EqChecks) = writeMultipleEqChecksForLoop(loopToCalculate, (numBaseTabs + 1))
			writeOneLoopCalculation(loopToCalculate, blockOperationString, (numBaseTabs + 2), forCachedCalcs, outputFile, indexVariable_EqChecks)

def writeEqChecksDictDefs(loopsWithMultipleEqChecks, numBaseTabs):
	if (loopsWithMultipleEqChecks == None):
		sys.exit("codegen->writeeqchecksdictdefs->loops struct passed in is None.")

	outputString = ""

	for loopName in loopsWithMultipleEqChecks:
		#print(loopName)
		outputString += getStringOfTabs(numBaseTabs)
		outputString += loopName + "[" + con.numSignaturesIndex + "] = {}\n"

	return outputString

def writeMultipleEqChecksForLoop(loopName, numTabs):
	outputString = ""
	outputString += getStringOfTabs(numTabs)

	codeGenSegNo = getCodeGenSegNo_Parser(loopInfo, loopName)

	finalBatchEqObj = finalBatchEqWithLoops[codeGenSegNo]

	if (finalBatchEqObj.getCodeGenSegmentNo() != codeGenSegNo):
		sys.exit("codegen->writemultipleeqchecks . . . mismatching codegensegno")

	indexVariable = finalBatchEqObj.getIndexVariable()
	startValue = finalBatchEqObj.getStartValue()
	loopOverValue = finalBatchEqObj.getLoopOverValue()

	outputString += "for " + str(indexVariable) + " in range(" + str(startValue) + ", " + str(loopOverValue) + "):\n"

	return (outputString, indexVariable)

def writeOneLoopCalculation(loopName, blockOperationString, numBaseTabs, forCachedCalcs, outputFile, indexVariable_EqChecks = None):
	if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (isStringALoopName(loopName) == False) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalcualtion:  problem with loop name parameter passed in.")

	if ( (numBaseTabs == None) or (type(numBaseTabs).__name__ != con.intTypePython) or (numBaseTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalculation:  problem with number of base tabs parameter passed in.")

	if ( (forCachedCalcs != True) and (forCachedCalcs != False) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalculation:  for cached calculations parameter is neither True nor False.")

	global cachedCalcsToPassToDC

	if ( (loopName not in cachedCalcsToPassToDC) and (forCachedCalcs == True) ):
		cachedCalcsToPassToDC.append(loopName)

	expression = getExpressionFromLoopInfoList(loopInfo, loopName)
	expressionCalcString = getExpressionCalcString(expression, loopName, blockOperationString, numBaseTabs, forCachedCalcs, True, indexVariable_EqChecks)

	outputString = ""
	outputString += getStringOfTabs(numBaseTabs)
	outputString += expressionCalcString
	outputString += "\n"

	outputFile.write(outputString)

def getExpressionCalcString(expression, loopName, blockOperationString, numBaseTabs, forCachedCalcs, forAssignment, indexVariable_EqChecks = None):
	outputString = ""

	if (forAssignment == True):
		#outputString += loopName
		if (forCachedCalcs == True):
			if (indexVariable_EqChecks == None):
				outputString += loopName + "[" + con.numSignaturesIndex + "] = "
			else:
				#outputString += loopName + "[" + con.numSignaturesIndex + "] = {}\n"
				#outputString += getStringOfTabs(numBaseTabs)
				outputString += loopName + "[" + con.numSignaturesIndex + "][" + indexVariable_EqChecks + "] = "
		else:
			outputString += loopName + "_loopVal = " + loopName + "_loopVal " + blockOperationString + " "

	expression = expression.lstrip('\'').rstrip('\'')
	expression = ensureSpacesBtwnTokens_CodeGen(expression)
	expression = expression.replace(' ^ ', ' ** ')
	expression = expression.replace(' e ', ' pair ')

	expressionSplit = expression.split()
	for tokenCopy in expressionSplit:
		token = copy.deepcopy(tokenCopy)

		if (token.count(con.loopIndicator) > 1):
			sys.exit("AutoBatch_CodeGen->getExpressionCalcString:  one of the tokens in the expression string contains more than one loop indicator symbol.  This is not currently supported.")

		newToken = None

		if (token.count(con.loopIndicator) == 1):
			if (forAssignment == False):
				sys.exit("getexpressioncalcstring . . . ")

			newToken = processTokenWithLoopIndicator(token)
			expression = expression.replace(token, newToken, 1)

		if (newToken != None):
			token = newToken

		if (token.count(con.subscriptIndicator) >= 1):
			newToken = processTokenWithSubscriptIndicator(token)
			expression = expression.replace(token, newToken, 1)

		if (isStringALoopName(token) == True):
			#if (forCachedCalcs == True):
				#sys.exit("getExpressionCalcString-> . . . here")
			if (indexVariable_EqChecks == None):
				newToken = token + "_loopVal"
			else:
				newToken = token + "_loopVal[" + indexVariable_EqChecks + "]"
			expression = expression.replace(token, newToken, 1)

	expression = ensureSpacesBtwnTokens_CodeGen(expression)
	for verifyArg in verifyFuncArgs:
		verifyArgWithSpaces = con.space + verifyArg + con.space
		replacementExpression = " verifyArgsDict[" + con.numSignaturesIndex + "]['" + verifyArg + "'][bodyKey] "

		expression = expression.replace(verifyArgWithSpaces, replacementExpression)

	expression = removeSpaceBeforeChar(expression, con.lParan)

	expression = removeSpaceBeforeChar(expression, '=')

	expression = removeSpaceAfterChar(expression, '-')

	expression = expression.replace(con.subscriptTerminator, '')

	outputString += expression
	return outputString

def processTokenWithSubscriptIndicator(token):
	tokenSplit = token.split(con.subscriptIndicator)

	for tokenIndex in range(0, len(tokenSplit)):
		if (tokenSplit[tokenIndex].count(con.subscriptTerminator) > 1):
			sys.exit("codegen->processtoken->too many subscript terminators")

		tokenSplit[tokenIndex] = tokenSplit[tokenIndex].replace(con.subscriptTerminator, '')

	structName = tokenSplit[0]
	if (tokenSplit[1].count(con.loopIndicator) > 1):
		print(token)
		sys.exit("AutoBatch_CodeGen->processTokenWithSubscriptIndicator . . . ")

	loopIndices = None

	dictBeginCharIndex = tokenSplit[1].find(con.dictBeginChar)

	if (dictBeginCharIndex != -1):
		keyNoAsString = tokenSplit[1][0:dictBeginCharIndex]
		loopIndices = tokenSplit[1][dictBeginCharIndex:len(tokenSplit[1])]
	else:
		keyNoAsString = tokenSplit[1]

	firstIndexIsNum = True

	try:
		keyNo = int(keyNoAsString)
	except:
		#print(token)
		#sys.exit("AutoBatch_CodeGen->processTokenWithSubscriptIndicator . . . ")
		firstIndexIsNum = False

	if (firstIndexIsNum == True):
		expandedName = expandEntryWithSubscriptPlaceholder(varAssignments, structName, keyNo)
	else:
		if (str(keyNoAsString) in con.loopTypes):
			newIndexToAdd = "(" + str(keyNoAsString) + " - 1)"
		else:
			newIndexToAdd = str(keyNoAsString)
		expandedName = structName + "[" + newIndexToAdd + "]"
		#print(expandedName)

	if (loopIndices != None):
		expandedName += loopIndices

	if (len(tokenSplit) == 2):
		return expandedName

	#print(tokenSplit)

	#numListIndices = len(tokenSplit) - 2
	#print(numListIndices)

	for listIndexNo in range(2, len(tokenSplit)):
		if (str(tokenSplit[listIndexNo]) in con.loopTypes):
			newIndexToAdd = "(" + str(tokenSplit[listIndexNo]) + " - 1)"
		else:
			newIndexToAdd = str(tokenSplit[listIndexNo])
		expandedName += "[" + newIndexToAdd + "]"

	#print(expandedName)

	return expandedName

def processTokenWithLoopIndicator(token):
	tokenSplit = token.split(con.loopIndicator)
	if (len(tokenSplit) != 2):
		sys.exit("AutoBatch_CodeGen->processTokenWithLoopIndicator:  token split by loop indicator symbol does not produce 2 sub-tokens.  This is not currently supported.")

	realTokenName = tokenSplit[0]

	if (realTokenName not in listVars):
		return realTokenName

	indicesString = listVars[realTokenName]

	indicesStringWithBraces = getIndicesStringWithBraces(indicesString)

	return realTokenName + indicesStringWithBraces

def getIndicesStringWithBraces(indicesString):
	if (indicesString.find(con.loopIndicesSeparator) == -1):
		return "[" + indicesString + "]"

	indicesStringSplit = indicesString.split(con.loopIndicesSeparator)

	retString = ""

	for index in indicesStringSplit:
		retString += "["
		retString += index
		retString += "]"

	return retString

def writeBodyOfNonCachedCalcsForDC():
	global verifySigsFile

	for block in loopBlocksForNonCachedCalculations:
		writeOneBlockToFile(block, 1, verifySigsFile, False)

def writeBodyOfCachedCalcsForBatch():
	global batchVerFile, nonLoopCachedVars

	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeBodyOfCachedCalcsForBatch:  problem with loopBlocksForCachedCalculations global parameter.")

	nonLoopCachedVars = []

	global cachedCalcsToPassToDC

	for currPrecomputeVar in precomputeVars:
		currPrecomputeVarName = currPrecomputeVar.getVarName().getStringVarName()
		if (doesVarHaveNumSignaturesIndex(currPrecomputeVarName) == True):
			continue

		nonLoopCachedVars.append(currPrecomputeVarName)
		if currPrecomputeVarName not in cachedCalcsToPassToDC:
			cachedCalcsToPassToDC.append(currPrecomputeVarName)

	if (len(nonLoopCachedVars) != 0):
		lineNosToWriteToFile = getAllLineNosThatImpactVarList(nonLoopCachedVars, con.verifyFuncName, lineNosPerVar, var_varDependencies)
		if ( (lineNosToWriteToFile == None) or (type(lineNosToWriteToFile).__name__ != con.listTypePython) or (len(lineNosToWriteToFile) == 0) ):
			sys.exit("AutoBatch_CodeGen->writeBodyOfCachedCalcsForBatch:  problem with value returned from getAllLineNosThatImpactVarList for non-loop cached variables.")

		writeLinesToFile(lineNosToWriteToFile, 0, batchVerFile)
		batchVerFile.write("\n")

	if (con.deltaDictName not in cachedCalcsToPassToDC):
		cachedCalcsToPassToDC.append(con.deltaDictName)

	for block in loopBlocksForCachedCalculations:
		writeOneBlockToFile(block, 1, batchVerFile, True)

	batchVerFile.write("\n")

def writeDictDefsOfCachedCalcsForBatch():
	global batchVerFile

	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeDictDefsOfCachedCalcsForBatch:  problem with loopBlocksForCachedCalculations global variable.")

	loopList = []

	for block in loopBlocksForCachedCalculations:
		if (block.getLoopsWithVarsToCalculate() != None):
			for loop in block.getLoopsWithVarsToCalculate():
				loopName = loop.getStringVarName()
				if (loopName not in loopList):
					loopList.append(loopName)

		if (block.getLoopsToCalculate() != None):
			for loop in block.getLoopsToCalculate():
				loopName = loop.getStringVarName()
				if (loopName not in loopList):
					loopList.append(loopName)

	batchOutputString = ""

	for loopName in loopList:
		currentLoopType = loopVarGroupTypes[loopName]
		batchOutputString += "\t" + currentLoopType + " " + loopName + "[" + con.numSignatures + "];\n"

	batchOutputString += "\n"

	for currentTypeVar in typeVars:
		batchOutputString += "\t" + typeVars[currentTypeVar] + " " + currentTypeVar + ";\n"

	batchOutputString += "\n"
	batchVerFile.write(batchOutputString)

def writeCallToDCAndRetToBatch():
	global batchVerFile

	outputString = ""
	outputString += "\tverifySigsRecursive(verifyArgsDict, " + con.group + ", incorrectIndices, 0, " + con.numSignatures
	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			outputString += ", "
			outputString += cachedCalcName

	outputString += ")\n\n"

	outputString += "\treturn incorrectIndices\n"

	batchVerFile.write(outputString)

def writeOpeningLinesToDCVerifySigsRecursiveFunc():
	global verifySigsFile

	verifyOutputString = ""
	verifyOutputString += "def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum"

	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			verifyOutputString += ", "
			verifyOutputString += cachedCalcName

	verifyOutputString += "):\n"

	verifyOutputString += "\t" + con.numSignaturesIndex + " = 0\n\n"

	verifyOutputString += "\t" + con.group + " = groupObj\n\n"
	verifySigsFile.write(verifyOutputString)
	verifyOutputString = ""
	writeNumSignersLine(verifySigsFile)
	writeNumEqChecksLine(verifySigsFile)

	if (verifyPrereqs != None):
		verifyOutputString += verifyPrereqs

	verifyOutputString += "\n"

	#verifyOutputString += verifySigsInitCall

	verifySigsFile.write(verifyOutputString)

def writeCachedCalcAssignmentsForDC():
	global verifySigsFile

	outputString = ""
	outputString += "\n"

	for cachedCalcName in cachedCalcsToPassToDC:
		if (isStringALoopName(cachedCalcName) == False):
			continue

		if (doesThisLoopHaveMultipleEqChecks(loopInfo, cachedCalcName) == True):
			continue

		loopGroupTypeForInit = loopVarGroupTypes[cachedCalcName]
		loopInitValueForInit = str(getInitValueOfLoop(loopInfo, cachedCalcName))

		outputString += "\t" + cachedCalcName + "_loopVal = group.init(" + loopGroupTypeForInit + ", " + loopInitValueForInit + ")\n"

	outputString += "\n"

	eqChecksDictDefs = ""
	eqChecksLoop = ""
	eqChecksBody = ""
	eqChecksDictAssign = ""

	for cachedCalcName in cachedCalcsToPassToDC:
		if (isStringALoopName(cachedCalcName) == False):
			continue

		if (doesThisLoopHaveMultipleEqChecks(loopInfo, cachedCalcName) == False):
			continue

		eqChecksDictDefs += "\t" + cachedCalcName + "_loopVal = {}\n"

		if (eqChecksLoop == ""):
			(eqChecksLoop, indexVariable_EqChecks) = writeMultipleEqChecksForLoop(cachedCalcName, 1)

		loopGroupTypeForInit = loopVarGroupTypes[cachedCalcName]
		loopInitValueForInit = str(getInitValueOfLoop(loopInfo, cachedCalcName))

		eqChecksBody += "\t\t" + cachedCalcName + "_loopVal[" + indexVariable_EqChecks + "] = group.init(" + loopGroupTypeForInit + ", " + loopInitValueForInit + ")\n"

		operationString = getOperationStringOfLoop(loopInfo, cachedCalcName)

		eqChecksDictAssign+="\t\t\t"+cachedCalcName+"_loopVal["+indexVariable_EqChecks+"] = "+cachedCalcName+"_loopVal["+indexVariable_EqChecks+"] "+operationString+" "+cachedCalcName+"[index]["+indexVariable_EqChecks+"]"
		eqChecksDictAssign += "\n"

	outputString += eqChecksDictDefs
	outputString += "\n"
	outputString += eqChecksLoop
	#outputString += "\n"
	outputString += eqChecksBody
	outputString += "\n"

	outputString += "\tfor index in range(startSigNum, endSigNum):\n"

	for cachedCalcName in cachedCalcsToPassToDC:
		if (isStringALoopName(cachedCalcName) == False):
			continue

		if (doesThisLoopHaveMultipleEqChecks(loopInfo, cachedCalcName) == True):
			continue

		operationString = getOperationStringOfLoop(loopInfo, cachedCalcName)
		outputString += "\t\t" + cachedCalcName + "_loopVal = " + cachedCalcName + "_loopVal " + operationString + " " + cachedCalcName + "[index]\n"

	outputString += "\n"
	outputString += eqChecksLoop
	#outputString += "\n"
	outputString += "\t\tfor index in range(startSigNum, endSigNum):\n"

	outputString += eqChecksDictAssign

	verifySigsFile.write(outputString)

def writeVerifyEqAndRecursionForDC():
	global verifySigsFile

	outputString = ""
	outputString += "\n"

	verifySigsFile.write(outputString)

	for codeGenSegment in finalBatchEqWithLoops:
		finalBatchEq = codeGenSegment.getEquation().replace(con.finalBatchEqWithLoopsString, '', 1)
		multipleEqChecks = codeGenSegment.getHasMultipleEqChecks()
		if (multipleEqChecks == False):
			finalBatchExp = getExpressionCalcString(finalBatchEq, None, None, None, False, False)
		else:
			indexVariable = codeGenSegment.getIndexVariable()
			finalBatchExp = getExpressionCalcString(finalBatchEq, None, None, None, False, False, indexVariable)

		writeVerifyEqRecursion_Ind(finalBatchExp, codeGenSegment, multipleEqChecks)

def writeVerifyEqRecursion_Ind(finalBatchExp, codeGenSegment, multipleEqChecks):
	global verifySigsFile

	numBaseTabs = None

	if (multipleEqChecks == True):
		numBaseTabs = 2
	else:
		numBaseTabs = 1

	outputString = ""

	if (multipleEqChecks == True):
		indexVariable = codeGenSegment.getIndexVariable()
		startValue = codeGenSegment.getStartValue()
		loopOverValue = codeGenSegment.getLoopOverValue()
		outputString += "\tfor " + str(indexVariable) + " in range(" + str(startValue) + ", " + str(loopOverValue) + "):\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "if (" + finalBatchExp + "):\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tpass\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "else:\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tmidWay = int( (endSigNum - startSigNum) / 2)\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tif (midWay == 0):\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\t\tif startSigNum not in incorrectIndices:\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\t\t\tincorrectIndices.append(startSigNum)\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\t\treturn\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tmidSigNum = startSigNum + midWay\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tverifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum"

	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			outputString += ", "
			outputString += cachedCalcName

	outputString += ")\n"

	outputString += getStringOfTabs(numBaseTabs)
	outputString += "\tverifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum"

	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			outputString += ", "
			outputString += cachedCalcName

	outputString += ")\n"
	outputString += getStringOfTabs(numBaseTabs + 1)
	outputString += "return\n\n"

	verifySigsFile.write(outputString)

def writeCallToSortFunction():
	global batchVerFile

	return

	if (len(sortVars) != 1):
		return
		#sys.exit("writecalltosortfunc in codegen py file.")

	outputString = ""
	outputString += "\n"
	outputString += "def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs, toSort):\n"
	outputString += "\tif (toSort == False):\n"
	outputString += "\t\tincorrectIndices = run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs)\n"
	outputString += "\t\treturn incorrectIndices\n\n"

	outputString += "\t" + con.numSignatures + " = len(verifyArgsDict)\n"
	outputString += "\tsortValues = {}\n"
	outputString += "\tsigNosMap = {}\n"
	outputString += "\tsortedSigEntries = {}\n"
	outputString += "\tfor " + con.numSignaturesIndex + " in range(0, " + con.numSignatures + "):\n"
	outputString += "\t\tcurrentSortVal = " + sortVars[0] + "\n"
	outputString += "\t\tmatchingIndex = None\n"
	outputString += "\t\tsortKey = -1\n"
	outputString += "\t\tfor sortKey in sortValues:\n"
	outputString += "\t\t\tif (sortValues[sortKey] == currentSortVal):\n"
	outputString += "\t\t\t\tmatchingIndex = sortKey\n"
	outputString += "\t\t\t\tbreak\n"
	outputString += "\t\tif (matchingIndex != None):\n"
	outputString += "\t\t\tsigNosMap[matchingIndex].append(" + con.numSignaturesIndex + ")\n"
	outputString += "\t\t\tlenCurrentSigsBatch = len(sortedSigEntries[matchingIndex])\n"
	outputString += "\t\t\tsortedSigEntries[matchingIndex][lenCurrentSigsBatch] = verifyArgsDict[" + con.numSignaturesIndex + "]\n"
	outputString += "\t\telse:\n"
	outputString += "\t\t\tnewIndex = sortKey + 1\n"
	outputString += "\t\t\tsortValues[newIndex] = currentSortVal\n"
	outputString += "\t\t\tsigNosMap[newIndex] = []\n"
	outputString += "\t\t\tsigNosMap[newIndex].append(" + con.numSignaturesIndex + ")\n"
	outputString += "\t\t\tsortedSigEntries[newIndex] = {}\n"
	outputString += "\t\t\tsortedSigEntries[newIndex][0] = verifyArgsDict[" + con.numSignaturesIndex + "]\n"
	outputString += "\n"
	outputString += "\tincorrectIndices = []\n"
	outputString += "\n"
	outputString += "\tfor sortValKey in sortedSigEntries:\n"
	outputString += "\t\tincorrectsFromSortedBatch = run_Batch_Sorted(sortedSigEntries[sortValKey], groupObjParam, verifyFuncArgs)\n"
	outputString += "\t\tactualIndices = sigNosMap[sortValKey]\n"
	outputString += "\t\tfor incorrect in incorrectsFromSortedBatch:\n"
	outputString += "\t\t\tincorrectIndices.append(actualIndices[incorrect])\n"
	outputString += "\n"
	outputString += "\treturn incorrectIndices\n"

	batchVerFile.write(outputString)

def processBatcherOutput():
	#global finalBatchEq, finalBatchEqWithLoops

	numPasses = len(codeGenRanges)
	for passNo in range(0, numPasses):
		startLineNo = codeGenRanges[passNo][0]
		endLineNo = codeGenRanges[passNo][1]
		processOneLineBatcherOutput(startLineNo, endLineNo, passNo)

def processOneLineBatcherOutput(startLineNo, endLineNo, passNo):
	global finalBatchEq, finalBatchEqWithLoops

	for lineNo in range(startLineNo, (endLineNo + 1)):
		line = batchVerifierOutput[lineNo - 1]
		#print(line)

		if (line.startswith(con.finalBatchEqString) == True):
			finalBatchEq.append(line)

		if (line.startswith(con.finalBatchEqWithLoopsString) == True):
			#finalBatchEqWithLoops.append(line)
			processFinalBatchEqWithLoops(copy.deepcopy(line), passNo)

		if (line.startswith(con.listString) == True):
			processListLine(line)

		if (line.startswith(con.precomputeString) == True):
			processPrecomputeLine(line, passNo)

		if (line.startswith(con.computeString) == True):
			processComputeLine(line, passNo)

		if (line.startswith(con.sortString) == True):
			processSortLine(line)

		if (line.startswith(con.codeString) == True):
			processCodeLine(line)

		if (line.startswith(con.typeString) == True):
			processTypeLine(line)

		linePrefix = line[0:con.maxStrLengthForLoopNames]
		if (isStringALoopName(linePrefix) == True):
			processLoopLine(line, passNo)

def processTypeLine(line):
	global typeVars

	line = line.replace(con.typeString, '', 1)

	lineSplit = line.split(con.batchVerifierOutputAssignment)

	currentVarName = lineSplit[0].lstrip().rstrip()
	currentVarType = lineSplit[1].lstrip().rstrip()

	typeVars[currentVarName] = currentVarType

def processCodeLine(line):
	global codeLinesFromBatcher

	lineSplit = line.split(con.batchVerifierOutputAssignment)
	codeLine = lineSplit[1].lstrip().rstrip()
	codeLinesFromBatcher.append(codeLine)

def processFinalBatchEqWithLoops(line, codeGenSegNo):
	global finalBatchEqWithLoops

	line = line.lstrip().rstrip()
	line = line.replace(con.finalBatchEqWithLoopsString, '', 1)

	finalEqStruct = FinalEqWithLoops()

	if (line.startswith('for') == False):
		finalEqStruct.setEquation(line)
		finalEqStruct.setCodeGenSegmentNo(codeGenSegNo)
		finalEqStruct.setHasMultipleEqChecks(False)
		finalBatchEqWithLoops.append(copy.deepcopy(finalEqStruct))
		del finalEqStruct
		return

	lineSplitOnDo = line.split(' do ')
	finalEqStruct.setEquation(lineSplitOnDo[1])
	finalEqStruct.setCodeGenSegmentNo(codeGenSegNo)
	finalEqStruct.setHasMultipleEqChecks(True)

	loopParameters = lineSplitOnDo[0].split('{')[1]
	loopParamsSplit = loopParameters.split(con.batchVerifierOutputAssignment)
	indexVariable = loopParamsSplit[0]
	finalEqStruct.setIndexVariable(indexVariable.lstrip().rstrip())

	startValue = loopParamsSplit[1].split(',')[0]
	startValue = int(startValue.lstrip().rstrip())
	finalEqStruct.setStartValue(startValue)

	loopOverValue = loopParamsSplit[1].split(',')[1].split('}')[0]
	finalEqStruct.setLoopOverValue(loopOverValue.lstrip().rstrip())

	finalBatchEqWithLoops.append(copy.deepcopy(finalEqStruct))
	del finalEqStruct

def main():
	if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python " + sys.argv[0] + "\n \
			[input path and filename of Python code for signature scheme] \n \
			[input path and filename of output file from batcher] \n \
			[input path and filename of pickled Python dictionary with verify function arguments] \n \
			[output path and filename of individual verification Python module] \n \
			[output path and filename of batch verification Python module] \n \
			[output path and filename of divide-and-conquer Python module] \n")

	try:
		pythonCodeArg = sys.argv[1]
		batchVerifierOutputFile = sys.argv[2]
		verifyParamFilesArg = sys.argv[3]
		individualVerArg = sys.argv[4]
		batchVerArg = sys.argv[5]
		verifySigsArg = sys.argv[6]
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem obtaining command-line arguments using sys.argv.")

	global pythonCodeLines, individualVerFile, batchVerFile, verifySigsFile, pythonCodeNode, varAssignments, verifyFuncNode, verifyLines 
	global verifyEqNode, functionArgMappings, callListOfVerifyFuncs, linePairsOfVerifyFuncs, verifyFuncArgs, indentationListVerifyLines
	global numTabsOnVerifyLine, batchVerifierOutput, finalBatchEq, finalBatchEqWithLoops, listVars, numSpacesPerTab, lineInfo
	global loopBlocksForCachedCalculations, loopBlocksForNonCachedCalculations, lineNosPerVar
	global lineNoOfFirstFunction, globalVars, var_varDependencies, functionArgNames, functionNames
	global verifySigsFileName, checkBlocks, codeGenRanges

	os.system("cp " + con.cppTemplate + " " + individualVerArg)
	os.system("cp " + con.cppTemplate + " " + batchVerArg)

	try:
		pythonCodeLines = open(pythonCodeArg, 'r').readlines()
		batchVerifierOutput = open(batchVerifierOutputFile, 'r').readlines()
		individualVerFile = open(individualVerArg, 'a')
		batchVerFile = open(batchVerArg, 'a')
		verifySigsFile = open(verifySigsArg, 'w')
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem opening input/output files passed in as command-line arguments.")

	#if (verifySigsArg.endswith(".py") == False):
		#sys.exit("no py ending")

	verifySigsFileName = verifySigsArg[0:(len(verifySigsArg) - 4)]

	myASTParser = ASTParser()
	pythonCodeNode = myASTParser.getASTNodeFromFile(pythonCodeArg)
	if (pythonCodeNode == None):
		sys.exit("AutoBatch_CodeGen->main:  root node obtained from ASTParser->getASTNodeFromFile is of None type.")

	globalVars = getGlobalDeclVars(pythonCodeNode)
	if ( (globalVars != None) and (type(globalVars).__name__ != con.listTypePython) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getGlobalDeclVars.")

	functionNames = myASTParser.getFunctionNames(pythonCodeNode)
	if (functionNames == None):
		sys.exit("AutoBatch_CodeGen->main:  function names obtained from ASTParser->getFunctionNames is of None type.")

	lineNoOfFirstFunction = getLineNoOfFirstFunction(functionNames, myASTParser)
	if ( (lineNoOfFirstFunction == None) or (type(lineNoOfFirstFunction).__name__ != con.intTypePython) or (lineNoOfFirstFunction < 1) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value obtained from getLineNoOfFirstFunction.")

	(functionArgNames, lenFunctionArgDefaults) = myASTParser.getFunctionArgNamesAndDefaultLen(pythonCodeNode)
	if ( (functionArgNames == None) or (lenFunctionArgDefaults == None) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with the values returned from ASTParser->getFunctionArgNamesAndDefaultLen.")

	for funcName in con.funcNamesNotToTest:
		if (funcName in functionNames):
			del functionNames[funcName]
		if (funcName in functionArgNames):
			del functionArgNames[funcName]
		if (funcName in lenFunctionArgDefaults):
			del lenFunctionArgDefaults[funcName]

	functionArgMappings = getFunctionArgMappings(functionNames, functionArgNames, lenFunctionArgDefaults, myASTParser)
	if (functionArgMappings == None):
		sys.exit("AutoBatch_CodeGen->main:  mappings of variables passed between functions from getFunctionArgMappings is of None type.")

	varAssignments = getVarAssignments(pythonCodeNode, functionNames, myASTParser)
	if (varAssignments == None):
		sys.exit("AutoBatch_CodeGen->main:  getVarAssignments returned None when trying to get the variable assignments.")

	verifyFuncNodeList = myASTParser.getFunctionNode(pythonCodeNode, con.verifyFuncName)
	if (verifyFuncNodeList == None):
		sys.exit("AutoBatch_CodeGen->main:  could not locate a function with name " + con.verifyFuncName)
	if (len(verifyFuncNodeList) > 1):
		sys.exit("AutoBatch_CodeGen->main:  located more than one function with the name " + con.verifyFuncName)

	verifyFuncNode = verifyFuncNodeList[0]

	verifyEqNode = myASTParser.getLastEquation(verifyFuncNode)
	if (verifyEqNode == None):
		sys.exit("AutoBatch_CodeGen->main:  could not locate the verify equation within the " + con.verifyFuncName + " function.")

	verifyStartLine = myASTParser.getLineNumberOfNode(verifyFuncNode)
	if ( (verifyStartLine == None) or (type(verifyStartLine).__name__ != con.intTypePython) or (verifyStartLine < 1) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned for starting line of " + con.verifyFuncName + " function.")

	numSpacesOnVerifyFuncList = []
	getLinesFromSourceCodeWithinRange(copy.deepcopy(pythonCodeLines), verifyStartLine, (verifyStartLine + 1), numSpacesOnVerifyFuncList)
	if ( (numSpacesOnVerifyFuncList == None) or (type(numSpacesOnVerifyFuncList).__name__ != con.listTypePython) or (len(numSpacesOnVerifyFuncList) != 2) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getLinesFromSourceCodeWithinRange to determine the number of spaces on the line of the " + con.verifyfuncName + " function.")

	numSpacesOnVerifyFunc = numSpacesOnVerifyFuncList[0]
	if ( (numSpacesOnVerifyFunc == None) or (type(numSpacesOnVerifyFunc).__name__ != con.intTypePython) or (numSpacesOnVerifyFunc < 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with number of spaces extracted on the line of the " + con.verifyFuncName + " function.")

	numSpacesPerTab = numSpacesOnVerifyFuncList[1] - numSpacesOnVerifyFunc
	if ( (numSpacesPerTab == None) or (type(numSpacesPerTab).__name__ != con.intTypePython) or (numSpacesPerTab < 1) ):
		sys.exit("AutoBatch_codeGen->main:  problem with number obtained for the number of spaces per tab.")

	numTabsOnVerifyLine = determineNumTabsFromSpaces(numSpacesOnVerifyFunc, numSpacesPerTab)
	if ( (numTabsOnVerifyLine == None) or (type(numTabsOnVerifyLine).__name__ != con.intTypePython) or (numTabsOnVerifyLine < 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with number of tabs extracted on the line of the " + con.verifyFuncName + " function.")

	verifyStartLine += 1

	verifyEndLine = myASTParser.getLineNumberOfNode(verifyEqNode)
	if ( (verifyEndLine == None) or (type(verifyEndLine).__name__ != con.intTypePython) or (verifyEndLine < verifyStartLine) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned for ending line of " + con.verifyFuncName + " function.")

	indentationListVerifyLines = []
	verifyLines = getLinesFromSourceCodeWithinRange(copy.deepcopy(pythonCodeLines), verifyStartLine, verifyEndLine, indentationListVerifyLines)

	verifyFuncArgs = getFunctionArgsAsStrings(functionArgNames, con.verifyFuncName)
	if ( (verifyFuncArgs == None) or (type(verifyFuncArgs).__name__ != con.listTypePython) or (len(verifyFuncArgs) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getFunctionArgsAsStrings to get arguments of " + con.verifyFuncName + " function.")

	callListOfVerifyFuncs = []
	funcsVisitedSoFar = []
	linePairsOfVerifyFuncs = None
	buildCallListOfFunc(functionArgMappings, con.verifyFuncName, callListOfVerifyFuncs, funcsVisitedSoFar)

	if (con.initFuncName in functionNames):
		if (con.initFuncName not in callListOfVerifyFuncs):
			callListOfVerifyFuncs.append(con.initFuncName)

	callListOfInitFuncs = []
	funcsVisitedSoFar = []
	buildCallListOfFunc(functionArgMappings, con.initFuncName, callListOfInitFuncs, funcsVisitedSoFar)

	if (len(callListOfInitFuncs) > 0):
		for initCalledFunc in callListOfInitFuncs:
			if (initCalledFunc not in callListOfVerifyFuncs):
				callListOfVerifyFuncs.append(initCalledFunc)

	if (len(callListOfVerifyFuncs) > 0):
		linePairsOfVerifyFuncs = getFirstLastLineNosOfFuncList(callListOfVerifyFuncs, pythonCodeNode)
		if ( (linePairsOfVerifyFuncs == None) or (type(linePairsOfVerifyFuncs).__name__ != con.listTypePython) or (len(linePairsOfVerifyFuncs) == 0) ):
			sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getFirstLastLineNosOfFuncList.")

	lineNosPerVar = getLineNosPerVar(varAssignments)
	if ( (lineNosPerVar == None) or (type(lineNosPerVar).__name__ != con.dictTypePython) or (len(lineNosPerVar) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getLineNosPerVar.")


	var_varDependencies = getVar_VarDependencies(varAssignments, globalVars)
	if ( (var_varDependencies == None) or (type(var_varDependencies).__name__ != con.dictTypePython) or (len(var_varDependencies) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getVar_VarDependencies.")

	#addImportLines()
	#addCommonHeaderLines()

	#if (linePairsOfVerifyFuncs != None):
		#addFunctionsThatVerifyCalls()

	addTemplateLines()
	#addPrerequisites()

	#if (con.initFuncName in functionNames):
		#addCallToInit()

	lineInfo = getLineInfoFromSourceCodeLines(copy.deepcopy(pythonCodeLines), numSpacesPerTab)
	if ( (lineInfo == None) or (type(lineInfo).__name__ != con.dictTypePython) or (len(lineInfo) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  could not extract any line information from the source code Python lines of the cryptoscheme.")

	checkBlocks = myASTParser.getStartEndLineCheckBlocks(copy.deepcopy(pythonCodeLines), lineInfo, verifyStartLine, (verifyEndLine - 1), numTabsOnVerifyLine)

	codeGenRanges = getSectionRanges(copy.deepcopy(batchVerifierOutput), con.finalBatchEqString)

	processBatcherOutput()

	addSigLoop()
	#addGroupMembershipChecks()
	writeBodyOfInd()

	if ( (len(finalBatchEq) == 0) or (len(finalBatchEqWithLoops) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem locating the various forms of the final batch equation from the output of the batch verifier.")

	if (con.deltaDictName not in listVars):
		listVars[con.deltaDictName] = con.numSignaturesIndex

	cleanFinalBatchEq()
	getBatchEqVars()
	distillBatchEqVars()

	getLoopNamesOfFinalBatchEq()
	distillLoopsWRTNumSignatures()
	loopBlocksForCachedCalculations = buildLoopBlockList(loopsOuterNumSignatures)
	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem obtaining loop blocks used for cached calculations.")

	if (len(loopsOuterNotNumSignatures) != 0):
		loopBlocksForNonCachedCalculations = buildLoopBlockList(loopsOuterNotNumSignatures, loopsOuterNumSignatures)
		if ( (loopBlocksForNonCachedCalculations == None) or (type(loopBlocksForNonCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForNonCachedCalculations) == 0) ):
			sys.exit("AutoBatch_CodeGen->main:  problem obtaining loop blocks used for non-cached calculations.")
	else:
		loopBlocksForNonCachedCalculations = None

	writeDictDefsOfCachedCalcsForBatch()
	writeBodyOfCachedCalcsForBatch()
	writeCallToDCAndRetToBatch()

	writeCallToSortFunction()

	writeOpeningLinesToDCVerifySigsRecursiveFunc()
	if (loopBlocksForNonCachedCalculations != None):
		writeBodyOfNonCachedCalcsForDC()

	writeCachedCalcAssignmentsForDC()
	writeVerifyEqAndRecursionForDC()

	try:
		batchVerFile.close()
		individualVerFile.close()
		verifySigsFile.close()
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem attempting to run close() on the output files of this program.")

if __name__ == '__main__':
	main()
