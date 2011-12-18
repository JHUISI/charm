import con, sys

class FunctionArgMap:
	def __init__(self):
		self.destFuncName = None
		self.callerArgList = None
		self.destArgList = None
		self.lineNo = None

	def getDestFuncName(self):
		return self.destFuncName

	def getCallerArgList(self):
		return self.callerArgList

	def getDestArgList(self):
		return self.destArgList

	def getLineNo(self):
		return self.lineNo

	def setDestFuncName(self, destFuncName):
		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.strTypePython) or (len(destFuncName) == 0) ):
			sys.exit("FunctionArgMap->setDestFuncName:  problem with function named passed in.")

		self.destFuncName = destFuncName

	def setCallerArgList(self, callerArgList):
		if ( (callerArgList == None) or (type(callerArgList).__name__ != con.listTypePython) or (len(callerArgList) == 0) ):
			sys.exit("FunctionArgMap->setCallerArgList:  problem with the caller arguments list passed in.")

		self.callerArgList = callerArgList

	def setDestArgList(self, destArgList):
		if ( (destArgList == None) or (type(destArgList).__name__ != con.listTypePython) or (len(destArgList) == 0) ):
			sys.exit("FunctionArgMap->setDestArgList:  problem with the destination arguments list passed in.")

		self.destArgList = destArgList

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("FunctionArgMap->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo
