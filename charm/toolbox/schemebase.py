from charm.toolbox.enum import *

# user-map
EU_CMA,SU_CMA="EU_CMA","SU_CMA"
SM,ROM,CRS = "SM","ROM","CRS"
OW,RSA,StrongRSA,DL,DH,CDH,DDH,DBDH,q_SDH,LRSW = "OW","RSA","StrongRSA","DL","DH","CDH","DDH","DBDH","q_SDH","LRSW"

# security models: standard, random oracle and common reference string
baseSecModels = Enum('SM', 'ROM', 'CRS')
# scheme types
SchemeType = Enum('PKEnc', 'PKSig', 'IBEnc', 'IBSig', 'RingSig', 'GroupSig', 'ABEnc', 'DABEnc','Commitment', 'Hash', 'ChamHash', 'Protocol', 'PREnc')
# security hardness assumptions
secAssump = Enum('OW','RSA','StrongRSA','DL','DH','CDH','DDH','DBDH','q_SDH','LRSW') # need to expand this since it captures implications

schemeType = "scheme"
assumptionType = "assumption"
messageSpaceType = "messageSpace"
secModelType = "secModel"
secDefType   = "secDef"

class SchemeBase:
    '''Base class for all crypto, which defines security properties of cryptosystem'''
    def __init__(self):
        self.properties = {}
        
    def _setProperty(self, scheme=None, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        if scheme is not None and scheme in SchemeType.getList(): self.properties[ schemeType ] = SchemeType[scheme]
        if assumption is not None and assumption in secAssump.getList(): self.properties[ assumptionType ] = secAssump[assumption]
        if messageSpace is not None and type(messageSpace) == list:
            self.properties[ messageSpaceType ] = list(messageSpace)
        elif messageSpace is not None:
            self.properties[ messageSpaceType ] = messageSpace # TODO: better error handling here

        if secModel is not None and secModel in baseSecModels.getList(): self.properties[ secModelType ] = baseSecModels[secModel]
        if secDef is not None: self.properties[ secDefType ] = secDef # defined by subclass
        for key in kwargs.keys():
            self.properties[ key ] = kwargs[key]
        return True

    def _getProperty(self):
        return dict(self.properties)

    def _checkProperty(self, scheme, prop):
        # verify scheme is a subclass of SchemeBase
        if not hasattr(scheme, 'getProperty'): 
            assert False, "ERROR: Scheme class not derived from any of the Charm scheme types."

        if type(prop) == list:
           criteria = list(prop)
           #print("criteria: ", criteria)
           targetProps = scheme.getProperty()
           #print("check list =>", targetProps)
           for k,v in criteria:
               #print(k, ":", v)
               if k in targetProps.keys():
                   # found a match
                   if (v == str(targetProps[k])):
                       continue
                   # criteria value is less than target value
                   elif v in baseSecModels.getList() and baseSecModels[v] < targetProps[k]:
                       continue
               else:
                   assert False, "ERROR: required property not in scheme dictionary or not satisfied: %s" % k
        return True
    
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
            # we do not mask error raised by the function not related to types
            output = func(*args)
            try:
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
