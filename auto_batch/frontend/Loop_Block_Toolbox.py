import con, sys
from Parser_CodeGen_Toolbox import *
from LoopBlock import LoopBlock

def buildLoopBlockList(loopList, loopListCachedLoops=None):
	if (areAllLoopNamesValid(loopList) == False):
		sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  one of the loop names in the loop list passed in is not valid.")

	if (loopListCachedLoops != None):
		cachedLoopNames = getLoopNamesAsStringsFromLoopList(loopListCachedLoops)
		if ( (cachedLoopNames == None) or (type(cachedLoopNames).__name__ != con.listTypePython) or (len(cachedLoopNames) == 0) ):
			sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  could not obtain the loop names of the cached loops in the loopListCachedLoops parameter passed in.")
	else:
		cachedLoopNames = None

	abbrLoopDict = buildAbbreviatedLoopDict(loopList)
	if ( (abbrLoopDict == None) or (type(abbrLoopDict).__name__ != con.dictTypePython) or (len(abbrLoopDict) == 0) ):
		sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  problem with return value from buildAbbreviatedLoopDict.")

	blocksMadeSoFar = []

	for loop in loopList:
		childLoopList = getChildrenLoopsOfLoop(loop)
		if (childLoopList != None):
			continue

		existingBlockList = isSingleBlockInCurrentList(loop, blocksMadeSoFar)
		if (existingBlockList == None):
			blocksMadeSoFar.append(createNewLoopBlock(loop, [loop.getLoopName()], None, None))
			del abbrLoopDict[loop.getLoopName().getStringVarName()]
		elif (len(existingBlockList) == 1):
			appendLoopToLoopBlock(existingBlockList[0], [loop.getLoopName()], None)
			del abbrLoopDict[loop.getLoopName().getStringVarName()]
		else:
			sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  error in logic when assigning blocks for loops that have no children.")

	if (len(abbrLoopDict) == 0):
		return blocksMadeSoFar

	while (len(abbrLoopDict) != 0):
		abbrLoopDictKeysList = list(abbrLoopDict.keys())
		for loopKeyName in abbrLoopDictKeysList:
			currentLoop = getLoopInfoObjFromLoopName(loopList, loopKeyName)
			if ( (currentLoop == None) or (type(currentLoop).__name__ != con.loopInfo) ):
				sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  problem with value returned from getLoopInfoObjFromLoopName function to get current loopInfo object.")

			childLoopList = getChildrenLoopsOfLoop(currentLoop)
			if (childLoopList == None):
				sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  extracted child-less loop in the iteration that handles only loops with children.")

			childBlockDict = getChildBlockDict(childLoopList, blocksMadeSoFar)
			if (childBlockDict == None):
				continue

			if (type(childBlockDict).__name__ != con.dictTypePython):
				sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  value returned from getChildBlockDict is not of type " + con.dictTypePython)

			buildChildBlocksForCachedLoops(childBlockDict, loopListCachedLoops, blocksMadeSoFar)

			childBlockList = []

			for childBlockIndex in childBlockDict:
				currentChildBlock = childBlockDict[childBlockIndex]

				if ( (currentChildBlock == None) or (currentChildBlock not in blocksMadeSoFar) ):
					sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  failed to create new blocks for all of the cached loops.")

				if (currentChildBlock not in childBlockList):
					childBlockList.append(currentChildBlock)

			mutualParentBlock = doesParentBlockAlreadyExist(childBlockList)
			if (mutualParentBlock == None):
				blocksMadeSoFar.append(createNewLoopBlock(currentLoop, [currentLoop.getLoopName()], None, childBlockList))
				del abbrLoopDict[loopKeyName]
			else:
				isMutualParentSameLoop = areLoopingParamsOfBlockAndLoopEqual(mutualParentBlock, currentLoop)
				if (isMutualParentSameLoop == False):
					sys.exit("Loop_Block_Toolbox->buildLoopBlockList:  found two loops that share the same children, but do not have the same looping parameters.  This is not currently supported.")
				appendLoopToLoopBlock(mutualParentBlock, [currentLoop.getLoopName()], None)
				del abbrLoopDict[loopKeyName]

	topLevelBlocks = []

	for blockMade in blocksMadeSoFar:
		if (blockMade.getParent() == None):
			topLevelBlocks.append(blockMade)

	return topLevelBlocks

def buildChildBlocksForCachedLoops(childBlockDict, loopListCachedLoops, blocksMadeSoFar):
	if ( (childBlockDict == None) or (type(childBlockDict).__name__ != con.dictTypePython) or (len(childBlockDict) == 0) ):
		sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with child block dictionary passed in.")

	if ( (loopListCachedLoops == None) or (type(loopListCachedLoops).__name__ != con.listTypePython) or (len(loopListCachedLoops) == 0) ):
		sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with loop list of cached loops passed in.")

	if ( (blocksMadeSoFar == None) or (type(blocksMadeSoFar).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with blocks made so far parameter passed in.")

	for childLoopName in childBlockDict:
		if ( (childLoopName == None) or (type(childLoopName).__name__ != con.strTypePython) or (isStringALoopName(childLoopName) == False) ):
			sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with one of the child loop names in the child block dictionary passed in.")

		currentChildBlock = childBlockDict[childLoopName]
		if (currentChildBlock != None):
			continue

		loopInfoObjOfNewBlock = getLoopInfoObjFromLoopName(loopListCachedLoops, childLoopName)
		if ( (loopInfoObjOfNewBlock == None) or (type(loopInfoObjOfNewBlock).__name__ != con.loopInfo) ):
			sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with return value from getLoopInfoObjFromLoopName.")

		newChildBlockForCachedLoop = createNewLoopBlock(loopInfoObjOfNewBlock, None, [loopInfoObjOfNewBlock.getLoopName()], None)
		if ( (newChildBlockForCachedLoop == None) or (type(newChildBlockForCachedLoop).__name__ != con.loopBlock) ): 
			sys.exit("Loop_Block_Toolbox->buildChildBlocksForCachedLoops:  problem with return value of createNewLoopBlock.")

		childBlockDict[childLoopName] = newChildBlockForCachedLoop

		blocksMadeSoFar.append(newChildBlockForCachedLoop)

def areLoopingParamsOfBlockAndLoopEqual(block, loop):
	if ( (block == None) or (type(block).__name__ != con.loopBlock) ):
		sys.exit("Loop_Block_Toolbox->areLoopingParamsOfBlockAndLoopEqual:  problem with block parameter passed in.")

	if ( (loop == None) or (type(loop).__name__ != con.loopInfo) ):
		sys.exit("Loop_Block_Toolbox->areLoopingParamsOfBlockAndLoopEqual:  problem with loop parameter passed in.")

	if (block.getStartValue().getValue() != loop.getStartValue().getValue() ):
		return False

	if (block.getIndexVariable().getStringVarName() != loop.getIndexVariable().getStringVarName() ):
		return False

	if (block.getLoopOverValue().getStringVarName() != loop.getLoopOverValue().getStringVarName() ):
		return False

	if (block.getOperation().getStringVarName() != loop.getOperation().getStringVarName() ):
		return False

	return True

def doesParentBlockAlreadyExist(childBlockList):
	if ( (childBlockList == None) or (type(childBlockList).__name__ != con.listTypePython) or (len(childBlockList) == 0) ):
		sys.exit("Loop_Block_Toolbox->doesParentBlockAlreadyExist:  problem with child block list passed in.")

	mutualParent = None

	for childBlock in childBlockList:
		if ( (childBlock == None) or (type(childBlock).__name__ != con.loopBlock) ):
			sys.exit("Loop_Block_Toolbox->doesParentBlockAlreadyExist:  problem with one of the child blocks in the child block list passed in.")

		possibleMutualParent = childBlock.getParent()
		if (possibleMutualParent == None):
			return None

		if (mutualParent == None):
			mutualParent = possibleMutualParent
		else:
			if (mutualParent != possibleMutualParent):
				return None

	return mutualParent

def getChildBlockDict(childLoopList, blocksMadeSoFar):
	if ( (childLoopList == None) or (type(childLoopList).__name__ != con.listTypePython) or (len(childLoopList) == 0) ):
		sys.exit("Loop_Block_Toolbox->getChildBlockDict:  problem with child loop list parameter passed in.")

	if ( (blocksMadeSoFar == None) or (type(blocksMadeSoFar).__name__ != con.listTypePython) or (len(blocksMadeSoFar) == 0) ):
		sys.exit("Loop_Block_Toolbox->getChildBlockDict:  problem with blocks made so far parameter passed in.")

	childBlocksReturnDict = {}
	foundAtLeastOneBlock = False

	for childLoop in childLoopList:
		if ( (childLoop == None) or (type(childLoop).__name__ != con.strTypePython) or (isStringALoopName(childLoop) == False) ):
			sys.exit("Loop_Block_Toolbox->getChildBlockDict:  problem with one of the loops in the child loop list parameter passed in.")

		childBlock = getBlockThatCalculatesThisLoop(childLoop, blocksMadeSoFar)
		if (childBlock != None):
			if (type(childBlock).__name__ != con.loopBlock):
				sys.exit("Loop_Block_Toolbox->getChildBlockDict:  problem with value returned from getBlockThatCalculatesThisLoop.")
			foundAtLeastOneBlock = True

		childBlocksReturnDict[childLoop] = childBlock

	if (foundAtLeastOneBlock == True):
		return childBlocksReturnDict
	else:
		return None

def getBlockThatCalculatesThisLoop(loopName, blocksMadeSoFar):
	if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (isStringALoopName(loopName) == False) ):
		sys.exit("Loop_Block_Toolbox->getBlockThatCalculatesThisLoop:  problem with loop name passed in.")

	if ( (blocksMadeSoFar == None) or (type(blocksMadeSoFar).__name__ != con.listTypePython) or (len(blocksMadeSoFar) == 0) ):
		sys.exit("Loop_Block_Toolbox->getBlockThatCalculatesThisLoop:  problem with blocks made so far parameter passed in.")

	retBlock = None

	for block in blocksMadeSoFar:
		foundInLoopsWithVarsToCalc = searchForLoopNameInLoopList(loopName, block.getLoopsWithVarsToCalculate())
		foundInLoopsToCalc = searchForLoopNameInLoopList(loopName, block.getLoopsToCalculate())
		if ( (foundInLoopsWithVarsToCalc == True) and (foundInLoopsToCalc == True) ):
			sys.exit("Loop_Block_Toolbox->getBlockThatCalculatesThisLoop:  found block that has the loop name in both lists of loops to calculate (duplicate).")
		if ( (foundInLoopsWithVarsToCalc == True) or (foundInLoopsToCalc == True) ):
			if (retBlock != None):
				sys.exit("Loop_Block_Toolbox->getBlockThatCalculatesThisLoop:  found loop name in more than one block.")
			retBlock = block

	return retBlock

def createNewLoopBlock(loop, loopsWithVarsToCalculate, loopsToCalculate, childBlockList):
	if ( (loop == None) or (type(loop).__name__ != con.loopInfo) ):
		sys.exit("Loop_Block_Toolbox->createNewLoopBlock:  problem with loop parameter passed in.")

	if ( (loopsWithVarsToCalculate != None) and (type(loopsWithVarsToCalculate).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->createNewLoopBlock:  problem with loopsWithVarsToCalculate parameter passed in.")

	if ( (loopsToCalculate != None) and (type(loopsToCalculate).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->createNewLoopBlock:  problem with loopsToCalculate parameter passed in.")

	if ( (childBlockList != None) and (type(childBlockList).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->createNewLoopBlock:  problem with child block list parameter passed in.")

	returnLoopBlock = LoopBlock()
	returnLoopBlock.setStartValue(copy.deepcopy(loop.getStartValue()))
	returnLoopBlock.setIndexVariable(copy.deepcopy(loop.getIndexVariable()))
	returnLoopBlock.setLoopOverValue(copy.deepcopy(loop.getLoopOverValue()))
	returnLoopBlock.setOperation(copy.deepcopy(loop.getOperation()))
	returnLoopBlock.setLoopOrder(copy.deepcopy(loop.getLoopOrder()))

	if (loopsWithVarsToCalculate != None):
		returnLoopBlock.setLoopsWithVarsToCalculate(copy.deepcopy(loopsWithVarsToCalculate))

	if (loopsToCalculate != None):
		returnLoopBlock.setLoopsToCalculate(copy.deepcopy(loopsToCalculate))

	if (childBlockList != None):
		returnLoopBlock.setChildrenList(childBlockList)
		for childBlock in childBlockList:
			childBlock.setParent(returnLoopBlock)

	return returnLoopBlock

def appendLoopToLoopBlock(loopBlock, loopsWithVarsToCalculate, loopsToCalculate):
	if ( (loopBlock == None) or (type(loopBlock).__name__ != con.loopBlock) ):
		sys.exit("Loop_Block_Toolbox->appendLoopToLoopBlock:  problem with loop block passed in.")

	if ( (loopsWithVarsToCalculate != None) and (type(loopsWithVarsToCalculate).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->appendLoopToLoopBlock:  problem with loopsWithVarsToCalculate parameter passed in.")

	if ( (loopsToCalculate != None) and (type(loopsToCalculate).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->appendLoopToLoopBlock:  problem with loopsToCalculate parameter passed in.")

	if (loopsWithVarsToCalculate != None):
		currentLoops = loopBlock.getLoopsWithVarsToCalculate()
		for newLoop in loopsWithVarsToCalculate:
			currentLoops.append(copy.deepcopy(newLoop))
		loopBlock.setLoopsWithVarsToCalculate(currentLoops)

	if (loopsToCalculate != None):
		currentLoops = loopBlock.getLoopsToCalculate()
		for newLoop in loopsToCalculate:
			currentLoops.append(copy.deepcopy(newLoop))
		loopBlock.setLoopsToCalculate(currentLoops)

def isSingleBlockInCurrentList(loop, blocksMadeSoFar):
	if ( (loop == None) or (type(loop).__name__ != con.loopInfo) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop parameter passed in.")

	loopStartValue = loop.getStartValue().getValue()
	loopOverValue = loop.getLoopOverValue().getStringVarName()
	loopOperation = loop.getOperation().getStringVarName()
	loopOrderAsString = loop.getLoopOrderAsString()

	if ( (loopStartValue == None) or (type(loopStartValue).__name__ != con.intTypePython) or (loopStartValue < 0) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop start value obtained from loop parameter passed in.")

	if ( (loopOverValue == None) or (type(loopOverValue).__name__ != con.strTypePython) or (loopOverValue not in con.loopTypes) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop over value obtained from loop parameter passed in.")

	if ( (loopOperation == None) or (type(loopOperation).__name__ != con.strTypePython) or (loopOperation not in con.operationTypes) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop operation obtained from loop parameter passed in.")

	if ( (loopOrderAsString == None) or (type(loopOrderAsString).__name__ != con.strTypePython) or (len(loopOrderAsString) == 0) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop order as string obtained from loop parameter passed in.")

	if ( (blocksMadeSoFar == None) or (type(blocksMadeSoFar).__name__ != con.listTypePython) ):
		sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with blocks made so far parameter sent in.")

	if (len(blocksMadeSoFar) == 0):
		return None

	retBlocks = []

	for indBlock in blocksMadeSoFar:
		if ( (indBlock == None) or (type(indBlock).__name__ != con.loopBlock) ):
			sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with one of the blocks in the blocks made so far parameter passed in.")

		currStartVal = indBlock.getStartValue().getValue()
		if ( (currStartVal == None) or (type(currStartVal).__name__ != con.intTypePython) or (currStartVal < 0) ):
			sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with one of the start values extracted from the block list passed in.")

		currLoopOverVal = indBlock.getLoopOverValue().getStringVarName()
		if ( (currLoopOverVal == None) or (type(currLoopOverVal).__name__ != con.strTypePython) or (currLoopOverVal not in con.loopTypes) ):
			sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop over value extracted for one of the blocks in the block list passed in.")

		currOperation = indBlock.getOperation().getStringVarName()
		if ( (currOperation == None) or (type(currOperation).__name__ != con.strTypePython) or (currOperation not in con.operationTypes) ):
			sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with operation value extracted for one of the blocks in the block list passed in.")

		currLoopOrderAsString = indBlock.getLoopOrderAsString()
		if ( (currLoopOrderAsString == None) or (type(currLoopOrderAsString).__name__ != con.strTypePython) or (len(currLoopOrderAsString) == 0) ):
			sys.exit("Loop_Block_Toolbox->isSingleBlockInCurrentList:  problem with loop order as string obtained from current block in blocks made so far parameter passed in.")

		if ( (currStartVal == loopStartValue) and (currLoopOverVal == loopOverValue) and (currOperation == loopOperation) and (currLoopOrderAsString == loopOrderAsString) ):
			retBlocks.append(indBlock)

	if (len(retBlocks) == 0):
		return None

	return retBlocks

def areAllChildrenInBlocksMadeSoFar(childLoopList, blocksMadeSoFar):
	if ( (childLoopList == None) or (type(childLoopList).__name__ != con.listTypePython) or (len(childLoopList) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->areAllChildrenInBlocksMadeSoFar:  problem with child loop list passed in.")

	if ( (blocksMadeSoFar == None) or (type(blocksMadeSoFar).__name__ != con.listTypePython) or (len(blocksMadeSoFar) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->areAllChildrenInBlocksMadeSoFar:  problem with blocks made so far list passed in.")

	for child in childLoopList:
		if ( (child == None) or (type(child).__name__ != con.strTypePython) or (isStringALoopName(child) == False) ):
			sys.exit("Parser_CodeGen_Toolbox->areAllChildrenInBlocksMadeSoFar:  problem with one of the child loop names in the child loop list passed in.")

		retVal = False

		for block in blocksMadeSoFar:
			if ( (block == None) or (type(block).__name__ != con.loopBlock) ):
				sys.exit("Parser_CodeGen_Toolbox->areAllChildrenInBlocksMadeSoFar:  problem with one of the blocks in the blocks made so far list passed in.")

			varsCalculatedInThisBlock = block.getLoopsWithVarsToCalculate()
