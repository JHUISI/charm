''' Operators in Batch language:

* MUL, EXP - '*' for multiply,'^' for exponent
* EQ - ':=' for assignment
* EQ_TST - '==' for equality testing
* PAIR - 'e(' arg1, arg2 ')'
* CONST - 'constant' declarator?
* VARIABLE - 'variable' declarator?
* FOR - 'for{i:=1,X} do x' loop from 1 to X on statement x
* PROD - 'prod{i:=1,N} on n' apply dot product to statement n
* ARR - 'a_1' for an array, a, with index = 1
* LIST - '[ x, y, z,...]' # not implemented yet

e.g., prod{i:=1,N} on (pk_i ^ del_i) 

AST simple rules

* check constraints assignment node exists.
* check verify assignment node exists.
* check variables have appropriate assignment types.
* support batch for different messages/signers/public keys.
'''

from toolbox.enum import *
import string

types = Enum('G1', 'G2', 'GT', 'ZR', 'str')
declarator = Enum('constants', 'verify')
ops = Enum('BEGIN', 'TYPE', 'ADD', 'MUL', 'DIV', 'EXP', 'EQ', 'EQ_TST', 'PAIR', 'ATTR', 'HASH', 'FOR','DO','PROD', 'ON', 'CONCAT','END', 'NONE')
levels = Enum('none', 'some', 'all')
debug = levels.none

# utilities over binary node structures
# list: 
# - searchNode => find a particular type of node (ops.PAIR) in a given subtree (node)

def getListNodes(subtree, parent_type, _list):
	if subtree == None: return None
	elif parent_type == ops.MUL:
		if subtree.type == ops.ATTR: _list.append(subtree)
		elif subtree.type == ops.EXP: _list.append(subtree)
		elif subtree.type == ops.HASH: _list.append(subtree)
		
	if subtree.left: getListNodes(subtree.left, subtree.type, _list)
	if subtree.right: getListNodes(subtree.right, subtree.type, _list)
	return

# checks whether a target node exists in a subtree
# note: returns True when it finds the first match 
def isNodeInSubtree(node, target):
	if node == None: return False
	else:
		if str(node) == str(target): return True
	result = isNodeInSubtree(node.left, target)
	if result: return result
	result = isNodeInSubtree(node.right, target)
	return result

# searches a subtree for a target node type
# it returns the first node that matches the target type.
# note: doesn't return all istances of a given type in the subtree
def searchNodeType(node, target_type):
	if node == None: return None
	elif node.type == target_type: return node		
	result = searchNode(node.left)
	if result: return result
	result = searchNode(node.right)		
	return result

# simplifies checking the type of a given node
def Type(node):
	if node == None: return ops.NONE
	return node.type

# short cut to creating a binary node of a given type
# with given children nodes.
def createNode(node_type, left=None, right=None):
	node = BinaryNode(node_type)
	node.left = left
	node.right = right
	return node

# binds a string representation of the operation to 
# the symbolic representation (Enums) above 
def createTree(op, node1, node2):
    if(op == "^"):
        node = BinaryNode(ops.EXP)
    elif(op == "*"):
        node = BinaryNode(ops.MUL)
    elif(op == "+"):
        node = BinaryNode(ops.ADD)
    elif(op == ":="):
        node = BinaryNode(ops.EQ)
    elif(op == "=="):
        node = BinaryNode(ops.EQ_TST)
    elif(op == "e("):
        node = BinaryNode(ops.PAIR)
    elif(op == "H("):
        node = BinaryNode(ops.HASH)
    elif(op == "prod{"):
        node = BinaryNode(ops.PROD)
    elif(op == "on"):
        # can only be used in conjunction w/ PROD (e.g. PROD must precede it)        
        node = BinaryNode(ops.ON)
    elif(op == "for{"):
    	node = BinaryNode(ops.FOR)
    elif(op == "do"):
    	node = BinaryNode(ops.DO)
    elif(op == "|"):
        node = BinaryNode(ops.CONCAT)
    # elif e( ... )
    else:    
        return None
    node.addSubNode(node1, node2)
    return node


class BinaryNode:
	def __init__(self, value, left=None, right=None):		
		if(isinstance(value, str)):
			if value in ['G1', 'G2', 'GT', 'ZR', 'str']:
				self.type = ops.TYPE
				self.attr = types[value]
				self.attr_index = None
			else:
				self.type = ops.ATTR
				arr = value.split('_')
				self.attr = arr[0]
				if len(arr) > 1: # True means a_b form
					self.attr_index = [arr[1]]
				else: # False means a and no '_' present
					self.attr_index = None
		elif value > ops.BEGIN and value < ops.END:
			self.type = value
			self.attr = None
			self.attr_index = None
		else:
			self.type = ops.NONE
			self.attr = None
			self.attr_index = None
		self.left = left
		self.right = right

	def __str__(self):
		if(self.type == ops.ATTR):
			msg = self.attr
			if self.attr_index != None and type(self.attr_index) == list:
				token = ""
				for t in self.attr_index:
					token += t + ","
				l = len(token) 
				token = token[:l-1]
				msg += '_' + token
			return msg
		elif(self.type == ops.TYPE):
			return str(self.attr)
		else:
			left = str(self.left)
			right = str(self.right)
			
			if debug >= levels.some:
			   print("Operation: ", self.type)
			   print("Left operand: ", left, "type: ", self.left.type)
			   print("Right operand: ", right, "type: ", self.right.type)
			if(self.type == ops.EXP):
				return (left + '^' + right)
			elif(self.type == ops.MUL):
				return ('(' + left + ' * ' + right + ')')
			elif(self.type == ops.DIV):
				return ('(' + left + ' / ' + right + ')')
			elif(self.type == ops.ADD):
				return ('(' + left + ' + ' + right + ')')
			elif(self.type == ops.EQ):
				return (left + ' := ' + right)
			elif(self.type == ops.EQ_TST):
				return (left + ' == ' + right)
			elif(self.type == ops.PAIR):
				return ('e(' + left + ',' + right + ')')
			elif(self.type == ops.HASH):
				return ('H(' + left + ',' + right + ')')
			elif(self.type == ops.PROD):
				return ('prod{' + left + ',' + right + '}')
			elif(self.type == ops.ON):
				 return ('(' + left + ' on ' + right + ')')
			elif(self.type == ops.FOR):
				return ('for{' + left + ',' + right + '}')
			elif(self.type == ops.DO):
				 return ( left + ' do ' + right)
			elif(self.type == ops.CONCAT):
				 return (left + ' | ' + right)
				# return ( left + ' on ' + right )				
		return None
	
	def setAttrIndex(self, value):
		if(self.type in [ops.ATTR, ops.HASH]):
			if self.attr_index == None: # could be a list of indices
				self.attr_index = [value]
			else:
				if not value in self.attr_index:
					self.attr_index.append(value)
			return True
		return False
	
	def getAttribute(self):
		if (self.type == ops.ATTR):
			return self.attr
		else:
			return None
	
	def getLeft(self):
		return self.left if self.left != None else None
	
	def getRight(self):
		return self.right if self.right != None else None

	def addSubNode(self, left, right):
		# set subNodes appropriately
		self.left = self.createSubNode(left) if left != None else None
		self.right = self.createSubNode(right) if left != None else None
		if debug == levels.all:
			print("addSubNode: ");
			print("left type =>", type(self.left), ' =>', self.left)
			print("right type =>", type(self.right), ' =>', self.right)

	def createSubNode(self, value):
		if isinstance(value, str):
			node = BinaryNode(value)		   
			return node
		return value

	@classmethod
	def copy(self, this):
		if this == None: return None
		new_node = BinaryNode(this.type)
		new_node.attr = this.attr
		new_node.attr_index = this.attr_index
		
		# recursively call copy on left 
		new_node.left = self.copy(this.left)
		new_node.right = self.copy(this.right)		
		return new_node	

	@classmethod
	def setNodeAs(self, dest, src):
		dest.type = src.type
		dest.attr = src.attr
		dest.attr_index = src.attr_index
		return

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
	
	
	
