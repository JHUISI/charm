import con, sys
from Value import Value

class OperationValue:
	def __init__(self):
		self.lineNo = None
		self.operation = None

	def getType(self):
		return con.operationValue

	def getLineNo(self):
		return self.lineNo

	def getOperation(self):
		return self.operation

	def getStringVarName(self):
		if (self.operation == None):
			return None

		if (type(self.operation).__name__ != con.stringValue):
			sys.exit("OperationValue->getStringVarName:  self.operation is not of type " + con.stringValue)

		operationAsString = self.operation.getStringVarName()
		if ( (operationAsString == None) or (type(operationAsString).__name__ != con.strTypePython) or (len(operationAsString) == 0) ):
			sys.exit("OperationValue->getStringVarName:  problem with value returned from getStringVarName() call on self.operation.")

		if (operationAsString not in con.operationTypes):
			sys.exit("OperationValue->getStringVarName:  operation as string (" + operationAsString + ") is not one of the supported types (" + con.operationTypes + ").")

		return str(operationAsString)

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("OperationValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("OperationValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

	def setOperation(self, operation):
		if ( (operation == None) or (type(operation).__name__ != con.stringValue) ):
			sys.exit("OperationValue->setOperation:  problem with operation passed in.")

		operationAsString = operation.getStringVarName()
		if ( (operationAsString == None) or (type(operationAsString).__name__ != con.strTypePython) or (operationAsString not in con.operationTypes) ):
			sys.exit("OperationValue->setOperation:  problem with string representation of operation passed in.")

		self.operation = operation

Value.register(OperationValue)
