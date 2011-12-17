class FunctionArgMap:
	def __init__(self):
		self.destFuncName = None
		self.argMap = {}
		self.lineNo = None

	def getDestFuncName(self):
		return self.destFuncName

	def getArgMap(self):
		return self.argMap

	def getLineNo(self):
		return self.lineNo

	def setDestFuncName(self, destFuncName):
		if ( (destFuncName == None) or (type(destFuncName).__name__ != con.strTypePython) or (len(destFuncName) == 0) ):
			sys.exit("FunctionArgMap->setDestFuncName:  problem with function named passed in.")

		self.destFuncName = destFuncName

	def setArgMap(self, argMap):
		if ( (argMap == None) or (type(argMap).__name__ != con.dictTypePython) or (len(argMap) == 0) ):
			sys.exit("FunctionArgMap->setArgMap:  problem with the arguments map passed in.")

		self.argMap = argMap

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("FunctionArgMap->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo
