#from batchlang import *
#from batchparser import *
import sdlpath
from sdlparser.SDLParser import *
from batchtechniques import AbstractTechnique
from batchoptimizer import PairInstanceFinder, PairInstanceFinderImproved, ParentExpNode, keyParentExp, InvertedPairing

# BEGIN: Small Exponent Related classes to assist with tracking index numbers assigned to delta variables 
# across multiple verification equations. 
class ApplyEqIndex(AbstractTechnique):
    def __init__(self, index):
        self.index = index
    
    def visit(self, node, data):
        pass
        
    def visit_attr(self, node, data):
        if node.getAttribute() != "1":
            node.setDeltaIndex(self.index)
    
    def visit_pair(self, node, data):
        node.setDeltaIndex(self.index)
    
class AfterTech2AddIndex(AbstractTechnique):
    def __init__(self):
        pass
    
    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        a = []
        if data.get('pair_index'): a = data.get('pair_index') # [str(i) for i in data['pair_index']]
        if Type(node.right) == ops.ATTR and node.right.getAttribute() == "delta":
            if len(a) > 0: node.right.setDeltaIndexFromSet(a)
            else: node.right.setDeltaIndexFromSet( node.left.getDeltaIndex() )
        elif Type(node.right) == ops.MUL:
            mul = node.right
            if Type(mul.left) == ops.ATTR and mul.left.getAttribute() == "delta":
                if len(a) > 0: mul.left.setDeltaIndexFromSet(a)
                else: mul.left.setDeltaIndexFromSet( node.left.getDeltaIndex() )
            if Type(mul.right) == ops.ATTR and mul.right.getAttribute() == "delta":
                if len(a) > 0: mul.right.setDeltaIndexFromSet(a)
                else: mul.right.setDeltaIndexFromSet( node.left.getDeltaIndex() )
        return
  
    def visit_pair(self, node, data):
        d = { 'pair_index':node.getDeltaIndex() }
        return d

class UpdateDeltaIndex(AbstractTechnique):
    def __init__(self):
        pass
    
    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        a = []
        if data.get('attr'): a = data.get('attr')
        if Type(node.right) == ops.ATTR and node.right.getAttribute() == "delta":
            if len(a) > 0: node.right.setDeltaIndexFromSet(a)
            else: node.right.setDeltaIndexFromSet( node.left.getDeltaIndex() )
        elif Type(node.right) == ops.MUL:
            mul = node.right
            if Type(mul.left) == ops.ATTR and mul.left.getAttribute() == "delta":
                if len(a) > 0: mul.left.setDeltaIndexFromSet(a)
                else: mul.left.setDeltaIndexFromSet( node.left.getDeltaIndex() )
            if Type(mul.right) == ops.ATTR and mul.right.getAttribute() == "delta":
                if len(a) > 0: mul.right.setDeltaIndexFromSet(a)
                else: mul.right.setDeltaIndexFromSet( node.left.getDeltaIndex() )
        return
  
    def visit_attr(self, node, data):
        d = { 'attr':node.getDeltaIndex() }
        return d


# END

class TestForMultipleEq:
    def __init__(self):
        self.multiple = False
    
    def visit_and(self, node, data):
        if Type(node.left) == Type(node.right) and Type(node.left) == ops.EQ_TST:
            self.multiple = True
            
    def visit(self, node, data):
        pass

def getIfEqCountTheSame(node):
    lchildnodes = []
    rchildnodes = []
    getListNodes(node.left, Type(node), lchildnodes)
    getListNodes(node.right, Type(node), rchildnodes)
    lsize = len(lchildnodes)
    rsize = len(rchildnodes)
#    print("lhs: ", lsize, node.left)
#    print("rhs: ", rsize, node.right)
    if lsize == rsize:
        return True
    else:
        return False

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


# So called technique 0
# addIndex: means that CombineMultipleEq will add index numbers to each equation for tracking purposes
# so that deltas will have appropriate numbers later.
class CombineMultipleEq(AbstractTechnique):
    def __init__(self, sdl_data=None, variables=None, addIndex=True):
        if sdl_data:
            AbstractTechnique.__init__(self, sdl_data, variables)
        self.inverse = BinaryNode("-1")
        self.finalAND   = [ ]
        self.attr_index = 0
        self.addIndex = addIndex
        self.debug      = False
        
    def visit_and(self, node, data):
        left = BinaryNode("1")
        right = BinaryNode("1")
        combined_eq = None
        marked = False
        if Type(node.left) == ops.EQ_TST and Type(node.right) == ops.EQ_TST:
            if getIfEqCountTheSame(node.left) and getIfEqCountTheSame(node.right):
                print("Next phase: ", node)
                combined_eq = CombineEqWithoutNewDelta(BinaryNode.copy(node.left), BinaryNode.copy(node.right))
                self.attr_index += 1
                aei = ApplyEqIndex(self.attr_index)
                ASTVisitor(aei).preorder(combined_eq)
                marked = True
            #else:
        #print("handle left :=>", node.left, node.left.type)
        #print("handle right :=>", node.right, node.right.type)        
        if not marked and Type(node.left) == ops.EQ_TST:
             self.attr_index += 1
             pair_eq_index = self.attr_index
             left = self.visit_equality(node.left, pair_eq_index)

        if not marked and Type(node.right) == ops.EQ_TST:
             self.attr_index += 1
             pair_eq_index2 = self.attr_index
             right = self.visit_equality(node.right, pair_eq_index2)
        if not marked: combined_eq = BinaryNode(ops.EQ_TST, left, right)
        print("combined_eq first: ", combined_eq)
        
        # test whether technique 6 applies, if so, combine?
#        tech6      = PairInstanceFinder()
#        ASTVisitor(tech6).preorder(combined_eq)
#        if tech6.testForApplication(): tech6.makeSubstitution(combined_eq); print("Result: ", combined_eq)# ; exit(-1)
#        if self.debug: print("Combined eq: ", combined_eq)
        tech6      = PairInstanceFinderImproved()
        ASTVisitor(tech6).preorder(combined_eq)
        if tech6.testForApplication(): tech6.makeSubstitution(combined_eq); print("Result: ", combined_eq)# ; exit(-1)
        if self.debug: print("Combined eq: ", combined_eq)
        self.finalAND.append(combined_eq)
        return
    
    # won't be called automatically (ON PURPOSE)
    def visit_equality(self, node, index):
        #print("index :=", index, " => ", node)
        if self.addIndex:
            aei = ApplyEqIndex(index)
            ASTVisitor(aei).preorder(node)
        # count number of nodes on each side
        lchildnodes = []
        rchildnodes = []
        getListNodes(node.left, Type(node), lchildnodes)
        getListNodes(node.right, Type(node), rchildnodes)
        lsize = len(lchildnodes)
        rsize = len(rchildnodes)
        _list = [ops.EXP, ops.PAIR, ops.ATTR]
#        if (lsize == 1 and rsize == 1):
#            print("lhs: ", node.left)
#            print("rhs: ", node.right)
        if (lsize == 1 and rsize > 1): # or (lsize == rsize):
            # move from left to right
            if self.debug: print("Moving from L to R: ", node)
            new_left = self.createExp2(BinaryNode.copy(node.left), BinaryNode.copy(self.inverse), _list)
            new_node = self.createMul(BinaryNode.copy(node.right), new_left)
            if self.debug: print("Result L to R: ", new_node)
            return new_node
        elif lsize > 1 and rsize == 1:
            # move from right to left
            if str(node.right) != "1":
                if self.debug: print("Moving from R to L: ", node)
                new_right = self.createExp2(BinaryNode.copy(node.right), BinaryNode.copy(self.inverse), _list)
                new_node = self.createMul(BinaryNode.copy(node.left), new_right)
            else:
                new_node = node.left
            if self.debug: print("Result R to L: ", new_node)
            return new_node
        else:
            lsize_pair = 0
            rsize_pair = 0
            for i in lchildnodes:
                if Type(i) == ops.PAIR: lsize_pair += 1
            for i in rchildnodes:
                if Type(i) == ops.PAIR: rsize_pair += 1
            if lsize_pair <= rsize_pair:
                if self.debug: print("Moving from L to R: ", node)
                new_left = self.createExp2(BinaryNode.copy(node.left), BinaryNode.copy(self.inverse), _list)
                new_node = self.createMul(BinaryNode.copy(node.right), new_left)
                if self.debug: print("Result L to R: ", new_node)
                return new_node
            else:               
                print("CE: missing case!") # count pairings?
                print("node: ", lsize_pair, rsize_pair, node)
                sys.exit(0)
            return

class SmallExpTestMul:
    def __init__(self, prefix=None):
        self.prefix = prefix
        
    def visit(self, node, data):
        pass

    def visit_pair(self, node, data):
        pass
#        print("pair node: ", node, ", delta_index: ", node.getAttrIndex())

    # find  'prod{i} on x' transform into ==> 'prod{i} on (x)^delta_i'
    def visit_eq_tst(self, node, data):
        # Restrict to only product nodes that we've introduced for 
        # iterating over the N signatures
        delta = BinaryNode("delta")
        _list = [ops.EXP, ops.PAIR, ops.ATTR]
        if str(node.left) != "1":
            node.left = AbstractTechnique.createExp2(BinaryNode.copy(node.left), delta, _list)            
        if str(node.right) != "1":
            node.right = AbstractTechnique.createExp2(BinaryNode.copy(node.right), BinaryNode.copy(delta), _list)


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
