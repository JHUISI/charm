
import sdlpath
from sdlparser.SDLParser import *
from batchtechniques import AbstractTechnique

pairing = Enum('Asymmetric', 'Symmetric')
# post-order traversal needed here?
class BasicTypeExist(AbstractTechnique):
    def __init__(self, variables):
        AbstractTechnique.__init__(self, None, variables)
        self.missing_symbols = []
        self.exclude_list = []
    
    def visit_for(self, node, data):
        left_node = node.left
        if Type(left_node) == ops.EQ:
            self.exclude_list.append(str(left_node.left))
        right_node = node.right
        if Type(right_node) in [ops.ATTR, ops.ADD, ops.SUB, ops.MUL, ops.DIV]:      
            self.exclude_list.append(str(right_node))
    
    def visit_attr(self, node, data):
        variable = node.getAttribute()
        # ignore reserved keywords
        variableMinusListIndex = variable.split(LIST_INDEX_SYMBOL)[0]
        if variable.isdigit(): pass # handles attributes that are really integers
        elif variable in ['y', 'l', 'z', 'N'] or variable in self.exclude_list: pass
        # consider storing variables in a list?
        elif not variable in self.vars.keys() and not variableMinusListIndex in self.vars.keys(): 
            print("Error: ", variable, "does not have a type!")
            self.missing_symbols.append(variable)
            
    
    def report(self, equation):
        if len(self.missing_symbols) > 0:
            print("<=================SDL ERRORS=================>")            
            print("Equation: ", equation)
            print("Missing Types For:", self.missing_symbols)
            print("<=================SDL ERRORS=================>")            
            print("Add types for the above variable in 'types' section of SDL.")            
            exit(0)
        else:
            pass

# description: validates that all pairing operations are well formed with respect to the 
# pairing curve.           
class PairingTypeCheck(AbstractTechnique):
    def __init__(self, variables, curve=pairing.Asymmetric):
        AbstractTechnique.__init__(self, None, variables)
        self.left_errors  = []
        self.right_errors = []
        self.curve_type   = curve
    
    def deriveType(self, node, target, _list):
        # preorder tarversal
        if node == None: return
        elif Type(node) == ops.EXP:
            attr = node.left.getAttribute()
            if self.vars.get(attr) and self.vars.get(attr) != target: _list.append(attr)
        elif Type(node) == ops.ATTR:
            attr = node.getAttribute()
            if self.vars.get(attr) and self.vars.get(attr) != target: _list.append(attr)
        else:
            if node.left: 
                self.deriveType(node.left, target, _list)
            if node.right: 
                self.deriveType(node.right, target, _list)
     
    # assumes we're working in an asymmetric group
    def visit_pair(self, node, data):
        # simple case
        if self.curve_type == pairing.Asymmetric:
            left_type = 'G1'; right_type = 'G2'
        
        if Type(node.left) == ops.ATTR:
            key = node.left.getAttribute()
            if key in ['0', '1', '-1', 'y', 'l', 'z', 'N']: pass
            elif self.curve_type == pairing.Asymmetric and self.vars.get(key) != left_type: self.left_errors.append(key)
        else:
            self.deriveType(node.left, left_type, self.left_errors)
        
        if Type(node.right) == ops.ATTR:
            key = node.right.getAttribute()
            if key in ['0', '1', '-1', 'y', 'l', 'z', 'N']: pass            
            elif self.curve_type == pairing.Asymmetric and self.vars.get(key) != right_type: self.right_errors.append(key)
        else:
            self.deriveType(node.right, right_type, self.right_errors)

    def report(self, equation):
        if len(self.left_errors) > 0 or len(self.right_errors) > 0:
            print("<=================SDL ERRORS=================>")            
            print("Equation: ", equation)
            print("Variable in pairing operation should be in G1: ", self.left_errors)
            print("Variable in pairing operation should be in G2: ", self.right_errors)
            print("<=================SDL ERRORS=================>")            
            exit(0)
        else:
            pass
        
