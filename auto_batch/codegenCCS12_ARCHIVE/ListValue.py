import con, sys
from Value import Value

class ListValue:
	def __init__(self):
		self.argList = None
		self.lineNo = None

	def getArgList(self):
		return self.argList

	def getType(self):
		return con.listValue

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		retString = ""
		retString += "["

		for arg in self.argList:
			retString += arg.getStringVarName()
			retString += ", "

		lenRetString = len(retString)
		retString = retString[0:(lenRetString - 2)]

		retString += "]"

		return retString

	def setArgList(self, argList):
		self.argList = argList

	def setLineNo(self, lineNo):
		self.lineNo = lineNo

Value.register(ListValue)
