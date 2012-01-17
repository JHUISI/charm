# These classes assist in finding optimizations that can be made in the batch equation.
# If one is detected, that is, more than one instance of an exponentiation or pairing with
# the same variables is found, then it is a candidate for further optimization. This is separate
# from the techniques in batch parser, however.
from batchlang import *
import batchparser
import string

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


class PairInstanceFinder:
    def __init__(self):
        # keys must match
        self.instance = {}
        self.index = 0
        self.rule = "Merge pairings with common first or second element (technique 6)"
        self.applied = False
        
    def visit(self, node, data):
        pass
    
    def visit_pair(self, node, data):
        lhs = node.left
        rhs = node.right
        key = None
        
        if Type(lhs) == ops.ATTR:
            key = 'lnode'

        if Type(rhs) == ops.ATTR:
            key = 'rnode'
                    
        if Type(data['parent']) == ops.ON:
            self.record(key, node, data['parent'])
        else:
            self.record(key, node)
        return

    def record(self, key, node, parent=None):
        lnode = node.left
        rnode = node.right
        #print("key =>", key, ", nodes =>", lnode, rnode)
        found = False
        for i in self.instance.keys():
            data = self.instance[ i ]
#            print("found another: ", data['key'], data['lnode'], data['rnode'], data['instance'])
            if data['key'] == 'lnode':
                if str(lnode) == str(data['lnode']): # found a match
                    data['instance'] += 1 # increment the finding of an instance
                    if data.get('rnode1'): data['rnode1'].append(rnode)
                    else: data['rnode1'] = [rnode] 
                    # save some state to delete this node on second pass  
                    if not data.get('rnode1_parent'): data['rnode1_parent'] = [] # create new list                  
                    if parent: data['rnode1_parent'].append(parent)
                    else: data['rnode1_parent'].append(node)                    
                    found = True
                    break
            elif data['key'] == 'rnode':
                if str(rnode) == str(data['rnode']):
                    data['instance'] += 1
                    if data.get('lnode1'): data['lnode1'].append(lnode)
                    else: data['lnode1'] = [lnode]
                    # save some state to delete this node on second pass
                    if not data.get('lnode1_parent'): data['lnode1_parent'] = [] # create new list                  
                    if parent: data['lnode1_parent'].append(parent)
                    else: data['lnode1_parent'].append(node)                    
                    found = True
                    break
        # if not found
        if not found:
            self.instance[ self.index ] = { 'key':key, 'lnode':lnode, 'rnode':rnode, 'instance':1 }
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
        pairDict = self.checkForMultiple()

        if pairDict != None:
#            print("Pair =>", pairDict)
#            for i in pairDict.keys():
#                if type(pairDict[i]) == list:
#                    for j in pairDict[i]:
#                        print("\tnodes:", j)
#                else:
#                    print(i, ":=>", pairDict[i])
            SP2 = SubstitutePairs2( pairDict )
            batchparser.ASTVisitor( SP2 ).preorder( equation )
            if SP2.pruneCheck:
                batchparser.ASTVisitor( PruneTree() ).preorder( equation )
            #print("Done\n")
    
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
        self.index = 0        
        if self.key == 'rnode': # if right, then extras will be on the left
            self.extra = pairDict['lnode1']
            self.extra_parent = pairDict['lnode1_parent']
        elif self.key == 'lnode':
            self.extra = pairDict['rnode1']
            self.extra_parent = pairDict['rnode1_parent']
        
        self.deleteOtherPair = self.pruneCheck = self.debug = False
        
    def visit(self, node, data):
        if self.deleteOtherPair:
#            print("visit: node.left: ", node.left)    
#            print("visit: node.right: ", node.right)        
            if node.left in self.extra_parent:
                batchparser.addAsChildNodeToParent(data, node.right) 
                BinaryNode.clearNode(node.left)
                self.pruneCheck = True 
            elif node.right in self.extra_parent:
                batchparser.addAsChildNodeToParent(data, node.left)
                BinaryNode.clearNode(node.right)
                self.pruneCheck = True 
            else:
                pass
        
    def visit_pair(self, node, data):
        if self.key == 'rnode':
            # find the attribute node on the right
            if self.debug: print(node.right, " =?= ", self.right)
            if str(node.right) == str(self.right) and Type(node.right) == ops.ATTR:
                #print("Found a right match: ", node)
                if node.left == self.left and Type(self.left) == ops.ON:                    
                    if self.debug: print("combine other nodes with ON node: ", self.left)
                    target = self.left
                    for nodes in self.extra:
                        target = self.combine(target, nodes) # may need to make this smarter to do a proper merge
                        self.left.right = target
                    #print("ans => ", self.left)
                    node.left = BinaryNode.copy(self.left)
                    #print("node =>", node)
                    self.deleteOtherPair = True

                elif node.left == self.left: # found the target node
                    #print("Need another case: ", node.left, self.left)
                    self.extra.insert(0, BinaryNode.copy(self.left))
                    muls = [ BinaryNode(ops.MUL) for i in range(len(self.extra)-1) ]
                    for i in range(len(muls)):
                        muls[i].left = BinaryNode.copy(self.extra[i])
                        if i < len(muls)-1: muls[i].right = muls[i+1]
                        else: muls[i].right = BinaryNode.copy(self.extra[i+1])
                    node.left = muls[0] # self.right doesn't change
                    #print("new pairing node: ", muls[0], self.right) # MUL nodes absorb the exponent
                    self.deleteOtherPair = True                    

                elif node.left in self.extra: # foudn the other nodes we want to delete
                    del node.left, node.right
                    node.left = None
                    node.right = None
                    BinaryNode.clearNode(node)
                    self.pruneCheck = True
                    
                    
            elif str(node.right) == str(self.right):
                print("Found a match: ", self.left)
                for i in self.extra:
                    print("node: ", i)
                # find the second pair node
#                n = BinaryNode(ops.MUL)
#                n.left = self.left
#                n.right = self.extra
                
                
        elif self.key == 'lnode':
            if str(node.left) == str(self.left):
                print("Found a left match: ", node)
                
    def combine(self, subtree1, subtree2, parentOfTarget=None):
        if subtree2 == None: return None
        elif subtree2.left == None: pass
        elif Type(subtree1.left) == Type(subtree2.left):
            result = self.combine(subtree1.right, subtree2.right, subtree1)
            if result:                 
                n = BinaryNode(ops.MUL)
                n.left = subtree1.right
                n.right = subtree2.right
                return n
            return None    
        # check if node is a LEAF. if so report that node is different 
        if Type(subtree2) == ops.ATTR:
            return True

    def mergeWithMul(self, subtree1, subtree2):
        checkSubtrees = False
        self.mergeWithMul(subtree1.left, subtree2.left)
        #if subtree2 == None: return None
#        if Type(subtree1) == Type(subtree2):
#            pass
        self.mergeWithMul(subtree1.right, subtree2.right)

class PruneTree:
    def __init__(self):
        pass
    
    def visit(self, node, data):
        if Type(node.left) != ops.NONE and Type(node.right) == ops.NONE:
            #print("prune this 1: ", node)
            batchparser.addAsChildNodeToParent(data, node.left)            
        elif Type(node.left) == ops.NONE and Type(node.right) != ops.NONE:
            #print("prune this 2: ", node)
            batchparser.addAsChildNodeToParent(data, node.right)            


class SubstitutePairs:
    def __init__(self, pairDict):
        self.pairDict = pairDict
        self.key = pairDict['key']
        self.left = pairDict['lnode']
        self.right = pairDict['rnode']
        if self.key == 'rnode': # if right, then extra left
            self.extra = pairDict['lnode1'] 
            self.extra_pair = pairDict['lnodePair']
        elif self.key == 'lnode':
            self.extra = pairDict['rnode1']
            self.extra_pair = pairDict['rnodePair']            
        
        self.deleteOtherPair = False
    
    def visit(self, node, data):
        if self.deleteOtherPair:
            if str(node.left) == str(self.extra_pair):
                # extra node we are to remove
                batchparser.addAsChildNodeToParent(data, node.right)                
            elif str(node.right) == str(self.extra_pair):
                # extra node we are to remove                
                batchparser.addAsChildNodeToParent(data, node.left)

        
        
    def visit_pair(self, node, data):
        if self.key == 'rnode':
            # find the attribute node on the right
            if str(node.right) == str(self.right) and Type(node.right) == ops.ATTR:
                #print("Found a right match: ", node)
                if Type(self.left) == Type(self.extra) and Type(self.left) and ops.ON:
                    n = self.combine(self.left, self.extra)
                    self.left.right = n
                    #print("ans => ", self.left)
                    node.left = BinaryNode.copy(self.left)
                    #print("node =>", node)
                    self.deleteOtherPair = True
                # find the second pair node
#                n = BinaryNode(ops.MUL)
#                n.left = self.left
#                n.right = self.extra
                
                
        elif self.key == 'lnode':
            if str(node.left) == str(self.left):
                print("Found a left match: ", node)
    def combine(self, subtree1, subtree2, parentOfTarget=None):
        if subtree2 == None: return None
        elif subtree2.left == None: pass
        elif Type(subtree1.left) == Type(subtree2.left):
            result = self.combine(subtree1.right, subtree2.right, subtree1)
            if result:                 
                n = BinaryNode(ops.MUL)
                n.left = subtree1.right
                n.right = subtree2.right
                return n
            return None    
        # check if node is a LEAF. if so report that node is different 
        if Type(subtree2) == ops.ATTR:
            return True

    def mergeWithMul(self, subtree1, subtree2):
        checkSubtrees = False
        self.mergeWithMul(subtree1.left, subtree2.left)
        #if subtree2 == None: return None
#        if Type(subtree1) == Type(subtree2):
#            pass
        self.mergeWithMul(subtree1.right, subtree2.right)

class SubstituteSigDotProds:
    def __init__(self, vars, index='z', sig='N' ):
        self.prefix = 'dot' # self.prefix + self.alpha[cnt]; cnt += 1
        self.alpha = string.ascii_uppercase
        self.cnt = 0        
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
    
    def store(self, key, value, the_type=None):
        self.dotprod[ 'dict' ][ key ] = value
        self.dotprod[ 'types' ][ key ] = the_type
        self.dotprod[ 'list' ].append( key )
    
    def visit(self, node, data):
        pass
    
    def visit_on(self, node, data):
        index = str(node.left.right.attr)
        dot_type = self.deriveNodeType(node.right)
        #print("node.right type +=> ", dot_type, node.right)
        #print("index =>", index)

        n = self.searchProd(node.right, node)
        if n:
            (t, p) = n
#            print("Found it:", t)
            dot_type2 = self.deriveNodeType(t.right)
            # perform substition
            subkey = BinaryNode(self.getkey())
            self.store(subkey, t, dot_type2)
            if p.left == t:
                p.left = subkey
#                print("p =>", p)
        
        if index == self.sig:
            key = BinaryNode(self.getkey())
            self.store(key, node, dot_type)
            
            batchparser.addAsChildNodeToParent(data, key)
    
    def visit_of(self, node, data):
        sig = str(node.left.right.attr)

        if sig == self.sig:
            key = BinaryNode(self.getkey('sum'))
            if node.right.getAttribute() == 'delta':
                self.store(key, node, 'ZR')
            else:
                self.store(key, node)
            batchparser.addAsChildNodeToParent(data, key)
            
                
    def searchProd(self, node, parent):
        if node == None: return None
        elif node.type == ops.ON:
            return (node, parent)
        else:
            result = self.searchProd(node.left, node)
            if result: return result            
            result = self.searchProd(node.right, node)
            return result

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
        if Type(data['parent']) == ops.PAIR or data.get('visited_pair'):
            #self.rule += "False "
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
