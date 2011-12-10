from abc import ABCMeta, abstractmethod

class Value(metaclass=ABCMeta):
	@abstractmethod
	def getType(self):
		return
