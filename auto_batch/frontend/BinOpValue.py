import con, sys
from Value import Value

class BinOpValue:
	def __init__(self):
		self.lineNo = None
		self.left = None
		self.op = None
		self.right = None

	def getType(self):
		return con.binOpTypeAST

	def getLineNo(self):
		return self.lineNo

	def getLeft(self):
		return self.left

	def getOp(self):
		return self.op

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

	def setOp(self, op):
		if ( (op == None) or (type(op).__name__ not in con.opTypesAST) ):
			sys.exit("BinOpValue->setOp:  problem with op parameter passed in.")

		self.op = op

	def setRight(self, right):
		if (right == None):
			sys.exit("BinOpValue->setRight:  right parameter passed in is of None type.")

		self.right = right

Value.register(BinOpValue)
