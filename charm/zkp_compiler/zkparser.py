"""
Zero-Knowledge Statement Parser.

This module provides a parser for ZK proof statements using pyparsing.
It converts statements like "h = g^x" or "(h = g^x) and (j = g^y)" into
a binary tree representation for processing by the ZKP compiler.

Supported Syntax:
    - Single variable names: x, y, g, h (backwards compatible)
    - Multi-character variable names: x1, x2, alpha, beta, gamma (NEW in v0.61)
    - Exponentiation: g^x, g1^x1
    - Equality: h = g^x
    - Conjunction: (h = g^x) and (j = g^y)
    - Disjunction: (h = g^x) or (j = g^y)

Examples::

    parser = ZKParser()
    result = parser.parse("h = g^x")  # Single-char variables
    result = parser.parse("h1 = g1^x1")  # Multi-char variables
    result = parser.parse("commitment = generator^secret")  # Descriptive names
"""
from pyparsing import *
from charm.toolbox.zknode import *
import string
import sys

# Compatibility shim for pyparsing 3.x where upcaseTokens was moved to pyparsing_common
try:
    # pyparsing 2.x has upcaseTokens at module level
    upcaseTokens
except NameError:
    # pyparsing 3.x moved it to pyparsing_common
    try:
        from pyparsing import pyparsing_common
        upcaseTokens = pyparsing_common.upcase_tokens
    except (ImportError, AttributeError):
        # Fallback: define our own
        def upcaseTokens(s, loc, toks):
            return [t.upper() for t in toks]


def _set_parse_action(element, action):
    """Compatibility wrapper for setParseAction/set_parse_action."""
    if hasattr(element, 'set_parse_action'):
        return element.set_parse_action(action)
    else:
        return element.setParseAction(action)


def _parse_string(parser, string):
    """Compatibility wrapper for parseString/parse_string."""
    if hasattr(parser, 'parse_string'):
        return parser.parse_string(string)
    else:
        return parser.parseString(string)


objStack = []


def createNode(s, loc, toks):
    """Create a BinNode from a parsed token."""
    print('createNode => ', toks)
    return BinNode(toks[0])


# convert 'attr < value' to a binary tree based on 'or' and 'and'
def parseNumConditional(s, loc, toks):
    """Parse numeric conditional expressions."""
    print("print: %s" % toks)
    return BinNode(toks[0])


def debug(s, loc, toks):
    """Debug helper to print tokens."""
    print("print: %s" % toks)
    return toks


def markPublic(s, loc, toks):
    """Mark tokens as public variables."""
    print("public: %s" % toks)
    return toks


def markSecret(s, loc, toks):
    """Mark tokens as secret variables."""
    print("secret: %s" % toks)
    return toks


def pushFirst(s, loc, toks):
    """Push the first token onto the object stack."""
    # print("Pushing first =>", toks[0])
    objStack.append(toks[0])


def createTree(op, node1, node2):
    """
    Create a binary tree node for an operator.

    Args:
        op: The operator string ("OR", "AND", "^", "=")
        node1: Left child node
        node2: Right child node

    Returns:
        BinNode with the operator type and children
    """
    if op == "OR":
        node = BinNode(1)
    elif op == "AND":
        node = BinNode(2)
    elif op == "^":
        node = BinNode(3)
    elif op == "=":
        node = BinNode(4)
    else:
        return None
    node.addSubNode(node1, node2)
    return node


class ZKParser:
    """
    Parser for Zero-Knowledge proof statements.

    Converts ZK statements into binary tree representation for processing.

    Supports both single-character variables (legacy) and multi-character
    variable names (new in v0.61).

    Examples::

        parser = ZKParser()

        # Single-character variables (legacy, still supported)
        result = parser.parse("h = g^x")

        # Multi-character variables (new in v0.61)
        result = parser.parse("h1 = g1^x1")
        result = parser.parse("commitment = generator^secret")

        # Complex statements
        result = parser.parse("(h = g^x) and (j = g^y)")
        result = parser.parse("(pk1 = g^sk1) and (pk2 = g^sk2)")
    """

    def __init__(self, verbose=False):
        """
        Initialize the ZK parser.

        Args:
            verbose: If True, print debug information during parsing
        """
        self.finalPol = self.getBNF()
        self.verbose = verbose

    def getBNF(self):
        """
        Build the Backus-Naur Form grammar for ZK statements.

        Returns:
            pyparsing grammar object

        Grammar supports:
            - Variable names: alphanumeric starting with letter (e.g., x, x1, alpha)
            - Operators: ^, =, AND, OR
            - Parentheses for grouping
        """
        # supported operators => (OR, AND, <
        OperatorOR = Literal("OR") | _set_parse_action(Literal("or"), upcaseTokens)
        OperatorAND = Literal("AND") | _set_parse_action(Literal("and"), upcaseTokens)
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()

        ExpOp = Literal("^")
        Equality = Literal("=")  # | Literal("==") | Word("<>", max=1)
        Token = Equality | ExpOp
        Operator = OperatorAND | OperatorOR | Token

        # describes an individual leaf node
        # UPDATED in v0.61: Support multi-character variable names
        # Old: Word(alphas, max=1) - only single characters like x, y, g
        # New: Word(alphas, alphanums) - alphanumeric starting with letter
        #      Examples: x, x1, x2, alpha, beta, generator, secret
        leafNode = _set_parse_action(Word(alphas, alphanums), createNode)
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
        atom = lpar + expr + rpar | _set_parse_action(leafNode, pushFirst)

        # NEED TO UNDERSTAND THIS SEQUENCE AND WHY IT WORKS FOR PARSING ^ and = in logical order?!?
        # Place more value on atom [ ^ factor}, so gets pushed on the stack before atom [ = factor], right?
        # In other words, adds order of precedence to how we parse the string. This means we are parsing from right
        # to left. a^b has precedence over b = c essentially
        factor << atom + ZeroOrMore(_set_parse_action(ExpOp + factor, pushFirst))

        term = atom + ZeroOrMore(_set_parse_action(Operator + factor, pushFirst))
        # define placeholder set earlier with a 'term' + Operator + another term, where there can be
        # more than zero or more of the latter. Once we find a term, we first push that into
        # the stack, then if ther's an operand + term, then we first push the term, then the Operator.
        # so on and so forth (follows post fix notation).
        expr << term + ZeroOrMore(_set_parse_action(Operator + term, pushFirst))
        # final bnf object
        finalPol = expr#.setParseAction( debug )
        return finalPol
    
    # method for evaluating stack assumes operators have two operands and pops them accordingly
    def evalStack(self, stack):
        op = stack.pop()
#        print("op: %s" % op)
        if op in ["AND","OR", "^", "="]: # == "AND" or op == "OR" or op == "^" or op == "=":
            op2 = self.evalStack(stack)
            op1 = self.evalStack(stack)
            return createTree(op, op1, op2)
#            print("debug tree => ", res)
#            return res
        else:
            # Node value
            return op
    
    # main loop for parser. 1) declare new stack, then parse the string (using defined BNF) to extract all
    # the tokens from the string (not used for anything). 3) evaluate the stack which is in a post
    # fix format so that we can pop an OR, AND, ^ or = nodes then pull 2 subsequent variables off the stack. Then,
    # recursively evaluate those variables whether they are internal nodes or leaf nodes, etc.
    def parse(self, str):
        global objStack
        del objStack[:]
        tokens = _parse_string(self.finalPol, str)
        print("stack =>", objStack)
        return self.evalStack(objStack)
   
    # experimental - type checking 
    def type_check(self, node, pk, sk):
        if node.type == node.EXP:
            print("public =>", node.getLeft(), "in pk?", pk.get(node.getLeft()))
            print("secret =>", node.getRight(), "in sk?", sk.get(node.getRight()))
            
        elif node.type == node.EQ:
            print("public =>", node.getLeft(), "in pk?", pk.get(node.getLeft()))
            self.type_check(node.getRight(), pk, sk)
        elif node.type == node.AND:
            self.type_check(node.getLeft(), pk, sk)
            self.type_check(node.getRight(), pk, sk)
        else:
            return None
        return None
    
if __name__ == "__main__":
    print(sys.argv[1:])
    statement = sys.argv[1]

    parser = ZKParser()
    final = parser.parse(statement)
    print("Final statement:  '%s'" % final)
    pk = { 'g':1, 'h':2, 'j':3 }
    sk = { 'x':4, 'y':5 }
    parser.type_check(final, pk, sk)
