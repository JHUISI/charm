
from batchparser import *

Tech_db = Enum('NoneApplied', 'ExpIntoPairing', 'DistributeExpToPairing', 'ProductToSum', 'CombinePairing', 'SplitPairing', 'ConstantPairing')

class AbstractTechnique:
    def __init__(self, constants, variables, meta):
        self.consts = constants
        self.vars   = variables
        self.meta   = meta

    def visit(self, node, data):
        return
# check whether left or right node is constant
    def isConstInSubtreeT(self, node):  
        if node == None: return None
        if Type(node) == ops.ATTR:
            return self.isConstant(node)
        elif Type(node) == ops.HASH:
            return self.isConstant(node.left)
        result = self.isConstInSubtreeT(node.left)
        if not result: return result
        result = self.isConstInSubtreeT(node.right)
        return result

    def isConstant(self, node):        
        for n in self.consts:
            if n == node.getAttribute(): return True
        return False

    def getNodes(self, tree, parent_type, _list):
        if tree == None: return None
        elif parent_type == ops.MUL:
            if tree.type == ops.ATTR: _list.append(tree)
            elif tree.type == ops.EXP: _list.append(tree)
            elif tree.type == ops.HASH: _list.append(tree)
        
        if tree.left: self.getNodes(tree.left, tree.type, _list)
        if tree.right: self.getNodes(tree.right, tree.type, _list)
        return

    def getMulTokens(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.MUL:
            if subtree.type in target_type: _list.append(subtree)
        if subtree.left: self.getMulTokens(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens(subtree.right, subtree.type, target_type, _list)
        return

    def findExpWithIndex(self, node, index):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.EXP:
            #print("node.right type =>", Type(node.right))
            if Type(node.right) == ops.MUL:
                return self.findExpWithIndex(node.right, index)                
            elif index in node.right.attr_index:
                #print("node =>", node)            
                return node.right
        elif node_type == ops.MUL:
            if index in node.left.attr_index and index in node.right.attr_index: 
                return node
            elif index in node.left.attr_index: return node.left
            elif index in node.right.attr_index: return node.right            
        else:
            result = self.findExpWithIndex(node.left, index)
            if result: return node
            result = self.findExpWithIndex(node.right, index)
            return result

    def isAttrIndexInNode(self, node, index):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.ATTR:
            #print("node.right type =>", Type(node.right))
            if str(node.attr) == "delta":
                pass
            elif node.attr_index and index in node.attr_index:
                return True
            return False
        else:
            result = self.isAttrIndexInNode(node.left, index)
            if result: return result
            result = self.isAttrIndexInNode(node.right, index)
            return result


    def createPair(self, left, right):
        pair = BinaryNode(ops.PAIR)
        pair.left = left
        pair.right = right
        return pair
    
    def createExp(self, left, right):
        if left.type == ops.EXP: # left => a^b , then => a^(b * c)
            mul = BinaryNode(ops.MUL)
            mul.left = left.right
            mul.right = right
            exp = BinaryNode(ops.EXP)
            exp.left = left.left
            exp.right = mul
        elif left.type in [ops.ATTR, ops.PAIR, ops.HASH]: # left: attr ^ right
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        else:
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        return exp
    # node - target subtree, parent - self-explanatory
    # target - node we would liek to delete, branch - side of tree that is traversed.
    def deleteFromTree(self, node, parent, target, branch=None):
        if node == None: return None
        elif str(node) == str(target):
            if branch == side.left: 
                BinaryNode.setNodeAs(parent, parent.right)
                parent.left = parent.right = None 
                return                
            elif branch == side.right: 
                BinaryNode.setNodeAs(parent, parent.left)
                parent.left = parent.right = None
                return
        else:
            self.deleteFromTree(node.left, node, target, side.left)
            self.deleteFromTree(node.right, node, target, side.right)

tech2 = Tech_db # Enum('NoneApplied', 'ExpIntoPairing', 'DistributeExpToPairing')

class Technique2(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.rule    = "Move the exponent(s) into the pairing (technique 2)"
        self.applied = False 
        self.score   = tech2.NoneApplied
        
        # TODO: in cases of chp.bv, where you have multiple exponents outside a pairing, move them all into the e().
    
    # find: 'e(g, h)^d_i' transform into ==> 'e(g^d_i, h)' iff g or h is constant
    # move exponent towards the non-constant attribute
    def visit_exp(self, node, data):
        #print("left node =>", node.left.type,"target right node =>", node.right)
        if(Type(node.left) == ops.PAIR):   # and (node.right.attr_index == 'i'): # (node.right.getAttribute() == 'delta'):
            pair_node = node.left
                                  # make cur node the left child of pair node
            # G1 : pair.left, G2 : pair.right
            if not self.isConstInSubtreeT(pair_node.left):
                addAsChildNodeToParent(data, pair_node) # move pair node one level up
                node.left = pair_node.left
                pair_node.left = node
                self.applied = True
                self.score   = tech2.ExpIntoPairing
                #self.rule += "Left := Move '" + str(node.right) + "' exponent into the pairing. "
            
            elif not self.isConstInSubtreeT(pair_node.right):       
                addAsChildNodeToParent(data, pair_node) # move pair node one level up                
                node.left = pair_node.right
                pair_node.right = node 
                self.applied = True                
                self.score   = tech2.ExpIntoPairing                
                #self.rule += "Right := Move '" + str(node.right) + "' exponent into the pairing. "
            else:
                print("T2: Need to consider other cases here: ", pair_node)
                return
        # blindly move the right node of prod{} on x^delta regardless    
        elif(Type(node.left) == ops.ON):
            # (prod{} on x) ^ y => prod{} on x^y
            # check whether prod right
            prod_node = node.left
            addAsChildNodeToParent(data, prod_node)
            #print("prod_node right =>", prod_node.right.type)
            # look into x: does x contain a PAIR node?
            pair_node = searchNodeType(prod_node.right, ops.PAIR)
            # if yes: 
            if pair_node:
                # move exp inside the pair node
                # check whether left side is constant
                if not self.isConstInSubtreeT(pair_node.left):
                    #print(" pair right type =>", pair_node.right.type)
                    if Type(pair_node.right) == ops.MUL:
                        _subnodes = []
                        getListNodes(pair_node.right, ops.NONE, _subnodes)
                        if len(_subnodes) > 2: # candidate for expanding
                            muls = [ BinaryNode(ops.MUL) for i in range(len(_subnodes)-1) ]
                            for i in range(len(muls)):
                                muls[i].left = self.createExp(_subnodes[i], BinaryNode.copy(node.right))
                                if i < len(muls)-1:
                                    muls[i].right = muls[i+1]
                                else:
                                    muls[i].right = self.createExp(_subnodes[i+1], BinaryNode.copy(node.right))
                            #print("root =>", muls[0])
                            pair_node.right = muls[0]
                            self.applied = True
                            self.score   = tech2.DistributeExpToPairing
                            #self.rule += "distributed exponent into the pairing: right side. "
                        else:
                            self.setNodeAs(pair_node, 'right', node, 'left')
                            self.applied = True       
                            self.score   = tech2.ExpIntoPairing                   
                            #self.rule += "moved exponent into the pairing: less than 2 mul nodes. "

                    elif Type(pair_node.right) == ops.ATTR:
                        # set pair node left child to node left since we've determined
                        # that the left side of pair node is not a constant
                        self.setNodeAs(pair_node, 'left', node, 'left')
                        self.applied = True
                        self.score   = tech2.ExpIntoPairing
                    else:
                        print("T2: what are the other cases: ", Type(pair_node.right))

                # check whether right side is constant
                elif not self.isConstInSubtreeT(pair_node.right):
                    # check the type of pair_node : 
                    if Type(pair_node.left) == ops.MUL:
                        print("T2: missing case - pair_node.left and MUL node.")
                    elif Type(pair_node.left) == ops.ATTR:
                        self.setNodeAs(pair_node, 'left', node, 'left')
                        self.applied = True
                        self.score   = tech2.ExpIntoPairing
            else:
            #    blindly make the exp node the right child of whatever node
                self.setNodeAs(prod_node, 'right', node, 'left')
                self.applied = True
                self.score   = tech2.ExpIntoPairing
                
        elif(Type(node.left) == ops.MUL):            
            #print("Consider: node.left.type =>", node.left.type)
            mul_node = node.left
            mul_node.left = self.createExp(mul_node.left, BinaryNode.copy(node.right))
            mul_node.right = self.createExp(mul_node.right, BinaryNode.copy(node.right))
            addAsChildNodeToParent(data, mul_node)            
            self.applied = True
            self.score   = tech2.DistributeExpToPairing
            #self.rule += " distributed the exp node when applied to a MUL node. "
            # Note: if the operands of the mul are ATTR or PAIR doesn't matter. If the operands are PAIR nodes, PAIR ^ node.right
            # This is OK b/c of preorder visitation, we will apply transformations to the children once we return.
            # The EXP node of the mul children nodes will be visited, so we can apply technique 2 for that node.
        else:
            #print("Other cases not ATTR?: ", Type(node.left))
            return
    
    def setNodeAs(self, orig_node, attr_str, target_node, target_attr_str='left'):
        if attr_str == 'right':  tmp_node = orig_node.right; orig_node.right = target_node
        elif attr_str == 'left': tmp_node = orig_node.left; orig_node.left = target_node
        else: return None
        if target_attr_str == 'left': target_node.left = tmp_node
        elif target_attr_str == 'right': target_node.right = tmp_node
        else: return None
        return True
        
tech3 = Tech_db # Enum('NoneApplied', 'ProductToSum','CombinePairing', 'SplitPairing')

class Technique3(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.rule    = "Combine pairings with common 1st or 2nd element. Reduce N pairings to 1 (technique 3)"
        self.applied = False
        self.score   = tech3.NoneApplied
        self.debug   = False

    # once a     
    def visit_pair(self, node, data):
        #print("State: ", node)
        left = node.left
        right = node.right
        if Type(left) == ops.ON:
            # assume well-formed prod node construct
            # prod {var := 1, N} on v : to get var => left.left.left.left
            index = str(left.left.left.left)
            #print("left ON node =>", index)
            exp_node = self.findExpWithIndex(right, index)
            if exp_node:
                base_node = left.right
                left.right = self.createExp(base_node, exp_node)
                self.deleteFromTree(right, node, exp_node, side.right) # cleanup right side tree?
#                self.applied = True
        elif Type(right) == ops.ON:
            index = str(right.left.left.left)
            #print("right ON node =>", index)
            exp_node = self.findExpWithIndex(left, index)
            if exp_node:
                base_node = right.right
                right.right = self.createExp(base_node, exp_node)
                self.deleteFromTree(left, node, exp_node, side.left)
#                self.applied = True
        elif Type(left) == ops.MUL:
            pass
        elif Type(right) == ops.MUL:
#            print("T3: Node =", right, " type:", Type(right))
            child_node1 = right.left
            child_node2 = right.right
            if Type(child_node1) == ops.ON:
                if self.debug: print("child type 1 =>", Type(child_node1))
            elif Type(child_node2) == ops.ON:
                mul = BinaryNode(ops.MUL)
                mul.left = self.createPair(left, child_node1)                
                mul.right = self.createPair(left, child_node2)
                #print("new node =+>", mul)
                addAsChildNodeToParent(data, mul)
                self.applied = True
                self.score   = tech3.SplitPairing
#                self.rule += "split one pairing into two pairings. "            
            else:
                if self.debug: 
                    print("TODO: T3 - missing case: ", Type(child_node1), " and ", Type(child_node2))
        else:
            return None

    # transform prod{} on pair(x,y) => pair( prod{} on x, y) OR pair(x, prod{} on y)
    # n pairings to 1 and considers the split reverse case
    def visit_on(self, node, data):
        index = str(node.left.right)
        if index != 'N' or Type(data['parent']) == ops.PAIR:
            return # should check for other things before returning in the multi-signer case
        
        if Type(node.right) == ops.PAIR:            
            pair_node = node.right
            
            l = []; r = [];
            self.getMulTokens(pair_node.left, ops.NONE, [ops.EXP, ops.HASH], l)
            self.getMulTokens(pair_node.right, ops.NONE, [ops.EXP, ops.HASH], r)
            if len(l) > 2: 
                print("TODO: T3 - Need to handle the left case in visit_on.")
            elif len(r) > 2:
                # special case: reverse split a \single\ pairing into two or more pairings to allow for application of 
                # other techniques. pair(a, b * c * d?) => p(a, b) * p(a, c) * p(a, d)
                # pair with a child node with more than two mult's?
                left = pair_node.left
                muls = [ BinaryNode(ops.MUL) for i in range(len(r)-1) ]
                for i in range(len(muls)):
                    muls[i].left = self.createPair(left, r[i])
                    if i < len(muls)-1:
                        muls[i].right = muls[i+1]
                    else:
                        muls[i].right = self.createPair(left, r[i+1])
                #print("root =>", muls[0])
                node.right = muls[0]
                self.applied = True
                self.score   = tech3.SplitPairing
                #self.rule += "split one pairing into two or three."
                #addAsChildNodeToParent(data, muls[0])
            else:                        
                # verify we can actually move dot prod into pairing otherwise, bail:
                # NOTE: this only applies to when trying to moving dot products inside pairing
                target = str(node.left.left.left)
                if not self.verifyCombinePair(target, pair_node):
                    # check if we pass the basic variable with index exists on both side of pairing check,
                    # then, check whether the variables found can be rearranged to the side we move the
                    # dot product to. If it can't be rearranged given other dependencies, then bail and do not
                    # apply the combine pairing technique.
                    if self.canRearrange(target, pair_node) == False:
                        if self.debug: print("Cannot rearrange, therefore, BAIL!")
                        return # bail, no dice!
                                    
                addAsChildNodeToParent(data, pair_node) # move pair one level up  

                #print("pair_node left +> ", pair_node.left, self.isConstInSubtreeT(pair_node.left))                              
                if not self.isConstInSubtreeT(pair_node.left): # if F, then can apply prod node to left child of pair node              
                    node.right = pair_node.left
                    pair_node.left = node # pair points to 'on' node
                    #self.rule += "common 1st (left) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)                    
                    self.applied = True
                    self.score   = tech3.CombinePairing                    
                elif not self.isConstInSubtreeT(pair_node.right):
                    node.right = pair_node.right
                    pair_node.right = node
                    #self.rule += "common 2nd (right) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)
                    self.applied = True
                    self.score   = tech3.CombinePairing
                else:
                    pass # do nothing if previous criteria isn't met.
            return
        elif Type(node.right) == ops.EXP:
            exp = node.right
            isattr = exp.left
            if Type(isattr) == ops.ATTR and isattr.attr_index == None and self.isConstant(isattr):
                bp = BatchParser()
                prod = node.left
                sumOf = bp.parse("sum{x,y} of z")
                sumOf.left = node.left
                sumOf.right = exp.right
                sumOf.left.type = ops.SUM
                exp.right = sumOf
                #print("output =>", exp)
                addAsChildNodeToParent(data, exp)
                self.applied = True
                self.score   = tech3.ProductToSum
    
    # Quick check that the dot product can be reliably moved inside the pairing
    def verifyCombinePair(self, index, pair):
        target = str(index)
        left = self.isAttrIndexInNode(pair.left, target)
        right = self.isAttrIndexInNode(pair.right, target)
        if self.debug: print("Pair: ", pair)
        if left and right: 
        # if both true (meaning index appears on left and right side), then do NOT apply transformation
            return False
        return True 
        
    def canRearrange(self, index, node, another_dp_index_found=None):
        another_index = another_dp_index_found
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.ATTR:
            #print("visiting: ", node.attr, node.attr_index)
            #print("Another_index 1: ", another_index)
            #print("index in list?: ", index in node.attr_index)
            if str(node.attr) == "delta": 
                # we know for sure there's only one index, therefore, delta can be rearranged
                return True
            elif node.attr_index and index in node.attr_index:
                if self.debug: print("Another_index: ", another_index)
                if len(node.attr_index) == 1:
                # if there is an index match AND that is the only index in the list. 
                # this effectively gives us the same condition as delta_z.
                # otherwise, false b/c we most likley cannot rearrange the variable in question due to
                # a dependency (from the other index) that belongs to another dot product loop.
                    if self.debug: print("attr_index len is 1!")
                    return True
                elif len(node.attr_index) > 1 and another_index == None:
                # TODO: must check whether that loop is within the pairing or outside? 
                    if self.debug: print("FOUND another index w/o a dot prod in pairing left or right.")
                    return True
#                elif len(node.attr_index) > 1 and another_index:
#                    print("found another index: ", another_index, " with its dot prod inside the pairing as well. can't move")
#                    return False
                else:
                    return False
            else:
                return True
        elif node_type == ops.ON:
                prod = node.left            
                if str(prod.left.left) != index: 
                    another_index = str(prod.left.left)
                    #print("another_index : ", prod.left.left)
                #print("visiting next: ", node.right)
                result = self.canRearrange(index, node.right, another_index)
                return result
        else:
            #print("Visiting: ", Type(node), node, another_index)
            result1 = self.canRearrange(index, node.left, another_index)
            result2 = self.canRearrange(index, node.right, another_index)
            #print("Result1: ", result1)
            #print("Result2: ", result2)
            if result1 == result2: return result1
            elif result1 or result2: return False
            return # most likely won't hit this condition

tech4 = Tech_db # Enum('NoneApplied', 'ConstantPairing')
        
class Technique4(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.rule = "Applied waters hash technique (technique 4)"
        self.applied = False
        self.score   = tech4.NoneApplied
        self.debug   = False
        #print("Metadata =>", meta)
        
    def visit_on(self, node, data):
        prod = node.left
        my_val = str(prod.right)
        # check right subnode for another prod node
        node_tuple = self.searchProd(node.right, node)
        if node_tuple: node2 = node_tuple[0]; node2_parent = node_tuple[1]
        else: node2 = None; node2_parent = None

        if node2 != None:
            # can apply technique 4 optimization
            prod2 = node2.left
            # N > x then we need to switch x with N
            if int(self.meta[str(prod.right)]) > int(self.meta[str(prod2.right)]):
                # switch nodes between prod nodes of x (constant) and N
                node.left = prod2
                node2.left = prod
                #self.rule += " waters hash technique. "
                # check if we need to redistribute or simplify?
#                print("node2 =>", node2)
#                print("parent =>", node2_parent, ":", Type(node2_parent))
                if Type(node2_parent) == ops.PAIR:
                    if self.debug: print("applied a transformation for technique 4")
                    self.adjustProdNodes( node2_parent )
                    self.applied = True
                    self.score   = tech4.ConstantPairing
                else:
                    self.applied = True                    
                    self.score   = tech4.ConstantPairing
                    if self.debug: 
                        print("No other transformation necessary since not a PAIR node instead:", Type(node2_parent))

    def adjustProdNodes(self, node): 
        if Type(node.left) == ops.ON:
            prod = node.left
            index = str(prod.left.left.left)              
            # check the following
            #print("prod =>", prod.right)
            #print("other =>", node.right)
            if not self.allNodesWithIndex(index, prod.right):
                print("TODO: need to handle this case 1.")
            elif not self.allNodesWithIndex(index, node.right):
                result = self.findExpWithIndex(node.right, index)
                if result:
                    new_prod = BinaryNode.copy(prod)
                    new_prod.right = self.createExp(prod.right, result)
                    # add new_prod into current node left
                    node.left = new_prod
                    self.deleteFromTree(node.right, node, result, side.right)
                    #print("updated node =>", node)
                
        elif Type(node.right) == ops.ON:
            prod = node.right
            index = str(prod.left.left.left)
            # print("index =>", index)

            if not self.allNodesWithIndex(index, prod.right):
                # get all the nodes that match index on right
                # first move the prod node
                result = self.findExpWithIndex(node.right, index)
                if result:
                    new_prod = BinaryNode.copy(prod)
                    new_prod.right = node.left
                    node.right = prod.right
                    new_prod.right = self.createExp(node.left, result)
                    # add new_prod into current node left                
                    node.left = new_prod    
                    self.deleteFromTree(node.right, node, result, side.right)
                    #print("updated node =>", node)
            elif not self.allNodesWithIndex(index, node.left):
                print("TODO: adjustProdNodes: need to handle the other case.")
        # first check the right side for product
    
    def allNodesWithIndex(self, index, subtree):
        if subtree == None: return True
        elif subtree.attr_index: 
            if not index in subtree.attr_index: return False
        result = self.allNodesWithIndex(index, subtree.left)
        if result == False: return result
        result = self.allNodesWithIndex(index, subtree.right)
        return result
    
    def searchProd(self, node, parent):
        if node == None: return None
        elif node.type == ops.ON:
            return (node, parent)
        else:
            result = self.searchProd(node.left, node)
            if result: return result            
            result = self.searchProd(node.right, node)
            return result
        

# Focuses on simplifying dot products of the form
# prod{} on (x * y)
class DistributeDotProducts(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.rule = "Distribute dot products: "
        self.applied = False

    def getMulTokens2(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.EXP and Type(subtree) == ops.MUL:
            return               
        elif parent_type == ops.MUL:
            if Type(subtree) in target_type: 
                found = False
                for i in _list:
                    if isNodeInSubtree(i, subtree): found = True
                if not found: _list.append(subtree)

        if subtree.left: self.getMulTokens2(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens2(subtree.right, subtree.type, target_type, _list)
        return
    
    def visit(self, node, data):
        pass

    # visit all the ON nodes and test whether we can distribute the product to children nodes
    # e.g., prod{} on (x * y) => prod{} on x * prod{} on y    
    def visit_on(self, node, data):
        if Type(data['parent']) == ops.PAIR:
            #self.rule += "False "
            return
        #print("test: right node of prod =>", node.right, ": type =>", node.right.type)
        #print("parent type =>", Type(data['parent']))
#        _type = node.right.type
        if Type(node.right) == ops.MUL:            
            # must distribute prod to both children of mul
            r = []
            mul_node = node.right
            self.getMulTokens2(mul_node, ops.NONE, [ops.EXP, ops.HASH, ops.PAIR, ops.ATTR], r)
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
                addAsChildNodeToParent(data, mul_node)
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
                addAsChildNodeToParent(data, muls[0])    
                self.applied = True            
                #self.rule += "True "
            else:
                #self.rule += "False "
                return                

