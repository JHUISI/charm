import getopt
import sys
import batchverify

version  = '1.0'
banner   = """
Batcher:
- takes as input a SDL file representation of a signature algorithm.
- produces modified SDL of batch verification equation
"""
verbose = precompute_check = threshold = codegen = proof = print_usage = print_options = False
strategy = 'bfs' # default strategy
input_file = test_statement = None
output_file = None

#print('ARGV      :', sys.argv[1:])

try:
    options, remainder = getopt.getopt(sys.argv[1:], 'o:bcdhpvs:f:', ['out_file=', 'sdl_file=', 'threshold', 'codegen', 'proof', 'strategy=', 
                                                                    'verbose', 'query', 'print', 'help'])
except:
    sys.exit("ERROR: Specified invalid arguments.")
    

for opt, arg in options:
    if opt in ('-h', '--help'):
        print_usage = True
    elif opt in ('-o', '--out_file'):
        output_file = arg
    elif opt in ('-f', '--sdl_file'):
        input_file = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-t', '--threshold'):
        threshold = True
    elif opt in ('-d', '--precompute'):
        precompute_check = True
    elif opt in ('-c', '--codegen'):
        codegen = True
    elif opt in ('-p', '--proof'):
        proof = True
    elif opt in ('-s', '--strategy'):
        strategy = arg
    elif opt in ('-q', '--query'):
        test_statement = arg
    elif opt == '--print':
        print_options = True

if verbose:
    print('OPTIONS   :', options)
if print_usage:
    print("Batcher,", version, "\n")
    print("Arguments: ")
    print("...")
    sys.exit(0)
if print_options:
    print('VERSION    :', version)
    print('VERBOSE    :', verbose)
    print('SDL INPUT  :', input_file)
    print('CODEGEN    :', codegen)
    print('SDL OUTPUT :', output_file)
    print('THRESHOLD  :', threshold)
    print('GEN PROOF  :', proof)
    print('STRATEGY   :', strategy)
    print('REMAINING :', remainder)

sys.exit("Need to specify SDL file.") if input_file == None else None

# construct the option dictionary
opts_dict = {}
opts_dict['verbose']   = verbose
opts_dict['sdl_file']  = input_file
opts_dict['out_file']  = output_file
opts_dict['codegen']   = codegen
opts_dict['threshold'] = threshold
opts_dict['proof']     = proof
opts_dict['strategy']  = strategy
opts_dict['pre_check'] = precompute_check
opts_dict['test_stmt'] = test_statement

# execute batcher on the provided options
batchverify.run_main(opts_dict)

