import con, sys
from Value import Value

class BinOpValue:
	def __init__(self):
		self.lineNo = None
		self.left = None
		self.opType = None
		self.right = None

	def getType(self):
		return con.binOpTypeAST

	def getLineNo(self):
		return self.lineNo

	def getLeft(self):
		return self.left

	def getOpType(self):
		return self.opType

	def getRight(self):
		return self.right

	def getOpString(self):
		if (self.opType == con.addTypeAST):
			return "+"

		if (self.opType == con.divTypeAST):
			return "/"

		if (self.opType == con.expTypeAST):
			return "**"

		if (self.opType == con.multTypeAST):
			return "*"

		if (self.opType == con.subTypeAST):
			return "-"

		sys.exit("BinOpValue->getOpString:  self.opType is not one of the supported types.")

	def getStringVarName(self):
		if ( (self.left == None) or (self.opType == None) or (self.right == None) ):
			return None

		leftStringVarName = self.left.getStringVarName()
		if ( (leftStringVarName == None) or (type(leftStringVarName).__name__ != con.strTypePython) or (len(leftStringVarName) == 0) ):
			return None

		rightStringVarName = self.right.getStringVarName()
		if ( (rightStringVarName == None) or (type(rightStringVarName).__name__ != con.strTypePython) or (len(rightStringVarName) == 0) ):
			return None

		opString = self.getOpString()
		if ( (opString == None) or (type(opString).__name__ != con.strTypePython) or (len(opString) == 0) ):
			sys.exit("BinOpValue->getStringVarName:  problem with the value returned from getOpString.")

		return leftStringVarName + " " + opString + " " + rightStringVarName

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("BinOpValue->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo

	def setLeft(self, left):
		if (left == None):
			sys.exit("BinOpValue->setLeft:  left parameter passed in is of None type.")

		self.left = left

	def setOpType(self, opType):
		if (opType not in con.opTypesAST):
			sys.exit("BinOpValue->setOpType:  op type passed in is not one of the supported types.")

		self.opType = opType

	def setRight(self, right):
		if (right == None):
			sys.exit("BinOpValue->setRight:  right parameter passed in is of None type.")

		self.right = right

Value.register(BinOpValue)
