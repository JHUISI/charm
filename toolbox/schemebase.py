from library.enum import *
# Base class for all crypto, which defines certain attributes

class SchemeBase:
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
