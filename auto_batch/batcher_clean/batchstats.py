# Used for benchmarking operations of intermediate representation
# and providing routines to determine when independent verification 
# is more efficient than batch verification.
import sdlpath
from sdlparser.SDLParser import *

SmallExp = 'delta'

def Copy(obj):
    new_obj = None
    key = obj.get('key')
    if type(obj) == dict:
        new_obj = obj.copy()
    if key != None and type(key) == list:
        new_obj['key'] = list(key)
    return new_obj


class RecordOperations:
    def __init__(self, vars):
        if debug >= levels.some:
            print("vars =>", vars)
        self.debug = True
        self.vars_def = vars
        N = self.vars_def.get('N')
        if N == None:
            assert False, "number of signatures not specified!" 
        # need to have type assignments 
        grps = {'ZR':0, 'G1':0, 'G2':0, 'GT':0 }
        self.ops = {'prng':0,'pair':0, 'mul':grps.copy(), 'exp':grps.copy(), 'hash':grps.copy() }
        # track prng for small exponents
    
    def visit(self, node, data, parent=None):
        if node == None:
            return None
        else:            
            if debug >= levels.some:
               print("Operation: ", node.type)
               print("Left operand: ", node.left)
               print("Right operand: ", node.right)            
            if(node.type == ops.EXP):
                base_type = self.map(self.deriveNodeType(node.left))
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
                self.visit(node.left, data.copy(), node)
                self.visit(node.right, data.copy(), node)

            elif(node.type == ops.MUL):
                base_type = self.map(self.deriveNodeType(node.left))
                keys = data.get('key')

                if keys != None:
                    _mul = 1
                    for i in keys:
                        _mul *= data[i]
                    self.ops[ 'mul' ][ base_type ] += _mul
                else:
                    self.ops['mul'][ base_type ] += 1
                
                self.visit(node.left, Copy(data), node)
                self.visit(node.right, Copy(data), node)

            elif(node.type == ops.EQ):
                pass
            elif(node.type == ops.EQ_TST):
                self.visit(node.left, Copy(data), node)
                self.visit(node.right, Copy(data), node)
                
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

                self.visit(node.left, Copy(data), node)
                self.visit(node.right, Copy(data), node)
            elif(node.type == ops.DO):
                key = node.left.right.attr
                
                if data.get('key') == None:
                    data['key'] = [key]
                else: # incase there are 
                    data['key'].append(key)

                key = key.split(LIST_INDEX_SYMBOL)[0]
                assert self.vars_def.get(key) != None, "key = '%s' not found in vars db." % key
                data[key] = int(self.vars_def.get(key)) # need to handle error

                if debug >= levels.some:
                   print("DO key => ", data['key'], data[key])
                
                cost = 1
                if Type(node.right) == ops.MUL: op = 'mul'
                elif Type(node.right) == ops.EXP: 
                    op = 'exp'
                    # Note: exponentiation to small exp is half an exponentiation
                    exp = node.right
                    if exp.right.getAttribute() == SmallExp: cost = 0.5
                elif Type(node.right) == ops.HASH: op = 'hash'
                elif Type(node.right) == ops.EQ_TST:
                    # in case of for{} do x == e(y, z) : we want to traverse EQ_TST children
                    return self.visit(node.right, Copy(data), node)
                else:
                    return
                right_type = self.map(self.deriveNodeType(node.right))
                _for = data[key] * cost
                print("Looping over '%s' node in '%s' => %s" % (op, right_type, _for))
                if right_type: self.ops[ op ][ right_type ] += _for
                
            # for every 
            elif(node.type == ops.ON):
                key = node.left.right.attr

                if data.get('key') == None:
                    data['key'] = [key]
                else: # incase there are 
                    data['key'].append(key)

                key = key.split(LIST_INDEX_SYMBOL)[0]
                assert self.vars_def.get(key) != None, "key = '%s' not found in vars db." % key
                data[key] = int(self.vars_def.get(key)) # need to handle error

                if debug >= levels.some:
                   print("ON key => ", data['key'], data[key])

                right_type = self.map(self.deriveNodeType(node.right))
#                print("Doing ", right_type, " of dot products to ", data[key])
                _prod = int(data[key])
#                print("Dot prod count =>", _prod, "in", right_type)
                if right_type: self.ops[ 'mul' ][ right_type ] += _prod
                self.visit(node.right, data.copy(), node)
            elif(node.type == ops.HASH):
                if node.right.attr in [types.ZR, types.G1, types.G2]:
                    _type_id = str(node.right.attr)
#                    print("value =>", node.right.attr)
                    keys = data.get('key')
                # print("pair: data =>", data)
                    if keys != None:
                        _hash = 1
                        for i in keys:
                            _hash *= data[i]
                        self.ops['hash'][ _type_id ] += _hash
                    else:
                        self.ops['hash'][ _type_id ] += 1
#            elif(node.type == ops.ATTR):
#                if Type(parent) == ops.ON:
#                    print("TODO: account for attribute nodes.")
#                print("data =>", data)
            else:
                return None
        return None    
    
    def __str__(self):
        return str(self.ops)
    
    def map(self, node_type):
        if node_type in ['listZR', 'listG1', 'listG2', 'listGT']:
            return node_type.strip('list')
        elif node_type in ['int', 'listInt']:
            return 'ZR'
        return node_type
    
    def deriveNodeType(self, node):
        if node.type == ops.ATTR:
            _type = node.attr
        elif node.type == ops.HASH:
            _type = str(node.right.attr)
            return _type
        elif node.type == ops.EXP:
#            print("node: ", node.left, node.left.type)
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
        _type = _type.split(LIST_INDEX_SYMBOL)[0] # get rid of "#" if present
        if _type == 'delta': return 'ZR'
        if _type == '1': return 'ZR' # probably computing an inverse here 
        assert self.vars_def.get(_type) != None, "Key error in vars db! => '%s'" % _type
        return self.vars_def[_type]
