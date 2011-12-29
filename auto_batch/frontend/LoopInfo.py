import con, sys
from Parser_CodeGen_Toolbox import *

class LoopInfo:
	def __init__(self):
		self.loopName = None
		self.indexVariable = None
		self.startValue = None
		self.loopOverValue = None
		self.operation = None
		self.varListNoSubscripts = None
		self.varListWithSubscripts = None
		self.loopOrder = None
		self.expression = None
		self.groupType = None

	def getLoopName(self):
		return self.loopName

	def getIndexVariable(self):
		return self.indexVariable

	def getStartValue(self):
		return self.startValue

	def getLoopOverValue(self):
		return self.loopOverValue

	def getOperation(self):
		return self.operation

	def getVarListNoSubscripts(self):
		return self.varListNoSubscripts

	def getVarListWithSubscripts(self):
		return self.varListWithSubscripts

	def getLoopOrder(self):
		return self.loopOrder

	def getLoopOrderAsString(self):
		return getLoopOrderAsString(self.loopOrder)

	def getExpression(self):
		return self.expression

	def getGroupType(self):
		return self.groupType

	def setLoopName(self, loopNameStringName):
		if ( (loopNameStringName == None) or (type(loopNameStringName).__name__ != con.stringName) ):
			sys.exit("LoopInfo->setLoopName:  problem with loop name parameter passed in.")

		loopName = loopNameStringName.getStringVarName()

		if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (len(loopName) == 0) ):
			sys.exit("LoopInfo->setLoopName:  problem with the string obtained from getStringVarName on the loop name StringName object passed in.")

		isValidLoopName = isStringALoopName(loopName)

		if (isValidLoopName == False):
			sys.exit("LoopInfo->setLoopName:  loop name passed in (" + loopName + ") is not one of the supported loop types (" + con.loopPrefixes + ").")
 
		self.loopName = loopNameStringName

	def setIndexVariable(self, indexVariable):
		if ( (indexVariable == None) or (type(indexVariable).__name__ != con.stringName) ):
			sys.exit("LoopInfo->setIndexVariable:  problem with indexVariable passed in.")

		self.indexVariable = indexVariable

	def setStartValue(self, startValue):
		if ( (startValue == None) or (type(startValue).__name__ != con.integerValue) ):
			sys.exit("LoopInfo->setStartValue:  problem with start value passed in.")

		startValueInt = startValue.getValue()
		if (startValueInt < 0):
			sys.exit("LoopInfo->setStartValue:  integer version of start value passed in is less than zero.")

		self.startValue = startValue

	def setLoopOverValue(self, loopOverValue):
		if ( (loopOverValue == None) or (type(loopOverValue).__name__ != con.stringName) ):
			sys.exit("LoopInfo->setLoopOverValue:  problem with loop over value passed in.")

		loopOverValueString = loopOverValue.getStringVarName()
		if ( (loopOverValueString == None) or (type(loopOverValueString).__name__ != con.strTypePython) ):
			sys.exit("LoopInfo->setLoopOverValue:  problem with string version of loop over value passed in.")

		if (loopOverValueString not in con.loopTypes):
			sys.exit("LoopInfo->setLoopOverValue:  loop over value passed in (" + loopOverValueString + ") is not one of the supported loop types (" + con.loopTypes + ").")

		self.loopOverValue = loopOverValue

	def setOperation(self, operation):
		if ( (operation == None) or (type(operation).__name__ != con.operationValue) ):
			sys.exit("LoopInfo->setOperation:  problem with operation parameter passed in.")

		operationAsString = operation.getStringVarName()
		if ( (operationAsString == None) or (type(operationAsString).__name__ != con.strTypePython) or (operationAsString not in con.operationTypes) ):
			sys.exit("LoopInfo->setOperation:  problem with string representation of operation parameter passed in.")

		self.operation = operation

	def setVarListNoSubscripts(self, list):
		if ( (list == None) or (type(list).__name__ != con.listTypePython) or (len(list) == 0) ):
			sys.exit("LoopInfo->setVarListNoSubscripts:  problem with variable list passed in.")

		for varName in list:
			if (type(varName).__name__ != con.stringName):
				sys.exit("LoopInfo->setVarListNoSubscripts:  one of the variable names in the list passed in is not of type " + con.stringName)

			varNameAsString = varName.getStringVarName()
			if (varNameAsString.find(con.loopIndicator) != -1):
				sys.exit("LoopInfo->setVarListNoSubscripts:  one of the variable names (" + varNameAsString + ") has the subscript character in it (" + con.loopIndicator + ").")

		self.varListNoSubscripts = list

	def setVarListWithSubscripts(self, list):
		if ( (list == None) or (type(list).__name__ != con.listTypePython) or (len(list) == 0) ):
			sys.exit("LoopInfo->setVarListWithSubscripts:  problem with variable list passed in.")

		for varName in list:
			if (type(varName).__name__ != con.stringName):
				sys.exit("LoopInfo->setVarListWithSubscripts:  one of the variable names in the list passed in is not of type " + con.stringName)

		self.varListWithSubscripts = list

	def setLoopOrder(self, loopOrder):
		if (checkLoopOrder(loopOrder) == False):
			sys.exit("LoopInfo->setExpression:  loop order passed in failed the call to checkLoopOrder.")

		self.loopOrder = loopOrder

	def setExpression(self, expression):
		if ( (expression == None) or (type(expression).__name__ != con.strTypePython) or (len(expression) == 0) ):
			sys.exit("LoopInfo->setExpression:  problem with expression passed in.")

		self.expression = expression

	def setGroupType(self, groupType):
		if ( (groupType == None) or (type(groupType).__name__ != con.stringName) or (groupType.getStringVarName() not in con.groupTypes) ):
			sys.exit("LoopInfo->setGroupType:  problem with group type parameter passed in.")

		self.groupType = groupType
