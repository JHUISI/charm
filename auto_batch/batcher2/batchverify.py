# Entry point to executing the batcher algorithm. It takes in an input bv file
# which describes the verification equation, variable types, components of the public, signature
# and message. Finally, an optional transform section to describe the specific order in which
# to apply the techniques 2, 3a, 3b and 4.

import sys
from batchtechniques import *
from batchproof import *
from batchorder import BatchOrder
from batchparser import BatchParser
from batchcomboeq import TestForMultipleEq,CombineMultipleEq,SmallExpTestMul
from batchsyntax import BasicTypeExist,PairingTypeCheck
from benchmark_interface import curve,param_id

#try:
    #import benchmarks
    #import miraclbench2
    #import miraclbench2_relic
    #curve = miraclbench2_relic.benchmarks
    #curve_key = 'mnt160'
#except:
#    print("Could not find the 'benchmarks' file that has measurement results! Generate and re-run.")
#    exit(0)

debug = False
THRESHOLD_FLAG = CODEGEN_FLAG = PROOFGEN_FLAG = PRECOMP_CHECK = VERBOSE = CHOOSE_STRATEGY = False
TEST_STATEMENT = False
global_count   = 0
flags = { 'multiple':None }
filePrefix = None

def handleVerifyEq(equation, index):
#    print("Input: ", Type(equation), equation)
    combined_equation = BinaryNode.copy(equation.right)
    print("Original eq:", combined_equation)
    tme = TestForMultipleEq()
    ASTVisitor(tme).preorder(combined_equation)
    flags['multiple' + str(index)] = False
    if tme.multiple:
        cme = CombineMultipleEq()
        ASTVisitor(cme).preorder(combined_equation)
        if len(cme.finalAND) == 1: 
            combined_equation = cme.finalAND.pop()
            print("Final combined eq: ", combined_equation)
            se_test = SmallExpTestMul()
            combined_equation2 = BinaryNode.copy(combined_equation)
            ASTVisitor(se_test).preorder(combined_equation2)            
            flags['multiple' + str(index)] = True
            flags[ str(index) ] = combined_equation2
        else:
            # may need to combine them further? or batch separaely
            print("Note: multiple equations left. Either batch each equation separately OR combine further.")
            if len(cme.finalAND) == 2:
                combined_equation2 = BinaryNode(ops.AND, cme.finalAND[0], cme.finalAND[1])
                cme2 = CombineMultipleEq()
                ASTVisitor(cme2).preorder(combined_equation2)
                combined = cme2.finalAND.pop()
                print("Combined: ", combined)
                se_test = SmallExpTestMul()
                combined2 = BinaryNode.copy(combined)
                ASTVisitor(se_test).preorder(combined2)
                print("combined: ", combined2)               
#                exit(0)
                flags['multiple' + str(index)] = True
                flags[ str(index) ] = combined2
                return combined

            return cme.finalAND
    return combined_equation

def countInstances(equation):
    Instfind = ExpInstanceFinder()
    ASTVisitor(Instfind).preorder(equation)
    print("Instances found =>", Instfind.instance, "\n")
    return Instfind.instance

def isOptimized(data):
    # check for counts greater than 1
    for i in data.keys():
        for j in data[i]:
            # if condition is true, then more optimizations are possible
            # effectively, a ^ b occurs more than once
            if data[i][j] > 1: return False
    return True

def checkForSigs(node):
    if node == None: return None
    if Type(node) == ops.HASH:
        return checkForSigs(node.left)
    elif Type(node) == ops.ATTR:
        if node.attr_index and 'z' in node.attr_index: return True
        else: return False
    else: # not sure about this but will see
        result = checkForSigs(node.left)
        if result: return result
        result = checkForSigs(node.right)
        return result

def benchIndivVerification(N, equation, sdl_dict, vars, precompute, _verbose):
    rop_ind = RecordOperations(vars)
    # add attrIndex to non constants
    ASTVisitor(ASTIndexForIndiv(sdl_dict, vars, None)).preorder(equation)
    print("Final indiv eq:", equation, "\n")
    if _verbose:
        print("<====\tINDIVIDUAL\t====>")
        print("vars =>", vars)
        print("Equation =>", equation)
    data = {'key':['N'], 'N': N }

    rop_ind.visit(equation, data)
    if _verbose: print("<===\tOperations count\t===>")
    for i in precompute.keys():
            # if a str, then was precompute introduced programmatically and should skip for individual verification case. 
            if checkForSigs(precompute[i]): data = {'key':['N'], 'N': N }
            else: data = {}            
            rop_ind.visit(precompute[i], data)
            if _verbose: print("Precompute:", i, ":=", precompute[i])
    if _verbose:
        print_results(rop_ind.ops)
    return calculate_times(rop_ind.ops, curve[param_id], N)
    

def benchBatchVerification(N, equation, sdl_dict, vars, precompute, _verbose):
    rop_batch = RecordOperations(vars)
    rop_batch.visit(equation, {})
    if _verbose:
        print("<====\tBATCH\t====>")
        print("Equation =>", equation)
        print("<===\tOperations count\t===>")
    for i in precompute.keys():
        if type(i) != str:
            if checkForSigs(precompute[i]): data = {'key':['N'], 'N': N }
            else: data = {}
            rop_batch.visit(precompute[i], data)
            if _verbose: print("Precompute:", i, ":=", precompute[i])
        else:
            if i == 'delta': # estimate cost of random small exponents
                rop_batch.ops['prng'] += N
                if _verbose: print("Precompute:", i, ":=", precompute[i])
            else:  # estimate cost of some precomputations
                bp = BatchParser()
                index = BinaryNode( i )
                if 'j' in index.attr_index:
                    compute = bp.parse( "for{z:=1, N} do " + precompute[i] )
                    rop_batch.visit(compute, {})
                    if _verbose: print("Precompute:", i, ":=", compute)
                else:
                    if _verbose: print("TODO: need to account for this: ", i, ":=", precompute[i])
    if _verbose:
        print_results(rop_batch.ops)
    return calculate_times(rop_batch.ops, curve[param_id], N)

def proofHeader(lcg, title, const, sigs, indiv_eq, batch_eq):
    const_str = ""; sig_str = ""
    for i in const:
        const_str += lcg.getLatexVersion(i) + ","
    const_str = const_str[:len(const_str)-1]
    for i in sigs:
        sig_str += lcg.getLatexVersion(i) + ","
    sig_str = sig_str[:len(sig_str)-1]
    result = header % (title, const_str, sig_str, indiv_eq, batch_eq)
    #print("header =>", result)
    return result

def proofBody(step, data):
    pre_eq = data.get('preq')
    cur_eq = data['eq']
    if pre_eq != None:
        result_eq = pre_eq + cur_eq
    else: result_eq = cur_eq    
    result = basic_step % (step, data['msg'], result_eq)
    #print('[STEP', step, ']: ', result)
    return result

def writeConfig(lcg, latex_file, lcg_data, const, vars, sigs):
    f = open('verification_gen' + latex_file + '.tex', 'w')
    title = latex_file.upper()
    outputStr = proofHeader(lcg, title, const, sigs, lcg_data[0]['eq'], lcg_data[0]['batch'])
    for i in lcg_data.keys():
        if i != 0:
            outputStr += proofBody(i, lcg_data[i])
    outputStr += footer
    f.write(outputStr)
    f.close()
    return
 
 
def runBatcher(file, verify, ast_struct, eq_number=0):
    global global_count, flags
    constants, types = ast_struct[ CONST ], ast_struct[ TYPE ]
    latex_subs = ast_struct[ LATEX ]
    if ast_struct.get(PRECOMP):
        (indiv_precompute, batch_precompute) = ast_struct[ PRECOMP ]
    else:
        (indiv_precompute, batch_precompute) = {}, {}
    batch_precompute[ "delta" ] = "for{z := 1, N} do prng_z"
    
    algorithm = ast_struct [ TRANSFORM ]
    FIND_ORDER     = False
    if not algorithm: FIND_ORDER = True 

    N = None
    setting = {}
    metadata = {}
    for n in ast_struct[ OTHER ]:
        if 'verify' in str(n.left):
            pass
        elif str(n.left) == 'N':
            N = int(str(n.right))
            metadata['N'] = str(n.right)
        elif str(n.left) in [SIGNATURE, PUBLIC, MESSAGE]:
            setting[ str(n.left) ] = str(n.right)
        else:
            metadata[ str(n.left) ] = str(n.right)
    
    sig_vars, pub_vars, msg_vars = ast_struct[ SIGNATURE ], ast_struct[ PUBLIC ], ast_struct[ MESSAGE ]
    batch_count = {} # F = more than one, T = only one exists
    MSG_set = setting.get(MESSAGE)
    PUB_set = setting.get(PUBLIC)
    SIG_set = setting.get(SIGNATURE)
    if MSG_set == SAME:
        batch_count[ MESSAGE ] = SAME 
    elif MSG_set in metadata.keys():
        checkDotProd = CheckExistingDotProduct(MSG_set)
        ASTVisitor(checkDotProd).preorder(verify)
        if not checkDotProd.applied:
            batch_count[ MESSAGE ] = MSG_set
        else:
            batch_count[ MESSAGE ] = None
    else:
        print("variable not defined but referenced: ", MSG_set)
    
    # check public key setting (can either be many keys or just one single key)
    if PUB_set == SAME:
        batch_count[ PUBLIC ] = SAME 
    elif PUB_set in metadata.keys():
        checkDotProd = CheckExistingDotProduct(PUB_set)
        ASTVisitor(checkDotProd).preorder(verify)
        if not checkDotProd.applied:
            batch_count[ PUBLIC ] = PUB_set
        else:
            batch_count[ PUBLIC ] = None
        
    else:
        print("variable not defined but referenced: ", PUB_set)
    
    if SIG_set in metadata.keys():
        batch_count[ SIGNATURE ] = SIG_set
    else:
        print("variable not defined but referenced: ", SIG_set)    
    
    if VERBOSE: print("setting: ", batch_count)
    
    vars = types
    vars['N'] = N
    vars.update(metadata)
    #print("variables =>", vars)
    #print("metadata =>", metadata)

    # build data inputs for technique classes    
    sdl_data = { CONST : constants, PUBLIC: pub_vars, MESSAGE : msg_vars, SETTING : batch_count }    
    if PROOFGEN_FLAG:
        lcg_data = {}; lcg_steps = 0
        lcg = LatexCodeGenerator(constants, vars, latex_subs)


    techniques = {'2':Technique2, '3':Technique3, '4':Technique4, '5':DotProdInstanceFinder, '6':PairInstanceFinder, '7':Technique7, '8':Technique8 }
    #print("VERIFY EQUATION =>", verify)
    if PROOFGEN_FLAG: 
        lcg_data[ lcg_steps ] = { 'msg':'Equation', 'eq': lcg.print_statement(verify) }
        if flags['multiple' + str(eq_number)]: lcg_data[ lcg_steps ]['eq'] = lcg.print_statement(flags[ str(eq_number) ]) # shortcut!
        lcg_steps += 1
    verify2 = BinaryNode.copy(verify)
#    ASTVisitor(CombineVerifyEq(const, vars)).preorder(verify2.right)
    ASTVisitor(CVForMultiSigner(vars, sig_vars, pub_vars, msg_vars, batch_count)).preorder(verify2)
    if PROOFGEN_FLAG: lcg_data[ lcg_steps ] = { 'msg':'Combined Equation', 'eq':lcg.print_statement(verify2) }; lcg_steps += 1
    # check whether this step is necessary!    
    verify_test = BinaryNode.copy(verify2)
    pif = PairInstanceFinder()
    ASTVisitor(pif).preorder(verify_test)
    if pif.testForApplication(): # if we can combine some pairings, then no need to distribute just yet
        pass
    else:
        ASTVisitor(SimplifyDotProducts()).preorder(verify2)

    if VERBOSE: print("\nStage A: Combined Equation =>", verify2)
    ASTVisitor(SmallExponent(constants, vars)).preorder(verify2)
    if VERBOSE: print("\nStage B: Small Exp Test =>", verify2, "\n")
    if PROOFGEN_FLAG: lcg_data[ lcg_steps ] = { 'msg':'Apply the small exponents test, using exponents $\delta_1, \dots \delta_\\numsigs \in_R \Zq$', 
                                               'eq':lcg.print_statement(verify2), 'preq':small_exp_label }; lcg_steps += 1

    # figure out order automatically (if not specified in bv file)
    if FIND_ORDER:
        result = BatchOrder(sdl_data, types, vars, BinaryNode.copy(verify2)).strategy()
        algorithm = [str(x) for x in result]
        print("<== Found Batch Algorithm ==>", algorithm)

    # execute the batch algorithm sequence 
    for option in algorithm:
        if option == '5':
            option_str = "Simplifying =>"
            Tech = techniques[option]()
        elif option == '6':
            option_str = "Combine Pairings:"
            Tech = techniques[option]()            
        elif option in techniques.keys():
            option_str = "Applying technique " + option
            Tech = techniques[option](sdl_data, vars, metadata)
        else:
            print("Unrecognized technique selection.")
            continue
        ASTVisitor(Tech).preorder(verify2)
        if option == '6':
            testVerify2 = Tech.makeSubstitution(verify2)
            if testVerify2 != None: verify2 = testVerify2
        if hasattr(Tech, 'precompute'):
            batch_precompute.update(Tech.precompute)
        if VERBOSE:
           print(Tech.rule, "\n")
           print(option_str, ":",verify2, "\n")
        if PROOFGEN_FLAG:
            lcg_data[ lcg_steps ] = { 'msg':Tech.rule, 'eq': lcg.print_statement(verify2) }
            lcg_steps += 1

    
    if PROOFGEN_FLAG:
        lcg_data[ lcg_steps-1 ]['preq'] = final_batch_eq
        lcg_data[0]['batch'] = lcg_data[ lcg_steps-1 ]['eq']
        
    if PRECOMP_CHECK:
        countDict = countInstances(verify2) 
        if not isOptimized(countDict):
            ASTVisitor(SubstituteExps(countDict, batch_precompute, vars)).preorder(verify2)
            print("Final batch eq:", verify2)
        else:
            print("Final batch eq:", verify2)

    # START BENCHMARK : THRESHOLD ESTIMATOR
    if THRESHOLD_FLAG:
        print("<== Running threshold estimator ==>")
        (indiv_msmt, indiv_avg_msmt) = benchIndivVerification(N, verify, sdl_data, vars, indiv_precompute, VERBOSE)
        print("Result N =",N, ":", indiv_avg_msmt)

        outfile = file.split('.bv')[0]
        indiv, batch = outfile + "_indiv.dat", outfile + "_batch.dat"
        if filePrefix: indiv = filePrefix + indiv; batch = filePrefix + batch # redirect output file
    
        output_indiv = open(indiv, 'w'); output_batch = open(batch, 'w')
        threshold = -1
        for i in range(1, N+1):
            vars['N'] = i
            (batch_msmt, batch_avg_msmt) = benchBatchVerification(i, verify2, sdl_data, vars, batch_precompute, VERBOSE)
            output_indiv.write(str(i) + " " + str(indiv_avg_msmt) + "\n")
            output_batch.write(str(i) + " " + str(batch_avg_msmt) + "\n")
            if batch_avg_msmt <= indiv_avg_msmt and threshold == -1: threshold = i 
        output_indiv.close(); output_batch.close()
        print("Result N =",N, ":", batch_avg_msmt)
        print("Threshold: ", threshold)
    # STOP BENCHMARK : THRESHOLD ESTIMATOR 
    # TODO: check avg for when batch is more efficient than 
    if CODEGEN_FLAG:
        print("Final batch eq:", verify2)
        subProds = SubstituteSigDotProds(vars, 'z', 'N', global_count)
        ASTVisitor(subProds).preorder(verify2)
        # update variable counter
        global_count = subProds.cnt
        # print("Dot prod =>", subProds.dotprod)
        # need to check for presence of other variables
#        key = None
#        for i in metadata.keys():
#            if i != 'N': key = i
        subProds1 = SubstituteSigDotProds(vars, 'y', 'l', global_count)
        global_count = subProds1.cnt
#        subProds1.setState(subProds.cnt)
        ASTVisitor(subProds1).preorder(verify2)
        if VERBOSE:  
          print("<====\tPREP FOR CODE GEN\t====>")
          print("\nFinal version =>", verify2, "\n")
          for i in subProds.dotprod['list']:
              print("Compute: ", i,":=", subProds.dotprod['dict'][i])    
          for i in subProds1.dotprod['list']:
              print("Compute: ", i,":=", subProds1.dotprod['dict'][i])
          for i in batch_precompute.keys():
              print("Precompute:", i, ":=", batch_precompute[i])
          for i in subProds.dotprod['list']:
              print(i,":=", subProds.dotprod['types'][i])
          for i in subProds1.dotprod['list']:
              print(i,":=", subProds1.dotprod['types'][i])

    if PROOFGEN_FLAG:
        print("Generated the proof for the given signature scheme.")
        latex_file = metadata['name'].upper() + str(eq_number)
        writeConfig(lcg, latex_file, lcg_data, constants, vars, sig_vars)
#        lcg = LatexCodeGenerator(const, vars)
#        equation = lcg.print_statement(verify2)
#        print("Latex Equation: ", equation)
        
def batcher_main(argv, prefix=None):
    global TEST_STATEMENT, THRESHOLD_FLAG, CODEGEN_FLAG, PROOFGEN_FLAG, PRECOMP_CHECK, VERBOSE, CHOOSE_STRATEGY
    global filePrefix
    if len(argv) == 1:
        print("%s [ file.bv ] -b -c -p" % argv[0])
        print("-b : estimate threshold for a given signature scheme with 1 to N signatures.")
        print("-c : generate the output for the code generator (temporary).")
        print("-d : check for further precomputations in final batch equation.")
        print("-p : generate the proof for the signature scheme.")
        print("-s : select strategy for the ordering of techniques. Options: basic, score, what else?")
        exit(-1)

    # main for batch input parser    
    try:
        print(argv)
        file = str(argv[1])
        if prefix: filePrefix = prefix
        for i in argv:
            if i == "-b": THRESHOLD_FLAG = True
            elif i == "-c": CODEGEN_FLAG = True
            elif i == "-v": VERBOSE = True
            elif i == "-p": PROOFGEN_FLAG = True
            elif i == "-d": PRECOMP_CHECK = True
            elif i == "-s": CHOOSE_STRATEGY = True
            elif i == "-t": TEST_STATEMENT = True
        if not TEST_STATEMENT: ast_struct = parseFile(file)
    except Exception as exc:
        print("An error occured while processing batch inputs: ", exc)
        exit(-1)

    if TEST_STATEMENT:
        debug = levels.all
        statement = argv[2]
        parser = BatchParser()
        final = parser.parse(statement)
        print("Final statement(%s): '%s'" % (type(final), final))
        exit(0)

    verify_eq, N = [], None; cnt = 0
    for n in ast_struct[ OTHER ]:
        if 'verify' in str(n.left):
            result = handleVerifyEq(n, cnt); cnt += 1
            if type(result) != list: verify_eq.append(result)
            else: verify_eq.extend(result)

    # verify 
    variables = ast_struct[ TYPE ]
    for eq in verify_eq:
        bte = BasicTypeExist( variables )
        ASTVisitor( bte ).preorder( eq )
        bte.report( eq )
        
        cte = PairingTypeCheck( variables )
        ASTVisitor( cte ).preorder( eq )
        cte.report( eq )

    # process settings
    for i in range(len(verify_eq)):    
        print("\nRunning batcher....\n")
        runBatcher(file + str(i), verify_eq[i], ast_struct, i)

if __name__ == "__main__":
   batcher_main(sys.argv)
