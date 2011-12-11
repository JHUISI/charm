import con, sys
from Name import Name

class StringName:
	def __init__(self):
		self.name = None

	def getName(self):
		return self.name

	def getType(self):
		return str

	def setName(self, name):
		if (type(name) is not str):
			sys.exit("Name passed to StringName class is not of type " + con.strTypePython)

		if (len(name) == 0):
			sys.exit("Name passed to StringName class is of length zero.")

		self.name = name

Name.register(StringName)
