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
    
    def verifyTypeDict(self, source, target):
        for i in target.keys():            
            if hasattr(source[i], 'type'): # check for charm elements
                assert source[i].type == target[i], "invalid type: '%s' should be '%s' not '%s'" % (i, target[i], source[i].type)
            elif type(source[i]) in [dict, list]: # all dict elements (charm or python) must match target type
                keys = source[i].keys() if type(source[i]) == dict else range(len(source[i]))
                for j in keys:
                    if hasattr(source[i][j ], 'type'):
                        assert source[i][j].type == target[i], "invalid type: '%s' should be '%s' not '%s'" % (j, target[i], source[i][j].type)
                    else:
                        assert type(source[i][j]) == target[i], "invalid type: %s" % (target[i], type(source[i][j]))
            else: # normal python type
                assert type(source[i]) == target[i], "invalid type: %s not %s" % (target[i], type(source[i]))
        return True
    
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
