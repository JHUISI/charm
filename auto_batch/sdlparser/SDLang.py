''' Operators in SDL language:

* ADD, SUB, DIV, MUL, EXP - '+','-','*', '/' for division,'^' for exponentiation
* EQ - ':=' for assignment
* EQ_TST - '==' for equality testing
* PAIR - 'e(' arg1, arg2 ')'
* RANDOM - 'random assignment'
* HASH - 'H(val, ZR)' compute 'hash' of a variable to ZR, G1 or G2 
* FOR - 'for{i:=1,X} do x' loop from 1 to X on statement x
* SUM - 'sum{t:=1,X} of x_t' computes summation of x at index t for all X
* PROD - 'prod{i:=1,N} on n' apply dot product to statement n
* LIST - 'list{x, y, z,...}'

e.g., prod{i:=1,N} on (pk_i ^ del_i) 

AST simple rules

* check constraints assignment node exists.
* check verify assignment node exists.
* check variables have appropriate assignment types.
* support batch for different messages/signers/public keys.
'''

from charm.toolbox.enum import *
import string, sys

inputKeyword = "input"
outputKeyword = "output"

BINARY_NODE_CLASS_NAME = 'BinaryNode'
ENUM_VALUE_CLASS_NAME = 'EnumValue'
VAR_INFO_CLASS_NAME = 'VarInfo'
NONE_FUNC_NAME = "NONE_FUNC_NAME"
NONE_STRING = 'None'
SYMMETRIC_SETTING = "symmetric"
ASYMMETRIC_SETTING = "asymmetric"
ALGEBRAIC_SETTING = "setting"
LIST_INDEX_SYMBOL = "#"
LIST_INDEX_END_SYMBOL = "?"
IF_BRANCH_HEADER = "if"
ELSE_BRANCH_HEADER = "else"
FOR_LOOP_HEADER = "for"
FOR_LOOP_INNER_HEADER = "forinner"
FORALL_LOOP_HEADER = "forall"
TYPES_HEADER = "types"
COUNT_HEADER = "count" # JAA: app-specific
PRECOMPUTE_HEADER = "precompute" # JAA: app-specific
LATEX_HEADER = "latex" # JAA: standard
LIST_TYPE = "list"
OTHER_TYPES = ['list', 'object']
DECL_FUNC_HEADER = "func:"
INIT_FUNC_NAME = "init"
FUNC_SYMBOL = "def func :"
START_TOKEN, BLOCK_SEP, END_TOKEN = 'BEGIN','::','END'
types = Enum('NO_TYPE','G1', 'G2', 'GT', 'ZR', 'int', 'str', 'list', 'object', 'listInt', 'listStr', 'listG1', 'listG2', 'listGT', 'listZR','symmap')
declarator = Enum('func', 'verify')
ops = Enum('BEGIN', 'ERROR', 'TYPE', 'AND', 'ADD', 'SUB', 'MUL', 'DIV', 'EXP', 'EQ', 'EQ_TST', 'PAIR', 'ATTR', 'HASH', 'RANDOM','FOR','DO', 'FORINNER', 'FORALL', 'PROD', 'SUM', 'ON', 'OF','CONCAT', 'LIST', 'SYMMAP', 'EXPAND', 'FUNC', 'SEQ', 'IF', 'ELSEIF', 'ELSE', 'END', 'NONE')
side = Enum('left', 'right')
levels = Enum('none', 'some', 'all')
debug = levels.none

# Note: when updating the grammar, there are four places that you have to update:
# - getBNF: symbol must be represented in the grammar (w/o) breaking the other rules.
# - batchparser: evalStack routine must be able to identify the new symbol in input file.
# - ops: definition above must include symbolic representation of new construct somewhere between BEGIN and END
# - createTree: need to add a clause for the new symbol.
# - BinaryNode: need to add a clause to the __str__ routine.

# utilities over binary node structures
# list: 
# - searchNode => find a particular type of node (ops.PAIR) in a given subtree (node)

def getNextListName(assignInfo, origListName, index):
    (listFuncNameInAssignInfo, listEntryInAssignInfo) = getVarNameEntryFromAssignInfo(assignInfo, origListName)
    if ( (listFuncNameInAssignInfo == None) or (listEntryInAssignInfo == None) ):
        sys.exit("Problem with return values from getVarNameEntryFromAssignInfo in getNextListName in SDLParser.py.")
    if ( (listEntryInAssignInfo.getIsList() == False) or (len(listEntryInAssignInfo.getListNodesList()) == 0) ):
        #sys.exit("Problem with list obtained from assignInfo in getNextListName in SDLParser.")
        return (None, None)

    listNodesList = listEntryInAssignInfo.getListNodesList()
    index = int(index)
    lenListNodesList = len(listNodesList)
    if (index >= lenListNodesList):
        sys.exit("getNextListName in SDLParser.py found that the index submitted as input is greater than the length of the listNodesList returned from getVarNameEntryFromAssignInfo.")

    return (listFuncNameInAssignInfo, listNodesList[index])

def hasDefinedListMembers(assignInfo, listName):
    (funcName, varInfoObj) = getVarNameEntryFromAssignInfo(assignInfo, listName)
    if ( (varInfoObj.getIsList() == True) and (len(varInfoObj.getListNodesList()) > 0) ):
        return True

    return False

def getVarNameFromListIndices(assignInfo, node, failSilently=False):
    if (node.type != ops.ATTR):
        if (failSilently == True):
            return (None, None)
        else:
            sys.exit("Node passed to getVarNameFromListIndex in SDLParser is not of type " + str(ops.ATTR))

    nodeAttrFullName = getFullVarName(node, False)

    if (nodeAttrFullName.find(LIST_INDEX_SYMBOL) == -1):
        if (failSilently == True):
            return (None, None)
        else:
            sys.exit("Node passed to getVarNameFromListIndex is not a reference to an index in a list.")

    nodeName = nodeAttrFullName
    nodeNameSplit = nodeName.split(LIST_INDEX_SYMBOL)
    currentListName = nodeNameSplit[0]
    nodeNameSplit.remove(currentListName)
    lenNodeNameSplit = len(nodeNameSplit)
    counter_nodeNameSplit = 0

    while (counter_nodeNameSplit < lenNodeNameSplit):
        listIndex = nodeNameSplit[counter_nodeNameSplit]
        if (listIndex.isdigit() == False):
            if (counter_nodeNameSplit == (lenNodeNameSplit - 1)):
                (tempFuncName, tempListName) = getVarNameEntryFromAssignInfo(assignInfo, currentListName)
                return (tempFuncName, currentListName)
            definedListMembers = hasDefinedListMembers(assignInfo, currentListName)
            if ( (definedListMembers == True) and (nodeNameSplit[counter_nodeNameSplit + 1].isdigit() == True) ):
                (currentFuncName, currentListName) = getNextListName(assignInfo, currentListName, nodeNameSplit[counter_nodeNameSplit + 1])
                if ( (currentFuncName == None) and (currentListName == None) ):
                    break
                counter_nodeNameSplit += 2
                continue
            else:
                (tempFuncName, tempListName) = getVarNameEntryFromAssignInfo(assignInfo, currentListName)
                return (tempFuncName, currentListName)
        (currentFuncName, currentListName) = getNextListName(assignInfo, currentListName, listIndex)
        if ( (currentFuncName == None) and (currentListName == None) ):
            break
        counter_nodeNameSplit += 1

    return (currentFuncName, currentListName)

def getVarNameEntryFromAssignInfo(assignInfo, varName):
    retFuncName = None
    retVarInfoObj = None
    currentRetVarInfoObjIsExpandNode = False

    for funcName in assignInfo:
        for currentVarName in assignInfo[funcName]:
            if (currentVarName == varName):
                if ( (retVarInfoObj != None) or (retFuncName != None) ):
                    if (funcName != TYPES_HEADER):
                        if ( (assignInfo[funcName][currentVarName].getIsExpandNode() == True) and (currentRetVarInfoObjIsExpandNode == True) ):
                            pass
                        elif ( (assignInfo[funcName][currentVarName].getIsExpandNode() == True) and (currentRetVarInfoObjIsExpandNode == False) ):
                            pass
                        elif ( (assignInfo[funcName][currentVarName].getIsExpandNode() == False) and (currentRetVarInfoObjIsExpandNode == True) ):
                            retFuncName = funcName
                            retVarInfoObj = assignInfo[funcName][currentVarName]
                            currentRetVarInfoObjIsExpandNode = False
                        elif ( (assignInfo[funcName][currentVarName].getIsExpandNode() == False) and (currentRetVarInfoObjIsExpandNode == False) ):
                            retFuncName = funcName
                            retVarInfoObj = assignInfo[funcName][currentVarName]
                            currentRetVarInfoObjIsExpandNode = False
                    elif (retFuncName != TYPES_HEADER):
                        pass
                    elif ( (retVarInfoObj.hasBeenSet() == False) and (assignInfo[funcName][currentVarName].hasBeenSet() == True) ):
                        retFuncName = funcName
                        retVarInfoObj = assignInfo[funcName][currentVarName]
                        if (retVarInfoObj.getIsExpandNode() == True):
                            currentRetVarInfoObjIsExpandNode = True
                        else:
                            currentRetVarInfoObjIsExpandNode = False
                    elif ( (retVarInfoObj.hasBeenSet() == True) and (assignInfo[funcName][currentVarName].hasBeenSet() == False) ):
                        pass
                    else:
                        sys.exit("getVarNameEntryFromAssignInfo in SDLParser.py found multiple assignments of the same variable is assignInfo in which neither of the functions is " + str(TYPES_HEADER))
                else:
                    retFuncName = funcName
                    retVarInfoObj = assignInfo[funcName][currentVarName]
                    if (retVarInfoObj.getIsExpandNode() == True):
                        currentRetVarInfoObjIsExpandNode = True
                    else:
                        currentRetVarInfoObjIsExpandNode = False

    #if ( (retVarInfoObj == None) or (retFuncName == None) ):
        #sys.exit("getVarNameEntryFromAssignInfo in SDLParser.py could not locate entry in assignInfo of the name passed in.")

    return (retFuncName, retVarInfoObj)

def isValidType(possibleType):
    for validType in types:
        if (str(possibleType) == str(validType)):
            return True

    #print(possibleType)

    if (type(possibleType).__name__ != ENUM_VALUE_CLASS_NAME):
        return False

    if ( (possibleType == ops.LIST) or (possibleType == ops.SYMMAP) ):
        return True

    return False

def getListNodeNames(node):
    listNodes = None
    retList = []

    try:
        listNodes = node.listNodes
    except:
        return retList

    for listNodeName in listNodes:
        retList.append(listNodeName)

    return retList

def addListNodesToList(node, listToAddTo):
    listNodes = getListNodeNames(node)
    if (listNodes == []):
        return

    for listNode in listNodes:
        listNodeFinal = dropListIndexIfNonNum(listNode)
        if ( (listNodeFinal not in listToAddTo) and (listNodeFinal.isdigit() == False) and (listNodeFinal != NONE_STRING) ):
            listToAddTo.append(listNodeFinal)

def dropListIndexIfNonNum(varName):
    if (varName.count(LIST_INDEX_SYMBOL) != 1):
        return varName

    listIndexPos = varName.find(LIST_INDEX_SYMBOL)
    lenVarName = len(varName)
    listIndex = varName[(listIndexPos+1):lenVarName]
    listIndexIsInt = None
    try:
        listIndexIsInt = int(listIndex)
    except:
        pass

    if (listIndexIsInt != None):
        return varName

    return varName[0:listIndexPos]

def expandVarNamesByIndexSymbols(varNameList):
    if (type(varNameList) is not list):
        sys.exit("expandVarNamesByIndexSymbols in SDLang.py:  varNameList parameter passed in is not of type list.")

    if (len(varNameList) == 0):
        return varNameList

    retList = []

    for varName in varNameList:
        varNameSplit = varName.split(LIST_INDEX_SYMBOL)
        for varNameSplit_Ind in varNameSplit:
            if (varNameSplit_Ind.isdigit() == True):
                continue
            if (varNameSplit_Ind not in retList):
                retList.append(varNameSplit_Ind)

    return retList

def getVarNameWithoutIndices(node):
    varName = node.attr
    if (node.attr_index != None):
        for index in node.attr_index:
            varName += "_" + index

    indexOfListSymbol = varName.find(LIST_INDEX_SYMBOL)
    if (indexOfListSymbol == -1):
        return varName
    return varName[0:indexOfListSymbol]

def getFullVarName(node, dropListIndexIfNonNum_Arg):
    if ( (dropListIndexIfNonNum_Arg != True) and (dropListIndexIfNonNum_Arg != False) ):
        sys.exit("getFullVarName in SDLang.py:  dropListIndexIfNonNum_Arg parameter passed in is not set to True or False.")

    varName = node.attr
    if (node.attr_index != None):
        for index in node.attr_index:
            varName += "_" + index

    #exception we're putting in so you can address direct elements in a list (e.g., S#k-1?) w/o errors
    if ( (type(varName) is str) and (varName.count(LIST_INDEX_END_SYMBOL) == 1) ):
        return varName

    if (dropListIndexIfNonNum_Arg == True):
        return dropListIndexIfNonNum(varName)

    return varName

def getListNodes(subtree, parent_type, _list):
	if subtree == None: return None
	# trying to capture most probable arrangements (may need to expand for other cases)
	elif parent_type == ops.MUL:
		if subtree.type == ops.ATTR: _list.append(subtree)
		elif subtree.type == ops.EXP: _list.append(subtree)
		elif subtree.type == ops.HASH: _list.append(subtree)
		elif subtree.type == ops.PAIR: _list.append(subtree)
	elif parent_type == ops.EQ_TST:
		if subtree.type == ops.PAIR: _list.append(subtree)
		elif subtree.type == ops.ATTR: _list.append(subtree)
		elif subtree.type == ops.ON: _list.append(subtree.right)
		
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
	result = searchNodeType(node.left, target_type)
	if result: return result
	result = searchNodeType(node.right, target_type)		
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

def validateCreatedNode(node):
	correct = True
	if Type(node) == ops.OF:
		if Type(node.left) != ops.SUM: correct = False
	elif Type(node) == ops.DO:
		if Type(node.left) != ops.FOR: correct = False
	elif Type(node) == ops.ON:
		if Type(node.left) != ops.PROD: correct = False
	# extend for other nodes like PAIR/MUL
	return correct


# binds a string representation of the operation to 
# the symbolic representation (Enums) above 
def createTree(op, node1, node2, op_value=None):
    if(op == START_TOKEN):
        node = BinaryNode(ops.BEGIN)
    elif(op == END_TOKEN):
    	node = BinaryNode(ops.END)
    elif(op == "^"):
        node = BinaryNode(ops.EXP)
    elif(op == "*"):
        node = BinaryNode(ops.MUL)
    elif(op == "/"):
    	node = BinaryNode(ops.DIV)
    elif(op == "+"):
        node = BinaryNode(ops.ADD)
    elif(op == "-"):
        node = BinaryNode(ops.SUB)
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
    elif(op == "forinner{"):
        node = BinaryNode(ops.FORINNER)
    elif(op == "forall{"):
        node = BinaryNode(ops.FORALL)        
    elif(op == "do"):
    	node = BinaryNode(ops.DO)
    elif(op == "sum{"):
    	node = BinaryNode(ops.SUM)
    elif(op == "of"):
    	node = BinaryNode(ops.OF)
    elif(op == "if {"):
        node = BinaryNode(ops.IF)
    elif(op == "elseif {"):
        node = BinaryNode(ops.ELSEIF)
    elif(op == "else"):
        node = BinaryNode(ops.ELSE)
    elif(op == "|"):
        node = BinaryNode(ops.CONCAT)
    elif(op == "and"):
    	node = BinaryNode(ops.AND)
    elif(op == "list{"):
    	node = BinaryNode(ops.LIST)
    elif(op == "symmap{"):
        node = BinaryNode(ops.SYMMAP)
    elif(op == "expand{"):
    	node = BinaryNode(ops.EXPAND)
    elif(op == "random("):
    	node = BinaryNode(ops.RANDOM)
    elif(op == "error("):
        node = BinaryNode(ops.ERROR)
        node.setAttribute(op_value)
    elif(FUNC_SYMBOL in op):
    	node = BinaryNode(ops.FUNC)
    	node.setAttribute(op_value)
    elif(op == ";"):
    	node = BinaryNode(ops.SEQ) # represents multi-line assignment statements
    	# rule: throw up an error if 
    # elif e( ... )
    else:    
        return None
    node.addSubNode(node1, node2)
    if not validateCreatedNode(node): del node; return False
    return node


class BinaryNode:
	def __init__(self, value, left=None, right=None):		
		self.negated = False	
		if(isinstance(value, str)):
			if value in ['G1', 'G2', 'GT', 'ZR', 'int', 'str', 'list', 'object']: # JAA: change me ASAP!!!
                # denotes group type of an attribute value
				self.type = ops.TYPE
				self.attr = types[value]
				self.attr_index = None                
				self.delta_index = None                
			else:
				self.type = ops.ATTR
				self.delta_index = None                
				arr = value.split('_')
				attr = arr[0]
				# test for negation in attribute
				if attr[0] != '-': self.attr = attr
				else:
					self.attr = attr[1:]
					self.negated = True
				# handle indices 
				if len(arr) > 1: # True means a_b form
					self.attr_index = [arr[1]]
				else: # False means a and no '_' present
					self.attr_index = None
		elif value >= ops.BEGIN and value <= ops.END:
			self.type = value
			self.attr = None
			self.attr_index = None
			self.delta_index = None                
		else:
			self.type = ops.NONE
			self.attr = None
			self.attr_index = None
			self.delta_index = None                
		self.left = left
		self.right = right

	def __str__(self):
		if self == None: return None
		elif(self.type == ops.ATTR):
			# check for negation
			if self.negated:
				msg = "-" + self.attr
			else:
				msg = self.attr
			if self.delta_index != None and type(self.delta_index) == list and self.attr == "delta":
                		token = ""
                		for t in self.delta_index:
                    			token += t + "#"
                		msg += token[:len(token)-1]
			if self.attr_index != None and type(self.attr_index) == list:
				token = ""
				for t in self.attr_index:
					token += t + "#"
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
			if(self.type == ops.BEGIN):
				return (START_TOKEN + ' :: ' + left)
			elif(self.type == ops.END):
				return (END_TOKEN + ' :: ' + left)
			elif(self.type == ops.EXP):
				return ('(' + left + '^' + right + ')')
			elif(self.type == ops.MUL):
				return ('(' + left + ' * ' + right + ')')
			elif(self.type == ops.DIV):
				return ('(' + left + ' / ' + right + ')')
			elif(self.type == ops.ADD):
				return ('(' + left + ' + ' + right + ')')
			elif(self.type == ops.SUB):
				return ('(' + left + ' - ' + right + ')')
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
			elif(self.type == ops.SUM):
				return ('sum{' + left + ',' + right + '}')			
			elif(self.type == ops.ON):
				 return ('(' + left + ' on ' + right + ')')
			elif(self.type == ops.FOR):
				return ('for{' + left + ',' + right + '}')
			elif(self.type == ops.FORINNER):
				return ('forinner{' + left + ',' + right + '}')
			elif(self.type == ops.FORALL):
				return ('forall{' + left + '}')
			elif(self.type == ops.RANDOM):
				return ('random(' + left + ')')
			elif(self.type == ops.ERROR):
				return ('error(' + str(self.attr) + ')')
			elif(self.type == ops.DO):
				 return (left + ' do { ' + right + ' }')
			elif(self.type == ops.IF):
				 return ('if {' + left + '}')
			elif(self.type == ops.ELSEIF):
    			 return ('elseif {' + left + '}')
			elif(self.type == ops.ELSE):
    			 return 'else '
			elif(self.type == ops.OF):
				 return ( left + ' of ' + right)
			elif(self.type == ops.CONCAT):
				 return (left + ' | ' + right)
			elif(self.type == ops.AND):
				 return ("{" + left + "} and {" + right + "}") 
			elif(self.type == ops.LIST):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'list{' + listVal + '}'
			elif(self.type == ops.SYMMAP):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'symmap{' + listVal + '}'    
			elif(self.type == ops.EXPAND):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'expand{' + listVal + '}'
			elif(self.type == ops.FUNC):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return self.attr + '(' + listVal + ')'
			elif(self.type == ops.SEQ):
				return (left + '; ' + right)
			elif(self.type == ops.NONE):
				 return 'NONE'
				# return ( left + ' on ' + right )				
		return None
	    
	def sdl_print(self):
		if self == None: return None
		elif(self.type == ops.ATTR):
			# check for negation
			if self.negated:
				msg = "-" + self.attr
			else:
				msg = self.attr
			if self.delta_index != None and type(self.delta_index) == list and self.attr == "delta":
                		token = ""
                		for t in self.delta_index:
                    			token += t + ""
                		msg += token # [:len(token)-1]
			if self.attr_index != None and type(self.attr_index) == list:
				token = ""
				for t in self.attr_index:
					token += t + "#"
				l = len(token) 
				token = token[:l-1]
				if token != '': msg += '#' + token
			return msg
		elif(self.type == ops.TYPE):
			return str(self.attr)
		else:
			left = self.left.sdl_print()
			right = self.right.sdl_print()
			
			if debug >= levels.some:
			   print("Operation: ", self.type)
			   print("Left operand: ", left, "type: ", self.left.type)
			   print("Right operand: ", right, "type: ", self.right.type)
			if(self.type == ops.BEGIN):
				return (START_TOKEN + ' :: ' + left)
			elif(self.type == ops.END):
				return (END_TOKEN + ' :: ' + left)
			elif(self.type == ops.EXP):
				return ('(' + left + '^' + right + ')')
			elif(self.type == ops.MUL):
				return ('(' + left + ' * ' + right + ')')
			elif(self.type == ops.DIV):
				return ('(' + left + ' / ' + right + ')')
			elif(self.type == ops.ADD):
				return ('(' + left + ' + ' + right + ')')
			elif(self.type == ops.SUB):
				return ('(' + left + ' - ' + right + ')')
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
			elif(self.type == ops.SUM):
				return ('sum{' + left + ',' + right + '}')			
			elif(self.type == ops.ON):
				 return ('(' + left + ' on ' + right + ')')
			elif(self.type == ops.FOR):
				return ('for{' + left + ',' + right + '}')
			elif(self.type == ops.FORINNER):
				return ('forinner{' + left + ',' + right + '}')
			elif(self.type == ops.FORALL):
				return ('forall{' + left + '}')
			elif(self.type == ops.RANDOM):
				return ('random(' + left + ')')
			elif(self.type == ops.ERROR):
				return ('error(' + self.attr.sdl_print() + ')')
			elif(self.type == ops.DO):
				 return (left + ' do { ' + right + ' }')
			elif(self.type == ops.IF):
				 return ('if {' + left + '}')
			elif(self.type == ops.ELSEIF):
    			 return ('elseif {' + left + '}')
			elif(self.type == ops.ELSE):
    			 return 'else '
			elif(self.type == ops.OF):
				 return ( left + ' of ' + right)
			elif(self.type == ops.CONCAT):
				 return (left + ' | ' + right)
			elif(self.type == ops.AND):
				 return ("{" + left + "} and {" + right + "}") 
			elif(self.type == ops.LIST):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'list{' + listVal + '}'
			elif(self.type == ops.SYMMAP):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'symmap{' + listVal + '}'    
			elif(self.type == ops.EXPAND):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return 'expand{' + listVal + '}'
			elif(self.type == ops.FUNC):
				 listVal = ""
				 for i in self.listNodes:
				 	listVal += str(i) + ', '
				 listVal = listVal[:len(listVal)-2]
				 return self.attr + '(' + listVal + ')'
			elif(self.type == ops.SEQ):
				return (left + '; ' + right)
			elif(self.type == ops.NONE):
				 return 'NONE'
		return None

	def isAttrIndexEmpty(self):
		if self.attr_index != None:
			if len(self.attr_index) > 0: return False
		return True

	def setType(self, value):
        	self.type = value
	
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
			return str(self.attr)
		return None
    
    # Delta specific adds to BinaryNode to account for small exps
	def isDeltaIndexEmpty(self):
		if self.delta_index != None:
			if len(self.delta_index) > 0: return False
		return True

	def getDeltaIndex(self):
		return self.delta_index
    
	def setDeltaIndexFromSet(self, value):
		if type(value) not in [set, list]: return
		if value == None: return
		value2 = [str(i) for i in sorted(value)]
		self.delta_index = value2
		return
    
	def setDeltaIndex(self, value):
		if(self.type in [ops.ATTR, ops.HASH, ops.PAIR]):
		    value2 = str(value)
		    if self.delta_index == None: # could be a list of indices
		        self.delta_index = [value2]
		    else:
		        if not value2 in self.delta_index:
		           self.delta_index.append(value2)
		    return True
		return False

	def getRefAttribute(self):
		if (self.type == ops.ATTR):
			attr = str(self)
			return dropListIndexIfNonNum(attr)
		return None

	def getFullAttribute(self):
		if (self.type == ops.ATTR):
			return str(self)
		return None	

	def setAttribute(self, value, clearAttrIndex=True):
		if self.type in [ops.ATTR, ops.FUNC, ops.ERROR]:
			self.attr = str(value)
			if clearAttrIndex: self.attr_index = None
			return True
		return False
	
	def addToList(self, value):
 		if self.type  in [ops.LIST, ops.EXPAND]:
 			if type(value) == str:
 				self.listNodes.append(value)
    
#	def getMySide(self):
#		return self.myside
	
	def getLeft(self):
		return self.left if self.left != None else None
	
	def getRight(self):
		return self.right if self.right != None else None

	def addSubNode(self, left, right):
		# set subNodes appropriately
		self.left = self.createSubNode(left) if left != None else None
		#self.left.myside = side.left
		self.right = self.createSubNode(right) if left != None else None
		#self.right.myside = side.right
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
		new_node.negated = this.negated
		new_node.attr = this.attr
		new_node.attr_index = this.attr_index
		new_node.delta_index = this.delta_index
		if this.type in [ops.LIST, ops.EXPAND]:
			new_node.listNodes  = this.listNodes
		# recursively call copy on left 
		new_node.left = self.copy(this.left)
		new_node.right = self.copy(this.right)		
		return new_node	

	# sets destination ref to src ref (type, attr value, and attr index)
	@classmethod
	def setNodeAs(self, dest, src):
		dest.type = src.type
		dest.attr = src.attr
		dest.negated = src.negated
		if src.attr_index:
			dest.attr_index = list(src.attr_index)
		else:
			dest.attr_index = None
		if src.delta_index:
			dest.delta_index = list(src.delta_index)
		else:
			dest.delta_index = None           
		dest.left = src.left
		dest.right = src.right
		return

	@classmethod
	def clearNode(self, dest):
		dest.type = ops.NONE
		dest.attr = None
		dest.negated = False
		dest.attr_index = None
		dest.delta_index = None        
		dest.left = None
		dest.right = None
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
	
