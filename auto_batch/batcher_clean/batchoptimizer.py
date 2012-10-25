# These classes assist in finding optimizations that can be made in the batch equation.
# If one is detected, that is, more than one instance of an exponentiation or pairing with
# the same variables is found, then it is a candidate for further optimization. This is separate
# from the techniques in batch parser, however.
import batchtechniques 
import sdlpath
import sdlparser.SDLParser as batchparser
from sdlparser.SDLang import *

import string

InvertedPairing = "invertedPairing"
ParentExpNode   = "parentExpAttr"                                                         
keyParentExp    = "keyParentExp"
class ExpInstanceFinder:
    def __init__(self):
        # keys must match
        self.instance = {}
    
    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        left = node.left
        right = node.right
        if left.type == ops.ATTR:
            if right.type == ops.ATTR:
                self.record(str(left), str(right))
            elif right.type == ops.MUL:
                # a ^ (b * c) ==> a : b, a : c
                value_1 = right.left
                value_2 = right.right
                if value_1.type == ops.ATTR:
                    self.record(str(left), str(value_1))
                if value_2.type == ops.ATTR:
                    self.record(str(left), str(value_2))
            else:
                # dont care for now
                return

    def record(self, key, value):
#        print("key =>", key, ", value =>", value)
        if self.instance.get( key ):
            if self.instance[ key ].get( value ):
                self.instance[ key ][ value ] += 1
            else:
                self.instance[ key ][ value ] = 1
            return

        self.instance[ key ] = { value: 1 }
        return


# Technique 6 - combining pairings with common elements (1st or 2nd)
class PairInstanceFinder:
    def __init__(self):
        # keys must match
        self.instance = {}
        self.index = 0
        self.rule = "Merge pairings with common first or second element (technique 6)"
        self.applied = False
        self.side = { 'left':[] }
        self.debug = False
        
    def visit(self, node, data):
        pass        

    def visit_eq_tst(self, node, data):
        lnodes = []
        getListNodes(node.left, Type(node), lnodes)
        for i in lnodes:
            if Type(i) == ops.PAIR: self.side['left'].append(str(i))
            elif i.left != None and Type(i.left) == ops.PAIR: self.side['left'].append(str(i.left))

    def visit_pair(self, node, data):
        #print("T6: parent type: ", Type(data['parent']))
        lhs = node.left
        rhs = node.right
        key = None
        
        # record which side
        if str(node) in self.side['left']:
            whichSide = side.left
        else:
            whichSide = side.right
        
        if Type(lhs) == ops.ATTR:
            key = 'lnode'

        if Type(rhs) == ops.ATTR:
            key = 'rnode'
                    
        if Type(data['parent']) == ops.ON:
            self.record(key, node, whichSide, data['parent'])
        else:
            self.record(key, node, whichSide)
            
        return

    def debugPrint(self, theDict, keys):
        print("<==== DEBUG ====>")
        for i in keys:
            print(i, ":", str(theDict.get(i)))
        print("<==== DEBUG ====>")
        return

    def record(self, key, node, whichSide, parent=None):
        lnode = node.left
        rnode = node.right
        #print("key =>", key, ", nodes =>", lnode, rnode)
        found = False
        for i in self.instance.keys():
            data = self.instance[ i ]
#            print("found another: ", data['key'], data['lnode'], data['rnode'], data['instance'])
            if data['key'] == 'lnode':
#                print("LNODE: Found a combo pairing instance 1: ", lnode, "==", data['lnode'])
                if str(lnode) == str(data['lnode']): # found a match
                    data['instance'] += 1 # increment the finding of an instance
                    if data.get('rnode1'): data['rnode1'].append(rnode)
                    else: data['rnode1'] = [rnode] 
                    data['side'][ str(rnode) ] = whichSide
                    # save some state to delete this node on second pass  
                    if not data.get('rnode1_parent'): data['rnode1_parent'] = [] # create new list                  
                    if parent: data['rnode1_parent'].append(parent)
                    else: data['rnode1_parent'].append(node)                                 
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    break
            elif data['key'] == 'rnode':
                if str(rnode) == str(data['rnode']):
#                    print("RNODE: Found a combo pairing instance: ", rnode, "==", data['rnode'])                
                    data['instance'] += 1
                    if data.get('lnode1'): data['lnode1'].append(lnode)
                    else: data['lnode1'] = [lnode]
                    data['side'][ str(lnode) ] = whichSide
                    # save some state to delete this node on second pass
                    if not data.get('lnode1_parent'): data['lnode1_parent'] = [] # create new list                  
                    if parent: data['lnode1_parent'].append(parent)
                    else: data['lnode1_parent'].append(node)                    
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    break
                elif str(lnode) == str(data['lnode']):
#                    print("LNODE: Found a combo pairing instance 2: ", lnode, "==", data['lnode'])                                    
                    # basically, find that non-constants match. for example,
                    # case: e(x * y, g) and e(x * y, h) transforms to e(x * y, g * h)
                    #print("found a new case.\ninput: ", lnode, rnode)
                    #print("data node: ", data['lnode'], data['rnode'], data['key'])
                    # switch sides
                    data['key'] = 'lnode'
                    data['instance'] += 1
                    if data.get('rnode1'): data['rnode1'].append(rnode)
                    else: data['rnode1'] = [rnode]
                    data['side'][ str(rnode) ] = whichSide
                    # save some state to delete this node on second pass
                    if not data.get('rnode1_parent'): data['rnode1_parent'] = [] # create new list                  
                    if parent: data['rnode1_parent'].append(parent)
                    else: data['rnode1_parent'].append(node)                    
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    #self.debugPrint(data, ['key', 'lnode', 'rnode', 'keyside', 'instance', 'rnode1', 'rnode1_parent', 'pair_index'])                    
                    break

        # if not found
        if not found:
            if not node.isDeltaIndexEmpty(): attr_index = set(node.getDeltaIndex())
            else: attr_index = None
            self.instance[ self.index ] = { 'key':key, 'lnode':lnode, 'rnode':rnode, 'keyside':whichSide,'instance':1, 'side':{}, 'pair_index':attr_index }
            if self.debug:
                print("<=== Adding base instance ====>")
                print("key: ", key)
                print("lnode: ", lnode)
                print("rnode: ", rnode)
                print("keyside: ", whichSide)
                print("pair_index: ", attr_index)
                print("<=== Adding base instance ====>")                
            self.index += 1
        return

    def checkForMultiple(self, check=False):
        for i in self.instance.keys():
            data = self.instance[ i ]
            if data['instance'] > 1:
                if not check: return data
                else: return True
        return None
    
    def makeSubstitution(self, equation):
        # first get a node in which 
#        tech6Applied = self.testForApplication()
#        print("tech 6 apply? =>", tech6Applied)
        pairDict = self.checkForMultiple()     
        equation2 = BinaryNode.copy(equation)
        if pairDict != None:
#            print("Pair =>", pairDict, "\n\n\n")
#            for i in pairDict.keys():
#                if type(pairDict[i]) == list:
#                    print("list: ", i)
#                    for j in pairDict[i]:
#                        print("\tnodes:", j)
#                else:
#                    print(i, ":=>", pairDict[i])
            SP2 = SubstitutePairs2( pairDict )
            batchparser.ASTVisitor( SP2 ).preorder( equation )
            if SP2.pruneCheck: 
                batchparser.ASTVisitor( PruneTree() ).preorder( equation )
            if self.failedTechnique(equation): self.applied = False; return equation2
            else: return None 
                
    def failedTechnique(self, equation):
        check = SanityCheckT6()
        batchparser.ASTVisitor( check ).preorder( equation )
#        print("Test sanity check: ", check.foundError)
        return check.foundError
#                print("Test sanity check: ", check.foundError)
#                print("result 1:", equation2)
#                print("result 2:", equation)
#                print("pairDict keys: ", pairDict.keys())
#                # update the dictionary
##                self.applied = check.foundError
#                return equation2
#            elif not check.foundError and not tech6Applied:
#                return equation
#            else:
#                print("Reverting state back: ", equation)
#                self.applied = False
#                return equation
#            print("Done\n")
    
    def testForApplication(self):
        self.applied = self.checkForMultiple(True)
        return self.applied
        

# substitute nodes that can be precomputed with a stub
# variable that is computed later
class SubstituteExps:
    def __init__(self, op_instance, precomp, variables):
        # assert input is not equal to None
        self.instance = op_instance
        self.inst_map = {}
        self.precomp = precomp
        self.precomp_code = {} # for new optimizations we find
        self.vars = variables
        self.prefix = 'pre' # self.prefix + self.alpha[cnt]; cnt += 1
        self.alpha = string.ascii_uppercase
        self.cnt = 0

    # TODO: clean-up this implementation
    def canExpBePrecomputed(self, base, exp):
        for i in self.instance.keys():
            for j in self.instance[ i ].keys():
                if self.instance[ i ][ j ] > 1 and (i == str(base) and j == str(exp)) and len(base.attr_index) == 1:
                    # combine sets: TODO
                    if base.attr_index: index = base.attr_index[0] 
                    if exp.attr_index: index = exp.attr_index[0]
                    else: index = None
                    _key = self.record(str(i), str(j), index)
                    #print("_key =>", _key, "\n\n")
                    k = BinaryNode(_key)

                    self.precomp[ _key ] = str(i) + "^" + str(j)
#                    if index == 'j': # "j => N", "i => whatever"
#                        bp = batchparser.BatchParser()
#                        self.precomp_code[ _key ] = bp.parse("for{j:=1, N} do " + str(i) + "^" + str(j))   
                    if self.vars.get(base.getAttribute()) == None:
                        print("Need to define variable: ", base.getAttribute())
                    else:
                        self.vars[ k.getAttribute() ] = self.vars[ base.getAttribute() ]
                    # can we find a precomp key for this? if so, return it
                    # otherwise, create one and return it.(IMPORTANT!!!!)
                    return _key
        return False

    def record(self, key, value, index=None):
#        print("key =>", key, ", value =>", value)
        if self.inst_map.get( key ):
            if self.inst_map[ key ].get( value ):
                var = self.inst_map[ key ][ value ]
                #print("recovered key =>", var)
                return var
            else:
                self.cnt += 1
                if index: var_index = index
                else: var_index = ''
                self.inst_map[ key ][ value ] = self.prefix + self.alpha[self.cnt] + '_' + var_index
                return self.inst_map[ key ][ value ]
            return 
        
        if index: var_index = index
        else: var_index = ''
        self.inst_map[ key ] = { value: self.prefix + self.alpha[self.cnt] + '_' + var_index }
        self.cnt += 1
        #print("found key =>", self.inst_map[ key ][ value ])
        return self.inst_map[ key ][ value ]

    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        left = node.left
        right = node.right
        #print("left type =>", Type(left))
        if Type(left) == ops.ATTR:
            if Type(right) == ops.ATTR:
                key = self.canExpBePrecomputed(left, right)
                if key:
                    # make substitution
                    new_node = BinaryNode(key)
                    batchparser.addAsChildNodeToParent(data, new_node)
                else:
                    pass
                    #print("left =>", left)
                    #print("right =>", right) 
                    # no need to apply any substitutions
            elif Type(right) == ops.MUL:
                node_1 = right.left
                node_2 = right.right
#                print("left =>", left)
#                print("node1 =>", node_1)
#                print("node2 =>", node_2)
                if Type(node_1) == ops.ATTR:
                    key = self.canExpBePrecomputed(left, node_1)
                    if key:
                        # a ^ (b * c) ==> A ^ c (if a^b can be precomputed)
                        new_node1 = BinaryNode(ops.EXP)
                        new_node1.left = BinaryNode(key)
                        new_node1.right = node_2                        
                        batchparser.addAsChildNodeToParent(data, new_node1)
                
                if Type(node_2) == ops.ATTR:
                    key = self.canExpBePrecomputed(left, node_2)
                    if key:
                        # a ^ (b * c) ==> A ^ b (if a^c can be precomputed)                        
                        new_node2 = BinaryNode(ops.EXP)
                        new_node2.left = BinaryNode(key)
                        new_node2.right = node_1
                        batchparser.addAsChildNodeToParent(data, new_node2)
            elif Type(right) == ops.OF:
                pass
            else:
                print("Substitute: missing some cases: ", Type(right))

# objective: combine or merge pairings that have a common first or second element. Takes a dictionary
# of multiple nodes that have a particular structure:
# pairDict =>
#    key : the side that has the constant?
#    lnode : the first left node that was found
#    rnode : the first right node that was found during traversal
#    
class SubstitutePairs2:
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

class PruneTree:
    def __init__(self):
        pass

    def visit_eq_tst(self, node, data):
        # used to clean up in the event we delete a node and cannot move 
        # up any further. In this case, just replace with a 1.
        if Type(node.left) == ops.NONE:
            node.left = BinaryNode("1")
        elif Type(node.right) == ops.NONE:
            node.right = BinaryNode("1")      
    
    def visit(self, node, data):
        if Type(node.left) != ops.NONE and Type(node.right) == ops.NONE:
            #print("prune this 1: ", node)
            batchparser.addAsChildNodeToParent(data, node.left)            
        if Type(node.left) == ops.NONE and Type(node.right) != ops.NONE:
            #print("prune this 2: ", node)
            batchparser.addAsChildNodeToParent(data, node.right)            

class SanityCheckT6:
    def __init__(self):
        self.foundError = False
    
    def visit(self, node, data):
        pass
    
    def visit_prod(self, node, data):
        if Type(data['parent']) != ops.ON:
            self.foundError = True
    
    def visit_on(self, node, data):
        if Type(node.left) != ops.PROD:
            self.foundError = True
    
    def visit_pair(self, node, data):
        if node.left == None or node.right == None:
            self.foundError = True
    
        
        
class SubstituteSigDotProds:
    def __init__(self, vars, index='z', sig='N', cnt=0 ):
        self.prefix = 'dot' # self.prefix + self.alpha[cnt]; cnt += 1
        self.alpha = string.ascii_uppercase
        self.cnt = cnt        
        self.sig = sig 
        self.index = index 
        self.vars_def = vars
        self.dotprod = { 'start':'1', 'stop':self.sig, 'index':self.index, 'list':[], 'dict':{}, 'types':{} }

    def setState(self, count):
        self.cnt = count # allow us to maintain a synchronized alphabet
        
    def getkey(self, prefix=None):
        if prefix:
            key = prefix + self.alpha[self.cnt]
        else: 
            key = self.prefix + self.alpha[self.cnt]
        self.cnt += 1
        #print('key =>', key)
        return key
    
    def getVarCount(self):
        return self.cnt
    
    def store(self, key, value, the_type=None):
        self.dotprod[ 'dict' ][ str(key) ] = value
        self.dotprod[ 'types' ][ str(key) ] = the_type
        self.dotprod[ 'list' ].append( str(key) )
    
    def visit(self, node, data):
        pass
    
    def visit_on(self, node, data):
        index = str(node.left.right.attr)
        dot_type = self.extractType(self.deriveNodeType(node.right))
        #print("node.right type +=> ", dot_type, node.right)
        #print("index =>", index)

        n = self.searchProd(node.right, node)
#        print("visit_on :=> ", node.right, Type(node.right))
        if n:
            (t, p) = n
#            print("Found parent : ", p)
#            print("Found it : ", t)
            dot_type2 = self.extractType(self.deriveNodeType(t.right))
            # perform substition
            subkey = BinaryNode(self.getkey())
            self.store(subkey, t, dot_type2)

            if p.left == t:
                p.left = subkey
#                print("p after substitution =>", p)
            elif p.right == t:
#                print("new substitution: ", p)
#                print("subkey: ", subkey)
                p.right = subkey
        
        if index == self.sig:
            key = BinaryNode(self.getkey())
            self.store(key, node, dot_type)
            
            batchparser.addAsChildNodeToParent(data, key)

    
    def visit_of(self, node, data):
        sig = str(node.left.right.attr)

        if sig == self.sig:
            key = BinaryNode(self.getkey('sum'))
#            if node.right.getAttribute() == 'delta':
#                self.store(key, node, 'ZR')
#            else:
            self.store(key, node, 'ZR') # most likely
            batchparser.addAsChildNodeToParent(data, key)
            
                
    def searchProd(self, node, parent):
        if node == None: return None
        elif node.type in [ops.ON]:
            return (node, parent)
        else:
            result = self.searchProd(node.left, node)
            if result: return result            
            result = self.searchProd(node.right, node)
            return result

    def extractType(self, typeValue):
        if typeValue == str(types.listZR):
            return 'ZR'
        elif typeValue == str(types.listG1):
            return 'G1'
        elif typeValue == str(types.listG2):
            return 'G2'
        elif typeValue == str(types.listGT):
            return 'GT'
        return typeValue

    def deriveNodeType(self, node):
        if node.type == ops.ATTR:
            _type = node.attr
        elif node.type == ops.HASH:
            _type = str(node.right.attr)
            return _type
        elif node.type == ops.EXP:
            return self.deriveNodeType(node.left)
        elif node.type == ops.PAIR:
            return 'GT'
        elif node.type == ops.ON:
            return self.deriveNodeType(node.right)
        elif node == None:
            return None
        else:
            return self.deriveNodeType(node.left)
        #print("printing type =>", _type)
        #print("node =>", node)
        assert self.vars_def.get(_type) != None, "Key error in vars db => '%s'" % _type
        return self.vars_def[_type]

# Focuses on simplifying dot products of the form
# prod{} on (x * y)
class DotProdInstanceFinder:
    def __init__(self):
        self.rule = "Distribute dot products (technique 5): "
        self.applied = False

    def getMulTokens(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.EXP and Type(subtree) == ops.MUL:
            return               
        elif parent_type == ops.MUL:
            if Type(subtree) in target_type: 
                found = False
                for i in _list:
                    if isNodeInSubtree(i, subtree): found = True
                if not found: _list.append(subtree)

        if subtree.left: self.getMulTokens(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens(subtree.right, subtree.type, target_type, _list)
        return
        
    def visit(self, node, data):
        pass

    def visit_pair(self, node, data):
        return { 'visited_pair': True }
    
    # Bandaid: cleaning up when about to distribute a dot products where PROD node has no ON node
    # in other words, dangling PROD node in verify equation
    def visit_prod(self, node, data):
        if Type(data['parent']) != ops.ON:
            #print("Found a candidate for cleaning!!!")
            new_node = BinaryNode(ops.ATTR)
            new_node.setAttribute("1")
            BinaryNode.clearNode(node)
            BinaryNode.setNodeAs(node, new_node)
            
            
    # visit all the ON nodes and test whether we can distribute the product to children nodes
    # e.g., prod{} on (x * y) => prod{} on x * prod{} on y    
    def visit_on(self, node, data):
#        print("DP finder: ", data.get('visited_pair'))
        if Type(data['parent']) == ops.PAIR or data.get('visited_pair'): # bail if dot prod already a child of a pairing node
            return
        #print("T5: right node type =>", Type(node.right), node.right)
        if Type(node.right) == ops.ON: # prod{} on (prod{} on x). thus, we should bail
            return
        #print("test: right node of prod =>", node.right, ": type =>", node.right.type)
        #print("parent type =>", Type(data['parent']))
#        _type = node.right.type
        if Type(node.right) == ops.MUL:            
            # must distribute prod to both children of mul
            r = []
            mul_node = node.right
            self.getMulTokens(mul_node, ops.NONE, [ops.EXP, ops.HASH, ops.PAIR, ops.ATTR], r)
            #for i in r:
            #    print("node =>", i)
            
            if len(r) == 0:
                pass
            elif len(r) <= 2:
            # in case we're dealing with prod{} on attr1 * attr2 
            # no need to simply further, so we can simply return
                if mul_node.left.type == ops.ATTR and mul_node.right.type == ops.ATTR:
                    return

                node.right = None
                prod_node2 = BinaryNode.copy(node)
            
            # add prod nodes to children of mul_node
                prod_node2.right = mul_node.right
                mul_node.right = prod_node2
            
                node.right = mul_node.left
                mul_node.left = node
                #self.rule += "True "
                # move mul_node one level up to replace the "on" node.
                batchparser.addAsChildNodeToParent(data, mul_node)
                self.applied = True
            elif len(r) > 2:
                #print("original node =>", node)
                muls = [BinaryNode(ops.MUL) for i in range(len(r)-1)]
                prod = [BinaryNode.copy(node) for i in r]
                # distribute the products to all nodes in r
                for i in range(len(r)):
                    prod[i].right = r[i]
#                    print("n =>", prod[i])
                # combine prod nodes into mul nodes                     
                for i in range(len(muls)):
                    muls[i].left = prod[i]
                    if i < len(muls)-1:
                        muls[i].right = muls[i+1]
                    else:
                        muls[i].right = prod[i+1]
#                print("final node =>", muls[0])
                batchparser.addAsChildNodeToParent(data, muls[0])       
                self.applied = True
                #self.rule += "True "
            else:
                #self.rule += "False "
                return                
    def testForApplication(self):
        return self.applied

class SubstituteAttr:
    def __init__(self, variable_map, loopVar=None, constants=None):
        self.variable_map = variable_map
        self.loopVar = loopVar
        self.constants = constants
        self.variable_keys = list(variable_map.keys())
        
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        varName = node.getAttribute() # just retrieve the name and do not include any index info
        if varName.isdigit(): return
        if varName in self.variable_map.keys():
            node.setAttribute(self.variable_map[varName], clearAttrIndex=False)
        if self.constants: # if variable is a constant, then no need adding the loopVar index since it is always the same value.
            if varName in self.constants: return
        if self.loopVar:            
            node.setAttrIndex(self.loopVar)
            node.attr_index.reverse()
    
    def visit_concat(self, node, data):
        varList = node.getListNode()
        if self.loopVar == None:
            newVarList = [self.variable_map[ x ] if x in self.variable_keys else x for x in varList]
        else:
            newVarList = [self.variable_map[ x ] + "#" + self.loopVar if x in self.variable_keys else x for x in varList]
        node.listNodes = newVarList

class DropIndexForPrecomputes:
    def __init__(self, variable_list, loopVarTarget):
        self.variable_list = variable_list
        self.loopVarTarget = loopVarTarget
        
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        varName = node.getAttribute()
        if varName in self.variable_list:
#            print("varName: ", varName, " in ", self.variable_list)
            node.attr_index.remove(self.loopVarTarget)
#            print("node: ", node, self.loopVarTarget)
#        elif varName == delta_word:
#            node.attr_index.remove(self.loopVarTarget)                       
            
class GetVarsInEq:
    def __init__(self, dotList):
        self.varList = []
        self.dotList = dotList
    
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        varName = node.getAttribute()
        if varName.isdigit(): return
        if varName not in self.varList and varName not in self.dotList:
            self.varList.append(varName)
    
    def getVarList(self):
        return self.varList 
    
class GetDeltaIndex:
    def __init__(self):
        self.delta_single_list = [] # e.g. delta1#z goes first
        self.delta_double_list = [] # e.g., delta#1#2#z goes second
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        varName = node.getAttribute()
        deltaList = node.getDeltaIndex()
        if deltaList == None: return
        if varName == "delta" and (deltaList not in self.delta_single_list) and (deltaList not in self.delta_double_list):
            if len(deltaList) == 1: 
                self.delta_single_list.extend( deltaList )
            elif len(deltaList) > 1:
                self.delta_double_list.append( deltaList )
                
    def getDeltaList(self):
        newList = list(set(self.delta_single_list))
        return (newList, self.delta_double_list)

# Technique 6 - combining pairings with common elements (1st or 2nd)
# THE NEW AND IMPROVED TECHNIQUE 6: only should be used for technique 0 (combining multiple verification equations properly)
class PairInstanceFinderImproved:
    def __init__(self):
        # keys must match
        self.instance = {}
        self.index = 0
        self.rule = "Merge pairings with common first or second element (technique 6)"
        self.applied = False
        self.side = { 'left':[] }
        self.debug = False
        
    def visit(self, node, data):
        pass        

    def visit_eq_tst(self, node, data):
        lnodes = []
        getListNodes(node.left, Type(node), lnodes)
        for i in lnodes:
            if Type(i) == ops.PAIR: self.side['left'].append(str(i))
            elif i.left != None and Type(i.left) == ops.PAIR: self.side['left'].append(str(i.left))

    def visit_pair(self, node, data):
#        print("T6: parent type: ", Type(data['parent']))
        lhs = node.left
        rhs = node.right
        key = None
        invertedPairing = False
        parentExpAttr = None
        
        # record which side
        if str(node) in self.side['left']:
            whichSide = side.left
        else:
            whichSide = side.right
        
        if Type(lhs) == ops.ATTR:
            key = 'lnode'

        if Type(rhs) == ops.ATTR:
            key = 'rnode'
                    
        if Type(data['parent']) == ops.EXP:
            if Type(data['sibling']) == ops.ATTR:
#                print("sibling: ", data['sibling'])
                varName = data['sibling'].getAttribute()
#                print("varName: ", varName, ", node: ", data['parent'])
                if varName.isdigit() and str(data['sibling']) == "-1":
                    # pairing has been negated and need to pass on that information.
                    invertedPairing = True 
#                    print("Found one for this node: ", node)
                else:
                    # just a normal attribute Node..we want to store this as well
                    parentExpAttr = BinaryNode.copy(data['sibling'])
        
        if Type(data['parent']) == ops.ON:
            self.record(key, node, whichSide, data['parent'], invertedPairing, parentExpAttr)
        else:
            self.record(key, node, whichSide, None, invertedPairing, parentExpAttr)
            
        return

    def debugPrint(self, theDict, keys):
        print("<==== DEBUG ====>")
        for i in keys:
            print(i, ":", str(theDict.get(i)))
        print("<==== DEBUG ====>")
        return

    def record(self, key, node, whichSide, parent=None, invertedPairing=False, parentExpAttr=None):
        lnode = node.left
        rnode = node.right
        #print("key =>", key, ", nodes =>", lnode, rnode)
        found = False
        for i in self.instance.keys():
            data = self.instance[ i ]
#            print("found another: ", data['key'], data['lnode'], data['rnode'], data['instance'])
            if data['key'] == 'lnode':
                #print("LNODE: Found a combo pairing instance 1: ", lnode, "==", data['lnode'])
                if str(lnode) == str(data['lnode']): # found a match
                    data['instance'] += 1 # increment the finding of an instance
                    if data.get('rnode1'): data['rnode1'].append(rnode)
                    else: data['rnode1'] = [rnode] 
                    data['side'][ str(rnode) ] = whichSide
                    # save some state to delete this node on second pass  
                    if not data.get('rnode1_parent'): data['rnode1_parent'] = [] # create new list                  
                    if parent: data['rnode1_parent'].append(parent)
                    else: data['rnode1_parent'].append(node)       
                    data['rnode1_' + InvertedPairing] = invertedPairing 
                    data['rnode1_' + ParentExpNode] = parentExpAttr                                                         
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    break
            elif data['key'] == 'rnode':
                if str(rnode) == str(data['rnode']):
                    #print("RNODE: Found a combo pairing instance: ", rnode, "==", data['rnode'])                
                    data['instance'] += 1
                    if data.get('lnode1'): data['lnode1'].append(lnode)
                    else: data['lnode1'] = [lnode]
                    data['side'][ str(lnode) ] = whichSide
                    # save some state to delete this node on second pass
                    if not data.get('lnode1_parent'): data['lnode1_parent'] = [] # create new list                  
                    if parent: data['lnode1_parent'].append(parent)
                    else: data['lnode1_parent'].append(node)       
                    data['lnode1_' + InvertedPairing] = invertedPairing
                    data['lnode1_' + ParentExpNode] = parentExpAttr                                                                             
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    break
                elif str(lnode) == str(data['lnode']):
                    #print("LNODE: Found a combo pairing instance 2: ", lnode, "==", data['lnode'])                                    
                    # basically, find that non-constants match. for example,
                    # case: e(x * y, g) and e(x * y, h) transforms to e(x * y, g * h)
                    #print("found a new case.\ninput: ", lnode, rnode)
                    #print("data node: ", data['lnode'], data['rnode'], data['key'])
                    # switch sides
                    data['key'] = 'lnode'
                    data['instance'] += 1
                    if data.get('rnode1'): data['rnode1'].append(rnode)
                    else: data['rnode1'] = [rnode]
                    data['side'][ str(rnode) ] = whichSide
                    # save some state to delete this node on second pass
                    if not data.get('rnode1_parent'): data['rnode1_parent'] = [] # create new list                  
                    if parent: data['rnode1_parent'].append(parent)
                    else: data['rnode1_parent'].append(node)
                    data['rnode1_' + InvertedPairing] = invertedPairing                
                    data['rnode1_' + ParentExpNode] = parentExpAttr                                                                             
                    found = True
                    if data['pair_index']: data['pair_index'] = data['pair_index'].union(node.getDeltaIndex())
                    #self.debugPrint(data, ['key', 'lnode', 'rnode', 'keyside', 'instance', 'rnode1', 'rnode1_parent', 'rnode1_' + InvertedPairing, ])                    
                    break

        # if not found
        if not found:
            if not node.isDeltaIndexEmpty(): attr_index = set(node.getDeltaIndex())
            else: attr_index = None
            self.instance[ self.index ] = { 'key':key, 'lnode':lnode, 'rnode':rnode, 'keyside':whichSide,'instance':1, 'side':{}, 'pair_index':attr_index, InvertedPairing : invertedPairing, keyParentExp: parentExpAttr }
            if self.debug:
                print("<=== Adding base instance ====>")
                print("key: ", key)
                print("lnode: ", lnode)
                print("rnode: ", rnode)
                print("keyside: ", whichSide)
                print("pair_index: ", attr_index)
                print("<=== Adding base instance ====>")                
            self.index += 1
        return

    def checkForMultiple(self, check=False):
        for i in self.instance.keys():
            data = self.instance[ i ]
            if data['instance'] > 1:
                if not check: return data
                else: return True
        return None
    
    def makeSubstitution(self, equation):
        # first get a node in which 
#        tech6Applied = self.testForApplication()
#        print("tech 6 apply? =>", tech6Applied)
        pairDict = self.checkForMultiple()     
        equation2 = BinaryNode.copy(equation)
        if pairDict != None:
#            print("Pair =>", pairDict, "\n\n\n")
#            for i in pairDict.keys():
#                if type(pairDict[i]) == list:
#                    print("list: ", i)
#                    for j in pairDict[i]:
#                        print("\tnodes:", j)
#                else:
#                    print(i, ":=>", pairDict[i])
            SP2 = SubstitutePairs2( pairDict )
            batchparser.ASTVisitor( SP2 ).preorder( equation )
            if SP2.pruneCheck: 
                batchparser.ASTVisitor( PruneTree() ).preorder( equation )
            if self.failedTechnique(equation): self.applied = False; return equation2
            else: return None 
                
    def failedTechnique(self, equation):
        check = SanityCheckT6()
        batchparser.ASTVisitor( check ).preorder( equation )
#        print("Test sanity check: ", check.foundError)
        return check.foundError
    
    def testForApplication(self):
        self.applied = self.checkForMultiple(True)
        return self.applied

