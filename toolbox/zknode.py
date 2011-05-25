#!/usr/bin/python

import string

class BinNode:
	def __init__(self, value, left=None, right=None):		
		#types of node
		self.OR = 1
		self.AND = 2
		self.EXP = 3  # '^' or exponent
		self.EQ = 4   # ==
		self.ATTR = 0

		#OF = '' # anything above 1 and 2
		if(isinstance(value, str)):
			self.type = self.ATTR
			self.attribute = string.upper(value)
						
		elif(isinstance(value, int)):
			if value > 0 and value <= self.EQ:
				self.type = value
			self.attribute = ''
			
		self.left = left
		self.right = right

	def __str__(self):
		if(self.type == self.ATTR):
			return self.attribute
		else:			
			left = str(self.left)
			right = str(self.right)
			
			if(self.type == self.OR):
				return ('('+ left + ') or (' + right + ')')
			elif(self.type == self.AND):
				return ('(' + left + ') and (' + right + ')')
			elif(self.type == self.EXP):
				return (left + '^' + right)
			elif(self.type == self.EQ):
				return (left + ' = ' + right)
		return None
	
	def getAttribute(self):
		if (self.type == self.ATTR):
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


