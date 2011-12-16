import con, sys
from Value import Value

class DictValue:
	def __init__(self):
		self.keys = None
		self.values = None
		self.lineNo = None

	def getKeys(self):
		return self.keys

	def getValues(self):
		return self.values

	def getType(self):
		return con.dictTypePython

	def getLineNo(self):
		return self.lineNo

	def setKeys(self, keys):
		if ( (keys == None) or (type(keys).__name__ != con.listTypePython) ):
			sys.exit("DictValue->setKeys:  problem with input passed in to the function.")

		self.keys = keys

	def setValues(self, values):
		if ( (values == None) or (type(values).__name__ != con.listTypePython) ):
			sys.exit("DictValue->setValues:  problem with input passed in to the function.")

		self.values = values

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("DictValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("DictValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(DictValue)
