import con
from Variable import Variable

class IntegerVariable:
	def __init__(self, name, value):
		if (type(name) is not str):
			self.exit("Name variable passed to IntegerVariable class is not of type " + con.strType)

		if (len(name) == 0):
			self.exit("Name variable passed to IntegerVariable class is of length zero.")

		if (type(value) is not int):
			self.exit("Value variable passed to IntegerVariable class is not of type " + con.intType)

		self.name = name
		self.value = value

	def getName(self):
		return self.name

	def getValue(self):
		return self.value

	def getType(self):
		return int

Variable.register(IntegerVariable)
