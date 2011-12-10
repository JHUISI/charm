import con, sys
from Value import Value

class StringValue:
	def __init__(self):
		self.value = None

	def getValue(self):
		return self.value

	def getType(self):
		return str

	def setValue(self, value):
		if (type(value) is not str):
			sys.exit("Value passed to StringValue class is not of type " + con.strTypePython)

		if (len(value) == 0):
			sys.exit("Value passed to StringValue class is of length zero.")

		self.value = value

Value.register(StringValue)
