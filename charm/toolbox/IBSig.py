'''
Base class for identity-based signatures
 
 Notes: This class implements an interface for a standard identity-based signatures scheme.
        Identity-based signatures consists of four algorithms: (setup, keygen, sign and verify).
'''
from charm.toolbox.schemebase import *

ibsigBaseSecDefs = Enum('EU_CMA', 'wEU_CMA', 'sEU_CMA')
EU_CMA,wEU_CMA,sEU_CMA="EU_CMA","wEU_CMA","sEU_CMA"

ibsigSchemeType='ibsigScheme'

class IBSig(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='IBSig')
    
    def setProperty(self, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        assert secDef is not None and secDef in ibsigBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, ibsigBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
        return True
    
    def getProperty(self):
        baseProp = SchemeBase._getProperty(self)
        return baseProp
    
    def checkProperty(self, schemeObj, _reqProps):
        reqProps = [ (str(k), str(v)) for k,v in _reqProps ]
        result = SchemeBase._checkProperty(self, schemeObj, reqProps)
        if result == True:
            self.setScheme(schemeObj)
        return result

    def updateProperty(self, scheme, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        # 1. inherit the scheme's properties
        assert hasattr(scheme, 'properties'), "schemeObj does not have getProperty() method."
        self.properties.update(scheme.getProperty())
        # 2. make sure things are consistent, then update to new properties
        assert self.properties[schemeType] is not None, "scheme type wasn't specified on initialization"
        assert secDef is not None and secDef in ibsigBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, ibsigBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
        return

    def printProperties(self):
        name = str(self.__class__).split("'")[-2].split(".")[-1]
        print("<=== %s Properties ===>" % name)
        for k,v in self.properties.items():
            print(k, ":", v)
        print("<=== %s Properties ===>" % name)            
        return
    
    def setup(self):
        raise NotImplementedError
    
    def keygen(self, msk, ID):
        raise NotImplementedError
    
    def sign(self, pk, sk, M):
        raise NotImplementedError
    
    def verify(self, pk, M, sig):
        raise NotImplementedError
        
