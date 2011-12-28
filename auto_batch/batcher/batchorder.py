from batchparser import *
from batchtechniques import Tech_db,Technique2,Technique3,Technique4,DistributeDotProducts
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
        self.techMap2 = { 5:DotProdInstanceFinder, 6:PairInstanceFinder }
        self.techTool = { 5:SimplifyDotProducts, 6:PairInstanceFinder }

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
    
    def testTechnique(self, tech_option, equation):
        eq2 = BinaryNode.copy(equation)
        
        tech = None
        if tech_option in self.techMap.keys():
            tech = self.techMap[tech_option](self.const, self.vars, self.meta)
        elif tech_option in self.techMap2.keys():
            tech = self.techMap2[tech_option]()
        else:
            return None
        
        # traverse equation with the specified technique
        ASTVisitor(tech).preorder(eq2)
        # return the results
        return (tech, eq2)
    
    def strategy(self, option=None):
        return self.BasicStrategy()
    
    # Try all permutations of techniques (does not repeat applying technique)
    def BasicStrategy(self):
        techniques = [2, 3, 4]
        count = fact(len(techniques))
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
    
    # take the current 
    def possibleTechniques(self, tech_applied, tech_obj, excl_tech_list):
        suggest = None
        if tech_obj.applied:
            if tech_applied == 2:
                if tech_obj.score in [Tech_db.ExpIntoPairing, Tech_db.DistributeExpToPairing]:
                    suggest = [5, 3] # move on to tech3 or distribute dot products if possible
            elif tech_applied == 3:
                if tech_obj.score == Tech_db.CombinePairing:
                    suggest = [5]
                elif tech_obj.score == Tech_db.SplitPairing:
                    suggest = [2, 4]
            elif tech_applied == 4:
                if tech_obj.score == Tech_db.ConstantPairing:
                    suggest = [5, 3, 6]
            elif tech_applied == 5: # distribute products
                if tech_obj.testForApplication:
                    suggest = [3, 4]
            elif tech_applied == 6: # combine pairings
                if tech_obj.testForApplication:
                    suggest = [3, 5]
            else:
                return
        else:
            # try something else, if didn't apply
            suggest = [2, 3, 4, 5, 6]
            suggest.remove(tech_applied)
            for i in excl_tech_list:
                suggest.remove(i)
        return suggest
    
    def BFStrategy(self, start_tech=None):
        techniques = list(self.detectMap2.keys())
        # starting point: start
        if start_tech:
            # 1. apply the start technique to equation
            cur_tech  = start_tech
            excl_list = []
            (tech, verify_eq) = self.testTechnique(cur_tech, self.verify)
                        
            # check score and get next option
            next_tech = self.possibleTechniques(cur_tech, tech, excl_list)
            
            
            # 2. suggest next technique or tool (2 - 6): current state, previous technique applied, and equation
            # 3. measure efficiency of current batch equation
            # 4. if measurement does not converge meaning savings before or after application of tech is thesame
            # 5. 
        
    
