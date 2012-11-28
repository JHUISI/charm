import sys, copy
from SDLang import *
from config import *
from DotProd import *

#TODO:  Replace "T1" with constant defined elsewhere that all T1 values pull from.
namesOfFutureDeclVars = [keygenSecVar + blindingSuffix, "T1", keygenBlindingExponent]

class VarInfo:
    def __init__(self):
        self.assignNode = None
        self.lineNo = None
        self.lineStr = None
        self.varDeps = []
        self.varDepsNoExponents = []
        self.hasPairings = None
        self.protectsM = None
        self.initType = None
        self.initValue = None
        self.beenSet = False
        self.initCall = None
        self.initCallHappenedAlready = False
        self.type = types.NO_TYPE
        self.funcName = None
        self.isList = False
        self.isSymmap = False
        self.listNodesList = []
        self.dotProdObj = None
        self.outsideForLoopObj = None
        self.outsideIfElseBranchObj = None
        self.hasRandomness = False
        self.isTypeEntryOnly = False
        self.listElementsType = None
        self.isUsedInHashCalc = False
        self.hashArgsInAssignNode = []
        self.hasListIndexSymInLeftAssign = False
        self.isExpandNode = False
        self.isBaseElement = False
        self.assignBaseElemsOnly = None
        self.assignInfo = None
    
    @classmethod
    def copy(self, obj):
        v = VarInfo()
        v.assignNode  = obj.assignNode 
        v.lineNo      = obj.lineNo
        v.varDeps     = list(obj.varDeps)
        v.varDepsNoExponents = list(obj.varDepsNoExponents)
        v.hasPairings = obj.hasPairings
        v.protectsM   = obj.protectsM
        v.initType    = obj.initType
        v.initValue   = obj.initValue
        v.beenSet     = obj.beenSet
        v.initCall    = obj.initCall
        v.initCallHappenedAlready = obj.initCallHappenedAlready
        v.type        = obj.type
        v.funcName    = obj.funcName
        v.isList      = obj.isList
        v.isSymmap    = obj.isSymmap
        v.listNodesList = list(obj.listNodesList)
        v.dotProdObj  = obj.dotProdObj
        v.outsideForLoopObj = obj.outsideForLoopObj
        v.outsideIfElseBranchObj = obj.outsideIfElseBranchObj
        v.hasRandomness = obj.hasRandomness
        v.isTypeEntryOnly = obj.isTypeEntryOnly
        v.listElementsType = obj.listElementsType
        v.isUsedInHashCalc = obj.isUsedInHashCalc
        v.hashArgsInAssignNode = obj.hashArgsInAssignNode
        v.hasListIndexSymInLeftAssign = obj.hasListIndexSymInLeftAssign
        v.isExpandNode = obj.isExpandNode
        v.isBaseElement = obj.isBaseElement
        v.assignBaseElemsOnly = obj.assignBaseElemsOnly
        v.assignInfo = obj.assignInfo
        return v
        
    def getAssignNode(self):
        return self.assignNode

    def getLineNo(self):
        return self.lineNo

    def getLineStrKey(self):
        return self.lineStr[0]
    
    def getLineStrValue(self):
        return self.lineStr[1]

    def getVarDeps(self):
        return self.varDeps

    def getVarDepsNoExponents(self):
        return self.varDepsNoExponents

    def getAssignVar(self):
        if self.assignNode and Type(self.assignNode) == ops.EQ:
            return self.assignNode.left.getFullAttribute()
        return None
    
    def setAssignVar(self, newString):
        if self.assignNode and Type(self.assignNode) == ops.EQ:
            self.assignNode.left.setAttribute(newString)
        return None

    def getHasPairings(self):
        return self.hasPairings

    def getProtectsM(self):
        if (self.assignNode == None):
            return False

        # generally, we're not interested in keywords that may reference the message
        if str(self.assignNode.left) in ['input', 'output']:
            return False         
        return self.protectsM

    def getInitType(self):
        return self.initType

    def getInitValue(self):
        return self.initValue

    def isUsedInHashCalc(self):
        return self.isUsedInHashCalc

    def getHashArgsInAssignNode(self):
        return self.hashArgsInAssignNode

    def hasBeenSet(self):
        return self.beenSet

    def getInitCall(self):
        return self.initCall

    def getInitCallHappenedAlready(self):
        return self.initCallHappenedAlready

    def getType(self):
        return self.type

    def getFuncName(self):
        return self.funcName

    def getIsList(self):
        return self.isList

    def getIsSymmap(self):
        return self.isSymmap

    def getListNodesList(self):
        return self.listNodesList

    def getDotProdObj(self):
        return self.dotProdObj

    def getOutsideForLoopObj(self):
        return self.outsideForLoopObj

    def getOutsideIfElseBranchObj(self):
        return self.outsideIfElseBranchObj

    def getHasRandomness(self):
        return self.hasRandomness

    def getIsTypeEntryOnly(self):
        return self.isTypeEntryOnly

    def getListElementsType(self):
        return self.listElementsType

    def getHasListIndexSymInLeftAssign(self):
        return self.hasListIndexSymInLeftAssign

    def getIsExpandNode(self):
        return self.isExpandNode

    def getIsBaseElement(self):
        return self.isBaseElement

    def getAssignBaseElemsOnly(self):
        return self.assignBaseElemsOnly

    def traverseAssignNodeRecursive(self, node, isExponent):
        if (node.type == ops.PAIR):
            self.hasPairings = True
        elif (node.type == ops.HASH):
            if (node.left.type not in [ops.ATTR, ops.CONCAT]): # JAA: added ops.CONCAT to account for hashing a concatenation of multiple variables
                sys.exit("traverseAssignNodeRecursive in VarInfo.py:  left child node of ops.HASH node encountred is not of type ATTR or CONCAT.")
            hashInputName = getFullVarName(node.left, False)
            if (hashInputName not in self.hashArgsInAssignNode):
                self.hashArgsInAssignNode.append(hashInputName)
        elif (node.type == ops.ATTR):
            varName = getFullVarName(node, True)
            if ( (varName not in self.varDeps) and (varName.isdigit() == False) and (varName != NONE_STRING) ):
                self.varDeps.append(varName)
                if (isExponent == False):
                    self.varDepsNoExponents.append(varName)
        elif (node.type == ops.FUNC):
            userFuncName = getFullVarName(node, True)
            if (userFuncName == INIT_FUNC_NAME):
                if (self.initCallHappenedAlready == True):
                    sys.exit("traverseAssignNodeRecursive found multiple calls to " + INIT_FUNC_NAME + " for the same variable in the same function.")
                self.initCallHappenedAlready = True
                listNodes = getListNodeNames(node)
                #if (len(listNodes) != 1):
                    #sys.exit("Init function call discovered by traverseAssignNodeRecursive has a number of arguments other than 1 (not supported).")
                if (len(listNodes) == 1):
                    self.initValue = listNodes[0]
                elif (len(listNodes) == 2):
                    self.initType = listNodes[0]
                    self.initValue = listNodes[1]
                else:
                    sys.exit("Init function call discovered by traverseAssignNodeRecursive has a number of arguments unequal to one or two (not supported).")

                if (self.initValue == LIST_TYPE):
                    self.isList = True
                self.initCall = True
        elif (node.type == ops.RANDOM):
            self.hasRandomness = True

        if (self.listElementsType == None):
            addListNodesToList(node, self.varDeps)
            if (isExponent == False):
                addListNodesToList(node, self.varDepsNoExponents)

        if (node.left != None):
            self.traverseAssignNodeRecursive(node.left, False)
        if (node.right != None):
            if (node.type == ops.EXP):
                self.traverseAssignNodeRecursive(node.right, True)
            else:
                self.traverseAssignNodeRecursive(node.right, False)

    def isOnlyListElementsTypeDecl(self, listNode):
        if (listNode.type != ops.LIST):
            sys.exit("isOnlyListElementsTypeDecl in VarInfo.py:  parameter passed in is not of type ops.LIST.")

        listNodeChildren = getListNodeNames(listNode)

        if (len(listNodeChildren) != 1):
            return None

        if (isValidType(listNodeChildren[0]) == True):
            return listNodeChildren[0]

        return None

    def getVarNameEntryFromAssignInfo_Wrapper(self, node, varNameString):
        numListIndexSymbols = varNameString.count(LIST_INDEX_SYMBOL)
        if (numListIndexSymbols == 0):
            (retFuncName, retVarInfoObj) = getVarNameEntryFromAssignInfo(self.assignInfo, varNameString)
        else:
            (retFuncName, retVarInfoObjString) = getVarNameFromListIndices(self.assignInfo, node)
            (retFuncName, retVarInfoObj) = getVarNameEntryFromAssignInfo(self.assignInfo, retVarInfoObjString)
        return (retFuncName, retVarInfoObj)

    def addNonNumListIndicesString(self, retNode, origNodeNameString):
        origNodeNameSplit = origNodeNameString.split(LIST_INDEX_SYMBOL)
        if (len(origNodeNameSplit) == 1):
            return

        skipFirst = True
        stillNumIndices = True

        for listIndex in origNodeNameSplit:
            if (skipFirst == True):
                skipFirst = False
                continue

            if (listIndex.isdigit() == True):
                if (stillNumIndices == True):
                    continue
            else:
                if (stillNumIndices == True):
                    stillNumIndices = False

    def traverseAssignBaseElemsOnlyRecursive(self, node):
        if (node.type == ops.ATTR):
            (retFuncName, retVarInfoObj) = self.getVarNameEntryFromAssignInfo_Wrapper(node, getFullVarName(node, False))
            if ( (retFuncName != None) and (retVarInfoObj != None) ):
                retNode = copy.deepcopy(retVarInfoObj.getAssignBaseElemsOnly())
                if (retNode == None):
                    return node
                else:
                    #self.addNonNumListIndicesString(retNode, getFullVarName(node, False))
                    return retNode
        elif ( (node.type == ops.LIST) or (node.type == ops.SYMMAP) or (node.type == ops.EXPAND) or (node.type == ops.FUNC) ):
            newListNodesList = []
            for oldListItem in node.listNodes:
                (retFuncName, retVarInfoObj) = self.getVarNameEntryFromAssignInfo_Wrapper(node, oldListItem)
                if ( (retFuncName == None) or (retVarInfoObj == None) ):
                    if (oldListItem in namesOfFutureDeclVars):
                        newListNodesList.append(oldListItem)
                    else:
                        sys.exit("traverseAssignBaseElemsOnlyRecursive in VarInfo.py:  call to getVarNameEntryFromAssignInfo() for node.getListNodesList() failed.")
                else:
                    baseElemsReplacement = retVarInfoObj.getAssignBaseElemsOnly()
                    if (baseElemsReplacement == None):
                        newListNodesList.append(oldListItem)
                    else:
                        newListNodesList.append(str(baseElemsReplacement))
            node.listNodes = newListNodesList

        if (node.left != None):
            retNodeLeft = self.traverseAssignBaseElemsOnlyRecursive(node.left)
            node.left = retNodeLeft
        if (node.right != None):
            retNodeRight = self.traverseAssignBaseElemsOnlyRecursive(node.right)
            node.right = retNodeRight

        return node

    def traverseAssignNode(self):
        if (self.assignNode == None):
            sys.exit("Attempting to run traverseAssignNode in VarInfo when self.assignNode is still None.")

        self.hasPairings = False
        self.protectsM = False

        if (self.assignNode.right.type == ops.LIST):
            self.isList = True
            self.type = ops.LIST
            onlyListElementsTypeDecl = self.isOnlyListElementsTypeDecl(self.assignNode.right)
            if (onlyListElementsTypeDecl != None):
                self.listElementsType = onlyListElementsTypeDecl
            else:
                addListNodesToList(self.assignNode.right, self.listNodesList)
        elif (self.assignNode.right.type == ops.SYMMAP):
            self.isSymmap = True
            self.type = ops.SYMMAP
            addListNodesToList(self.assignNode.right, self.listNodesList)
        elif ( (self.assignNode.right.type == ops.ON) and (self.assignNode.right.left.type == ops.PROD) ):
            dotProdObj = DotProd()
            dotProdObj.setDotProdObj(self.assignNode.right, self.lineNo, self.funcName)
            self.dotProdObj = dotProdObj
        elif (self.assignNode.right.type == ops.EXPAND):
            self.isExpandNode = True
        elif (self.assignNode.right.type == ops.RANDOM):
            self.isBaseElement = True
            self.assignBaseElemsOnly = self.assignNode.left
        elif (self.assignNode.right.type == ops.HASH):
            self.isBaseElement = True
            self.assignBaseElemsOnly = self.assignNode.left            
# JAA: activates the awesome symbolic executor!
#        if (self.assignBaseElemsOnly == None):
#            assignNodeRightDeepCopy = copy.deepcopy(self.assignNode.right)
#            newAssignBaseElemsOnlyNode = self.traverseAssignBaseElemsOnlyRecursive(assignNodeRightDeepCopy)
#            self.assignBaseElemsOnly = newAssignBaseElemsOnlyNode

        self.traverseAssignNodeRecursive(self.assignNode.right, False)

        if (M in self.varDeps):
            self.protectsM = True

    def setAssignNode(self, assignInfo, assignNode, funcName, outsideForLoopObj, outsideIfElseBranchObj, traverseAssignNode=True):
        if (type(assignNode).__name__ != BINARY_NODE_CLASS_NAME):
            sys.exit("Assignment node passed to VarInfo is invalid.")

        if ( (assignInfo == None) or (type(assignInfo) is not dict) ):
            sys.exit("assignInfo structure passed into setAssignNode of VarInfo.py is invalid.")

        self.initCall = False
        self.assignInfo = assignInfo
        self.assignNode = assignNode
        self.funcName = funcName
        self.outsideForLoopObj = outsideForLoopObj
        self.outsideIfElseBranchObj = outsideIfElseBranchObj

        if (getFullVarName(self.assignNode.left, False).find(LIST_INDEX_SYMBOL) != -1):
            self.hasListIndexSymInLeftAssign = True

        if traverseAssignNode:
            self.traverseAssignNode()

        self.beenSet = not(self.initCall)

        return (self.varDeps, self.hashArgsInAssignNode)

    def updateAssignNode(self, newNode):
        # can only update if assignNode was already set
        if self.assignNode == None: return None
        self.assignNode = newNode
        
    def setLineNo(self, lineNo):
        if ( (type(lineNo) is not int) or (lineNo < 1) ):
            sys.exit("Line number passed to VarInfo is invalid.")

        self.lineNo = lineNo
    
    def setLineStr(self, lineStr):
        if type(lineStr) != str:
            return
        
        tokens = lineStr.split(':=')
        if len(tokens) != 2:
            print("lineNo: ", self.lineNo)
            print("lineStr: ", lineStr)
            sys.exit("Latex symbol not formatted correctly.")
        
        tokens[0] = tokens[0].strip()
        tokens[1] = tokens[1].strip()
        self.lineStr = (tokens[0], tokens[1])

    def setIsTypeEntryOnly(self, isTypeEntryOnly):
        if (self.isTypeEntryOnly == True):
            sys.exit("setIsTypeEntryOnly in VarInfo.py has been set more than once.")

        if (isTypeEntryOnly != True):
            sys.exit("setIsTypeEntryOnly in VarInfo.py received input that is not valid.")

        self.isTypeEntryOnly = isTypeEntryOnly

    def setIsUsedInHashCalc(self, isUsedInHashCalc):
        if ( (isUsedInHashCalc != True) and (isUsedInHashCalc != False) ):
            sys.exit("setIsUsedInHashCalc in VarInfo.py:  isUsedInHashCalc parameter passed in is neither True nor False.")

        self.isUsedInHashCalc = isUsedInHashCalc

    def setListNodesList(self, newListNodesList):
        if ( (newListNodesList == None) or (type(newListNodesList) is not list) or (len(newListNodesList) == 0) ):
            sys.exit("setListNodesList in VarInfo.py:  problem with newListNodesList parameter passed in.")

        for newListItem in newListNodesList:
            if ( (newListItem == None) or (type(newListItem) is not str) or (len(newListItem) == 0) ):
                sys.exit("setListNodesList in VarInfo.py:  problem with one of the list members of the newListNodesList parameter passed in.")

        self.listNodesList = copy.deepcopy(newListNodesList)
