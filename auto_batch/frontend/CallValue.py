import con, sys
from Value import Value

class CallValue:
	def __init__(self):
		self.funcName = None
		self.attrName = None
		self.argList = None
		self.lineNo = None

	def getType(self):
		return con.callTypeAST

	def getFuncName(self):
		return self.funcName

	def getAttrName(self):
		return self.attrName

	def getArgList(self):
		return self.argList

	def getLineNo(self):
		return self.lineNo

	def setFuncName(self, funcName):
		if ( (funcName == None) or (type(funcName).__name__ != con.strTypePython) or (len(funcName) == 0) ):
			sys.exit("CallValue->setFuncName:  problem with the function name passed in.")

		self.funcName = funcName

	def setAttrName(self, attrName):
		if ( (attrName == None) or (type(attrName).__name__ != con.strTypePython) or (len(attrName) == 0) ):
			sys.exit("CallValue->setAttrName:  problem with the attribute name passed in.")

		self.attrName = attrName

	def setArgList(self, argList):
		if ( (argList == None) or (type(argList).__name__ != con.listTypePython) ):
			sys.exit("CallValue->setArgList:  problem with the argument list passed in.")

		self.argList = argList

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("CallValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("CallValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(CallValue)
