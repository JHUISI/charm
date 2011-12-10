import con, sys
from Value import Value

class IntegerValue:
	def __init__(self):
		self.value = None

	def getValue(self):
		return self.value

	def getType(self):
		return int

	def setValue(self, value):
		if (type(value) is not int):
			sys.exit("Value passed to IntegerValue class is not of type " + con.intTypePython)

		self.value = value

Value.register(IntegerValue)
