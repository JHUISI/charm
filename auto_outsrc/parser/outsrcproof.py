# This class generates the latex macros for the batch verification proofs of security
import sdlpath, re, string
from SDLang import *

hashtag = '#'
underscore = '_'
header = """\n
\\catcode`\^ = 13 \def^#1{\sp{#1}{}}
\\newcommand{\\newln}{\\\&\quad\quad{}}
\\newcommand{\schemename}{{\sf %s}}
\\newcommand{\schemeref}{%s_proof}
\\newcommand{\schemecite}{\cite{REF}}
\\newcommand{\secretkey}{ %s }
\\newcommand{\listofbfs}{ %s }
\\newcommand{\listofmskvalues}{ %s }
\\newcommand{\listofrandomvalues}{ %s }
\\newcommand{\keydefinitions}{ %s }
\\newcommand{\originalkey}{ %s }
\\newcommand{\\transformkey}{ %s }
\\newcommand{\pseudokey}{ %s }
"""
# schemename - title
# schemeref - title
# list of msk 
# list of random values
# key definitions
# original key
# transform key

proof_header = """\n
\\newcommand{\gutsoftheproof}{
""" 
proof_footer = "\n}\n"
# pk variables : pk, g  (just print constants)
# sig variables : h,sig  (easy as well in signature variable)
# indiv eq => 'e(h,pk) = e(sig,g)' = easy
# batch eq => e(\prod_{j=1}^{\numsigs} h_j^{\delta_j},pk) = e(\prod_{j= 1}^\numsigs sig_j^{\delta_j},g) 
# needs => delta = {\delta_j}, \prod{j=1}^\numsigs == prod{j:=1, N}, 

basic_step = """\medskip \\noindent
{\\bf %s Step %d:} %s:
\\begin{equation}
%s
\end{equation}
""" # (step #, message of what we are doing, resulting equation)

#small_exp_label = "\label{eqn:smallexponents}\n"
#final_batch_eq  = "\label{eqn:finalequation}\n"

main_proof_header_standalone = """\n"""
    
class LatexCodeGenerator:
    def __init__(self):
        self.latexVars  = {'alpha':'\\alpha', 'beta':'\beta', 'gamma':'\gamma', 'delta':'\delta', 'epsilon':'\epsilon',
             'zeta':'\zeta', 'eta':'\eta', 'Gamma':'\Gamma', 'Delta':'\Delta', 'theta':'\theta', 
             'kappa':'\kappa', 'lambda':'\lambda', 'mu':'\mu', 'nu':'\\nu', 'xi':'\\xi', 'sigma':'\\sigma',
             'tau':'\\tau', 'phi':'\phi', 'chi':'\\chi', 'psi':'\psi', 'omega':'\omega'}
        
    def getLatexVersion(self, name):
        if name.find(hashtag) != -1: # matches words separated by hashtags. x#1 => 'x_1'
            return name.replace(hashtag, underscore)
        else:
            # matches word + numbers => 'x1' => 'x_1'
            res = re.findall(r"[a-zA-Z]+|\d+", name)
            if len(res) == 2:
                return name.replace(res[0] + res[1], res[0] + "_" + res[1])
            else:
                for i,j in self.latexVars.items():
                    if i in name: return name.replace(i, j)
#            return self.latexVars.get(name)
        return name    
    
    def print_statement(self, node, parent=None):
        if node == None:
            return None
        elif(node.type == ops.ATTR):
            msg = node.attr
            msg = self.getLatexVersion(str(msg))
            if node.delta_index != None and 'delta' in node.attr:
#                print("Found IT!!!")
                msg = msg + '_{' + node.delta_index[0] + '}'
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
            left = self.print_statement(node.left, node)
            right = self.print_statement(node.right, node)

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
                if parent != None and parent.type == ops.PROD:
                    return (left + ' = ' + str(right).replace("0", "1"))
                else:
                    return (left + ' = ' + str(right))
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
            elif(node.type == ops.OR):
                 return ( left + " \mbox{ or } " + right )
             
        return None

class GenerateProof:
    def __init__(self):
        self.lcg_data = {} 
        self.__lcg_steps = 0
        self.lcg = None
        self.stepPrefix = ''
    
    def setPrefix(self, prefixStr):
        assert type(prefixStr) == str, "expecting string for the step prefix."
        self.stepPrefix = prefixStr
        return
        
    def initLCG(self, skList, bfList, mskList, randList, keyDefsList, originalKeyNodes, transformKeyNodes, pseudoKey):
        if self.lcg == None:
            self.lcg = LatexCodeGenerator()
            self.skList = skList
            self.bfList = bfList
            self.mskList = mskList
            self.randList = randList
            self.keyDefsList = keyDefsList
            self.originalKeyList = originalKeyNodes
            self.transformKeyList = transformKeyNodes
            self.pseudoKey = pseudoKey
            return True
        else:
            # init'ed already
            return False
    
#    def setBreakPoint(self):
#        self.lcg_data[ self.__lcg_steps ] = {} # how should this work?
#        self.__lcg_steps += 1
#        return
    
#    def setNextStep(self, msg, equation):
#        preq = None
#        if self.single_mode:
#            if msg == 'consolidate':
#                msg = 'Consolidate the verification equations (technique 0)'
#            elif msg == 'smallexponents':
#                msg = 'Apply the small exponents test, using exponents $\delta_1, \dots \delta_\\numsigs \in \left[1, 2^\lambda\\right]$'
#                preq = small_exp_label
#            elif msg == 'finalbatcheq':                
#                self.lcg_data[ self.__lcg_steps-1 ]['preq'] = final_batch_eq
#                self.lcg_data['batch'] = self.lcg_data[ self.__lcg_steps-1 ]['eq']
#                return
#        else: # need to handle multiple equations mode differently!
#            if msg in ['consolidate', 'smallexponents']:
#                return
#            elif msg == 'step1':
#                msg = 'Consolidate the verification equations (technique 0), merge pairings with common first or second element (technique 6), and apply the small exponents test, using exponents $\delta_1, \dots \delta_\\numsigs \in \left[1, 2^\lambda\\right]$ for each equation'
#            elif msg == "Move the exponent(s) into the pairing (technique 2)" and self.__lcg_steps == 1:
#                msg = 'Combine $\\numsigs$ signatures (technique 1), move the exponent(s) in pairing (technique 2)'
#            elif msg == 'finalbatcheq':                
#                self.lcg_data[ self.__lcg_steps-1 ]['preq'] = final_batch_eq
#                self.lcg_data['batch'] = self.lcg_data[ self.__lcg_steps-1 ]['eq']
#                return
                
#        self.lcg_data[ self.__lcg_steps ] = {'msg': msg, 'eq': self.lcg.print_statement( equation ), 'preq':preq, 'stepPrefix':self.stepPrefix }
##        if new_msg != None: self.lcg_data[ self.__lcg_steps ]['new_msg'] = new_msg
#        self.__lcg_steps += 1
#        return
    
    # starting point
    def proofHeader(self, title, list_sks, list_bfs, list_msk, list_rand, key_defs, original_key, transform_key, pseudo_key):
        list_sks_str = ""; list_bfs_str = ""; list_msk_str = ""; list_rand_str = ""; key_defs_str = ""; 
        original_key_str = ""; transform_key_str = ""; pseudo_key_str = ""
        # list of msk values
        for i in list_sks:
            list_sks_str += i + ","
        list_sks_str = list_sks_str[:len(list_sks_str)-1]
        # list of msk values
        for i in list_bfs:
            list_bfs_str += i + ","
        list_bfs_str = list_bfs_str[:len(list_bfs_str)-1]
        # list of msk values
        for i in list_msk:
            list_msk_str += self.lcg.getLatexVersion(i) + ","
        list_msk_str = list_msk_str[:len(list_msk_str)-1]
        # list of random values
        for i in list_rand:
            list_rand_str += self.lcg.getLatexVersion(i) + ","
        list_rand_str = list_rand_str[:len(list_rand_str)-1]
        # list of key definitions
        for i in key_defs:
            key_defs_str += i + ","
        key_defs_str = key_defs_str[:len(key_defs_str)-1]
        # original key definitions
        for i in original_key:
            original_key_str += self.lcg.print_statement(i)  + ","
        original_key_str = original_key_str[:len(original_key_str)-1]
        # transform key definition
        for i in transform_key:
            transform_key_str += self.lcg.print_statement(i) + ","
        transform_key_str = transform_key_str[:len(transform_key_str)-1]
        # pseudo key definition
        for i in pseudo_key:
            pseudo_key_str += i + ","
        pseudo_key_str = pseudo_key_str[:len(pseudo_key_str)-1]
        
        result = header % (title, title, list_sks_str, list_bfs_str, list_msk_str, list_rand_str, key_defs_str, original_key_str, transform_key_str, pseudo_key_str)
        return result

    def proofBody(self, step, data):
        pre_eq = data.get('preq')
        cur_eq = data['eq']
        step_prefix = data.get('stepPrefix')
        if pre_eq != None:
            result_eq = pre_eq + cur_eq
        else: result_eq = cur_eq
        result = basic_step % (step_prefix, step, data['msg'], result_eq)
        #print('[STEP', step, ']: ', result)
        return result

    def writeConfig(self, latex_file):
        title = string.capwords(latex_file)
        outputStr = self.proofHeader(title, self.skList, self.bfList, self.mskList, self.randList, self.keyDefsList, self.originalKeyList, self.transformKeyList, self.pseudoKey)        
#        outputStr = self.proofHeader(title, self.constants, self.sig_vars, self.lcg_data['indiv'], self.lcg_data['batch'])
#        for i in range(self.__lcg_steps):
#            outputStr += self.proofBody(i+1, self.lcg_data[i])
#        outputStr += footer
        return outputStr
    
    def writeProof(self, latex_file):
        f = open('proof_gen' + latex_file + '.tex', 'w')
        output = self.writeConfig(latex_file)
        f.write(output)
        f.close()
        return True

    #def appendDecryptToProof(self, latex_file):
        #f = open('proof_gen' + latex_file + '.tex', 'a')
        #output = 
