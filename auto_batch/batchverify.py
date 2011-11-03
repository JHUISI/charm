from batchparser import *

try:
    import benchmarks
    curve = benchmarks.benchmarks
except:
    print("Could not find the 'benchmarks' file that has measurement results! Generate and re-run.")
    exit(0)


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
    print("<====\tINDIVIDUAL\t====>")
    print("vars =>", vars)
    print("Equation =>", equation)
    data = {'key':['N'], 'N': N }

    rop_ind.visit(verify.right, data)
    print("<===\tOperations count\t===>")
    for i in precompute.keys():
            # if a str, then was precompute introduced programmatically and should skip for individual verification case. 
            rop_ind.visit(precompute[i], {})
            print("Precompute:", i, ":=", precompute[i])
    print_results(rop_ind.ops)
    calculate_times(rop_ind.ops, curve['d224.param'], N)
    return

def benchBatchVerification(N, equation, const, vars, precompute):
    rop_batch = RecordOperations(vars)
    rop_batch.visit(equation, {})
    print("<====\tBATCH\t====>")    
    print("Equation =>", equation)
    print("<===\tOperations count\t===>")
    for i in precompute.keys():
        if type(i) != str:
            rop_batch.visit(precompute[i], {})
            print("Precompute:", i, ":=", precompute[i])
        else:
            if i == 'delta': # estimate cost of random small exponents
                rop_batch.ops['prng'] += N
                print("Precompute:", i, ":=", precompute[i])
            else:  # estimate cost of some precomputations
                bp = BatchParser()
                index = BinaryNode( i )
                if 'j' in index.attr_index:
                    compute = bp.parse( "for{j:=1, N} do " + precompute[i] )
                    rop_batch.visit(compute, {})
                    print("Precompute:", i, ":=", compute)
                else:
                    print("TODO: need to account for this: ", i, ":=", precompute[i])
    print_results(rop_batch.ops)
    calculate_times(rop_batch.ops, curve['d224.param'], N)
    return
    
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
    batch_precompute[ "delta" ] = "for{j := 1, N} do prng_j"
    
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
    
    # TODO: fill in the blanks here
    benchIndivVerification(N, verify.right, const, vars, indiv_precompute)
    benchBatchVerification(N, verify2.right, const, vars, batch_precompute)
    
    print("<====\tPREP FOR CODE GEN\t====>")
    subProds = SubstituteSigDotProds()
    ASTVisitor(subProds).preorder(verify2.right)
    print("\nFinal version =>", verify2.right, "\n")
    print("Dot prod =>", subProds.dotprod)
    for i in subProds.dotprod['list']:
        print("Compute: ", subProds.dotprod['dict'][i])
    # TODO: generate code for both which includes the detecting of invalid signatures from a batch
    #codeGenerator()