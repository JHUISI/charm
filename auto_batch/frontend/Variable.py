from abc import ABCMeta, abstractmethod

class Variable(metaclass=ABCMeta):
	@abstractmethod
	def getName(self):
		return

	@abstractmethod
	def getValue(self):
		return

	@abstractmethod
	def getType(self):
		return
