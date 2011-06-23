from enum import *
import string

''' Operators in Batch language: 
EXP - '^' for exponent
EQ - ':=' for assignment
EQ_TST - '==' for equality testing
PAIR - 'e(' arg1, arg2 ')'
CONST - 'constant' declarator?
VARIABLE - 'variable' declarator?


AST simple rules

'''
types = Enum('G1', 'G2', 'GT', 'ZR', 'str')
declarator = Enum('constants', 'verify')
ops = Enum('BEGIN', 'MUL', 'EXP', 'EQ', 'EQ_TST', 'PAIR', 'ATTR', 'END')
debug = False	

class BinaryNode:
	def __init__(self, value, left=None, right=None):		
		if(isinstance(value, str)):
			self.type = ops.ATTR
			self.attribute = string.upper(value)
		elif value > ops.BEGIN and value < ops.END:
			self.type = value
			self.attribute = ''
		else:
			self.type = ops.NONE
			self.attribute = ''
			
		self.left = left
		self.right = right

	def __str__(self):
		if(self.type == ops.ATTR):
			return self.attribute
		else:			
			left = str(self.left)
			right = str(self.right)
			
			if debug:
			   print("Operation: ", self.type)
			   print("Left operand: ", left)
			   print("Right operand: ", right)			
			if(self.type == ops.EXP):
				return (left + '^' + right)
			elif(self.type == ops.MUL):
				return (left + ' * ' + right)
			elif(self.type == ops.EQ):
				return (left + ' := ' + right)
			elif(self.type == ops.EQ_TST):
				return (left + ' == ' + right)
			elif(self.type == ops.PAIR):
				return ('e(' + left + ',' + right + ")")
		return None
	
	def getAttribute(self):
		if (self.type == ops.ATTR):
			return self.attribute
		else:
			return None
	
	def getLeft(self):
		return self.left
	
	def getRight(self):
		return self.right

	def addSubNode(self, left, right):
		# set subNodes appropriately
		self.left = left if left != None else None
		self.right = right if left != None else None

	# only applies function on leaf nodes
	def traverse(self, function):
		# visit node then traverse left and right
		function(self.type, self)
		if(self.left == None):
			return None
		self.left.traverse(function)
		if(self.right == None):
			return None
		self.right.traverse(function)
		return None	
	
	
	