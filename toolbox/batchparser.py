from pyparsing import *
from batchlang import *
import string,sys

objStack = []

def createNode(s, loc, toks):
    print('createNode => ', toks)
    return BinaryNode(toks[0])

# convert 'attr < value' to a binary tree based on 'or' and 'and'
def parseNumConditional(s, loc, toks):
    print("print: %s" % toks)
    return BinaryNode(toks[0])

def markPublic(s, loc, toks):
    print("public: %s" % toks)
    return toks

def markSecret(s, loc, toks):
    print("secret: %s" % toks)
    return toks
        
def pushFirst( s, loc, toks ):
    if debug:
       print("Pushing first =>", toks[0])
    objStack.append( toks[0] )

def createTree(op, node1, node2):
#    if(op == "OR"):
#        node = BinNode(1)
#    elif(op == "AND"):
#        node = BinNode(2)
    if(op == "^"):
        node = BinaryNode(ops.EXP)
    elif(op == "*"):
        node = BinaryNode(ops.MUL)
    elif(op == ":="):
        node = BinaryNode(ops.EQ)
    elif(op == "=="):
        node = BinaryNode(ops.EQ_TST)
    elif(op == "e("):
        node = BinaryNode(ops.PAIR)
    # elif e( ... )
    else:    
        return None
    node.addSubNode(node1, node2)
    return node

class BatchParser:
    def __init__(self, verbose=False):
        self.finalPol = self.getBNF()
        self.verbose = verbose

    def getBNF(self):
        # supported operators => (OR, AND, <
        OperatorOR = Literal("OR") | Literal("or").setParseAction(upcaseTokens)
        OperatorAND = Literal("AND") | Literal("and").setParseAction(upcaseTokens)
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        ExpOp = Literal("^")
        MulOp = Literal("*")
        Equality = Literal(":=") | Literal("==") # | Word("<>", max=1)
        Pairing = Literal('e(') 
        Token = Equality | ExpOp | MulOp
        Operator = OperatorAND | OperatorOR | Token

        # describes an individual leaf node
        leafNode = Word(alphanums).setParseAction( createNode )
        # describes expressions such as (attr < value)
#        leafConditional = (Word(alphanums) + ExpOp + Word(nums)).setParseAction( parseNumConditional )

        # describes the node concept
        node = leafNode
#        secret = variable.setParseAction( markSecret )
#        public = variable.setParseAction( markPublic )

#        expr = public + Equality + public + ExpOp + secret.setParseAction( pushFirst )
        expr = Forward()
        term = Forward()
        factor = Forward()
        atom = (Pairing + expr + ',' + expr + rpar).setParseAction(pushFirst) | lpar + expr + rpar | (leafNode).setParseAction( pushFirst )

        # NEED TO UNDERSTAND THIS SEQUENCE AND WHY IT WORKS FOR PARSING ^ and = in logical order?!?
        # Place more value on atom [ ^ factor}, so gets pushed on the stack before atom [ = factor], right?
        # In other words, adds order of precedence to how we parse the string. This means we are parsing from right
        # to left. a^b has precedence over b = c essentially
        factor << atom + ZeroOrMore( ( ExpOp + factor ).setParseAction( pushFirst ) )
        
        term = atom + ZeroOrMore((Operator + factor).setParseAction( pushFirst ))
        # define placeholder set earlier with a 'term' + Operator + another term, where there can be
        # more than zero or more of the latter. Once we find a term, we first push that into
        # the stack, then if ther's an operand + term, then we first push the term, then the Operator.
        # so on and so forth (follows post fix notation).
        expr << term + ZeroOrMore((Operator + term).setParseAction( pushFirst ))
        # final bnf object
        finalPol = expr#.setParseAction( debug )
        return finalPol
    
    # method for evaluating stack assumes operators have two operands and pops them accordingly
    def evalStack(self, stack):
        op = stack.pop()
        if debug:
            print("op: %s" % op)
        if op in ["*", "^", ":=", "==", "e("]: # == "AND" or op == "OR" or op == "^" or op == "=":
            op2 = self.evalStack(stack)
            op1 = self.evalStack(stack)
            return createTree(op, op1, op2)
        else:
            # Node value
            return op
    
    # main loop for parser. 1) declare new stack, then parse the string (using defined BNF) to extract all
    # the tokens from the string (not used for anything). 3) evaluate the stack which is in a post
    # fix format so that we can pop an OR, AND, ^ or = nodes then pull 2 subsequent variables off the stack. Then,
    # recursively evaluate those variables whether they are internal nodes or leaf nodes, etc.
    def parse(self, str):
        # use lineCtr to track line of code.
        global objStack
        del objStack[:]
        tokens = self.finalPol.parseString(str)
        if debug:
           print("stack =>", objStack)
        return self.evalStack(objStack)
   
    # experimental - type checking 
#    def type_check(self, node):
#        if node.type == node.EXP:
#            print("public =>", node.getLeft(), "in pk?")
#            print("secret =>", node.getRight(), "in sk?")
            
#        elif node.type == node.EQ:
#            print("public =>", node.getLeft(), "in pk?")
#            self.type_check(node.getRight())
#        elif node.type == node.AND:
#            self.type_check(node.getLeft())
#            self.type_check(node.getRight())
        else:
            return None
        return None
    
if __name__ == "__main__":
    print(sys.argv[1:])
    statement = sys.argv[1]

    parser = BatchParser()
    final = parser.parse(statement)
    print("Final statement:  '%s'" % final)

