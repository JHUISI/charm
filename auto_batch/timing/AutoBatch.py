#import sys
#if ".../batcher2" not in sys.path:
#   sys.path.insert(0, '../batcher2')
#from batchverify import *
import gc, os

gc.enable()

def clearBatcherGlobals():
    """clear all globals"""
    excludeList = ["clearBatcherGlobals", "batcher_main"]
    for uniquevar in [var for var in globals().copy() if var[0] != "_" and not var in excludeList]:
        pass
#        print("del global =>", uniquevar)
#        del globals()[uniquevar]

def getBatcherInstance(sys_args, prefix=None):
#    batcher_main(sys_args, prefix)
#    return benchmark_batcher(sys_args, prefix)
    BatcherCall = """\n
import sys
sys.path.insert(0, '../batcher_clean/')
sys.path.insert(0, '../../')
sys.path.insert(0, '../../sdlparser')
import sdlpath
import batchverify

startList = [0.0]
stopList = [0.0]
batchverify.run_main(%s, startList, stopList)
start = startList[0]
stop = stopList[0]
print("result: ", (stop - start) * 1000)
# reset globals
batchverify.global_count   = 0
batchverify.delta_count    = 1
batchverify.flags = { 'multiple':None, 'step1':None }
batchverify.singleVE = True # flag to define whether working with a single or multi-eq for verification
filePrefix = None
batchverify.crypto_library = batchverify.curve = batchverify.param_id = None
batchverify.applied_technique_list = []

""" % (str(sys_args))
    dummy_class = '<string>'
    Benchmark_batcher = compile(BatcherCall, dummy_class, 'exec')
    return Benchmark_batcher

def runBatcherTimer(argsStr):
    print("Batcher args: ", argsStr)
    os.system("cd ../batcher_clean/; python batcher_main.py " + argsStr)
    return

def runCodegenPyTimer(argsStr):
    print("Codegen ars: ", argsStr)
    os.system("cd ../../codegen; python codegenAutoBatch_PY.py " + argsStr) # TODO: complete
    return

def CodegenPY(sys_args, prefix=None):
    CodegenCall = """\n
import sys, time
sys.path.insert(0, '../../')
sys.path.insert(0, '../../sdlparser')
sys.path.insert(0, '../../codegen')
import codegenAutoBatch_PY

start = time.time()
codegenAutoBatch_PY.main('%s', True, '%s')
stop = time.time()

#reset globals
codegenAutoBatch_PY.assignInfo = None
codegenAutoBatch_PY.inputOutputVars = None
codegenAutoBatch_PY.functionNameOrder = None
codegenAutoBatch_PY.varNamesToFuncs_All = None
codegenAutoBatch_PY.varNamesToFuncs_Assign = None
codegenAutoBatch_PY.setupFile = None
codegenAutoBatch_PY.transformFile = None
codegenAutoBatch_PY.decOutFile = None
codegenAutoBatch_PY.userFuncsFile = None
codegenAutoBatch_PY.userFuncsCPPFile = None
#codegenAutoBatch_PY.currentFuncName = NONE_FUNC_NAME
codegenAutoBatch_PY.numTabsIn = 1
codegenAutoBatch_PY.returnValues = {}
codegenAutoBatch_PY.globalVarNames = []
codegenAutoBatch_PY.lineNoBeingProcessed = 0
codegenAutoBatch_PY.numLambdaFunctions = 0
codegenAutoBatch_PY.userFuncsList_CPP = []
codegenAutoBatch_PY.userFuncsList = []
codegenAutoBatch_PY.currentLambdaFuncName = None
codegenAutoBatch_PY.CPP_varTypesLines = None
codegenAutoBatch_PY.CPP_funcBodyLines = None

codegenAutoBatch_PY.blindingFactors_NonLists = None
codegenAutoBatch_PY.blindingFactors_Lists = None

codegenAutoBatch_PY.initDictDefsAlreadyMade = None
""" % (sys_args[0], sys_args[1])
    dummy_class = '<string>'
    Benchmark_codegen_PY = compile(CodegenCall, dummy_class, 'exec')

    ns = {} # local variables
    exec(Benchmark_codegen_PY, None, ns)    
    del Benchmark_codegen_PY
    return (ns['start'], ns['stop'])
