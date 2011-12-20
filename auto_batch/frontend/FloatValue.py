import con, sys
from Value import Value

class FloatValue:
	def __init__(self):
		self.value = None
		self.lineNo = None

	def getValue(self):
		return self.value

	def getType(self):
		return float

	def getLineNo(self):
		return self.lineNo

	def setValue(self, value):
		if (type(value) is not float):
			sys.exit("Value passed to FloatValue class is not of type " + con.floatTypePython)

		self.value = value

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("Line number passed to FloatValue class (setLineNo method) is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("Line number passed to FloatValue class (setLineNo method) is less than one.")

		self.lineNo = lineNo

Value.register(FloatValue)
