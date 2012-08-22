#!/usr/bin/python

from pyparsing import *
from charm.toolbox.node import *
import string

objStack = []

def createAttribute(s, loc, toks):
    if toks[0] == '!':
        newtoks = ""
        for i in toks:
            newtoks += i
        return BinNode(newtoks)
    return BinNode(toks[0]) # create

# convert 'attr < value' to a binary tree based on 'or' and 'and'
def parseNumConditional(s, loc, toks):
    print("print: %s" % toks)
    return BinNode(toks[0])

def printStuff(s, loc, toks):
    print("print: %s" % toks)
    return toks
        
def pushFirst( s, loc, toks ):
    objStack.append( toks[0] )

def createTree(op, node1, node2):
    if(op == "or"):
        node = BinNode(OpType.OR)
    elif(op == "and"):
        node = BinNode(OpType.AND)
    else:
        return None
    node.addSubNode(node1, node2)
    return node

class PolicyParser:
    def __init__(self, verbose=False):
        self.finalPol = self.getBNF()
        self.verbose = verbose

    def getBNF(self):
        # supported operators => (OR, AND, <
        OperatorOR = Literal("OR").setParseAction(downcaseTokens) | Literal("or")
        OperatorAND = Literal("AND").setParseAction(downcaseTokens) | Literal("and")
        Operator = OperatorAND | OperatorOR
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        BinOperator = Literal("<=") | Literal(">=") | Literal("==") | Word("<>", max=1)

        # describes an individual leaf node
        leafNode =  (Optional("!") + Word(alphanums+'-_./\?!@#$^&*%')).setParseAction( createAttribute )
        # describes expressions such as (attr < value)
        leafConditional = (Word(alphanums) + BinOperator + Word(nums)).setParseAction( parseNumConditional )

        # describes the node concept
        node = leafConditional | leafNode 

        expr = Forward()
        term = Forward()
        atom = lpar + expr + rpar | (node).setParseAction( pushFirst )
        term = atom + ZeroOrMore((Operator + term).setParseAction( pushFirst ))
        expr << term + ZeroOrMore((Operator + term).setParseAction( pushFirst ))
        finalPol = expr#.setParseAction( printStuff )
        return finalPol
    
    def evalStack(self, stack):
        op = stack.pop()
        if op in ["or", "and"]:
            op2 = self.evalStack(stack)
            op1 = self.evalStack(stack)
            return createTree(op, op1, op2)
        else:
            # Node value (attribute)
            return op
    
    def parse(self, string):
        global objStack
        del objStack[:]
        self.finalPol.parseString(string)
        return self.evalStack(objStack)

    def findDuplicates(self, tree, _dict):
        if tree.left: self.findDuplicates(tree.left, _dict)
        if tree.right: self.findDuplicates(tree.right, _dict)
        if tree.getNodeType() == OpType.ATTR:
            key = tree.getAttribute()
            if _dict.get(key) == None: _dict[ key ] = 1
            else: _dict[ key ] += 1

    def labelDuplicates(self, tree, _dictLabel):
        if tree.left: self.labelDuplicates(tree.left, _dictLabel)
        if tree.right: self.labelDuplicates(tree.right, _dictLabel)
        if tree.getNodeType() == OpType.ATTR:
            key = tree.getAttribute()
            if _dictLabel.get(key) != None: 
                tree.index = _dictLabel[ key ]
                _dictLabel[ key ] += 1
                
    def prune(self, tree, attributes):
        """given policy tree and attributes, determine whether the attributes satisfy the policy.
           if not enough attributes to satisfy policy, return None otherwise, a pruned list of
           attributes to potentially recover the associated secret.
        """
        (policySatisfied, prunedList) = self.requiredAttributes(tree, attributes)
#        print("pruned attrs: ", prunedList)
#        if prunedList:
#            for i in prunedList:
#                print("node: ", i)
        if not policySatisfied:
            return policySatisfied        
        return prunedList

    def requiredAttributes(self, tree, attrList):
        """ determines the required attributes to satisfy policy tree and returns a list of BinNode
        objects."""
        if tree == None: return 0
        Left = tree.getLeft()
        Right = tree.getRight()
        if Left: resultLeft, leftAttr = self.requiredAttributes(Left, attrList)
        if Right: resultRight, rightAttr = self.requiredAttributes(Right, attrList)
                
        if(tree.getNodeType() == OpType.OR):
            # never return both attributes, basically the first one that matches from left to right
            if resultLeft: sendThis = leftAttr
            elif resultRight: sendThis = rightAttr
            else: sendThis = None

            result = (resultLeft or resultRight)
            if result == False: return (False, sendThis)            
            return (True, sendThis)
        if(tree.getNodeType() == OpType.AND):
            if resultLeft and resultRight: sendThis = leftAttr + rightAttr
            elif resultLeft: sendThis = leftAttr
            elif resultRight: sendThis = rightAttr
            else: sendThis = None

            result = (resultLeft and resultRight)
            if result == False: return (False, sendThis)
            return (True, sendThis)
            
        elif(tree.getNodeType() == OpType.ATTR):
            if(tree.getAttribute() in attrList):
                return (True, [tree])
            else:
                return (False, None)
            
        return
    
if __name__ == "__main__":
    # policy parser test cases 
    parser = PolicyParser()
    attrs = ['1', '3']
    print("Attrs in user set: ", attrs)    
    tree1 = parser.parse("(1 or 2) and (2 and 3))")
    print("case 1: ", tree1, ", pruned: ", parser.prune(tree1, attrs))        
    
    tree2 = parser.parse("1 or (2 and 3)")
    print("case 2: ", tree2, ", pruned: ", parser.prune(tree2, attrs))
    
    tree3 = parser.parse("(1 or 2) and (4 or 3)")
    print("case 3: ", tree3, ", pruned: ", parser.prune(tree3, attrs))
    
