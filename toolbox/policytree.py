#!/usr/bin/python

from pyparsing import *
from toolbox.node import *
import string

objStack = []

def createNode(s, loc, toks):
    if toks[0] == '!':
        newtoks = ""
        for i in toks:
            newtoks += i
        return BinNode(newtoks)
    return BinNode(toks[0])

# convert 'attr < value' to a binary tree based on 'or' and 'and'
def parseNumConditional(s, loc, toks):
    print("print: %s" % toks)
    return BinNode(toks[0])

def debug(s, loc, toks):
    print("print: %s" % toks)
    return toks
        
def pushFirst( s, loc, toks ):
    objStack.append( toks[0] )

def createTree(op, node1, node2):
    if(op == "OR"):
        node = BinNode(1)
    elif(op == "AND"):
        node = BinNode(2)
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
        OperatorOR = Literal("OR") | Literal("or").setParseAction(upcaseTokens)
        OperatorAND = Literal("AND") | Literal("and").setParseAction(upcaseTokens)
        Operator = OperatorAND | OperatorOR
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        BinOperator = Literal("<=") | Literal(">=") | Literal("==") | Word("<>", max=1)

        # describes an individual leaf node
        leafNode =  (Optional("!") + Word(alphanums)).setParseAction( createNode )
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
        if op == "AND" or op == "OR":
            op2 = self.evalStack(stack)
            op1 = self.evalStack(stack)
            return createTree(op, op1, op2)
        else:
            # Node value
            return op
    
    def parse(self, str):
        global objStack
        del objStack[:]
        policy = self.finalPol.parseString(str)
        return self.evalStack(objStack)

    # determine whether subset will satisfy
    # the tree
    def prune(self, tree, list):
        global new_list
        new_list = []
        self.verifyExistence(tree, list, new_list)
        return new_list

        
    def verifyExistence(self, tree, list, n_list):        
        if(tree == None):
            return 0
        # if AND-gate, both nodes must be in list if attr's
        if(tree.getNodeType() == tree.ATTR):
            leaf = tree.getAttribute()
            if(list.count(leaf) == 1):
                n_list.append(leaf)
            return list.count(leaf)
        
        # check OR and AND gates
        result1 = self.verifyExistence(tree.getLeft(), list, n_list)
        if result1 == 1 and tree.getNodeType() == tree.OR:
           # if OR case and we found an attribute, then just end search
           return result1     
        result2 = self.verifyExistence(tree.getRight(), list, n_list)
        if result2 == 1 and tree.getNodeType() == tree.OR:
           return result2
        elif result1 == 1 and result2 == 1 and tree.getNodeType() == tree.AND:
            return result1 + result2
        return 0
        
    
