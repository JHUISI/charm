# Used for benchmarking operations of intermediate representation
# and providing routines to determine when independent verification 
# is more efficient than batch verification.

from batchlang import *

class RecordOperations:
    def __init__(self, vars):
        print("vars =>", vars)
        self.debug = False
        self.vars_def = vars
        N = self.vars_def.get('N')
        if N == None:
            assert False, "number of signatures not specified!" 
        # need to have type assignments 
        grps = {'G1':0, 'G2':0, 'GT':0 }
        self.ops = {'pair':0, 'mul':grps.copy(), 'exp':grps.copy() }
    
    def visit(self, node, data):
        if node == None:
            return None
#        elif(node.type == ops.ATTR):
#            msg = node.attr
#            if node.attr_index != None:
#                msg += '[' + str(node.attr_index) + ']'
#            return msg
#        elif(node.type == ops.TYPE):
#            return str(node.attr)
        else:
#            left = self.print_statement(node.left)
#            right = self.print_statement(node.right)
            
            if debug >= levels.some:
               print("Operation: ", node.type)
               print("Left operand: ", left)
               print("Right operand: ", right)            
            if(node.type == ops.EXP):
                base_type = self.deriveNodeType(node.left)
                keys = data.get('key')
                # exp node a child of a product node
                if keys != None:
                    for i in keys:
                        self.ops['exp'][ base_type ] += data[i]
                else: 
                    self.ops['exp'][ base_type ] += 1
                self.visit(node.left, data)

            elif(node.type == ops.MUL):
                base_type = self.deriveNodeType(node.left)
                keys = data.get('key')
                
                if keys != None:
                    for i in keys:
                        self.ops[ 'mul' ][ base_type ] += data[i]
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
                    for i in keys:
                        self.ops['pair'] += data[i]
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
        print("printing type =>", _type)
        print("node =>", node)
        return self.vars_def[_type]
            