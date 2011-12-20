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
