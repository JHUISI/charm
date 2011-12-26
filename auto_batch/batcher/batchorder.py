from batchparser import *
from batchtechniques import Technique2,Technique3,Technique4
from batchoptimizer import *
import random

try:
    #import benchmarks
    import miraclbench
    curves = miraclbench.benchmarks
    c_key = 'mnt160'
except:
    print("Could not find the 'benchmarks' file that has measurement results! Generate and re-run.")
    exit(0)


def fact(n):
    if n == 0:
        return 1
    elif n == 1 or n == 2:
        return n
    else:
        return n * fact(n - 1)

def score(eq):
    pass

# Class for pre-processing SDL to determine the order in which the optimization techniques
# are applied to the batch equation.
class BatchOrder:
    def __init__(self, const, vars, metadata, equation):
        self.const = const
        self.vars  = vars
        self.meta  = metadata
        self.verify = equation
        self.debug  = False
        self.techMap = { 2:Technique2, 3:Technique3, 4:Technique4 }
        # a quick way to test that a particular technique will transform the equation (pre-check)
        #self.detectMap2 = { 2:Technique2Check, 3:Technique3Check, 4:Technique4Check, 5:DotProdInstanceFinder, 6:PairInstanceFinder }
        self.detectMap2 = self.techMap

    def testSequence(self, combo):
        eq = BinaryNode.copy(self.verify)
        order = []
        for k in combo:
            tech = self.techMap[k](self.const, self.vars, self.meta)
            # traverse verify with tech operations
            ASTVisitor(tech).preorder(eq)
#            print("Result: ", self.verify, "\nApplied: ", tech.applied)
            if tech.applied: 
                if self.debug: print("Applied ", k, ":", self.verify)
                order.append(k)
        return (order, eq)
    
    def strategy(self, option=None):
        return self.BasicStrategy()
    
    # Try all permutations of techniques (does not repeat applying technique)
    def BasicStrategy(self):
        techniques = [2, 3, 4]
        count = fact(len(techniques))
        tools = {'S':SimplifyDotProducts, 'P':PairInstanceFinder }
        if self.debug: print("Basic Strategy...")
        order = []
        
        t = list(techniques)
        possib_set = []; i = 0
        final_list = []; batch_time = []
        N = int(self.vars['N'])
        # get all the permutations of the techniques
        while i < count:
            random.shuffle(t)
            if not t in possib_set:
                new = list(t)
                possib_set.append(new)
                (order, verify_eq) = self.testSequence(new)
                if self.debug:
                    print("sequence: ", j, " : applied order: ", order)
                    print("verify_eq: ", verify_eq)
                if not order in final_list:
                    final_list.append(order)
                    # measure
                    rop_batch = RecordOperations(self.vars)
                    rop_batch.visit(verify_eq, {})
                    (msmt, avg) = calculate_times(rop_batch.ops, curves[c_key], N)
                    batch_time.append(avg)
                i += 1 # breaks permutation loop

        index = batch_time.index(min(batch_time))
        if self.debug: print("Final list: ", final_list)
        print("Technique order: ", final_list[index], ": avg batch time: ", batch_time[index])
        return final_list[index]

    # recognized patterns of techniques that lead to the optimized batch algorithm 
    # this could load from a db with each pattern that is discovered in the past?
    def RPStrategy(self):
        # db = loadDB() # list of orderings 
        pass
    
    def BFStrategy(self):
        techniques = list(self.detectMap2.keys())
        # starting point: choose a tech
        
        pass
    
    
