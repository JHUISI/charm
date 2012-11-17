# Entry point to executing the batcher algorithm. It takes in an input bv file
# which describes the verification equation, variable types, components of the public, signature
# and message. Finally, an optional transform section to describe the specific order in which
# to apply the techniques 2, 3a, 3b and 4.

import sdlpath
from sdlparser.SDLParser import *
from batchtechniques import *
from batchproof import *
from batchconfig import *
from batchorder import BatchOrder
from batchcomboeq import TestForMultipleEq,CombineMultipleEq,SmallExpTestMul,AfterTech2AddIndex,UpdateDeltaIndex
from batchsyntax import BasicTypeExist,PairingTypeCheck
from batchoptimizer import PairInstanceFinderImproved
from loopunroll import *
from benchmark_interface import getBenchmarkInfo
from constructbatch import *

debug = False
THRESHOLD_FLAG = CODEGEN_FLAG = PRECOMP_CHECK = VERBOSE = CHOOSE_STRATEGY = False
global_count   = 0
delta_count    = 1
flags = { 'multiple':None, 'step1':None }
singleVE = True # flag to define whether working with a single or multi-eq for verification
filePrefix = None
crypto_library = curve = param_id = None
applied_technique_list = []

def handleVerifyEq(equation, index, verbose):
    global singleVE, flags
    VERBOSE = verbose
    multipleEquationsHere = False
#    print("Input: ", Type(equation), equation)
    if Type(equation) == ops.EQ:
        combined_equation = BinaryNode.copy(equation.right)
    else:
        combined_equation = BinaryNode.copy(equation)
    
    if VERBOSE: print("Original eq:", combined_equation)
    tme = TestForMultipleEq()
    ASTVisitor(tme).preorder(combined_equation)
    flags['multiple' + str(index)] = False
    if tme.multiple:
        singleVE = False
        cme = CombineMultipleEq()
        ASTVisitor(cme).preorder(combined_equation)
        if len(cme.finalAND) == 1: 
            multipleEquationsHere = True            
            combined_equation = cme.finalAND.pop()
            if VERBOSE: print("Final combined eq: ", combined_equation)
            se_test = SmallExpTestMul()
            combined_equation2 = BinaryNode.copy(combined_equation)
            ASTVisitor(se_test).preorder(combined_equation2)    
            aftTech2 = UpdateDeltaIndex()
            ASTVisitor(aftTech2).preorder(combined_equation2)                      
            flags['multiple' + str(index)] = True
            flags[ str(index) ] = combined_equation2
            flags[ 'verify' + str(index) ] = equation.right # used for verify in tex
            # this is step0 for multi equation case
            flags[ 'step1' ] = combined_equation2 # add delta index #s here
            if VERBOSE: print("delta eq: ", combined_equation2)
            #sys.exit("Testing stuff!!")
        else:
            # may need to combine them further? or batch separaely
            print("Note: multiple equations left. Either batch each equation separately OR combine further.")
            if len(cme.finalAND) == 2:
                multipleEquationsHere = True
                combined_equation2 = BinaryNode(ops.AND, cme.finalAND[0], cme.finalAND[1])
                cme2 = CombineMultipleEq(addIndex=False)
                ASTVisitor(cme2).preorder(combined_equation2)
                combined = cme2.finalAND.pop()
                if VERBOSE: print("Combined: ", combined)
                se_test = SmallExpTestMul()
                combined2 = BinaryNode.copy(combined)
                ASTVisitor(se_test).preorder(combined2)
                aftTech2 = UpdateDeltaIndex()
                ASTVisitor(aftTech2).preorder(combined2)                      
                if VERBOSE: print("combined: ", combined2)               
#                exit(0)
                flags['multiple' + str(index)] = True
                flags[ str(index) ] = combined2
                flags[ 'verify' + str(index) ] = equation.right # used for verify in tex        
                flags[ 'step1' ] = combined2 # add delta index #s here
                return (combined, multipleEquationsHere)
#            sys.exit("Testing Stuff 2!!!")

            return (cme.finalAND, multipleEquationsHere)
    return (combined_equation, multipleEquationsHere)

def countInstances(equation):
    Instfind = ExpInstanceFinder()
    ASTVisitor(Instfind).preorder(equation)
    if VERBOSE: print("Instances found =>", Instfind.instance, "\n")
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
    ASTVisitor(ASTIndexForIndiv(sdl_dict, vars)).preorder(equation)
    if VERBOSE: print("Final indiv eq:", equation, "\n")
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
                bp = SDLParser()
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

def writeFile(file_name, file_contents):
     f = open(file_name, 'w')
     f.write(file_contents)
     f.close()        

def runBatcher2(opts, proofGen, file, verify, settingObj, loopDetails, eq_number=1):
    """core of the Batcher algorithm. handles a variety of things from 
    technique search, proof generation, benchmarking of batch and individual, and so on.
    """
    global PROOFGEN_FLAG, THRESHOLD_FLAG, CODEGEN_FLAG, PRECOMP_CHECK, VERBOSE, CHOOSE_STRATEGY
    global global_count, delta_count, flags, singleVE, applied_technique_list
    PROOFGEN_FLAG, THRESHOLD_FLAG, CODEGEN_FLAG, PRECOMP_CHECK = opts['proof'], opts['threshold'], opts['codegen'], opts['pre_check']
    VERBOSE, CHOOSE_STRATEGY = opts['verbose'], opts['strategy']
    SDL_OUT_FILE = opts['out_file']
    constants, types = settingObj.getConstantVars(), settingObj.getTypes()
    sigVars, pubVars, msgVars = settingObj.getSignatureVars(), settingObj.getPublicVars(), settingObj.getMessageVars()
    latex_subs = settingObj.getLatexVars()

    if settingObj.getPrecomputeVars():
        (indiv_precompute, batch_precompute) = settingObj.getPrecomputeVars()
    else:
        (indiv_precompute, batch_precompute) = {}, {}
    batch_precompute[ "delta" ] = "for{z := 1, N} do prng_z"
    algorithm = settingObj.getTransformList()
    FIND_ORDER     = False
    if not algorithm: FIND_ORDER = True

    N = settingObj.getNumSignatures()    
#    sig_vars, pub_vars, msg_vars = ast_struct[ SIGNATURE ], ast_struct[ PUBLIC ], ast_struct[ MESSAGE ]
    setting = settingObj.getBatchCount()
    batch_count = {} # F = more than one, T = only one exists
    MSG_set = setting[MSG_CNT]
    PUB_set = setting[PUB_CNT]
    SIG_set = setting[SIG_CNT]
    if MSG_set == SAME:
        batch_count[ MESSAGE ] = SAME 
    elif MSG_set in types.keys(): # where N is defined
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
    elif PUB_set in types.keys():
        checkDotProd = CheckExistingDotProduct(PUB_set)
        ASTVisitor(checkDotProd).preorder(verify)
        if not checkDotProd.applied:
            batch_count[ PUBLIC ] = PUB_set
        else:
            batch_count[ PUBLIC ] = None
        
    else:
        print("variable not defined but referenced: ", PUB_set)
    
    if SIG_set in types.keys():
        batch_count[ SIGNATURE ] = SIG_set
    else:
        print("variable not defined but referenced: ", SIG_set)    
    
    if VERBOSE: print("setting: ", batch_count)
    
    if VERBOSE: print("variables =>", types)
    # build data inputs for technique classes    
    sdl_data = { SECPARAM: settingObj.getSecParam(), CONST : constants, PUBLIC: pubVars, MESSAGE : msgVars, SETTING : batch_count, BATCH_VERIFY:settingObj.getVerifyInputArgs(), BATCH_VERIFY_MAP:settingObj.getVerifyInputArgsMap() } 
    if PROOFGEN_FLAG:
        # start the LCG
        proofGen.initLCG(constants, types, sigVars, latex_subs)
        if flags['step1']: proofGen.setStepOne(flags['step1'])

    techniques = {'2':Technique2, '3':Technique3, '4':Technique4, '5':DotProdInstanceFinder, '6':PairInstanceFinder, '7':Technique7, '8':Technique8 }
    #print("VERIFY EQUATION =>", verify)
    if PROOFGEN_FLAG: 
        if flags['multiple' + str(eq_number)]: 
            proofGen.setIndVerifyEq(flags[ 'verify' + str(eq_number) ])
        else:
            proofGen.setIndVerifyEq( verify )
        
    verify2 = BinaryNode.copy(verify)
    ASTVisitor(CVForMultiSigner(types, sigVars, pubVars, msgVars, batch_count)).preorder(verify2)
    if PROOFGEN_FLAG: 
        proofGen.setNextStep( 'consolidate', verify2 )
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
    if PROOFGEN_FLAG: 
        proofGen.setNextStep( 'smallexponents', verify2 )
        
    # figure out order automatically (if not specified in bv file)
    if FIND_ORDER:
        result = BatchOrder(sdl_data, types, BinaryNode.copy(verify2), crypto_library).strategy()
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
            Tech = techniques[option](sdl_data, types)
        else:
            print("Unrecognized technique selection.")
            continue
        ASTVisitor(Tech).preorder(verify2)
        if option == '2' and not singleVE:
            # add index numbers to deltas if dealing with multiple verification equations
            aftTech2 = UpdateDeltaIndex()
            ASTVisitor(aftTech2).preorder(verify2)  
        elif option == '6':
            testVerify2 = Tech.makeSubstitution(verify2)
            if testVerify2 != None: verify2 = testVerify2
        if hasattr(Tech, 'precompute'):
            batch_precompute.update(Tech.precompute)
        if VERBOSE:
           print(Tech.rule, "\n")
           print(option_str, ":",verify2, "\n")
        if PROOFGEN_FLAG:
            proofGen.setNextStep(Tech.rule, verify2)
        # record final technique list
        if option == '3':
            applied_technique_list.extend( list(Tech.tech_list) )
        else:
            applied_technique_list.append( int(option) )
    
    # now we check if Technique 10 is applicable (aka loop unrolling)
    Tech10 = Technique10(sdl_data, types, loopDetails)
    
    if Tech10.testForApplication():
        verify2 = Tech10.makeSubsitution(verify2.right, delta_count) # strips the FOR loop node
        if VERBOSE: print(Tech10.rule, ":", verify2, "\n")
        if PROOFGEN_FLAG:
            proofGen.setNextStep(Tech10.rule, verify2)
        applied_technique_list.append(10) # add to list
    ##################################################################
        
    if PRECOMP_CHECK:
        countDict = countInstances(verify2) 
        if not isOptimized(countDict):
            ASTVisitor(SubstituteExps(countDict, batch_precompute, types)).preorder(verify2)
            print("Final batch eq:", verify2)
        else:
            print("Final batch eq:", verify2)

    # START BENCHMARK : THRESHOLD ESTIMATOR
    if THRESHOLD_FLAG:
        print("<== Running threshold estimator ==>")
        (indiv_msmt, indiv_avg_msmt) = benchIndivVerification(N, verify, sdl_data, types, indiv_precompute, VERBOSE)
        print("Result N =",N, ":", indiv_avg_msmt)

        outfile = file.split('.bv')[0]
        indiv, batch = outfile + "_indiv.dat", outfile + "_batch.dat"
        if filePrefix: indiv = filePrefix + indiv; batch = filePrefix + batch # redirect output file
    
        output_indiv = open(indiv, 'w'); output_batch = open(batch, 'w')
        threshold = -1
        for i in range(1, N+1):
            types['N'] = i
            (batch_msmt, batch_avg_msmt) = benchBatchVerification(i, verify2, sdl_data, types, batch_precompute, VERBOSE)
            output_indiv.write(str(i) + " " + str(indiv_avg_msmt) + "\n")
            output_batch.write(str(i) + " " + str(batch_avg_msmt) + "\n")
            if batch_avg_msmt <= indiv_avg_msmt and threshold == -1: threshold = i 
        output_indiv.close(); output_batch.close()
        print("Result N =",N, ":", batch_avg_msmt)
        print("Threshold: ", threshold)

    return (SDL_OUT_FILE, sdl_data, verify2, batch_precompute, global_count)
    
def buildSDLBatchVerifier(sdlOutFile, sdl_data, types, verify2, batch_precompute, var_count, setting):
    """constructs the SDL batch verifier"""
    if sdlOutFile == None: sdlOutFile = types['name'] + "-full-batch"
    sdlBatch = SDLBatch(sdlOutFile, sdl_data, types, verify2, batch_precompute, var_count, setting)
    sdlBatch.construct(VERBOSE)
    return sdlBatch.getVariableCount()

def run_main(opts):
    """main entry point for generating batch verification algorithms"""
    global singleVE, crypto_library, curve, param_id, assignInfo, varTypes, global_count, delta_count, applied_technique_list
    verbose   = opts['verbose']
    statement = opts['test_stmt']
    file      = opts['sdl_file']
    crypto_library   = opts['library']
    proof_flag = opts['proof']
    curve, param_id = getBenchmarkInfo(crypto_library)
    if statement:
        debug = levels.all
        parser = SDLParser()
        final = parser.parse(statement)
        print("Final statement(%s): '%s'" % (type(final), final))
        sys.exit(0)
    else:
        # Parse the SDL file into binary tree
#        ast_struct = parseFile(file)
        parseFile2(file, verbose, ignoreCloudSourcing=True)
        setting = SDLSetting(verbose)
        setting.parse(getAssignInfo(), getVarTypes()) # check for errors and pass on to user before continuing

    # process single or multiple equations
    verify_eq, N = [], None
    #for n in ast_struct[ OTHER ]:
    if len(setting.getVerifyEq()) == 0:
        sys.exit("Could not locate the individual verification equation. Please edit SDL file.\n");
    
    verifyEqDict = setting.getVerifyEq()
    verifyEqUpdated = {}
    isSingleEquation = {}
    verifyList = list(verifyEqDict.keys())
    verifyList.sort()
    
    for k in verifyList:
#        print("k := ", k, ", v := ", verifyEqDict[k])
        if VERIFY in k:
            (result, singleEq) = handleVerifyEq(verifyEqDict[k].get(VERIFY), delta_count, verbose)
            delta_count += 1 # where we do actual verification on # of eqs
            verifyEqUpdated[ k ] = result
            isSingleEquation[ k ] = singleEq 

    # santiy checks to verify setting makes sense for given equation 
    variables = setting.getTypes()
    for k,v in verifyEqUpdated.items():
        bte = BasicTypeExist( variables )
        ASTVisitor( bte ).preorder( v )
        bte.report( v )
    
    #sys.exit(0)
    # initiate the proof generator    
    print("Single verification equation: ", singleVE)
    genProof = GenerateProof(singleVE)
    # process settings
    i = 1
    finalVerifyList = []
    types = setting.getTypes()
    if len(verifyList) == 2:
        batch_precompute = {}
        sdlOutFile = None
        for k in verifyList:
            loopDetails = None
            if verifyEqDict[ k ][ hasLoop ]:
                try:
                    endValue = str(eval(verifyEqDict[k][endVal], setting.getTypes()))
                    # updates the types section to store the value for estimation purposes
                    setting.getTypes()[verifyEqDict[k][endVal]] = endValue
                except:
                    print("Could not determine loop end value. Please define: ", verifyEqDict[k][endVal])
                    sys.exit(0)
                loopDetails = (verifyEqDict[k][loopVar], verifyEqDict[k][startVal], endValue) 
            genProof.setPrefix('EQ' + str(i + 1))
            (sdlOutFile, sdl_data, verify2, batch_precompute0, var_count) = runBatcher2(opts, genProof, file + str(i), verifyEqUpdated[k], setting, loopDetails, i)
            genProof.changeMode( isSingleEquation[ k ] )
            i += 1
#            print("BATCH EQUATION: ", verify2)
            finalVerifyList.append(verify2)
#            sdl_data.update(sdl_data0)
#            types.update(types0)
            batch_precompute.update(batch_precompute0)

        eq1, eq2 = finalVerifyList
        finalEq = CombineEqWithoutNewDelta(eq1, eq2)
        if verbose: print("FINAL BATCH EQUATION:\n", finalEq)
        if proof_flag: 
            genProof.setPrefix('')
            genProof.setNextStep('Combine equations 1 and 2, then pairings within final equation (technique 6)', finalEq)

#        buildSDLBatchVerifier(sdlOutFile, sdl_data, types, finalEq, batch_precompute, global_count, setting)
    else:
        for k in verifyList:
            loopDetails = None
            if verifyEqDict[ k ][ hasLoop ]:
                try:
                    endValue = str(eval(verifyEqDict[k][endVal], setting.getTypes()))
                    setting.getTypes()[verifyEqDict[k][endVal]] = endValue
                except:
                    print("Could not determine loop end value. Please define: ", verifyEqDict[k][endVal])
                    sys.exit(0)
                loopDetails = (verifyEqDict[k][loopVar], verifyEqDict[k][startVal], endValue)
            (sdlOutFile, sdl_data, verify2, batch_precompute, global_count) = runBatcher2(opts, genProof, file, verifyEqUpdated[k], setting, loopDetails)
            finalEq = verify2
            #buildSDLBatchVerifier(sdlOutFile, sdl_data, types, finalEq, batch_precompute, global_count, setting)
    if proof_flag:
        genProof.setNextStep('finalbatcheq', None)
        latex_file = types['name'].upper()
        print("Generated the proof written to file: verification_gen%s.tex" % latex_file)
        genProof.compileProof(latex_file)
    
    # last step:construct SDL batch verifier
    print("technique list: ", applied_technique_list)
    return buildSDLBatchVerifier(sdlOutFile, sdl_data, types, finalEq, batch_precompute, global_count, setting)        
    

