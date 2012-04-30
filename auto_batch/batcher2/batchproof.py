# This class generates the latex macros for the batch verification proofs of security
from batchlang import *
from batchparser import *
import sys

header = """\n
\\catcode`\^ = 13 \def^#1{\sp{#1}{}}
\\newcommand{\\newln}{\\\&\quad\quad{}}
\\newcommand{\schemename}{{\sf %s}}
\\newcommand{\pkvariables}{ %s }
\\newcommand{\sigvariables}{ %s }
\\newcommand{\indivverificationeqn}{ %s }

\\newcommand{\\batchverificationeqn}{ %s  }

\\newcommand{\gutsoftheproof}{
""" 
# pk variables : pk, g  (just print constants)
# sig variables : h,sig  (easy as well in signature variable)
# indiv eq => 'e(h,pk) = e(sig,g)' = easy
# batch eq => e(\prod_{j=1}^{\numsigs} h_j^{\delta_j},pk) = e(\prod_{j= 1}^\numsigs sig_j^{\delta_j},g) 
# needs => delta = {\delta_j}, \prod{j=1}^\numsigs == prod{j:=1, N}, 

basic_step = """\medskip \\noindent
{\\bf Step %d:} %s:
\\begin{multline}
%s
\end{multline}
""" # (step #, message of what we are doing, resulting equation)

small_exp_label = "\label{eqn:smallexponents}\n"
final_batch_eq  = "\label{eqn:finalequation}\n"
footer = "\n}\n"

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
    
class LatexCodeGenerator:
    def __init__(self, constants, variables, latex_info):
        self.consts = constants
        self.vars   = variables
        self.latex  = latex_info # used for substituting attributes
    
    def getLatexVersion(self, name):
        if self.latex != None and self.latex.get(name):
            return self.latex[ name ]
        return name
    
    def print_statement(self, node):
        if node == None:
            return None
        elif(node.type == ops.ATTR):
            msg = node.attr
            if 'delta' in str(msg):
                msg = '\delta'
            elif str(msg) =='N':
                msg = '\\numsigs'
            else:
                msg = self.getLatexVersion(str(msg))
#                if msg.find('_') != -1: msg = "{" + msg + "}" # prevent subscript
#            print("msg : ", msg)
            if node.attr_index != None:
                keys = ""
                if msg.find('_') != -1:
                    s = msg.split('_', 1)
                    #print("s : ", s)
                    for i in node.attr_index:
                        keys += i + ","
                    keys = keys[:len(keys)-1]
                    msg = s[0] + '_{' + keys + "," + s[1] + '}'
                    #print("msg :=", msgs)
                else:
                    for i in node.attr_index:
                        keys += i + ","
                    keys = keys[:len(keys)-1]
                    if len(node.attr_index) > 1:
                        msg += '_{' + keys + '}'
                    else:
                        msg += '_' + keys
                    msg = "{" + msg + "}"
#                    print("result: ", msg)
            if node.negated: msg = '-' + msg
#            print("msg2 : ", msg)
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
                if Type(node.left) == ops.EXP:
                    l = self.print_statement(node.left.left)
                    r = self.print_statement(node.left.right)
                    return ( l + "^{" + r + ' \cdot ' + right + "}")
                elif Type(node.left) in [ops.ATTR, ops.PAIR]:
                    if str(right) == "1": return left 
                    return ( left + '^{' + right + "}")
                return ("(" + left + ')^{' + right + "}")
            elif(node.type == ops.MUL):
                return ( left + ' \cdot ' + right)
            elif(node.type == ops.ADD):
                return ("("+ left + ' + ' + right + ")")
            elif(node.type == ops.SUB):
                return ("("+ left + ' - ' + right + ")")
            elif(node.type == ops.EQ):
                return (left + ' = ' + str(int(right) + 1)) 
            elif(node.type == ops.EQ_TST):
                return (left + ' \stackrel{?}{=} ' + right)
            elif(node.type == ops.PAIR):
                return ('e(' + left + ',' + right + ')')
            elif(node.type == ops.HASH):
                return ('H(' + left + ')')
            elif(node.type == ops.SUM):
                return ('\sum_{' + left + '}^{' + right + '}')
            elif(node.type == ops.PROD):
                return ('\prod_{' + left + '}^' + right)
            elif(node.type == ops.ON):
                return ("{" + left + " " + right + "}")
            elif(node.type == ops.OF):
                return ("{" + left + " " + right + "}")
            elif(node.type == ops.CONCAT):
                 return (left + ' | ' + right)
            elif(node.type == ops.FOR):
                return ('\\text{for }' + left + '\\text{ to }  ' + right)
            elif(node.type == ops.DO):
                 return ( left + ' \\text{ it holds: }  ' + right)
        return None    



#if __name__ == "__main__":
#    file = sys.argv[1]
#    ast = parseFile(file)
#    (const, verify, vars) = astParser(ast)
#
#    # START
#    print("\nVERIFY EQUATION =>", verify, "\n")
#    verify2 = BinaryNode.copy(verify)
#    ASTVisitor(CombineVerifyEq(const, vars)).preorder(verify2.right)
#    ASTVisitor(SimplifyDotProducts()).preorder(verify2.right)
#
#    print("\nStage 1: Combined Equation =>", verify2, "\n")
#    ASTVisitor(SmallExponent(const, vars)).preorder(verify2.right)
#    print("\nStage 2: Small Exp Test =>", verify2, "\n")
#    ASTVisitor(Technique2(const, vars)).preorder(verify2.right)
#    #ASTVisitor(Technique2(const, vars)).preorder(verify2.right)    
#    print("\nStage 3: Apply tech 2 =>", verify2, "\n")
#    ASTVisitor(Technique3(const, vars)).preorder(verify2.right)
#    print("\nStage 4: Apply tech 3 =>", verify2, "\n")    
#    # END 

#    cg = CodeGenerator(const, vars, verify2.right)
#    result = cg.print_batchverify()
#    result = cg.print_statement(verify2.right)
    
#    print("Result =>", result)
