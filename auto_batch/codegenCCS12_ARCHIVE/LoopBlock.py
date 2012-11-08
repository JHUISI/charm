import con, sys
from Parser_CodeGen_Toolbox import *

class LoopBlock:
	def __init__(self):
		self.startValue = None
		self.indexVariable = None
		self.loopOverValue = None
		self.operation = None
		self.loopsWithVarsToCalculate = None
		self.loopsToCalculate = None
		self.childrenList = None
		self.parent = None
		self.loopOrder = None

	def getStartValue(self):
		return self.startValue

	def getIndexVariable(self):
		return self.indexVariable

	def getLoopOverValue(self):
		return self.loopOverValue

	def getOperation(self):
		return self.operation

	def getLoopsWithVarsToCalculate(self):
		return self.loopsWithVarsToCalculate

	def getLoopsToCalculate(self):
		return self.loopsToCalculate

	def getChildrenList(self):
		return self.childrenList

	def getParent(self):
		return self.parent

	def getLoopOrder(self):
		return self.loopOrder

	def getLoopOrderAsString(self):
		return getLoopOrderAsString(self.loopOrder)

	def setStartValue(self, startValue):
		if ( (startValue == None) or (type(startValue).__name__ != con.integerValue) ):
			sys.exit("LoopBlock->setStartValue:  problem with start value passed in.")

		valueAsInt = startValue.getValue()
		if ( (valueAsInt == None) or (type(valueAsInt).__name__ != con.intTypePython) or (valueAsInt < 0) ):
			sys.exit("LoopBlock->setStartValue:  problem with integer value of start value passed in.")

		self.startValue = startValue

	def setIndexVariable(self, indexVariable):
		if ( (indexVariable == None) or (type(indexVariable).__name__ != con.stringName) ):
			sys.exit("LoopBlock->setIndexVariable:  problem with index variable passed in.")

		indexVarAsString = indexVariable.getStringVarName()
		if ( (indexVarAsString == None) or (type(indexVarAsString).__name__ != con.strTypePython) or (indexVarAsString not in con.loopIndexTypes) ):
			sys.exit("LoopBlock->setIndexVariable:  problem with string version of index variable passed in.")

		self.indexVariable = indexVariable

	def setLoopOverValue(self, loopOverValue):
		if ( (loopOverValue == None) or (type(loopOverValue).__name__ != con.stringName) ):
			sys.exit("LoopBlock->setLoopOverValue:  problem with loop over value passed in.")

		loopOverValueAsStr = loopOverValue.getStringVarName()
		if ( (loopOverValueAsStr == None) or (type(loopOverValueAsStr).__name__ != con.strTypePython) or (loopOverValueAsStr not in con.loopTypes) ):
			sys.exit("LoopBlock->setLoopOverValue:  problem with string version of loop over value passed in.")

		self.loopOverValue = loopOverValue

	def setOperation(self, operation):
		if ( (operation == None) or (type(operation).__name__ != con.operationValue) ):
			sys.exit("LoopBlock->setOperation:  problem with operation parameter passed in.")

		operationAsString = operation.getStringVarName()
		if ( (operationAsString == None) or (type(operationAsString).__name__ != con.strTypePython) or (operationAsString not in con.operationTypes) ):
			sys.exit("LoopBlock->setOperation:  problem with string representation of operation parameter passed in.")

		self.operation = operation

	def setLoopsWithVarsToCalculate(self, loopList):
		if ( (loopList == None) or (type(loopList).__name__ != con.listTypePython) or (len(loopList) == 0) ):
			sys.exit("LoopBlock->setLoopsWithVarsToCalculate:  problem with the loopList parameter passed in.")

		for loop in loopList:
			if (type(loop).__name__ != con.stringName):
				sys.exit("LoopBlock->setLoopsWithVarsToCalculate:  one of the loops in the loop list passed in is not of type " + con.stringName)

		if (areAllLoopNamesValid(loopList) == False):
			sys.exit("LoopBlock->setLoopsWithVarsToCalculate:  one of the loop names in the loop list passed in is not valid.")

		self.loopsWithVarsToCalculate = loopList

	def setLoopsToCalculate(self, loopList):
		if ( (loopList == None) or (type(loopList).__name__ != con.listTypePython) or (len(loopList) == 0) ):
			sys.exit("LoopBlock->setLoopsToCalculate:  problem with the loop list passed in.")

		for loop in loopList:
			if (type(loop).__name__ != con.stringName):
				sys.exit("LoopBlock->setLoopsToCalculate:  one of the loops in the loop list passed in is not of type " + con.stringName)

		if (areAllLoopNamesValid(loopList) == False):
			sys.exit("LoopBlock->setLoopsToCalculate:  one of the loopNames in the loop list passed in is not valid.")

		self.loopsToCalculate = loopList

	def setChildrenList(self, childrenList):
		if ( (childrenList == None) or (type(childrenList).__name__ != con.listTypePython) or (len(childrenList) == 0) ):
			sys.exit("LoopBlock->setChildrenList:  problem with children list passed in.")

		for child in childrenList:
			if (type(child).__name__ != con.loopBlock):
				sys.exit("LoopBlock->setChildrenList:  one of the children passed in is not of type " + con.loopBlock)

		self.childrenList = childrenList

	def setParent(self, parent):
		if ( (parent == None) or (type(parent).__name__ != con.loopBlock) ):
			sys.exit("LoopBlock->setParent:  problem with parent parameter passed in.")

		self.parent = parent

	def setLoopOrder(self, loopOrder):
		if (checkLoopOrder(loopOrder) == False):
			sys.exit("LoopBlock->setLoopOrder:  loop order passed in failed call to checkLoopOrder.")

		self.loopOrder = loopOrder
