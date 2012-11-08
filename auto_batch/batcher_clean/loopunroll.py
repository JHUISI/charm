import sdlpath
from sdlparser.SDLParser import *
from batchtechniques import *
from batchcomboeq import ApplyEqIndex,UpdateDeltaIndex
tech10 = Tech_db

# performs step 1 from above. Replaces 't' (target variables) with integer values in each attribute
class EvaluateAtIntValue:
    def __init__(self, target_var, int_value):
        self.target_var = target_var
        self.int_value  = int_value
        self.debug      = False
    
    def visit(self, node, data):
        pass
   
    def visit_attr(self, node, data):#    
        attr = node.getAttribute()
        new_attr = ''
        if attr[-1] == LIST_INDEX_END_SYMBOL:
            attr = attr[0:-1] # don't include last symbol
            addIndexEndLater = LIST_INDEX_END_SYMBOL
        else:
            addIndexEndLater = ''
        s = attr.split(LIST_INDEX_SYMBOL)
        #print("EvaluateAtIntValue: ", s) 
        if( len(s) > 1 ):
            if self.debug: print("attr: ", node, s)
            for i in s:
                if i == self.target_var:
                    new_attr += str(self.int_value)
                elif self.target_var in i: # instead of t+1 or t-1 or etc replace with the evaluated result                    
                    exec("%s = %s" % (self.target_var, self.int_value))
                    new_attr += str(eval(i))
                else:
                    new_attr += i
                new_attr += '#'
            new_attr = new_attr[:-1] # cut off last character
            if self.debug: print("new_attr: ", new_attr)
            node.setAttribute(new_attr + addIndexEndLater)

# objective: combine or merge pairings that have a common first or second element. Takes a dictionary
# of multiple nodes that have a particular structure:
# pairDict =>
#    key : the side that has the constant?
#    lnode : the first left node that was found
#    rnode : the first right node that was found during traversal
#    
class SubstitutePairs3: # modified SubstitutePairs2 specifically for loop unrolling technique
    def __init__(self, pairDict):
        self.pairDict = pairDict
        self.key = pairDict['key']
        self.left = pairDict['lnode']
        self.right = pairDict['rnode']
        self.node_side = pairDict['keyside']
        self.extra_side = pairDict['side']
        self.extra_index = pairDict['pair_index']
        self.parentExpNode = pairDict.get(ParentExpNode) # TODO: come back to this                                                         
        self.keyParentExp  = pairDict.get(keyParentExp)        
        self.index = 0        
        if self.key == 'rnode': # if right, then extras will be on the left
            self.extra = pairDict['lnode1']
            self.extra_parent = pairDict['lnode1_parent']
            self.extra_inverted = pairDict.get('lnode1_' + InvertedPairing)
        elif self.key == 'lnode':
            self.extra = pairDict['rnode1']
            self.extra_parent = pairDict['rnode1_parent']
            self.extra_inverted = pairDict.get('rnode1_' + InvertedPairing)
#        print("DEBUG: ", self.extra_inverted)
            
        self.deleteOtherPair = self.pruneCheck = False
        self.debug = False
        
    def visit(self, node, data):
        if self.deleteOtherPair:
#            print("Type(node) :=", Type(node), node)
#            print("visit: node.right: ", node.right)        
#            print("visit: node.left: ", node.left)    
            if node.left in self.extra_parent:
                if Type(node) != ops.EXP:
                    batchparser.addAsChildNodeToParent(data, node.right)
                    BinaryNode.clearNode(node.left)
                else:
                    # has an exp node therefore treat accordingly
                    #print("warning: found another EXP node: ", node.left, node.right)
                    batchparser.addAsChildNodeToParent(data, node.right)
                    BinaryNode.clearNode(node.left)
                    BinaryNode.clearNode(node.right)
                self.pruneCheck = True 
            elif node.right in self.extra_parent:
                batchparser.addAsChildNodeToParent(data, node.left)
                BinaryNode.clearNode(node.right)
                self.pruneCheck = True 
            else:
                pass
        
    def visit_pair(self, node, data):
#        print("complete list: ", self.extra_side)
        if self.key == 'rnode':
            # find the attribute node on the right
            if self.debug: 
                print("DEBUG: ", node.right, " =?= ", self.right, "left type:", Type(self.left), node.left, self.left)
            if str(node.right) == str(self.right) and Type(node.right) == ops.ATTR:
                #print("Found a right match: ", node, self.left, self.right)
                if node.left == self.left and Type(self.left) == ops.ON:                    
                    if self.debug: print("combine other nodes with ON node: ", self.left)
                    target = self.left
                    for nodes in self.extra:
                        if self.debug: print("other nodes: ", nodes)
                        #print("target :=> ", nodes, " inverted: ", self.extra_inverted)
                        target = self.combine(target, self.checkForInverse(nodes)) # may need to make this smarter to do a proper merge
                        self.left.right = target
                    #print("result => ", self.left)
                    node.left = BinaryNode.copy(self.left)
                    #print("node =>", node)
                    self.deleteOtherPair = True
                
                elif node.left == self.left: # found the target node
                    #print("Need another case: ", node.left, self.left)
                    self.extra.insert(0, BinaryNode.copy(self.left))
                    muls = [ BinaryNode(ops.MUL) for i in range(len(self.extra)-1) ]
                    for i in range(len(muls)):
                        muls[i].left = BinaryNode.copy(self.checkForInverse(self.extra[i]))
                        if i < len(muls)-1: muls[i].right = muls[i+1]
                        else: muls[i].right = BinaryNode.copy(self.checkForInverse(self.extra[i+1]))
                    node.left = muls[0] # self.right doesn't change
                    if self.extra_index: node.setDeltaIndexFromSet(self.extra_index)
                    if self.debug: print("modified nodes: ", node, node.getDeltaIndex())                    
                    #print("new pairing node: ", muls[0], self.right) # MUL nodes absorb the exponent
                    self.deleteOtherPair = True                    

                elif node.left in self.extra: # foudn the other nodes we want to delete                    
                    del node.left, node.right
                    node.left = None
                    node.right = None
                    BinaryNode.clearNode(node)
                    self.pruneCheck = True
                
                    
            elif str(node.right) == str(self.right):
                #print("Found a match, general right case: ", self.left, self.right)
                for i in self.extra:
                    print("node: ", i)                
                
        elif self.key == 'lnode':
            if str(node.left) == str(self.left) and Type(node.left) == ops.ATTR:
                if self.debug: print("handle this case: ", node)
                if node.right == self.right and Type(self.right) == ops.ON:
                    if self.debug: print("combine other nodes with ON node: ", self.right)
                    target = self.right
                    for nodes in self.extra:
                        target = self.combine(target, self.checkForInverse(nodes)) # may need to make this smarter to do a proper merge
                        self.right.right = target
                    #print("ans => ", self.left)
                    node.left = BinaryNode.copy(self.left)
                    #print("node =>", node)
                    self.deleteOtherPair = True
                elif node.right == self.right:
#                    print("Type of parent: ", Type(data['parent'])) # in case of e(a,b)^c and we're about to merge the pairing...we need to move c into pairing first                    
                    self.extra.insert(0, BinaryNode.copy(self.right))
                    muls = [ BinaryNode(ops.MUL) for i in range(len(self.extra)-1) ]
                    for i in range(len(muls)):                        
                        muls[i].left = BinaryNode.copy(self.checkForInverse(self.extra[i]))
                        if i < len(muls)-1: muls[i].right = muls[i+1]
                        else: 
                            muls[i].right = BinaryNode.copy(self.checkForInverse(self.extra[i+1]))
                    node.right = muls[0] # self.right doesn't change
                    if self.extra_index: node.setDeltaIndexFromSet(self.extra_index)
                    if self.debug: print("modified nodes: ", node, node.getDeltaIndex())
                    #print("new pairing node: ", self.left, muls[0]) # MUL nodes absorb the exponent
                    self.deleteOtherPair = True                    
#                    print("New node: ", node)
                elif node.right in self.extra:
                    #print("delete node: ", node)
                    del node.left, node.right
                    node.left = None
                    node.right = None
                    BinaryNode.clearNode(node)
                    self.pruneCheck = True                
            elif str(node.left) == str(self.left):
                #print("Found a match, general left case: ", self.left, self.right)
#                if Type(data['parent']) != ops.ON:
                    # potentially prevent infinite loop of reverse split tech 3 and combine pairing of tech 6
#                    return
                if self.debug: print("warning: this code has not been fully tested yet.", self.left, node.left, self.right)
                target = self.right
                for i in self.extra:
                    target = self.combine(target, BinaryNode.copy(self.checkForInverse(i)))
#                    print("mul: ", target)
                    node.right = target
                    self.deleteOtherPair = True
        else:
            print("invalid or unrecognized key: ", self.key)
    
    def checkForInverse(self, node):
        if self.extra_side.get(str(node)):
            if self.node_side != self.extra_side[str(node)]:
                if self.debug:
                    print('different side! take inverse')
                    print("node: ", node, self.extra_side[str(node)])
                if self.extra_inverted: 
                    #print("The CL fix: ", self.extra_inverted)
                    return node
                    # this means we shouldn't invert the node because we're combining from another node
                return batchtechniques.AbstractTechnique.createInvExp(node)
        
        if self.debug: print('same side: ', self.node_side, node, self.extra_side)
        if self.extra_inverted: return batchtechniques.AbstractTechnique.createInvExp(node) # ONLY DIFFERENCE BETWEEN SP2 and SP3
        return node
                        
    def combine(self, subtree1, subtree2, parentOfTarget=None):
        #print("DEBUG: Combining two subtrees: ", subtree1,"<= with =>" , subtree2)
        if Type(subtree1) == Type(subtree2) and Type(subtree1) == ops.ON:
            #print("Found ON node: ", subtree1)
            return self.combine(subtree1.right, subtree2.right)
        elif Type(subtree1) == Type(subtree2) and Type(subtree1) == ops.MUL:
            #print("Found MUL node: ", subtree1, subtree2)
            return batchtechniques.AbstractTechnique.createMul(subtree1, subtree2)
        elif Type(subtree1) == Type(subtree2) and Type(subtree1) == ops.EXP:
            if str(subtree1.left) == str(subtree2.left):
                # print("Found EXP node bases that match: ", subtree1, subtree2)
                # this is for the situation where the bases are the same
                # e.g., g^x * g^y => g^(x + y)
                addNode = BinaryNode(ops.ADD)
                addNode.left = subtree1.right
                addNode.right = subtree2.right
                return batchtechniques.AbstractTechnique.createExp(subtree1.left, addNode)
            return batchtechniques.AbstractTechnique.createMul(subtree1, subtree2)
        else:
            #print("Found node: ", Type(subtree1), Type(subtree2))
            #print("Now combining these two: ", subtree1, "<= WITH => ", subtree2)
            return BinaryNode(ops.MUL, BinaryNode.copy(subtree1), BinaryNode.copy(subtree2))


# This class determines whether a binary node tree that includes a for loop node can actually be unrolled
# if so, proceed to execute the UnrollLoop made up of two sub classes:
# 1) Evaluates a given binary node tree at a particular iteration point and proceeds to combine it with the previous equation, 
# 2) Applies combo techniques to optimize the unrolled equations, etc.
class Technique10(AbstractTechnique):
    def __init__(self, sdl_data, variables, loopInfo):
        AbstractTechnique.__init__(self, sdl_data, variables) 
        self.sdl_data = sdl_data
        self.types = variables 
        self.rule    = "Unroll constant-size for loop (technique 10)"
        self.applied = False 
        self.score   = tech10.NoneApplied
        self.debug = False      
        self.loopStmt   = None
        if loopInfo == None:
            self.for_iterator = self.for_start = self.for_end = None
            return
        self.for_iterator = str(loopInfo[0])
        if loopInfo[1].isdigit():
            self.for_start = int(loopInfo[1])
        else:
            # perform lookup
            self.for_start = int(variables[loopInfo[1]])
        if loopInfo[2].isdigit():
            self.for_end = int(loopInfo[2])
        else:
            # perform lookup
            self.for_end = int(variables[loopInfo[2]])
    
    def testForApplication(self):
        if self.for_start != None and self.for_iterator != None and self.for_end != None:
            self.applied = True
            self.score   = tech10.ConstantSizeLoop
        else:
            self.applied = False
        return self.applied

    def makeSubsitution(self, equation, delta_count=0):
        evalint = EvaluateAtIntValue(self.for_iterator, self.for_start)
        testEq = BinaryNode.copy(equation)
        ASTVisitor(evalint).preorder(testEq)
        
        aei = ApplyEqIndex(delta_count)
        ASTVisitor(aei).preorder(testEq)
        delta_count += 1
        aftTech2 = UpdateDeltaIndex()
        ASTVisitor(aftTech2).preorder(testEq)  

#        print("Evaluated version at %d: %s" % (Tech10.for_start, testEq))
#        print("Combine the rest into this one...")
        for t in range(self.for_start+1, self.for_end):
            evalint = EvaluateAtIntValue(self.for_iterator, t)  
            testEq2 = BinaryNode.copy(equation)
            ASTVisitor(evalint).preorder(testEq2)
            
            aei = ApplyEqIndex(delta_count)
            ASTVisitor(aei).preorder(testEq2)
            delta_count += 1
            aftTech2 = UpdateDeltaIndex()
            ASTVisitor(aftTech2).preorder(testEq2)
            
#            print("Eval-n-Combine version at %d: %s" % (t, testEq2))  
            # break up
            if Type(testEq2) == ops.EQ_TST:
                lhsNode = testEq2.left
                rhsNode = testEq2.right
                #print("Combine: %d => %s =?= %s" % (t, lhsNode, rhsNode))
                cie = CombineIntoEq(lhsNode, rhsNode)
                ASTVisitor(cie).preorder(testEq)

                tech6      = PairInstanceFinderImproved()
                ASTVisitor(tech6).preorder(testEq)        
                if tech6.testForApplication(): 
                    tech6.makeSubstitution(testEq, SubstitutePairs3)
                # simplify exponents    
                tech2 = Technique2(self.sdl_data, self.types)
                ASTVisitor(tech2).preorder(testEq)
        
        return testEq
        
        # simplify exponents
#        print("NEW T6: ", testEq, "\n\n")
#        tech2 = Technique2(self.sdl_data, self.types)
#        ASTVisitor(tech2).preorder(testEq)
#        print("Simplified RESULT: ", testEq)
#        sys.exit(0)

def CombineEqWithoutNewDelta(eq1, eq2):
#    print("\n\nEq 1: ", eq1, "\n")
    
#    print("Eq 2 l: ", eq2.left, "\n\n")
#    print("Eq 2 r: ", eq2.right, "\n\n")    
    if Type(eq1) == ops.EQ_TST and Type(eq2) == ops.EQ_TST:        
        mul = BinaryNode(ops.MUL)
        mul.left = BinaryNode.copy(eq1.left)
        mul.right = BinaryNode.copy(eq2.left)
                
        mul2 = BinaryNode(ops.MUL)
        mul2.left = BinaryNode.copy(eq1.right)
        mul2.right = BinaryNode.copy(eq2.right)
        
        eq1.left = mul
        eq1.right = mul2
        
#        cie = CombineIntoEq(eq2.left, eq2.right)
#        ASTVisitor(cie).preorder(eq1)
#        print("COMBINED: ", eq1, "\n")
        tech6 = PairInstanceFinderImproved()
        ASTVisitor(tech6).preorder(eq1)
        if tech6.testForApplication(): 
            tech6.makeSubstitution(eq1, SubstitutePairs3)    
#        print("FINAL eq: ", eq1)
#        sys.exit(0)
    return eq1
    
        
class CombineIntoEq:
    def __init__(self, lhsNode=None, rhsNode=None):
        self.lhsNode = lhsNode
        self.rhsNode = rhsNode
    
    def visit(self, node, data):
        pass
    
    def visit_eq_tst(self, node, data):
        mul = BinaryNode(ops.MUL)
        mul.left = BinaryNode.copy(node.left)
        mul.right = AbstractTechnique.createInvExpImproved(self.lhsNode)
                
        mul2 = BinaryNode(ops.MUL)
        mul2.left = BinaryNode.copy(node.right)
        mul2.right = AbstractTechnique.createInvExpImproved(self.rhsNode)
                
        node.left = mul
        node.right = mul2
        
    
    