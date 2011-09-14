from pyparsing import *
#from batchlang import *
from batchgen import *
import string,sys

test_run = False
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
    if debug >= levels.some:
       print("Pushing first =>", toks[0])
    objStack.append( toks[0] )

def createTree(op, node1, node2):
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
    elif(op == "H("):
        node = BinaryNode(ops.HASH)
    elif(op == "prod{"):
        node = BinaryNode(ops.PROD)
    elif(op == "on"):
        # can only be used in conjunction w/ PROD (e.g. PROD must precede it)        
        node = BinaryNode(ops.ON) 
    elif(op == "|"):
        node = BinaryNode(ops.CONCAT)
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
        # supported operators => (OR, AND, <, prod{
        #OperatorOR = Literal("OR") | Literal("or").setParseAction(upcaseTokens)
        #OperatorAND = Literal("AND") | Literal("and").setParseAction(upcaseTokens)
        lpar = Literal("(").suppress() | Literal("{").suppress()
        rpar = Literal(")").suppress() | Literal("}").suppress()
        rcurly = Literal("}").suppress()

        MulOp = Literal("*")
        Concat = Literal("|")
        ExpOp = Literal("^")
        BinOp = ExpOp | MulOp | Concat
        Equality = Literal("==") # | Word("<>", max=1)
        Assignment =  Literal(":=")
        Pairing = Literal('e(') # Pairing token
        Hash = Literal('H(')
        Prod = Literal("prod{") # dot product token
        ProdOf = Literal("on")
        # captures order of parsing token operators
        Token = Equality | ExpOp | MulOp | ProdOf | Concat | Assignment
        Operator = Token 
        #Operator = OperatorAND | OperatorOR | Token

        # describes an individual leaf node
        leafNode = Word(alphanums + '_').setParseAction( createNode )
        expr = Forward()
        term = Forward()
        factor = Forward()
        atom = (Hash + expr + rpar).setParseAction( pushFirst ) | \
               (Pairing + expr + ',' + expr + rpar).setParseAction( pushFirst ) | \
               (Prod + expr + ',' + expr + rcurly).setParseAction( pushFirst ) | \
               lpar + expr + rpar | (leafNode).setParseAction( pushFirst )

        # NEED TO UNDERSTAND THIS SEQUENCE AND WHY IT WORKS FOR PARSING ^ and = in logical order?!?
        # Place more value on atom [ ^ factor}, so gets pushed on the stack before atom [ = factor], right?
        # In other words, adds order of precedence to how we parse the string. This means we are parsing from right
        # to left. a^b has precedence over b = c essentially
        #factor << atom + ZeroOrMore( ( ExpOp + factor ).setParseAction( pushFirst ) )
        factor << atom + ZeroOrMore( ( BinOp + factor ).setParseAction( pushFirst ) )
        
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
        if debug >= levels.some:
            print("op: %s" % op)
        if op in ["*", "^", ":=", "==", "e(", "prod{", "on", "|"]: # == "AND" or op == "OR" or op == "^" or op == "=":
            op2 = self.evalStack(stack)
            op1 = self.evalStack(stack)
            return createTree(op, op1, op2)
        elif op in ["H("]:
            op1 = self.evalStack(stack)
            return createTree(op, op1, None)
        else:
            # Node value
            return op
    
    # main loop for parser. 1) declare new stack, then parse the string (using defined BNF) to extract all
    # the tokens from the string (not used for anything). 3) evaluate the stack which is in a post
    # fix format so that we can pop an OR, AND, ^ or = nodes then pull 2 subsequent variables off the stack. Then,
    # recursively evaluate those variables whether they are internal nodes or leaf nodes, etc.
    def parse(self, line):
        # use lineCtr to track line of code.
        if len(line) == 0 or line[0] == '#': 
#            print("comments or empty strings will be ignored.")
            return None 
        global objStack
        del objStack[:]
        tokens = self.finalPol.parseString(line)
        if debug >= levels.some:
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
#        else:
#            return None
#        return None
def parseFile(filename):
    fd = open(filename, 'r')
    ast_tree = []
    parser = BatchParser()
    code = fd.readlines(); i = 1
    for line in code:
        line = line.strip('\n')
        if len(line) == 0 or line[0] == '#':
            if debug == levels.all: print(line)
            continue
        ast_node = parser.parse(line)
        print(i, ":", ast_node)
        ast_tree.append(ast_node)
        # ast_tree[i] = ast_node # store for later processing        
        i += 1
    fd.close()
    return ast_tree

# Takes the tree and iterates through each line 
# and verifies X # of rules. This serves to notify
# the user on any errors that might have been made in
# specifying the batch inputs.
def astSyntaxChecker(astTree):
    pass

# Perform some type checking here?
# rules: find constants, verify, variable definitions
def astParser(astList):
    constants = []
    verify_eq = None
    variables = {}
    
    for i in astList:
        s = str(i.left)
        if s == 'constant':
            constants.append(i.right)
        elif s == 'verify':
            verify_eq = i
        else:
            variables[s] = str(i.right)

    return (constants, verify_eq, variables)

class ASTIterator:
    def __init__(self, _node, _type):
        self.cur_node = _node
        self.of_type = _type
    
    def __iter__(self):
        # if we've found a match
        if self.cur_node.type == _type:
            return self.cur_node
        else:
            self.cur_node = self.cur_node.right
    
    def next(self):
        if self.cur_node:
            raise StopIteration
        else:
            self.cur_node = _node.right

# decorator for selecting which operation to call on 
# each node visit...
class dispatch(object):
    def __init__(self, target=None):
#        print("initialized dispatcher...")
        self.target = target
        self.default = 'visit'        
        #self.meths = {}; 
        self.hit = 0
    
    def __call__(self, visitor, *args):
        def wrapped_func(*args):
            try:
                name = str(args[0].type)
                #print("dispatch for => visit_", name.lower())
                func_name = 'visit_' + name.lower()
                if hasattr(visitor, 'cache') and visitor.cache.get(func_name) == None:
                    meth = getattr(visitor, func_name, self.default)
                    if meth == self.default:
                        meth = getattr(visitor, self.default)
                    visitor.cache[func_name] = meth # cache for next call
                    meth(*args)
                else:
                    # call cached function
                    self.hit += 1
                    # print("hitting cache: ", self.hit) 
                    visitor.cache[func_name](*args)
            except Exception as e:
                print(e)

        return wrapped_func(*args)

class ASTVisitor(object):
    def __init__(self, visitor):    
        self.visitor = visitor
        if not hasattr(self.visitor, 'visit'):
            raise Exception("No generic visit method defined in AST operation class")
        if not hasattr(self.visitor, 'cache'):
            self.visitor.cache = {} # for caching funcs
        # pointers to other parts of the tree
        # allows for keeping track of where we are in
        # AST.

    @dispatch
    def visit(self, visitor, node, info):
        """Generic visit function or sub nodes"""
        return
        
    def preorder(self, root_node, parent_node=None, sib_node=None):
        if root_node == None: return None
        # if parent_node == None: parent_node = root_node
        info = { 'parent': parent_node, 'sibling': sib_node }
        self.visit(self.visitor, root_node, info) 
        self.preorder(root_node.left, root_node, root_node.right)
        self.preorder(root_node.right, root_node, root_node.left)
    
    def postorder(self, root_node, parent_node=None, sib_node=None):
        if root_node == None: return None
        # if parent_node == None: parent_node = root_node
        info = { 'parent': parent_node, 'sibling': sib_node }
        self.postorder(root_node.left, root_node, root_node.right)
        self.postorder(root_node.right, root_node, root_node.left)
        self.visit(self.visitor, root_node, info)
    
    def inorder(self, root_node, parent_node=None, sib_node=None):
        if root_node == None: return None
        # if parent_node == None: parent_node = root_node        
        info = { 'parent': parent_node, 'sibling': sib_node }
        self.inorder(root_node.left, root_node, root_node.right)
        self.visit(self.visitor, root_node, info)
        self.inorder(root_node.right, root_node, root_node.left)


def addAsChildNodeToParent(data, target_node):
    if data['parent'].right == data['sibling']:
        data['parent'].left = target_node
    else:
        data['parent'].right = target_node              

class ASTOperations:
    def __init__(self):
        pass

    def visit(self, node, data):
        pass
#    def visit_pair(self, node, data):
#        print("Visit : pair =>", node.type)
#        if data['parent']: print("my parent =>", data['parent'].type, "\n")        
#        return None
#
#    def visit_exp(self, node, data):
#        print("Visit : exp =>", node.type)
#        if data['parent']: print("my parent =>", data['parent'].type, "\n")        
#        return None
        
    def visit_attr(self, node, data):
#        node.attr_index = 'j'
#        print("Visit : attr =>", node.type)
#        if data['parent']: print("my parent =>", data['parent'].type, "\n")        
        return None

#    def visit_eq(self, node, data):
#        print("Visit : eq =>", node.type)
#        if data['parent']: print("my parent =>", data['parent'].type, "\n")        
#        return None
        
class CombineVerifyEq:
    def __init__(self, constants, variables):
        self.consts = constants
        self.vars = variables
    
    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        if node.left.type == ops.PAIR:
            prod = self.newProdNode()
            prod.right = node
            addAsChildNodeToParent(data, prod)
    
    def visit_pair(self, node, data):
        if data['parent'].type == ops.EXP:
            pass
        else:
            prod = self.newProdNode()
            prod.right = node
            addAsChildNodeToParent(data, prod)
    
    def visit_hash(self, node, data):
        if node.left.type == ops.ATTR:
            # save me and parent for future use
            self.hash_node = { 'node': node, 'parent':data['parent'], 
                               'sibling':data['sibling'] }
            
    def visit_attr(self, node, data):
        if not self.isConstant(node):
            node.setAttrIndex('i') # add index to each attr that isn't constant
#            prod = self.newProdNode()
#            if data['parent'].type != ops.HASH:
#                prod.right = node
#                # add new node to prod{i=1, N} on cur_node            
#                addAsChildNodeToParent(data, prod)
#            else:
#                # if hash node above is parent we visited: then proceed
#                # to retrieve the parent of that hash node
#                if self.hash_node['node'] == data['parent']:
#                    prod.right = data['parent']
#                    addAsChildNodeToParent(self.hash_node, prod)                    
    
    def newProdNode(self):
        p = BatchParser()
        new_node = p.parse("prod{i:=1, N} on x")
        return new_node

    def isConstant(self, node):        
        for n in self.consts:
            if n.getAttribute() == node.getAttribute(): return True
        return False

# Adds an exponent to a \delta to every pairing node
class SmallExponent:
    def __init__(self, constants, variables):
        self.consts = constants
        self.vars   = variables
    
    def visit(self, node, data):
        pass

    def visit_pair(self, node, data):
#        if data['parent'].type != ops.EXP:
        new_node = self.newExpNode()
        new_node.left = node
        new_node.right = BinaryNode("delta_i")
            #print("new node =>", new_node)  
        addAsChildNodeToParent(data, new_node)
    
    def newExpNode(self):
        p = BatchParser()
        _node = p.parse("a ^ b_i")
        return _node

class Technique2:
    def __init__(self, constants, variables, group='G1'):
        self.consts = constants
        self.vars   = variables
        print("Rule 2: Move the exponent(s) into the pairing")
        self.group = group # can orogrammatically set which group we move exponent into
        # TODO: pre-processing to determine context of how to apply technique 2...here?
        # TODO: in cases of chp.bv, where you have multiple exponents outside a pairing, move them all into the e().
    
    def visit(self, node, data):
        pass

    # detect rule: e(g, h)^d_i ==> e(g^d_i, h)
    def visit_exp(self, node, data):
        # print("left node =>", node.left.type,"target right node =>", node.right)
        if(node.left.type == ops.PAIR):   # and (node.right.attr_index == 'i'): # (node.right.getAttribute() == 'delta'):
            pair_node = node.left
            addAsChildNodeToParent(data, pair_node) # move pair node one level up
                                  # make cur node the left child of pair node
            # G1 : pair.left, G2 : pair.right
            self.isConstInSubtree(pair_node.left)
            if not self.const_result:
                node.left = pair_node.left
                pair_node.left = node
            
            self.isConstInSubtree(pair_node.right)
            if not self.const_result:
                node.left = pair_node.right
                pair_node.right = node    
        elif(node.left.type == ops.ON):
            # check whether prod right
            prod_node = node.left
            addAsChildNodeToParent(data, prod_node)
            
            # blindly make the exp node the right child of whatever
            # node
            some_node = prod_node.right
            prod_node.right = node
            node.left = some_node

    def isConstInSubtree(self, node): # check whether left or right node is constant  
        if not node: return
        if node.type == ops.ATTR:
            self.const_result = self.isConstant(node)
            return
        self.isConstInSubtree(node.left)
        self.isConstInSubtree(node.right)

    def isConstant(self, node):        
        for n in self.consts:
            if n.getAttribute() == node.getAttribute(): return True
        return False


class Technique3:
    def __init__(self, constants, variables, group='G1'):
        self.consts = constants
        self.vars   = variables
        self.group  = group
        print("Rule 3: When two pairings with common 1st or 2nd element appear, then can be combined. n pairs to 1.")
    
    def visit(self, node, data):
        pass
    
    def visit_on(self, node, data):
        if node.right.type == ops.PAIR:
            pair_node = node.right
            addAsChildNodeToParent(data, pair_node) # move pair one level up
            
            self.isConstInSubtree(pair_node.left)
            if not self.const_result:  # if F, then can apply prod node to left child of pair node              
                node.right = pair_node.left
                pair_node.left = node # pair points to 'on' node
            
            self.isConstInSubtree(pair_node.right)
            if not self.const_result:
                node.right = pair_node.right
                pair_node.right = node
    
    def isConstInSubtree(self, node): # check whether left or right node is constant  
        if not node: return
        if node.type == ops.ATTR:
            # set appropriate field when we've found an attribute we can check
            self.const_result = self.isConstant(node)
            return
        self.isConstInSubtree(node.left)
        self.isConstInSubtree(node.right)

    def isConstant(self, node):        
        for n in self.consts:
            if n.getAttribute() == node.getAttribute(): return True
        return False

        
if __name__ == "__main__":
    if test_run:
        print(sys.argv[1:])
        statement = sys.argv[1]
        parser = BatchParser()
        final = parser.parse(statement)
        print("Final statement:  '%s'" % final)

    
    # print(ast)
    file = sys.argv[1]
    ast = parseFile(file)
    (const, verify, vars) = astParser(ast)
    print("Constants =>", const)
    print("Variables =>", vars)

    verify2 = BinaryNode.copy(verify)
    ASTVisitor(CombineVerifyEq(const, vars)).preorder(verify2.right)
    ASTVisitor(ASTOperations()).preorder(verify)
    print("\nVERIFY EQUATION =>", verify, "\n")
    print("\nStage 1: Combined Equation =>", verify2, "\n")
    ASTVisitor(SmallExponent(const, vars)).preorder(verify2.right)
    print("\nStage 2: Small Exp Test =>", verify2, "\n")
    ASTVisitor(Technique2(const, vars)).preorder(verify2.right)
    ASTVisitor(Technique2(const, vars)).preorder(verify2.right)    
    print("\nStage 3: Apply tech 2 =>", verify2, "\n")
    ASTVisitor(Technique3(const, vars)).preorder(verify2.right)
    print("\nStage 4: Apply tech 3 =>", verify2, "\n")    
    
    cg = CodeGenerator(const, vars, verify2.right)
    result = cg.print_batchverify()
#    result = cg.print_statement(verify2.right)    
    print("Python => '%s'" % result) # should be able to compile this