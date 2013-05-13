'''
Base class for identity-based encryption
 
 Notes: This class implements an interface for a standard identity-based encryption scheme.
        Identity-based encryption consists of three algorithms: (setup, extract, encrypt, and decrypt).
'''
from charm.toolbox.schemebase import *

ibeBaseSecDefs = Enum('IND_ID_CPA','IND_sID_CPA','IND_ID_CCA','IND_sID_CCA', 'IND_ID_CCA2')
IND_ID_CPA,IND_sID_CPA,IND_ID_CCA,IND_sID_CCA,IND_ID_CCA2='IND_ID_CPA','IND_sID_CPA','IND_ID_CCA','IND_sID_CCA', 'IND_ID_CCA2'

ibeSchemeType='ibeScheme'

class IBEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='IBEnc')
    
    def setProperty(self, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        assert secDef is not None and secDef in ibeBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, ibeBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
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
        assert secDef is not None and secDef in ibeBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, ibeBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
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
    
    def extract(self, mk, ID):
        raise NotImplementedError
    
    def encrypt(self, pk, ID, message):
        raise NotImplementedError
    
    def decrypt(self, pk, sk, ct):
        raise NotImplementedError
        
