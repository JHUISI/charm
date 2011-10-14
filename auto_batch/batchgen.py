from batchlang import *
from batchparser import *
import sys

class PrintLambdaStatement:
    def __init__(self, constants):
        self.consts = constants
        self.var_key = string.ascii_lowercase 
        self.var_dict = {}
        self.order = []
        self.ctr = 0
    
    def visit(self, node, data):
        pass

    def visit_attr(self, node, data):
        if node.attr_index:
            # extract attribute
#           print("replace => ", node.attr)
           self.var_dict[self.var_key[self.ctr]] = node.attr
           self.order.append(node.attr)
           node.attr = self.var_key[self.ctr]
           self.ctr += 1 # move on to next alphabet 
        # for constants the variables get mapped when the lambda is defined, thus we do not require
        # special processing to make anything work.
    
    def isConstant(self, node):        
        for n in self.consts:
            if n.getAttribute() == node.getAttribute(): return True
        return False


    def args(self):
        if self.order:
            result = ""
            for i in self.order:
                result += i + ","
            result = result.rstrip(',')
            return result
        return None
    
    # handles arguments used to instantiate the lambda
    # i, a, b, c,... where i represents the counter to N (signatures), and
    # a,b,c represents the number of arguments expected by the labmda.
    def vars(self):
        if self.ctr > 0:
            result = "i," # to account for iterating through list
            for i in range(0, self.ctr):
                result += self.var_key[i] + ","
            result = result.rstrip(',') # remove last comma
            result += ": " # denotes end of argument list for lambda arguments
            return result
        return None

class CodeGenerator:
    def __init__(self, constants, variables, verify_stmt):
        self.consts = constants
        self.vars   = variables
        self.verify  = verify_stmt
    
    def print_batchverify(self):
        # 
        return self.print_statement(self.verify)
    
    def print_statement(self, node):
        if node == None:
            return None
        elif(node.type == ops.ATTR):
            msg = node.attr
            if node.attr_index != None:
                msg += '[' + str(node.attr_index) + ']'
            return msg
        elif(node.type == ops.TYPE):
            return str(node.attr)
        else:
            left = self.print_statement(node.left)
            right = self.print_statement(node.right)
            
            if debug >= levels.some:
               print("Operation: ", node.type)
               print("Left operand: ", left)
               print("Right operand: ", right)            
            if(node.type == ops.EXP):
                return ("(" + left + ' ** ' + right + ")")
            elif(node.type == ops.MUL):
                return ('(' + left + ' * ' + right + ')')
            elif(node.type == ops.EQ):
                return (left + ' = ' + right)
            elif(node.type == ops.EQ_TST):
                return (left + ' == ' + right)
            elif(node.type == ops.PAIR):
                return ('pair(' + left + ',' + right + ')')
            elif(node.type == ops.HASH):
                return ('group.hash(' + left + "," + right + ')')
#                return ('group.hash(' + left + ')')
            elif(node.type == ops.PROD):
                left = str(node.left.right) # we don't need the EQ node here
                return ('dotprod(' + left + ', ' + right)
            elif(node.type == ops.ON):
                 pls = PrintLambdaStatement(self.consts)
                 ASTVisitor(pls).inorder(node.right)
                 right = self.print_statement(node.right)
                 return (left + ", lambda " + pls.vars()  + right + ", " + pls.args() + ")")
            elif(node.type == ops.CONCAT):
                 return (left + ' + ' + right)
        return None    
    
    def print_dotprod(self):
        func = """
def dotprod(i, n, func, *args):
    prod = 1
    for j in range(i, n):
        prod *= func(j, *args)
    print("product =>", prod)
    return prod
"""
        # compile func and return ref?
        return func

if __name__ == "__main__":
    file = sys.argv[1]
    ast = parseFile(file)
    (const, verify, vars) = astParser(ast)

    # START
    print("\nVERIFY EQUATION =>", verify, "\n")
    verify2 = BinaryNode.copy(verify)
    ASTVisitor(CombineVerifyEq(const, vars)).preorder(verify2.right)
    ASTVisitor(SimplifyDotProducts()).preorder(verify2.right)

    print("\nStage 1: Combined Equation =>", verify2, "\n")
    ASTVisitor(SmallExponent(const, vars)).preorder(verify2.right)
    print("\nStage 2: Small Exp Test =>", verify2, "\n")
    ASTVisitor(Technique2(const, vars)).preorder(verify2.right)
    #ASTVisitor(Technique2(const, vars)).preorder(verify2.right)    
    print("\nStage 3: Apply tech 2 =>", verify2, "\n")
    ASTVisitor(Technique3(const, vars)).preorder(verify2.right)
    print("\nStage 4: Apply tech 3 =>", verify2, "\n")    
    # END 

    cg = CodeGenerator(const, vars, verify2.right)
    result = cg.print_batchverify()
    result = cg.print_statement(verify2.right)
    
    print("Result =>", result)
