# Used for benchmarking operations of intermediate representation
# and providing routines to determine when independent verification 
# is more efficient than batch verification.

from batchlang import *

SmallExp = 'delta'

class RecordOperations:
    def __init__(self, vars):
        #print("vars =>", vars)
        self.debug = False
        self.vars_def = vars
        N = self.vars_def.get('N')
        if N == None:
            assert False, "number of signatures not specified!" 
        # need to have type assignments 
        grps = {'ZR':0, 'G1':0, 'G2':0, 'GT':0 }
        self.ops = {'pair':0, 'mul':grps.copy(), 'exp':grps.copy(), 'hash':grps.copy() }
        # track prng for small exponents
    
    def visit(self, node, data):
        if node == None:
            return None
        else:            
            if debug >= levels.some:
               print("Operation: ", node.type)
               print("Left operand: ", left)
               print("Right operand: ", right)            
            if(node.type == ops.EXP):
                base_type = self.deriveNodeType(node.left)
                # check if node.right ==> 'delta' keyword, modify cost to half of full exp
                right = node.right
                if right != None and right.getAttribute() == SmallExp:
                    cost = 0.5
                else:
                    cost = 1
                keys = data.get('key')
                # exp node a child of a product node
                if keys != None:
                    _exp = cost
                    for i in keys:
                        _exp *= data[i]
                    self.ops['exp'][ base_type ] += _exp
                else: 
                    self.ops['exp'][ base_type ] += 1
                self.visit(node.left, data.copy())
                self.visit(node.right, data.copy())

            elif(node.type == ops.MUL):
                base_type = self.deriveNodeType(node.left)
                keys = data.get('key')
                
                if keys != None:
                    _mul = 1
                    for i in keys:
                        _mul *= data[i]
                    self.ops[ 'mul' ][ base_type ] += _mul
                else:
                    self.ops['mul'][ base_type ] += 1
                
                self.visit(node.left, data.copy())
                self.visit(node.right, data.copy())

            elif(node.type == ops.EQ):
                pass
            elif(node.type == ops.EQ_TST):
                self.visit(node.left, data.copy())
                self.visit(node.right, data.copy())
                
            elif(node.type == ops.PAIR):
                keys = data.get('key')
                # print("pair: data =>", data)
                if keys != None:
                    _pair = 1
                    for i in keys:
                        _pair *= data[i]
                    self.ops['pair'] += _pair
                else:
                    self.ops['pair'] += 1
                
                self.visit(node.left, data)
                self.visit(node.right, data)
            
            # for every 
            elif(node.type == ops.ON):
                key = node.left.right.attr
                if data.get('key') == None:
                    data['key'] = [key]
                else: # incase there are 
                    data['key'].append(key)
                data[key] = int(self.vars_def.get(key))         
                if debug >= levels.some:
                   print("ON key => ", data['key'], data[key])
                
                self.visit(node.right, data.copy())
#                 return (left + ", lambda " + pls.vars()  + right + ", " + pls.args() + ")")
            elif(node.type == ops.HASH):
                if node.right.attr == types.G1:
#                    print("value =>", node.right.attr)
                    keys = data.get('key')
                # print("pair: data =>", data)
                    if keys != None:
                        _hash = 1
                        for i in keys:
                            _hash *= data[i]
                        self.ops['hash']['G1'] += _hash
                    else:
                        self.ops['hash']['G1'] += 1
            else:
                return None
        return None    


#    def visit_on(self, node, data):
#        # prod = node.left
#        pass
#    
#    def visit_pair(self, node, data):
#        # check for 'on' parent, which means pairing is done N times
#        self.ops['pair'] += 1            
#
#    # track operations in G1, G2, GT      
#    def visit_mul(self, node, data):
#        if node.left:
#            base_type = self.deriveNodeType(node.left)
#            self.ops[ 'mul' ][ base_type ] += 1
#            if self.debug: 
#                print("mul: node.left =>", node.left)            
#                print("mul: type =>", base_type)
#
#    # track operations in G1, G2, GT    
#    def visit_exp(self, node, data):
#        if node.left:
#            base_type = self.deriveNodeType(node.left)
#            self.ops[ 'exp' ][ base_type ] += 1
#            if self.debug:
#                print("exp: node.left =>", node.left)
#                print("exp: type =>", base_type)
    
    def __str__(self):
        return str(self.ops)
    
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
        return self.vars_def[_type]
