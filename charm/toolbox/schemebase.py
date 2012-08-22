from charm.toolbox.enum import *

class SchemeBase:
    '''Base class for all crypto, which defines certain attributes'''
    def __init__(self):
        self.baseSchemeTypes = Enum('PKEnc', 'PKSig', 'IBEnc', 'IBSig', 'ABEnc', 'Commitment', 'Hash', 'Protocol')
	    # self.baseSecDefs defined by derived scheme types
        self.baseSecDefs = None
        self.baseAssumptions = Enum('RSA','StrongRSA','DL','DH','CDH','DDH','DBDH','q_SDH','LRSW') 
        self.baseSecModels = Enum('SM', 'ROM')
        
    def setProperty(self, scheme=None, secdef=None, assumption=None, message_space=None, secmodel=None, other=None):
        if scheme != None: self.schemeType = self.baseSchemeTypes[scheme]
        if secdef != None: self.secdef = self.baseSecDefs[secdef]
        if assumption != None: self.assumption = self.baseAssumptions[assumption]

        self.message_space = message_space
        if secmodel != None: self.secmodel = self.baseSecModels[secmodel]

        self.other = other
        return None

    def getProperty(self):
        props = []
        if hasattr(self, 'schemeType'): props.append(self.schemeType)
        if hasattr(self, 'secdef'): props.append(self.secdef)
        if hasattr(self, 'assumption'): props.append(self.assumption)
        if hasattr(self, 'message_space'): props.extend(self.message_space)
        if hasattr(self, 'secmodel'): props.append(self.secmodel)
        if type(self.other) == dict: props.extend(self.other.values())
        return set(props)

    def checkProperty(self, scheme, prop):
        if type(prop) == dict:
           values = set(prop.values())           
           #print("values =>", values)
           check = scheme.getProperty()
           #print("check list =>", check)
           if(values.issubset(check)):
               return True
        return False
    
    @classmethod
    def verifyTypeStruct(self, source, target, _types=dict):
        # make sure src and targ the same type otherwise raise error
        if type(source) != type(target): 
           assert False, "type mismatch between src='%s' and targ='%s'" % (type(source), type(target)) 
        if _types == dict: _iter = target.keys()
        elif _types in [list, tuple]: 
           _iter = range(len(source))
           target = [target[0] for i in _iter] 
           #print("target =>", target)
        #if struct unknown, then we shouldn't be calling this method
        else:
           assert False, "invalid structure type. wrong method"

        for i in _iter:            
            if hasattr(source[i], 'type'): # check for charm elements
                assert source[i].type == target[i], "invalid type: '%s' should be '%s' not '%s'" % (i, target[i], source[i].type)
            elif type(source[i]) in [dict, tuple, list]: # all dict elements (charm or python) must match target type
                keys = source[i].keys() if type(source[i]) == dict else range(len(source[i]))
                for j in keys:
                    if hasattr(source[i][j ], 'type'):
                        assert source[i][j].type == target[i], "invalid type: '%s' should be '%s' not '%s'" % (j, target[i], source[i][j].type)
                    else:
                        assert type(source[i][j]) == target[i], "invalid type: %s" % (target[i], type(source[i][j]))
            else: # normal python type
                assert type(source[i]) == target[i], "invalid type: %s not %s" % (target[i], type(source[i]))
        return True
    
    @classmethod
    def verifyType(self, source, target):
        if hasattr(source, 'type'):
            # source must be one of our base module types
            if source.type == target: 
               return True
            else: return False
        elif type(source) == target:
            return True
    
    @classmethod
    def getTypes(self, object, keys, _type=tuple):
        if _type == tuple:
            ret = []
        else: ret = {}
        # get the data 
        for i in keys:
            if _type == tuple:
                ret.append(object.__annotations__[i])
            else: # dict
                ret[ i ] = object.__annotations__[i]            
        # return data
        if _type == tuple:                
            return tuple(ret)
        return ret

"""
Decorator to handle checking an algorithms inputs and validating that types
match. The only requirement other than structure def matching is that the type
associated with the elements match target type (both python and charm types).
"""
class Input:
    def __init__(self, *_types):
        self._types = _types
        #print("INPUT TYPE: Defined types: ", self._types)
    
    def __call__(self, func, *args):
        def check_input(*args):
            result = None
            try:
                # check inputs
                inputs = args[1:]
                for i in range(0, len(self._types)):
                   _res_type = type(self._types[i])
                   if _res_type in [list, dict]: # make sure it's either a dict, list or tuple
                     assert SchemeBase.verifyTypeStruct(inputs[i], self._types[i], _res_type), "invalid '%s' type for '%s'" % (self._types[i], i)
                   else:
                     assert SchemeBase.verifyType(inputs[i], self._types[i]), "invalid '%s' type for '%s'" % (self._types[i], i)
                result = func(*args)
            except Exception as e:
                print(e)
            return result
        
        return check_input

"""
Decorator to handle checking an algorithms outputs and validating that types
match. Similar to input, the only requirement other than structure def matching is that the type
associated with the elements match target type (both python and charm types).
"""
class Output:
    def __init__(self, *_types):
        self._types = _types
        self._type_len = len(_types)
        self.check_first = True
        if self._type_len > 1: self.check_first = False
        #print("OUTPUT TYPE: ", self._types)

    def __call__(self, func, *args):
        def check_output(*args):
            try:
                output = func(*args)
                # check the output        
                if self.check_first:
                    # situation where only one type is defined and it could be a single dict or list of many types, 
                    # or a single object with one type  
                    _res_type = type(self._types[0])
                    if _res_type in [list, dict]:
                        assert SchemeBase.verifyTypeStruct(output, self._types[0], _res_type), "invalid return type"
                    else:
                        assert SchemeBase.verifyType(output, self._types[0]), "invalid return output for '%s'" % func.__name__
                else:        
                    # situation where a list of types is defined and mirrors how we look at inputs
                    for i in range(0, self._type_len):              
                        if type(self._types[i]) == dict:
                            assert SchemeBase.verifyTypeStruct(output[i], self._types[i]), "invalid return type"
                        elif type(self._types[i]) == tuple:
                            assert SchemeBase.verifyTypeStruct(output[i], self._types[i], list)
                        else:
                            assert SchemeBase.verifyType(output[i], self._types[i]), "invalid return type"
            except Exception as e:
                print(e)
            return output
        return check_output
