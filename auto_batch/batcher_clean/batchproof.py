# This class generates the latex macros for the batch verification proofs of security
import sdlpath
from sdlparser.SDLParser import *

header = """\n
\\catcode`\^ = 13 \def^#1{\sp{#1}{}}
\\newcommand{\\newln}{\\\&\quad\quad{}}
\\newcommand{\schemename}{{\sf %s}}
\\newcommand{\schemeref}{%s_proof}
\\newcommand{\schemecite}{\cite{REF}}
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
\\begin{equation}
%s
\end{equation}
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
            elif(node.type == ops.AND):
                 return ( left + " \mbox{ and } " + right )
        return None    


# 1. Finish rewriting proof generator for single equation sig schemes
# 2. Rewrite proof generator for multiple equation sig schemes and steps
# 3. Add index #s to delta when dealing with multiple delta exponents 
# 4. What else?
class GenerateProof:
    def __init__(self, single=True):
        self.single_mode = single
        self.lcg_data = {} 
        self.__lcg_steps = 0
        self.lcg = None
        
    def initLCG(self, constants, vars, sig_vars, latex_vars):
        if self.lcg == None:
            self.lcg = LatexCodeGenerator(constants, vars, latex_vars)
            self.constants = constants
            self.vars      = vars
            self.sig_vars  = sig_vars
            return True
        else:
            # init'ed already
            return False
        
    def setIndVerifyEq(self, equation):
        self.lcg_data['indiv'] = self.lcg.print_statement( equation )
        return
    
#    def setBatchVerifyEq(self, equation):
#        self.lcg_data['batch'] = self.lcg.print_statement( equation )
#        return
    def setStepOne(self, equation):
        if not self.single_mode: self.setNextStep('step1', equation)
        return
    
    def setNextStep(self, msg, equation):
        preq = None
        if self.single_mode:
            if msg == 'consolidate':
                msg = 'Consolidate the verification equations (technique 0)'
            elif msg == 'smallexponents':
                msg = 'Apply the small exponents test, using exponents $\delta_1, \dots \delta_\\numsigs \in \left[1, 2^\lambda\\right]$'
                preq = small_exp_label
            elif msg == 'finalbatcheq':                
                self.lcg_data[ self.__lcg_steps-1 ]['preq'] = final_batch_eq
                self.lcg_data['batch'] = self.lcg_data[ self.__lcg_steps-1 ]['eq']
                return
        else: # need to handle multiple equations mode differently!
            if msg in ['consolidate', 'smallexponents']:
                return
            elif msg == 'step1':
                msg = 'Consolidate the verification equations (technique 0), merge pairings with common first or second element (technique 6), and apply the small exponents test, using exponents $\delta_1, \dots \delta_\\numsigs \in \left[1, 2^\lambda\\right]$ for each equation'
            elif msg == "Move the exponent(s) into the pairing (technique 2)" and self.__lcg_steps == 1:
                msg = 'Combine $\\numsigs$ signatures (technique 1), move the exponent(s) in pairing (technique 2)'
            elif msg == 'finalbatcheq':                
                self.lcg_data[ self.__lcg_steps-1 ]['preq'] = final_batch_eq
                self.lcg_data['batch'] = self.lcg_data[ self.__lcg_steps-1 ]['eq']
                return
                
        self.lcg_data[ self.__lcg_steps ] = {'msg': msg, 'eq': self.lcg.print_statement( equation ), 'preq':preq }
#        if new_msg != None: self.lcg_data[ self.__lcg_steps ]['new_msg'] = new_msg
        self.__lcg_steps += 1
        return
    
    def proofHeader(self, title, const, sigs, indiv_eq, batch_eq):
        const_str = ""; sig_str = ""
        for i in const:
            const_str += self.lcg.getLatexVersion(i) + ","
        const_str = const_str[:len(const_str)-1]
        for i in sigs:
            sig_str += self.lcg.getLatexVersion(i) + ","
        sig_str = sig_str[:len(sig_str)-1]
        result = header % (title, title, const_str, sig_str, indiv_eq, batch_eq)
        #print("header =>", result)
        return result

    def proofBody(self, step, data):
        pre_eq = data.get('preq')
        cur_eq = data['eq']
        if pre_eq != None:
            result_eq = pre_eq + cur_eq
        else: result_eq = cur_eq    
        result = basic_step % (step, data['msg'], result_eq)
        #print('[STEP', step, ']: ', result)
        return result

    def writeConfig(self, latex_file):
        #f = open('verification_gen' + latex_file + '.tex', 'w')
        title = latex_file.upper()
        outputStr = self.proofHeader(title, self.constants, self.sig_vars, self.lcg_data['indiv'], self.lcg_data['batch'])
        for i in range(self.__lcg_steps):
            outputStr += self.proofBody(i+1, self.lcg_data[i])
        outputStr += footer
        #f.write(outputStr)
        #f.close()
        return outputStr
    
    def compileProof(self, latex_file):
        f = open('verification_gen' + latex_file + '.tex', 'w')
        output = self.writeConfig(latex_file)
        f.write(output)
        f.close()
        return True

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
