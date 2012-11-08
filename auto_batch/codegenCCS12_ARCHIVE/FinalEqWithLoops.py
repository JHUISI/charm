import con, sys

class FinalEqWithLoops:
	def __init__(self):
		self.equation = None
		self.codeGenSegmentNo = None
		self.hasMultipleEqChecks = None
		self.indexVariable = None
		self.startValue = None
		self.loopOverValue = None

	def getEquation(self):
		return self.equation

	def getCodeGenSegmentNo(self):
		return self.codeGenSegmentNo

	def getHasMultipleEqChecks(self):
		return self.hasMultipleEqChecks

	def getIndexVariable(self):
		return self.indexVariable

	def getStartValue(self):
		return self.startValue

	def getLoopOverValue(self):
		return self.loopOverValue

	def setEquation(self, equation):
		self.equation = equation

	def setCodeGenSegmentNo(self, codeGenSegmentNo):
		self.codeGenSegmentNo = codeGenSegmentNo

	def setHasMultipleEqChecks(self, hasMultipleEqChecks):
		self.hasMultipleEqChecks = hasMultipleEqChecks

	def setIndexVariable(self, indexVariable):
		self.indexVariable = indexVariable

	def setStartValue(self, startValue):
		self.startValue = startValue

	def setLoopOverValue(self, loopOverValue):
		self.loopOverValue = loopOverValue
