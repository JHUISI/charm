'''
Base class for public-key encryption
 
Notes: This class implements an interface for a standard public-key encryption scheme.
A public key encryption consists of four algorithms: (paramgen, keygen, encrypt, decrypt).
'''
from charm.toolbox.schemebase import *

encBaseSecDefs = Enum('OW_CPA','OW_CCA1','OW_CCA','IND_CPA','IND_CCA1','IND_CCA',
                    'NM_CPA','NM_CCA1','NM_CCA','KA_CPA','KA_CCA1','KA_CCA')

OW_CPA,OW_CCA1,OW_CCA="OW_CPA","OW_CCA1","OW_CCA"
IND_CPA,IND_CCA1,IND_CCA="IND_CPA","IND_CCA1","IND_CCA"
NM_CPA,NM_CCA1,NM_CCA="NM_CPA","NM_CCA1","NM_CCA"
KA_CPA,KA_CCA1,KA_CCA='KA_CPA','KA_CCA1','KA_CCA'

pkencSchemeType="pkeScheme"

class PKEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='PKEnc')
    
    def setProperty(self, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        assert secDef is not None and secDef in encBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, encBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
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
        assert secDef is not None and secDef in encBaseSecDefs.getList(), "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, encBaseSecDefs[secDef], str(assumption), messageSpace, str(secModel), **kwargs)
        return

    def printProperties(self):
        name = str(self.__class__).split("'")[-2].split(".")[-1]
        print("<=== %s Properties ===>" % name)
        for k,v in self.properties.items():
            print(k, ":", v)
        print("<=== %s Properties ===>" % name)            
        return
    
    def paramgen(self, param1=None, param2=None):
        return NotImplemented

    def keygen(self, securityparam):
        return NotImplemented

    def encrypt(self, pk, M):
        return NotImplemented

    def decrypt(self, pk, sk, c):
        return NotImplemented
