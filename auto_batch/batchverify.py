from batchparser import *

try:
    import benchmarks
    curve = benchmarks.benchmarks
except:
    print("Could not find the 'benchmarks' file that has measurement results! Generate and re-run.")
    exit(0)

debug = False

def countInstances(equation):
    Instfind = InstanceFinder()
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

def benchIndivVerification(N, equation, const, vars, precompute):
    rop_ind = RecordOperations(vars)
    # add attrIndex to non constants
    ASTVisitor(ASTAddIndex(const, vars)).preorder(equation)
    print("Final indiv eq:", equation, "\n")
    if debug:
        print("<====\tINDIVIDUAL\t====>")
        print("vars =>", vars)
        print("Equation =>", equation)
    data = {'key':['N'], 'N': N }

    rop_ind.visit(verify.right, data)
    if debug: print("<===\tOperations count\t===>")
    for i in precompute.keys():
            # if a str, then was precompute introduced programmatically and should skip for individual verification case. 
            rop_ind.visit(precompute[i], {})
            if debug: print("Precompute:", i, ":=", precompute[i])
    if debug:
        print_results(rop_ind.ops)
    return calculate_times(rop_ind.ops, curve['d224.param'], N)
    

def benchBatchVerification(N, equation, const, vars, precompute):
    rop_batch = RecordOperations(vars)
    rop_batch.visit(equation, {})
    if debug:
        print("<====\tBATCH\t====>")
        print("Equation =>", equation)
        print("<===\tOperations count\t===>")
    for i in precompute.keys():
        if type(i) != str:
            rop_batch.visit(precompute[i], {})
            if debug: print("Precompute:", i, ":=", precompute[i])
        else:
            if i == 'delta': # estimate cost of random small exponents
                rop_batch.ops['prng'] += N
                if debug: print("Precompute:", i, ":=", precompute[i])
            else:  # estimate cost of some precomputations
                bp = BatchParser()
                index = BinaryNode( i )
                if 'j' in index.attr_index:
                    compute = bp.parse( "for{z:=1, N} do " + precompute[i] )
                    rop_batch.visit(compute, {})
                    if debug: print("Precompute:", i, ":=", compute)
                else:
                    if debug: print("TODO: need to account for this: ", i, ":=", precompute[i])
    if debug:
        print_results(rop_batch.ops)
    return calculate_times(rop_batch.ops, curve['d224.param'], N)
    
def codeGenerator(Struct):
    pass

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("%s [ batch-input.bv ]" % sys.argv[0])
        exit(-1)
    # main for batch input parser    
    try:
        file = sys.argv[1]
        print(sys.argv[1:])
        ast_struct = parseFile2(file)
    except:
        print("An error occured while processing batch inputs.")
        exit(-1)
    const, types = ast_struct[ CONST ], ast_struct[ TYPE ]
    (indiv_precompute, batch_precompute) = ast_struct[ PRECOMP ]
    batch_precompute[ "delta" ] = "for{z := 1, N} do prng_z"
    
    algorithm = ast_struct [ TRANSFORM ]
    if not algorithm: algorithm = ['2', '3'] # standard transform that applies to most signature schemes we've tested
    
    verify, N = None, None
    metadata = {}
    for n in ast_struct[ OTHER ]:
        if str(n.left) == 'verify':
            verify = n
        elif str(n.left) == 'N':
            N = int(str(n.right))
            metadata['N'] = str(n.right)
        else:
            metadata[ str(n.left) ] = str(n.right)
    
    vars = types
    vars['N'] = N
    vars.update(metadata)
    print("variables =>", vars)
    print("metadata =>", metadata)
    print("batch algorithm =>", algorithm)

    print("\nVERIFY EQUATION =>", verify)
    verify2 = BinaryNode.copy(verify)
    ASTVisitor(CombineVerifyEq(const, vars)).preorder(verify2.right)
    ASTVisitor(SimplifyDotProducts()).preorder(verify2.right)

    print("\nStage A: Combined Equation =>", verify2)
    ASTVisitor(SmallExponent(const, vars)).preorder(verify2.right)
    print("\nStage B: Small Exp Test =>", verify2, "\n")

    techniques = {'2':Technique2, '3':Technique3, '4':Technique4, 'S':SimplifyDotProducts }

    for option in algorithm:
        if option == 'S':
            option_str = "Simplifying =>"
            Tech = techniques[option]()
        elif option in techniques.keys():
            option_str = "Applying technique " + option + " =>"
            Tech = techniques[option](const, vars, metadata)
        else:
            print("Unrecognized technique selection.")
            continue
        ASTVisitor(Tech).preorder(verify2.right)
        print(Tech.rule, "\n")
        print(option_str, ":",verify2, "\n")
    
    countDict = countInstances(verify2) 
    if not isOptimized(countDict):
        ASTVisitor(Substitute(countDict, batch_precompute, vars)).preorder(verify2.right)
        print("Final batch eq:", verify2.right)
    else:
        print("Final batch eq:", verify2.right)
    
    # START BENCHMARK : THRESHOLD ESTIMATOR
    (indiv_msmt, indiv_avg_msmt) = benchIndivVerification(N, verify.right, const, vars, indiv_precompute)
    print("Result N =",N, ":", indiv_avg_msmt)

    outfile = file.split('.')[0]
    indiv, batch = outfile + "_indiv.dat", outfile + "_batch.dat"
    
    output_indiv = open(indiv, 'w'); output_batch = open(batch, 'w')
    threshold = -1
    for i in range(2, N+1):
        vars['N'] = i
        (batch_msmt, batch_avg_msmt) = benchBatchVerification(i, verify2.right, const, vars, batch_precompute)
        output_indiv.write(str(i) + " " + str(indiv_avg_msmt) + "\n")
        output_batch.write(str(i) + " " + str(batch_avg_msmt) + "\n")
        if batch_avg_msmt <= indiv_avg_msmt and threshold == -1: threshold = i 
    output_indiv.close(); output_batch.close()
    print("Result N =",N, ":", batch_avg_msmt)
    print("Threshold: ", threshold)
    # STOP BENCHMARK : THRESHOLD ESTIMATOR 
    # TODO: check avg for when batch is more efficient than 
    
    subProds = SubstituteSigDotProds(vars, 'z', 'N')
    ASTVisitor(subProds).preorder(verify2.right)
    # print("Dot prod =>", subProds.dotprod)
    # need to check for presence of other variables
    key = None
    for i in metadata.keys():
        if i != 'N': key = i
    subProds1 = SubstituteSigDotProds(vars, 'y', key)
    subProds1.setState(subProds.cnt)
    ASTVisitor(subProds1).preorder(verify2.right)
    
    print("<====\tPREP FOR CODE GEN\t====>")
    print("\nFinal version =>", verify2.right, "\n")
    for i in subProds.dotprod['list']:
        print("Compute: ", i,":=", subProds.dotprod['dict'][i])    
#    print("Dot prod =>", subProds1.dotprod)
    for i in subProds1.dotprod['list']:
        print("Compute: ", i,":=", subProds1.dotprod['dict'][i])
    for i in batch_precompute.keys():
        print("Precompute:", i, ":=", batch_precompute[i])
    for i in subProds.dotprod['list']:
        print(i,":=", subProds.dotprod['types'][i])    


    # TODO: generate code for both which includes the detecting of invalid signatures from a batch
    #codeGenerator()
