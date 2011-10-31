from batchparser import *

def benchIndivVerification(equation):
    pass

def benchBatchVerification(equation):
    pass

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
    precompute = ast_struct[ PRECOMP ]
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
    print("variables =>", vars)
    print("batch algorithm =>", algorithm)

    print("\nVERIFY EQUATION =>", verify, "\n")
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
    
    # TODO: fill in the blanks here
    #benchIndivVerification(verify)
    #benchBatchVerification()
    # TODO: generate code for both which includes the detecting of invalid signatures from a batch
    #codeGenerator()