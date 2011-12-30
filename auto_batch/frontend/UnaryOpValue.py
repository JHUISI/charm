import con, sys
from Value import Value

class UnaryOpValue:
	def __init__(self):
		self.lineNo = None
		self.operand = None
		self.opType = None

	def getType(self):
		return con.unaryOpTypeAST

	def getLineNo(self):
		return self.lineNo

	def getOperand(self):
		return self.operand

	def getOpType(self):
		return self.opType

	def getOpString(self):
		if (self.opType == uSubTypeAST):
			return "-"

		sys.exit("UnaryOpValue->getOpString:  self.opType is not one of the supported types.")

	def getStringVarName(self):
		if ( (self.operand == None) or (self.opType == None) ):
			return None

		operandStringVarName = self.operand.getStringVarName()
		if ( (operandStringVarName == None) or (type(operandStringVarName).__name__ != con.strTypePython) or (len(operandStringVarName) == 0) ):
			return None

		opString = self.getOpString()
		if ( (opString == None) or (type(opString).__name__ != con.strTypePython) or (len(opString) == 0) ):
			sys.exit("UnaryOpValue->getStringVarName:  problem with the value returned from getOpString.")

		return opString + operandStringVarName

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("UnaryOpValue->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo

	def setOperand(self, operand):
		if (operand == None):
			sys.exit("UnaryOpValue->setOperand:  operand parameter passed in is of None type.")

		self.operand = operand

	def setOpType(self, opType):
		if (opType not in con.unaryOpTypesAST):
			sys.exit("UnaryOpValue->setOpType:  op type passed in is not one of the supported types.")

		self.opType = opType

Value.register(UnaryOpValue)
