'''
Base class for public-key signatures
 
Notes: This class implements an interface for a standard public-key signature scheme.
A public key signature consists of three algorithms: (keygen, sign, verify).
'''
from charm.toolbox.schemebase import *

pksigBaseSecDefs = Enum('EU_CMA', 'wEU_CMA', 'sEU_CMA')
EU_CMA,wEU_CMA,sEU_CMA="EU_CMA","wEU_CMA","sEU_CMA"

class PKSig(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='PKSig')
    
    def setProperty(self, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        assert secDef is not None and secDef in pksigBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, pksigBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
        return True
    
    def getProperty(self):
        baseProp = SchemeBase._getProperty(self)
        return baseProp
    
    def checkProperty(self, schemeObj, _reqProps):
        reqProps = [ (str(k), str(v)) for k,v in _reqProps ]
        result = SchemeBase._checkProperty(self, schemeObj, reqProps)
        return result

    def updateProperty(self, scheme, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        # 1. inherit the scheme's properties
        assert hasattr(scheme, 'properties'), "schemeObj does not have getProperty() method."
        self.properties.update(scheme.getProperty())
        # 2. make sure things are consistent, then update to new properties
        assert self.properties[schemeType] is not None, "scheme type wasn't specified on initialization"
        assert secDef is not None and secDef in pksigBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, pksigBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
        return

    def printProperties(self):
        name = str(self.__class__).split("'")[-2].split(".")[-1]
        print("<=== %s Properties ===>" % name)
        for k,v in self.properties.items():
            print(k, ":", v)
        print("<=== %s Properties ===>" % name)            
        return
    
    def keygen(self, securityparam):
        raise NotImplementedError		

    def sign(self, pk, sk, message):
        raise NotImplementedError
    
    def verify(self, pk, message, sig):
        raise NotImplementedError
