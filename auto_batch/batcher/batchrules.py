
from batchlang import *


# Rules Engine:
# Each class detects the use of a particular rule. Each application of a rule prodcues a score
# which is based on the number of operations we are able to save that is reducing pairings
# and exponentiations in particular groups. 

class Technique2Check(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.score = tech.NoneApplied
        self.transformStack = [] # grows

    # find: 'e(g, h)^d_i' transform into ==> 'e(g^d_i, h)' iff g or h is constant
    # move exponent towards the non-constant attribute
    def visit_exp(self, node, data):
        #print("left node =>", node.left.type,"target right node =>", node.right)
        if(Type(node.left) == ops.PAIR):   # and (node.right.attr_index == 'i'): # (node.right.getAttribute() == 'delta'):
            pair_node = node.left
                                  # make cur node the left child of pair node
            # G1 : pair.left, G2 : pair.right
            if not self.isConstInSubtreeT(pair_node.left):
#                addAsChildNodeToParent(data, pair_node) # move pair node one level up
#                node.left = pair_node.left
#                pair_node.left = node
                #self.rule += "Left := Move '" + str(node.right) + "' exponent into the pairing. "
                pass
            elif not self.isConstInSubtreeT(pair_node.right):       
                pass
#                
#                addAsChildNodeToParent(data, pair_node) # move pair node one level up                
#                node.left = pair_node.right
#                pair_node.right = node 
                #self.rule += "Right := Move '" + str(node.right) + "' exponent into the pairing. "
            else:
                pass # must handle other cases 
            
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
                            pass
                            #self.rule += "distributed exponent into the pairing: right side. "
                        else:
                            #self.setNodeAs(pair_node, 'right', node, 'left')
                            #self.rule += "moved exponent into the pairing: less than 2 mul nodes. "
                            pass

                    elif Type(pair_node.right) == ops.ATTR:
                        # set pair node left child to node left since we've determined
                        # that the left side of pair node is not a constant
                        #self.setNodeAs(pair_node, 'left', node, 'left')
                        pass

                    else:
                        print("T2: what case are we missing: ", Type(pair_node.right))

                # check whether right side is constant
                elif not self.isConstInSubtreeT(pair_node.right):
                    # check the type of pair_node : 
                    if Type(pair_node.left) == ops.MUL:
                        pass
                    elif Type(pair_node.left) == ops.ATTR:
                        self.setNodeAs(pair_node, 'left', node, 'left')

            else:
            #    blindly make the exp node the right child of whatever node
                self.setNodeAs(prod_node, 'right', node, 'left')

        elif(Type(node.left) == ops.MUL):
            #print("Consider: node.left.type =>", node.left.type)
            mul_node = node.left
            mul_node.left = self.createExp(mul_node.left, BinaryNode.copy(node.right))
            mul_node.right = self.createExp(mul_node.right, BinaryNode.copy(node.right))
            addAsChildNodeToParent(data, mul_node)            
            #self.rule += " distributed the exp node when applied to a MUL node. "
            # Note: if the operands of the mul are ATTR or PAIR doesn't matter. If the operands are PAIR nodes, PAIR ^ node.right
            # This is OK b/c of preorder visitation, we will apply transformations to the children once we return.
            # The EXP node of the mul children nodes will be visited, so we can apply technique 2 for that node.
        else:
            pass

tech3 = Enum('NoneApplied', 'CombinePairing', 'SplitPairing')

class Technique3Check(AbstractTechnique):
    def __init__(self, constants, variables, meta):
        AbstractTechnique.__init__(self, constants, variables, meta)
        self.rule    = "Combine pairings with common 1st or 2nd element. Reduce N pairings to 1 (technique 3)"
        self.score   = tech3.NoneApplied

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
#                base_node = left.right
#                left.right = self.createExp(base_node, exp_node)
#                self.deleteFromTree(right, node, exp_node, side.right) # cleanup right side tree?
#                self.score = tech3.CombinePairing
        elif Type(right) == ops.ON:
            index = str(right.left.left.left)
            #print("right ON node =>", index)
            exp_node = self.findExpWithIndex(left, index)
            if exp_node:
#                base_node = right.right
#                right.right = self.createExp(base_node, exp_node)
#                self.deleteFromTree(left, node, exp_node, side.left)
                self.score = tech3.CombinePairing
        elif Type(left) == ops.MUL:
            pass
        elif Type(right) == ops.MUL:
            child_node1 = right.left
            child_node2 = right.right
#            print("child type 1 =>", Type(child_node1))
            if Type(child_node1) == ops.ON:
                pass
            elif Type(child_node2) == ops.ON:
                mul = BinaryNode(ops.MUL)
                mul.left = self.createPair(left, child_node1)                
                mul.right = self.createPair(left, child_node2)
                #print("new node =+>", mul)
                addAsChildNodeToParent(data, mul)
                self.score = tech3.SplitPairing
#                self.rule += "split one pairing into two pairings. "
            else:
                print("T3: missing case: right.left: ", Type(child_node1), "right.right: ", Type(child_node2))
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
                print("T3: Need to code this case!")
            elif len(r) > 2:
                # special case: reverse split a \single\ pairing into two or more pairings to allow for application of 
                # other techniques. pair(a, b * c * d?) => p(a, b) * p(a, c) * p(a, d)
                # pair with a child node with more than two mult's?
#                left = pair_node.left
#                muls = [ BinaryNode(ops.MUL) for i in range(len(r)-1) ]
#                for i in range(len(muls)):
#                    muls[i].left = self.createPair(left, r[i])
#                    if i < len(muls)-1:
#                        muls[i].right = muls[i+1]
#                    else:
#                        muls[i].right = self.createPair(left, r[i+1])
                #print("root =>", muls[0])
#                node.right = muls[0]
#                addAsChildNodeToParent(data, muls[0])
                self.score = tech3.SplitPairing
                #self.rule += "split one pairing into two or three."
            else:        
                addAsChildNodeToParent(data, pair_node) # move pair one level up  
# TODO: REVISIT THIS SECTION
                #print("pair_node left +> ", pair_node.left, self.isConstInSubtreeT(pair_node.left))                              
                if not self.isConstInSubtreeT(pair_node.left): # if F, then can apply prod node to left child of pair node              
                    node.right = pair_node.left
                    pair_node.left = node # pair points to 'on' node
                    #self.rule += "common 1st (left) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)                    
                    self.score = tech3.CombinePairing
                elif not self.isConstInSubtreeT(pair_node.right):
                    node.right = pair_node.right
                    pair_node.right = node
                    #self.rule += "common 2nd (right) node appears, so can reduce n pairings to 1. "
                    self.visit_pair(pair_node, data)
                    self.score = tech3.CombinePairing
                else:
                    pass
            return
        elif Type(node.right) == ops.EXP:
            exp = node.right
            isattr = exp.left
            if Type(isattr) == ops.ATTR and isattr.attr_index == None:
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

        