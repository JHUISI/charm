
from batchlang import *
from batchparser import *

Tech_db = Enum('NoneApplied', 'ExpIntoPairing', 'DistributeExpToPairing', 'ProductToSum', 'CombinePairing', 'SplitPairing', 'ConstantPairing', 'MoveExpOutPairing')

#TODO: code up reverse 2 : pull values from pairing outside, 

class AbstractTechnique:
    def __init__(self, sdl_data, variables, meta):
        if sdl_data != None:
            self.consts = sdl_data['constant']
            self.public = sdl_data['public']
            self.message = sdl_data['message']
            self.setting = sdl_data['setting']
        else:
            self.consts = self.public = self.message = self.setting = None
        self.vars   = variables
        if meta != None:
            self.meta   = meta
        else:
            self.meta   = None
        self.debug  = None

    def visit(self, node, data):
        return
    # check whether left or right node is constant
    def isConstInSubtreeT(self, node):  
        if node == None: return None
        if Type(node) == ops.EXP: 
            # when presented with A^B_z or A^B type nodes 
            # (checking the base value should be sufficient)
#            return self.isConstInSubtreeT(node.left)
            result1 = self.isConstInSubtreeT(node.left)
            result2 = self.isConstInSubtreeT(node.right)
#            print("constant: ", result1, result2)
            if result1 == result2: return result1
            elif result1 or result2: return False
            return True
        if Type(node) == ops.ATTR:
            return self.isConstant(node)
        elif Type(node) == ops.HASH:
            return self.isConstant(node.left)
        result = self.isConstInSubtreeT(node.left)
        if not result: return result
        result = self.isConstInSubtreeT(node.right)
        return result

    def isConstant(self, node):        
#        for n in self.data['constants']:
#            if n == node.getAttribute(): return True
        if node.getAttribute() in self.consts:
            if self.debug: print("node is constant: ", node.getAttribute())
            return True
        elif node.getAttribute() in self.public and self.setting['public'] == SAME:
            return True            
        elif node.getAttribute() in self.message and self.setting['message'] == SAME:
            return True
        return False

    def varDefineValue(self, var_name):
        var = self.vars.get(str(var_name))
        return var
        

    def getNodes(self, tree, parent_type, _list):
        if tree == None: return None
        elif parent_type == ops.MUL:
            if tree.type == ops.ATTR: _list.append(tree)
            elif tree.type == ops.EXP: _list.append(tree)
            elif tree.type == ops.HASH: _list.append(tree)
        
        if tree.left: self.getNodes(tree.left, tree.type, _list)
        if tree.right: self.getNodes(tree.right, tree.type, _list)
        return

    @classmethod
    def getMulTokens(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.MUL:
            if subtree.type in target_type: _list.append(subtree); return
        if subtree.left: self.getMulTokens(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens(subtree.right, subtree.type, target_type, _list)
        return
    
    @classmethod
    def addATTRToList(self, node, _list_dups, _list_unique):
        _list_dups.append(node)
        for i in _list_unique:
            if str(node) == str(i): return            
        _list_unique.append(node)
        return

    def findManyExpWithIndex(self, node, index, _list, _list2):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.EXP:
            # look for a^b_z or a^(b_z * s) where if z appears in right then return
            # the EXP right node as a acceptable candidate
            print("node.right type =>", Type(node.right))
            if Type(node.right) == ops.MUL:
                my_list = []
                self.getMulTokens(node.right, node_type, [ops.ATTR], my_list) # we are just interested in ATTR ndoes for this side
                for i in my_list:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2) # _list.append(i)
                my_list2 = []
                self.getMulTokens(node.left, Type(node.left), [ops.EXP, ops.ATTR], my_list2) # interested in EXP and ATTR nodes here
#                print("should test left?: ", node.left, len(my_list2))
                for i in my_list2:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: _list.append(i) # standard x_z case
                    elif Type(i) == ops.EXP and not i.right.isAttrIndexEmpty() and index in i.right.attr_index: self.addATTRToList(i.right, _list, _list2) # handle a^x_z case
            
            if Type(node.left) == ops.MUL:
                print("JAA: in this case now.")
                my_list = []; my_list2 = []
                self.getMulTokens(node.left, node_type, [ops.EXP, ops.ATTR], my_list) # we are just interested in ATTR ndoes for this side
                for i in my_list:
                    print("i: ", i)
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: _list.append(i)
                    elif Type(i) == ops.EXP and not i.right.isAttrIndexEmpty() and index in i.right.attr_index: self.addATTRToList(i.right, _list, _list2) # handle a^x_z case                    
                if Type(node.right) == ops.ATTR:
                    print("i2: ", node.right)
                    if not node.right.isAttrIndexEmpty() and index in node.right.attr_index: self.addATTRToList(node.right, _list, _list2)
                else:
                    self.getMulTokens(node.right, node_type, [ops.ATTR], my_list2) # interested in EXP and ATTR nodes here                    
                    for i in my_list2:
                        if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2) # standard x_z case
                

        elif node_type == ops.MUL:
            my_list = []; my_list2 = []
            if Type(node.left) == ops.MUL:
                self.getMulTokens(node.left, ops.MUL, [ops.ATTR], my_list)
                #print("\t\tCONSIDER THIS CASE 1: ", len(my_list))
                for i in my_list:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2)
            else:
                print("JAA: missing case: ", )
            
            if Type(node.right) == ops.MUL:
                self.getMulTokens(node.right, ops.MUL, [ops.ATTR], my_list2)
                print("\t\tCONSIDER THIS CASE 2: ", len(my_list2))
                for i in my_list2:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2)
                
        else:
            result = self.findManyExpWithIndex(node.left, index, _list)
            result = self.findManyExpWithIndex(node.right, index, _list)
            return
    
    @classmethod
    def findManyExpWithIndex2(self, node, index, _list, _list2):
        debug = False
        if node.left: self.findManyExpWithIndex2(node.left, index, _list, _list2)
        if node.right: self.findManyExpWithIndex2(node.right, index, _list, _list2)
        if debug: print("visiting child node: ", node)
        if Type(node) == ops.ATTR:
            if debug: print("does node matche? :=> ", node)
            if not node.isAttrIndexEmpty() and index in node.attr_index:
               if debug:  print("add this node: ", node)
               self.addATTRToList(node, _list, _list2)
        else:
            if debug: print("continue...", node)
            pass
        return

    def findExpWithIndex(self, node, index):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.EXP:
            # look for a^b_z or a^(b_z * s) where if z appears in right then return
            # the EXP right node as a acceptable candidate
            # debug: print("node.right type =>", Type(node.right))
            if Type(node.right) == ops.MUL:
                return self.findExpWithIndex(node.right, index)                
            elif not node.right.isAttrIndexEmpty() and index in node.right.attr_index:
                #print("node =>", node)            
                return node.right
        elif node_type == ops.MUL:
            if not node.left.isAttrIndexEmpty() and not node.right.isAttrIndexEmpty():
                if index in node.left.attr_index and index in node.right.attr_index: 
                    return node
            elif not node.left.isAttrIndexEmpty() and index in node.left.attr_index: return node.left
            elif not node.left.isAttrIndexEmpty() and index in node.right.attr_index: return node.right            
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
    
    @classmethod
    def createPair2(self, left, right):
        pair = BinaryNode(ops.PAIR)
        pair.left = BinaryNode.copy(left)
        pair.right = BinaryNode.copy(right)
        return pair
        
    def createPair(self, left, right):
        pair = BinaryNode(ops.PAIR)
        pair.left = left
        pair.right = right
        return pair
    
    def createSplitPairings(self, left, right, list_nodes):        
        nodes = list_nodes;
        muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
        if left.type == ops.MUL:
            for i in range(len(muls)):
                muls[i].left = self.createPair(nodes[i], BinaryNode.copy(right))
                if i < len(muls)-1:
                    muls[i].right = muls[i+1]
                else:
                    muls[i].right = self.createPair(nodes[i+1], BinaryNode.copy(right))
            return muls[0]
        elif right.type == ops.MUL:
            for i in range(len(muls)):
                muls[i].left = self.createPair(BinaryNode.copy(left), nodes[i])
                if i < len(muls)-1:
                    muls[i].right = muls[i+1]
                else:
                    muls[i].right = self.createPair(BinaryNode.copy(left), nodes[i+1])
            return muls[0]            
        return None
    
    @classmethod
    def createMul(self, left, right):
        if left.type == right.type and left.type == ops.EXP:
            # test whether exponents are the same
            l = str(left.right)
            r = str(right.right)
#            print(l, r)
            if l == r: # in other words, the same exponent
                mul = AbstractTechnique.createMul(left.left, right.left)
                exp = BinaryNode(ops.EXP, mul, BinaryNode.copy(left.right))
                return exp
            else:
                return BinaryNode(ops.MUL, left, right) # for now
        else:
            return BinaryNode(ops.MUL, BinaryNode.copy(left), BinaryNode.copy(right))
    
    @classmethod    
    def createInvExp(self, left):
        inv_node = BinaryNode("-1")
        new = BinaryNode.copy(left)
        if Type(new) == ops.EXP:
            if Type(new.right) == ops.ATTR:
                new.right.negated = not new.right.negated
            elif Type(new.right) == ops.MUL:
                # case 1: a^(b * c) transforms to a^(-b * -c)
                # case 2: a^((x + y) * b) transforms to a^((x + y) * -b) 
                subnodes = []
                getListNodes(new.right, ops.EXP, subnodes)
                if len(subnodes) > 0:
                    for i in subnodes: 
                        if Type(i) == ops.ATTR: i.negated = not i.negated
                else:
                    return self.createMul(new, inv_node)
#                print("Result: ", new)
                return new
            else: # ADD, DIV, SUB, etc
                print("warning: not tested yet in createInvExp():", Type(new), 
                      self.createMul(new, inv_node))
                return new
        elif Type(new) == ops.ON:
            new.right = self.createInvExp(new.right)
        else:
#            print("handle case 2.")
            return self.createExp(new, inv_node)
        return new
    
    def createMulFromList(self, _list):
        if len(_list) > 1:
            muls = [ BinaryNode(ops.MUL) for i in range(len(_list)-1) ]
            for i in range(len(muls)):
                muls[i].left = BinaryNode.copy(_list[i])
                if i < len(muls)-1: muls[i].right = muls[i+1]
                else: muls[i].right = BinaryNode.copy(_list[i+1])
            return muls[0] # MUL nodes absorb the exponent
        else:
            return BinaryNode.copy(_list[0]) # don't bother creating a MUL node for this

    @classmethod
    def negateThis(self, node):
        if Type(node) == ops.ATTR:
            node.negated = True
        if node.left: self.negateThis(node.left)
        if node.right: self.negateThis(node.right)
    
    # TODO: turn EXP and Pair into classmethods
    @classmethod
    def createExp(self, left, right):
        if left.type == ops.EXP: # left => a^b , then => a^(b * c)
#            exp = BinaryNode(ops.EXP)
            if Type(left.right) == ops.ATTR:
                value = left.right.getAttribute()
                if value.isdigit() and int(value) <= 1:  
#                    exp.left = left.left
                    if right.negated: left.right.negated = False; right.negated = False 
                    #left.right.setAttribute(str(right))
                    self.negateThis(right)
                    BinaryNode.setNodeAs(left.right, right)
                    #print("adjusted negation nodes: ", left.right)
# JAA commented out to avoid extra index, for example, 'delta_z_z' for VRF 
#                    print("original: ", left.right.attr_index)
#                    left.right.attr_index = right.attr_index                    
#                    print("post: ", left.right.attr_index)
                    mul = left.right
                else:
                    mul = BinaryNode(ops.MUL)
                    mul.left = left.right
                    mul.right = right                    
            else:
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
        elif left.type == ops.MUL:
            nodes = []
            self.getMulTokens(left, ops.NONE, [ops.EXP, ops.PAIR, ops.HASH, ops.ATTR], nodes)
            #getListNodes(left, ops.NONE, nodes)
#            print("createExp sub nodes:")
#            for i in nodes:
#                print("subnodes: ", i)
            if len(nodes) > 2: # only distribute exponent when there are 
                muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
                for i in range(len(muls)):
                    muls[i].left = self.createExp(nodes[i], BinaryNode.copy(right))
                    if i < len(muls)-1: muls[i].right = muls[i+1]
                    else: muls[i].right = self.createExp(nodes[i+1], BinaryNode.copy(right))
                exp = muls[0] # MUL nodes absorb the exponent
            else:
                exp = BinaryNode(ops.EXP)
                exp.left = left
                exp.right = right
        else:
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        return exp

    @classmethod
    def createExp2(self, left, right, _listIFMul=None):
        if left.type == ops.EXP: # left => a^b , then => a^(b * c)
#            exp = BinaryNode(ops.EXP)
            if Type(left.right) == ops.ATTR:
                value = left.right.getAttribute()
                if value.isdigit() and int(value) <= 1:  
#                    exp.left = left.left                   
#                    print("mul : ", str(right), left.right) 
                    if right.negated: left.right.negated = False; right.negated = False 
                    left.right.setAttribute(str(right)) 
#                    left.right.attr_index = right.attr_index
                    mul = left.right
                else:
                    mul = BinaryNode(ops.MUL)
                    mul.left = left.right
                    mul.right = right                    
            else:
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
        elif left.type == ops.MUL:
            nodes = []
            if not _listIFMul: _listIFMul = [ops.EXP, ops.HASH, ops.ATTR]
            self.getMulTokens(left, ops.MUL, _listIFMul, nodes)
#            getListNodes(left, ops.EQ_TST, nodes)
#            print("createExp sub nodes:")
#            for i in nodes:
#                print("subnodes: ", i)
            if len(nodes) >= 2: # only distribute exponent when there are 
                muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
                for i in range(len(muls)):
                    muls[i].left = self.createExp2(nodes[i], BinaryNode.copy(right), _listIFMul)
                    if i < len(muls)-1: muls[i].right = muls[i+1]
                    else: muls[i].right = self.createExp2(nodes[i+1], BinaryNode.copy(right), _listIFMul)
                exp = muls[0] # MUL nodes absorb the exponent
            else:
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

    def deleteNodesFromTree(self, node, parent, targets, branch=None):
        if node.left: self.deleteNodesFromTree(node.left, node, targets, side.left)
        if node.right: self.deleteNodesFromTree(node.right, node, targets, side.right)
        if self.debug: print("visiting child node: ", node)
        if node.left == None and node.right == None:
            if self.debug: print(node, " in target? ", node in targets)
            if node in targets:
               if self.debug:  print("delete myself: ", node) # delete myself 
               BinaryNode.clearNode(node)
        elif Type(node.left) != ops.NONE and Type(node.right) == ops.NONE: 
            if self.debug: print("left is there and right NOT there! action: delete right and move up left")
            BinaryNode.setNodeAs(node, node.left)
        elif Type(node.left) == ops.NONE and Type(node.right) != ops.NONE:
            if self.debug: print("left is NOT there and right is there. action: delete left and move up right")
            BinaryNode.setNodeAs(node, node.right)
        elif Type(node.left) == ops.NONE and Type(node.right) == ops.NONE:
            if self.debug: print("left is NOT there and right is NOT there. action: delete root node and move on")
            BinaryNode.clearNode(node)
        elif Type(node.left) != ops.NONE and Type(node.right) != ops.NONE:
            if self.debug: print("left and right BOTH there. action: do nothing and continue")
            pass
        else:
            if self.debug: print("continue...", node)
            pass
        
tech2 = Tech_db # Enum('NoneApplied', 'ExpIntoPairing', 'DistributeExpToPairing')

class Technique2(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)
        self.rule    = "Move the exponent(s) into the pairing (technique 2)"
        self.applied = False 
        self.score   = tech2.NoneApplied
        self.debug   = False
        
        # TODO: in cases of chp.bv, where you have multiple exponents outside a pairing, move them all into the e().
    
    # find: 'e(g, h)^d_i' transform into ==> 'e(g^d_i, h)' iff g or h is constant
    # move exponent towards the non-constant attribute
    def visit_exp(self, node, data):
        #print("left node =>", node.left.type,"target right node =>", node.right)
        if(Type(node.left) == ops.PAIR):   # and (node.right.attr_index == 'i'): # (node.right.getAttribute() == 'delta'):
            pair_node = node.left
                                  # make cur node the left child of pair node
            # G1 : pair.left, G2 : pair.right
            left_check = not self.isConstInSubtreeT(pair_node.left)
            right_check = not self.isConstInSubtreeT(pair_node.right)
            if self.debug: print("T2: visit_exp => left check:", left_check, ", right check:", right_check)
            if left_check == right_check and left_check == False:
                #print("T2: handle this case :=>", pair_node)
                # move to first by default since both are constant!
                addAsChildNodeToParent(data, pair_node) # move pair node one level up
                pair_node.left = self.createExp(pair_node.left, node.right)
                self.applied = True
                self.score   = tech2.ExpIntoPairing                
            elif left_check:
                addAsChildNodeToParent(data, pair_node) # move pair node one level up                                
                pair_node.left = self.createExp(pair_node.left, node.right)
                #print("pair_node :", pair_node.left)
#               node.left = pair_node.left
#               pair_node.left = node                
                self.applied = True
                self.score   = tech2.ExpIntoPairing
                #print("T2: Left := Move '" + str(node.right) + "' exponent into the pairing.")
            
            elif right_check:       
                addAsChildNodeToParent(data, pair_node) # move pair node one level up                
                pair_node.right = self.createExp(pair_node.right, node.right)
#                node.left = pair_node.right
#                pair_node.right = node 
                self.applied = True                
                self.score   = tech2.ExpIntoPairing                
                #print("T2: Right := Move '" + str(node.right) + "' exponent into the pairing.")
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
                if self.debug:
                    print("Check left: ", self.isConstInSubtreeT(pair_node.left))
                    print("Check right: ", self.isConstInSubtreeT(pair_node.right))
                if not self.isConstInSubtreeT(pair_node.left):
                    if self.debug: print("exponent moving towards right: ", pair_node.right)
                    #print(" pair right type =>", pair_node.right.type)
                    if Type(pair_node.right) == ops.MUL:
#                        print("T2: dot prod with pair: ", pair_node)
#                        print("MUL on right: ", pair_node.right)
                        _subnodes = []
                        getListNodes(pair_node.right, ops.NONE, _subnodes)
                        if len(_subnodes) > 2:
                            # basically call createExp to distribute the exponent to each
                            # MUL node in pair_node.right
                            new_mul_node = self.createExp(pair_node.right, node.right)
                            pair_node.right = new_mul_node
                            self.applied = True
                            self.score   = tech2.DistributeExpToPairing
#                            print("new pair node: ", pair_node, "\n")                            
                            #self.rule += "distributed exponent into the pairing: right side. "
                        else:
                            self.setNodeAs(pair_node, side.right, node, side.left)
                            self.applied = True       
                            self.score   = tech2.ExpIntoPairing                   
                            #self.rule += "moved exponent into the pairing: less than 2 mul nodes. "

                    elif Type(pair_node.right) in [ops.HASH, ops.ATTR]:
                        if self.debug: print("T2 - exercise pair_node : right = ATTR : ", pair_node.right)
                        # set pair node left child to node left since we've determined
                        # that the left side of pair node is not a constant
                        self.setNodeAs(pair_node, side.right, node, side.left)
                        self.applied = True
                        self.score   = tech2.ExpIntoPairing
                    else:
#                        print("T2: what are the other cases: ", Type(pair_node.right))
                        pass

                # check whether right side is constant
                elif not self.isConstInSubtreeT(pair_node.right):
                    # check the type of pair_node : 
                    if Type(pair_node.left) == ops.MUL:
#                        print("T2: missing case - pair_node.left and MUL node.")
                        _subnodes = []
                        getListNodes(pair_node.left, ops.NONE, _subnodes)
#                        print("len: ", len(_subnodes))
#                        for i in _subnodes:
#                            print("found: ", i)
                        if len(_subnodes) > 2:
                            new_mul_node = self.createExp(pair_node.left, node.right)
                            pair_node.left = new_mul_node
                            self.applied = True
                            self.score   = tech2.DistributeExpToPairing                            
                        else:
                            # pair_node -> left side is set to node (then which side)
                            self.setNodeAs(pair_node, side.left, node, side.left)
                            self.applied = True
                            self.score   = tech2.ExpIntoPairing                            
                    elif Type(pair_node.left) in [ops.HASH, ops.ATTR]:
#                        print("T2 - exercise pair_node : left = ATTR : ", pair_node.left)
                        # set pair node right child to 
                        self.setNodeAs(pair_node, side.left, node, side.left)
                        self.applied = True
                        self.score   = tech2.ExpIntoPairing
                    else:
                        pass
            else:
                #    blindly make the exp node the right child of whatever node
                self.setNodeAs(prod_node, side.right, node, side.left)
                self.applied = True
                self.score   = tech2.ExpIntoPairing
                
        elif(Type(node.left) == ops.MUL):    
            # distributing exponent over a MUL node (which may have more MUL nodes)        
            #print("Consider: node.left.type =>", node.left.type)
                
                
            mul_node = node.left
            if self.debug: 
                print("distribute exp correctly =>")
                print("left: ", mul_node.left)
                print("right: ", mul_node.right, Type(mul_node.right))
            if Type(data['parent']) != ops.PAIR: 
                pass
                mul_node.left = self.createExp(mul_node.left, BinaryNode.copy(node.right))
                mul_node.right = self.createExp(mul_node.right, BinaryNode.copy(node.right))
#                print("result for right: ", mul_node.right, "\n\n")
                addAsChildNodeToParent(data, mul_node)
                self.applied = True
                self.score   = tech2.DistributeExpToPairing
            #else:
            #    print("something went wrong!")
            #self.rule += " distributed the exp node when applied to a MUL node. "
            # Note: if the operands of the mul are ATTR or PAIR doesn't matter. If the operands are PAIR nodes, PAIR ^ node.right
            # This is OK b/c of preorder visitation, we will apply transformations to the children once we return.
            # The EXP node of the mul children nodes will be visited, so we can apply technique 2 for that node.
        else:
            #print("Other cases not ATTR?: ", Type(node.left))
            return
    
    # A quick way to reassign node pointers
    # 1. sets orig_node (left or right side) to target_node
    # 2. sets target_node (left or right side) to orig_node's specified side
    def setNodeAs(self, orig_node, attr_str, target_node, target_attr_str=side.left):
        if attr_str == side.right:  tmp_node = orig_node.right; orig_node.right = target_node
        elif attr_str == side.left: tmp_node = orig_node.left; orig_node.left = target_node
        else: return None
        if target_attr_str == side.left: target_node.left = tmp_node
        elif target_attr_str == side.right: target_node.right = tmp_node
        else: return None
        return True
    
#    def visit_attr(self, node, data):
        #d = None
        #d = { 'pair_index':node.getDeltaIndex() }
        #return d
        
tech3 = Tech_db # Enum('NoneApplied', 'ProductToSum','CombinePairing', 'SplitPairing')

class Technique3(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)
        self.rule    = "Move dot products inside pairings to reduce $\\numsigs$ pairings to 1 (technique 3)"
        self.applied = False
        self.score   = tech3.NoneApplied
        self.debug   = False


    def checkSubtreeForSameBase(self, node, parent, data):
        if node.left: 
            result = self.checkSubtreeForSameBase(node.left, node, data)
            if not result: return False
        if node.right: 
            result = self.checkSubtreeForSameBase(node.right, node, data)
            if not result: return False
        if Type(node) == ops.ATTR and Type(parent) == ops.EXP and node == parent.left: 
            if self.debug: print("T3: JAA - this check may not be SOUND. Please re-inspect!!!  =>", parent)
            exp_node = parent.right
            if not exp_node.isAttrIndexEmpty() and len(exp_node.attr_index) > 1: return False # Is this sound?!?
            if len(data) == 0: data.append(str(node)); return True
            else:
                if str(node) in data: return True
                else: return False
        return True
        
    def visit_pair(self, node, data):
        if self.debug: 
            print("Current state: ", node)
            print("left type: ", Type(node.left))
            print("right type: ", Type(node.right))
        left = node.left
        right = node.right
        if Type(left) == ops.ON:
            # assume well-formed prod node construct
            # prod {var := 1, N} on v : to get var => left.left.left.left
            index = str(left.left.left.left)
 #           print("left ON node =>", right, index)
            _listNodes = []; _listNodes_uniq = []
            self.findManyExpWithIndex2(right, index, _listNodes, _listNodes_uniq)
#            for i in _listNodes_uniq:
#                print("found: ", i)
#            print("T3: before =>", node)
            if len(_listNodes_uniq) == 0: return # nothing to do here
            exp_node = self.createMulFromList(_listNodes_uniq)
#            print("left := ON => moving EXP node: ", exp_node, "\n\n")
            if exp_node != None:
                base_node = left.right
                left.right = self.createExp(base_node, exp_node)
                self.deleteNodesFromTree(right, node, _listNodes, side.right) # cleanup right side tree?
#                self.applied = True
        elif Type(right) == ops.ON:
            index = str(right.left.left.left)
#            print("right ON node =>", index)
#            exp_node = self.findExpWithIndex(left, index)
            _listNodes = []; _listNodes_uniq = []
            self.findManyExpWithIndex2(left, index, _listNodes, _listNodes_uniq)
#            for i in _listNodes_uniq:
#                print("found: ", i)
            if len(_listNodes_uniq) == 0: return # nothing to do here            
            exp_node = self.createMulFromList(_listNodes_uniq)
#            print("\t NEW RESULT: ", exp_node)
#            print("T3: before =>", node)
#            print("right := ON => moving EXP node: ", exp_node, "\n\n")
            if exp_node != None:
                base_node = right.right
                right.right = self.createExp(base_node, exp_node)
                self.deleteNodesFromTree(left, node, _listNodes, side.left)
 #               self.deleteFromTree(left, node, exp_node, side.left)
#                self.applied = True
#                print("T3: result right =>", node)
            else: pass
#                print("T3: result w/o transform =>", node)
        
        if Type(left) == ops.MUL:
            if self.debug:
                print("T3: visit pair - Do nothing.")
                print("OK because we want to move as many operations as possible into the smallest group G1.")
                print("left: ", left)
                print("right: ", right, "\n")
            pass
            
        elif Type(right) == ops.MUL:
            if self.debug: print("T3: visit pair - Node =", right, " type:", Type(right))
#            child_node1 = right.left
#            child_node2 = right.right
#            if Type(child_node1) == ops.ON:
#                if self.debug: print("child type 1 =>", Type(child_node1))
#            elif Type(child_node2) == ops.ON:
#                mul = BinaryNode(ops.MUL)
#                mul.left = self.createPair(left, child_node1)                
#                mul.right = self.createPair(left, child_node2)
#                #print("new node =+>", mul)
#                addAsChildNodeToParent(data, mul)
#                self.applied = True
#                self.score   = tech3.SplitPairing
##                self.rule += "split one pairing into two pairings. "
            r = []
            self.getMulTokens(right, ops.NONE, [ops.EXP, ops.HASH, ops.ATTR, ops.ON], r)
            # count # of nodes in list. criteria: len(r) >= 2                                
            if len(r) < 2: return
            n = [ self.createPair2(left, i) for i in r ]
            addAsChildNodeToParent(data, self.createMulFromList(n))
            self.applied = True
            self.score   = tech3.SplitPairing
        else:
            return

    # transform prod{} on pair(x,y) => pair( prod{} on x, y) OR pair(x, prod{} on y)
    # n pairings to 1 and considers the split reverse case
    def visit_on(self, node, data):
        index = str(node.left.right)
        if index != 'N' or Type(data['parent']) == ops.PAIR:
            return # should check for other things before returning in the multi-signer case
        
        #print("T3: visit_on : current_state :=", node)
        if Type(node.right) == ops.PAIR:  
            pair_node = node.right
            
            l = []; r = [];
            self.getMulTokens(pair_node.left, ops.NONE, [ops.EXP, ops.HASH, ops.ATTR], l)
            self.getMulTokens(pair_node.right, ops.NONE, [ops.EXP, ops.HASH, ops.ATTR], r)
            if self.debug:
                print("T3: visit_on left list: ")
                for i in l: print(i)
                print("right list: ")
                for i in r: print(i)
            
            #if len(l) > 2 and len(r) < 2: 
                #right = pair_node.right # right side of pairing is the constant
                #node.right = self.createSplitPairings(pair_node.left, right, l)
                #self.applied = True
                #self.score   = tech3.SplitPairing
            # Note the same check does not apply to the left side b/c we want to move as many operations
            # into the smallest group G1. Therefore, if there are indeed more than two MUL nodes on the left side
            # of pairing, then that's actually a great thing and will give us the most savings.
            if len(r) > 2 and len(l) < 2:
                # special case: reverse split a \single\ pairing into two or more pairings to allow for application of 
                # other techniques. pair(a, b * c * d?) => p(a, b) * p(a, c) * p(a, d)
                # pair with a child node with more than two mult's?
                left = pair_node.left # left side of pairing is the constant
                node.right = self.createSplitPairings(left, pair_node.right, r)
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
                    if self.debug: print("can supposedly rearrange. Is that true? ", pair_node)
                #addAsChildNodeToParent(data, pair_node) # move pair one level up  
                left_check = not self.isConstInSubtreeT(pair_node.left)
                right_check = not self.isConstInSubtreeT(pair_node.right)
                if self.debug: print("left check:", left_check, ", right check:", right_check, ": ", pair_node)
                if left_check == right_check and left_check: 
                    # thus far, we've determined that both side are candidates for dot product.
                    # so we need another indicator to determine which side.
#                    print("T3: this case not fully explored. There maybe other corner cases!!!")
                    if self.debug: print("index of interest: ", target)
                    loop_left_check = self.isLoopOverTarget(pair_node.left, target)
                    loop_right_check = self.isLoopOverTarget(pair_node.right, target)
                    if self.debug: print("loop on left: ", loop_left_check, ", loop on right: ", loop_right_check)
                    if loop_left_check: # move dot prod to left side
                        #print("move dot prod to left: ", pair_node.left)
                        addAsChildNodeToParent(data, pair_node) # move pair one level up  
                        node.right      = pair_node.left # set dot prod right to pair_node left
                        pair_node.left  = node # pair node moves up and set pair left to dot prod
                        self.visit_pair(pair_node, data) # organize exponents that maybe in the wrong side
                        self.applied    = True
                        self.score      = tech3.CombinePairing
                    elif loop_right_check:
                        #print("move dot prod to right: ", pair_node.right)                        
                        addAsChildNodeToParent(data, pair_node) # move pair one level up                          
                        node.right      = pair_node.right
                        pair_node.right = node
                        self.visit_pair(pair_node, data)
                        self.applied    = True
                        self.score      = tech3.CombinePairing
                    
                elif left_check: # if F, then can apply prod node to left child of pair node  
                    addAsChildNodeToParent(data, pair_node) # move pair one level up                                  
#                    print("T3: before _pair left: combinepair: ", node)                                      
                    node.right = pair_node.left
                    pair_node.left = node # pair points to 'on' node
                    #self.rule += "common 1st (left) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)                    
#                    print("T3: after _pair left: combinepair: ", pair_node, "\n") 
                    self.applied = True
                    self.score   = tech3.CombinePairing  
                elif right_check:
                    addAsChildNodeToParent(data, pair_node) # move pair one level up                                                      
#                    print("T3: before _pair right: combinepair: ", node)                                      
                    node.right = pair_node.right
                    pair_node.right = node
                    #self.rule += "common 2nd (right) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)
                    self.applied = True
                    self.score   = tech3.CombinePairing
#                    print("T3: after _pair right: combinepair: ", node,"\n")                                                          
                else:
                    if self.debug: print("did nothing here.") # do nothing if previous criteria isn't met.
#                    print("last chance: ", self.isConstInSubtreeT(pair_node.left))
                    # warning: not a general solution here... (very specific cases: e.g. VRF)
                    #print("Type: ", Type(pair_node.left), pair_node.left.right)
                    #if Type(pair_node.left) == ops.EXP:
                    #    print("isConstant: ", self.isConstInSubtreeT(pair_node.left))
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
        else:
            if self.debug: print("T3: missing type check :=>", Type(node.right))
            pass
    
    # Quick check that the dot product can be reliably moved inside the pairing
    def verifyCombinePair(self, index, pair):
        target = str(index)
        left = self.isAttrIndexInNode(pair.left, target)
        right = self.isAttrIndexInNode(pair.right, target)
        if self.debug: print("Pair: ", pair, left, right)
        if left and right: 
        # if both true (meaning index appears on left and right side), then do NOT apply transformation
            return False
        return True 
        
    def canRearrange(self, index, node, another_dp_index_found=None):
        another_index = another_dp_index_found
        node_type = Type(node)
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
                    if self.debug: print("attr_index len is 1 : ", node.attr_index)
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
        elif node_type == ops.MUL:
            # call external function to traverse the subtrees
            #print("JAA: Checking whether we can rearrange when visiting MUL nodes...")
            _list = []
            result = self.checkSubtreeForSameBase(node , None, _list)
            if self.debug:
                for i in _list:
                    print("nodes after checkSubtreeForSameBase: ", i)
            if result: return True
            else: return False
        else:
            #print("Visiting else: ", Type(node), node, another_index)
            result1 = self.canRearrange(index, node.left, another_index)
            result2 = self.canRearrange(index, node.right, another_index)
            #print("Result1: ", result1)
            #print("Result2: ", result2)
            if result1 == result2: return result1
            elif result1 or result2: return False
            return # most likely won't hit this condition

    def isLoopOverTarget(self, tree, target):
        if tree == None: return None
        elif Type(tree) in [ops.EXP, ops.HASH]:
            if not tree.left.isAttrIndexEmpty() and target in tree.left.attr_index: return True
        elif Type(tree) == ops.ATTR:
            if not tree.isAttrIndexEmpty() and target in tree.attr_index: return True
        else:
            result = self.isLoopOverTarget(tree.left, target)
            if result: return result 
            return self.isLoopOverTarget(tree.right, target)
        return False

tech4 = Tech_db # Enum('NoneApplied', 'ConstantPairing')

class Technique4(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)
        self.rule = "Applied waters hash technique (technique 4)"
        self.applied = False
        self.score   = tech4.NoneApplied
        self.debug   = False
        #print("Metadata =>", meta)
    
    # need to handle cases where there are more than one dot product nodes that need to be switched!
    def visit_on(self, node, data):
        # if see our parent is a PAIR node. if so, BAIL no point applying waters hash
        if Type(data['parent']) == ops.PAIR:            
            return
        
        prod = node.left
        var_index = int(self.meta[str(prod.right)])
        my_val = str(prod.right)
        # check right subnode for another prod node
        node_tuple = []
        self.searchProd(node.right, node, node_tuple)
        if self.debug: print("T4: node_tuple =>", len(node_tuple))
        if node_tuple != None and len(node_tuple) >= 1:
            for i in node_tuple:
                node2 = i[0]
                parent = i[1]
                prod2 = node2.left
                if self.debug:
                    print("node: ", node2)
                    print("parent: ", parent, "\n")
                if var_index > int(self.meta[str(prod2.right)]):
                    node.left = BinaryNode.copy(prod2)
                    node2.left = BinaryNode.copy(prod)
                    if Type(parent) == ops.PAIR:
                        self.adjustProdNodes(parent)
                    self.applied = True
                    self.score   = tech4.ConstantPairing

    def adjustProdNodes(self, node): 
        if Type(node.left) == ops.ON:
            prod = node.left
            index = str(prod.left.left.left)              
            # check the following
            print("prod =>", prod.right)
            print("other =>", node.right)
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
        #elif Type(node) == ops.EXP:
        #    print("Found somehting? ", node)
        # first check the right side for product
    
    def allNodesWithIndex(self, index, subtree):
        if subtree == None: return True
        elif subtree.attr_index: 
            if not index in subtree.attr_index: return False
        result = self.allNodesWithIndex(index, subtree.left)
        if result == False: return result
        result = self.allNodesWithIndex(index, subtree.right)
        return result
    
    # JAA: consider building as a list rather than a single element?
    def searchProd(self, node, parent, _listProds):
        if node == None: return None
        elif node.type == ops.ON:
            _listProds.append( (node, parent) )
#        elif node.type == ops.EXP:
#            exp = node.right
#            if Type(exp) == ops.MUL: pass
#            elif Type(exp) == ops.ATTR and 'z' in exp.attr_index: 
        else:
            self.searchProd(node.left, node, _listProds)
            self.searchProd(node.right, node, _listProds)    
    
class Technique7(AbstractTechnique):
    """ looks for e( a^c_z, b^d_z ) where a and b are constants and c and d are variable"""
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)        
        self.applied = False
        self.score   = Tech_db.NoneApplied
        self.rule    = "Reverse technique 2. Move exponents outside pairing"
        
    def visit_pair(self, node, data):
        left = node.left
        right = node.right
        # note that there are several cases that will need to account for
        if Type(left) == ops.EXP and Type(right) == ops.EXP:         
            if self.isConstant(left.left) and self.isConstant(right.left):
                if not self.isConstant(left.right) and not self.isConstant(right.right):
                    #print("Candidate for technique 7:  ", left.right, right.right)
                    new_mul = BinaryNode(ops.MUL, BinaryNode.copy(left.right), BinaryNode.copy(right.right))
                    new_pair = self.createPair(BinaryNode.copy(left.left), BinaryNode.copy(right.left))
                    new_exp = self.createExp(new_pair, new_mul)
                    addAsChildNodeToParent(data, new_exp)
                    del node # clean up
                    self.applied = True
                    self.score   = Tech_db.MoveExpOutPairing
                    
    
class Technique8(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)        
        self.applied = False
        self.score   = Tech_db.NoneApplied
        self.rule    = "Precompute pairings with constant first and second elements."
        self.prefix  = "preP"
        self.ctr     = 0 # in case there are more than one. go from 0 to N intances
        self.precompute = {}
    
    def visit_pair(self, node, data):
        left = node.left
        right = node.right
        if Type(left) == ops.ATTR and Type(right) == ops.ATTR:
            if self.isConstant(left) and self.isConstant(right):
                #print("Candidate for technique 8:")
                precomp_key = self.record(node)
                addAsChildNodeToParent(data, precomp_key)
                del node
                self.applied = True
                self.score   = Tech_db.ConstantPairing

    def record(self, node):
        key      = self.prefix + str(self.ctr)
        keyNode  = BinaryNode(key)
        self.precompute[ keyNode ] = BinaryNode.copy(node)
        # take note in the other dictionaries: vars and consts
        self.vars[ key ] = 'GT' 
        self.consts.append( key )
        self.ctr += 1
        return keyNode
    
class ASTIndexForIndiv(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta) 
        
    def visit_attr(self, node, data):
        if data['parent'].type in [ops.PROD, ops.EQ, ops.FOR, ops.SUM]:
            return
        if not self.isConstant(node) and not str(node) in ['1', '-1']:
            node.setAttrIndex('z') # add index to each attr that isn't constant
    


class Technique10(AbstractTechnique):
    def __init__(self, sdl_data, variables, meta):
        AbstractTechnique.__init__(self, sdl_data, variables, meta)  
        self.debug = False      
        self.for_start = None
        self.for_end = None
        self.for_iterator = None

    def visit_for(self, node, data):
        if(Type(node.left) == ops.EQ):
            start = node.left
            self.for_iterator = start.left.getAttribute()
            self.for_start = start.right.getAttribute()
            if self.for_start == None or self.for_iterator == None: sys.exit("ERROR: for loop not well formed!") 
            print("for: ", self.for_iterator, ":", self.for_start)                       
        if(Type(node.right) == ops.ATTR):
            val = node.right.getAttribute()
            self.for_end = self.varDefineValue(val)
            if self.for_end == None: sys.exit("ERROR: %s is not defined in SDL." % val)
            print("until: ", node.right, self.for_end)
    
    def visit_attr(self, node, data):
        self.checkExistenceOfAttribute(node, self.for_iterator)
    
    # need a function that can replace variables with integers from 1 until X. 
    def checkExistenceOfAttribute(self, node, var):
        if self.for_end == None: return False
        attr = node.getAttribute()
        s = attr.split('#') 
        if( len(s) > 1):
            print("attr: ", node, s)
            match = False
            for i in s:
                if var in i: match = True; break            
            return False
        return False 