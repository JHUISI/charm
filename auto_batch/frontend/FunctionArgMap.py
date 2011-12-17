import con, sys

class FunctionArgMap:
	def __init__(self):
		self.destFuncName = None
		self.callerArgsList = None
		self.destArgsList = None
		self.lineNo = None

	def getDestFuncName(self):
		return self.destFuncName

	def getCallerArgsList(self):
		return self.callerArgsList

	def getDestArgsList(self):
		return self.destArgsList

	def getLineNo(self):
		return self.lineNo

	def setDestFuncName(self, destFuncName):
		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.strTypePython) or (len(destFuncName) == 0) ):
			sys.exit("FunctionArgMap->setDestFuncName:  problem with function named passed in.")

		self.destFuncName = destFuncName

	def setCallerArgsList(self, callerArgsList):
		if ( (callerArgsList == None) or (type(callerArgsList).__name__ != con.listTypePython) or (len(callerArgsList) == 0) ):
			sys.exit("FunctionArgMap->setCallerArgsList:  problem with the caller arguments list passed in.")

		self.callerArgsList = callerArgsList

	def setDestArgsList(self, destArgsList):
		if ( (destArgsList == None) or (type(destArgsList).__name__ != con.listTypePython) or (len(destArgsList) == 0) ):
			sys.exit("FunctionArgMap->setDestArgsList:  problem with the destination arguments list passed in.")

		self.destArgsList = destArgsList

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("FunctionArgMap->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo
