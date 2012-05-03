#import sys
#if ".../batcher2" not in sys.path:
#   sys.path.insert(0, '../batcher2')
#from batchverify import *

def clearBatcherGlobals():
    """clear all globals"""
    excludeList = ["clearBatcherGlobals", "batcher_main"]
    for uniquevar in [var for var in globals().copy() if var[0] != "_" and not var in excludeList]:
        pass
#        print("del global =>", uniquevar)
#        del globals()[uniquevar]

def Batcher(sys_args, prefix=None):
#    batcher_main(sys_args, prefix)
#    return benchmark_batcher(sys_args, prefix)
    BatcherCall = """\n
import sys, time
sys.path.insert(0, '../batcher2')
from batchverify import benchmark_batcher

start = time.time()
benchmark_batcher(%s, %s)
stop = time.time()""" % (str(sys_args), "None")
    dummy_class = '<string>'
    Benchmark_batcher = compile(BatcherCall, dummy_class, 'exec')

    ns = {} # local variables
    exec(Benchmark_batcher, None, ns)    
    del Benchmark_batcher
    return (ns['start'], ns['stop'])
