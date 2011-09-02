from toolbox.enum import *

class SchemeBase:
    '''Base class for all crypto, which defines certain attributes'''
    def __init__(self):
        self.baseSchemeTypes = Enum('PKEnc', 'PKSig', 'IBEnc', 'IBSig', 'ABEnc', 'Commitment', 'Hash', 'Protocol')
	    # self.baseSecDefs defined by derived scheme types
        self.baseAssumptions = Enum('DH', 'DBDH', 'DL') 
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
    def verifyTypeDict(self, source, target):
        for i in target.keys():            
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
    def verifyTypeTuple(self, source, target):
        return self.verifyTypeDict(source, target)
    
    @classmethod
    def verifyType(self, source, target):
        if hasattr(source, 'type'):
            # source must be one of our base module types
            if source.type == target: return True
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

class input:
    def __init__(self, *_types):
        self._types = _types
        #print("INPUT TYPE: Defined types: ", self._types)
    
    def __call__(self, func, *args):
        def check_input(*args):
            #print("func =>", func)
            #print("func name =>", func.__name__)
            #print("cur arguments =>", args[1:])
            #print("type arguments =>", self._types)
            try:
                # check inputs
                inputs = args[1:]
                for i in range(0, len(self._types)):
                    if type(self._types[i]) == dict:
                        assert SchemeBase.verifyTypeDict(inputs[i], self._types[i]), "invalid '%s' target type" % self._types[i].__name__
                    else:
                        assert SchemeBase.verifyType(inputs[i], self._types[i]), "invalid '%s' target type" % self._types[i].__name__ 
                result = func(*args)
            except Exception as e:
                print(e)
            return result
        
        return check_input

class output:
    def __init__(self, *_types):
        self._types = _types
        self._type_len = len(_types)
        self.check_first = True
        if self._type_len > 1: self.check_first = False
#        print("OUTPUT TYPE: ", self._types)

    def __call__(self, func, *args):
        def check_output(*args):
            try:
                output = func(*args)
                # check the output        
                if self.check_first:
                    # situation where only one type is defined and it could be a single dict of many types, 
                    # or a single object with one type  
                    if type(self._types[0]) == dict:
                        assert SchemeBase.verifyTypeDict(output, self._types[0]), "invalid return type"
                    else:
                        assert SchemeBase.verifyType(output, self._types[0])
                else:        
                    # situation where a list of types is defined and mirrors how we look at inputs
                    for i in range(0, self._type_len):              
                        if type(self._types[i]) == dict:
                            assert SchemeBase.verifyTypeDict(output[i], self._types[i]), "invalid return type"
                        elif type(self._types[i]) == tuple:
                            assert SchemeBase.verifyTypeDict(output[i], self._types[i])
                        else:
                            assert SchemeBase.verifyType(output[i], self._types[i]), "invalid return type"
            except Exception as e:
                print(e)
            return output
        return check_output

