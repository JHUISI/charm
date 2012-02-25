from __future__ import print_function
import string
from toolbox.enum import *

OpType = Enum('or', 'and', 'attr')

class BinNode:
  def __init__(self, value, left=None, right=None):		
    #types of node
    self.OR = 1
    self.AND = 2
    self.ATTR = 0
    self.negated = False
    self.index   = None
    #OF = '' # anything above 1 and 2
    if(isinstance(value, unicode)):
      if value[0] == '!': 
          value = value[1:] # remove but set flag
          self.negated = True
      if value.find('_') != -1:
          val = value.split('_')
          self.index = int(val[1]) # index
          value = val[0]
      self.type = self.ATTR
      self.attribute = value.upper()      
      
    elif(isinstance(value, int)):
      self.type = self.OR if value == self.OR else self.AND
      self.attribute = ''
    
    self.left = left
    self.right = right

  def __str__(self):
    if(self.type == self.ATTR):
        if self.negated: prefix = '!'
        else: prefix = ''
        if self.index != None: postfix = '_' + str(self.index)
        else: postfix = ''
        return prefix + self.attribute + postfix
    else:
      left = str(self.left)
      right = str(self.right)
      
      if(self.type == self.OR):
        return ('('+ left + ' or ' + right + ')')
      else:
      	return ('(' + left + ' and ' + right + ')')
    return None
  
  def getAttribute(self):
    if (self.type == self.ATTR):
        if self.negated: prefix = '!'
        else: prefix = ''        
        return prefix + self.attribute
    return

  def getAttributeAndIndex(self):
    if (self.type == self.ATTR):
        if self.negated: prefix = '!'
        else: prefix = ''
        if self.index != None: postfix = '_' + str(self.index)
        else: postfix = ''
        
        return prefix + self.attribute + postfix
    return

  def __iter__(self):
      return self

  def __eq__(self, other):
      #print("checking...:", self, str(other))
      if other == None:
          return False
      if type(self) == type(other):
          return self.getAttribute() == other.getAttribute()
      elif type(other) in [str, unicode]:
          return other in self.getAttributeAndIndex()
      elif type(self) in [str, unicode]:
          return self in other.getAttributeAndIndex()
      else:
          raise ValueError('BinNode - invalid comparison.')

  def getLeft(self):
    return self.left
  
  def getRight(self):
    return self.right
        
  def getNodeType(self):
    return self.type
    
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


