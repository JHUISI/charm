import con, sys
from Value import Value

class FloatValue:
	def __init__(self):
		self.value = None

	def getValue(self):
		return self.value

	def getType(self):
		return float

	def setValue(self, value):
		if (type(value) is not float):
			sys.exit("Value passed to FloatValue class is not of type " + con.floatTypePython)

		self.value = value

Value.register(FloatValue)
