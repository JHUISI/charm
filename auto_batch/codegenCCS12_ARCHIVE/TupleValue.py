import con, sys
from Value import Value

class TupleValue:
	def __init__(self):
		self.tupleList = None
		self.lineNo = None

	def getTupleList(self):
		return self.tupleList

	def getType(self):
		return con.tupleValue

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		retString = ""
		retString += "("

		for tupleArg in self.tupleList:
			retString += tupleArg.getStringVarName()
			retString += ", "

		lenRetString = len(retString)
		retString = retString[0:(lenRetString - 2)]

		retString += ")"

		return retString

	def setTupleList(self, tupleList):
		self.tupleList = tupleList

	def setLineNo(self, lineNo):
		self.lineNo = lineNo

Value.register(TupleValue)
