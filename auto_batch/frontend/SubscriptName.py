import con, sys
from Name import Name

class SubscriptName:
	def __init__(self):
		self.lineNo = None

	def getType(self):
		return str

	def getLineNo(self):
		return self.lineNo

	def setName(self, name):
		if (type(name) is not str):
			sys.exit("Name passed to StringName class is not of type " + con.strTypePython)

		if (len(name) == 0):
			sys.exit("Name passed to StringName class is of length zero.")

		self.name = name

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("StringName->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("StringName->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Name.register(StringName)
