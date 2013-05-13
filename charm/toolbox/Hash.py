from charm.toolbox.schemebase import *

class Hash(SchemeBase):
    ''' Base class for Hash functions

    Notes: This class implements an interface for a standard hash function scheme.
    A hash function consists of two algorithms: (paramgen or keygen and hash).
    '''
    
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='Hash')
        self.baseSecDefs = None # Enum('EU_CMA')
    # base methods?
    def paramgen(self, *args):
        raise NotImplementedError
    
    def hash(self, *args):
        raise NotImplementedError


class ChamHash(Hash):
    '''
    Notes: This class implements an interface for a chameleon hash function. 
    A standard charmeleon hash scheme has two algorithms paramgen and hash.
    paramgen accepts a security parameter and the length of p and q. Hash accepts
    public key, label, a message and a random element.
    '''
    
    def __init__(self):
        Hash.__init__(self)
        Hash._setProperty(self, scheme='ChamHash')
        self.baseSecDefs = None # Enum('EU_CMA')
        
    def paramgen(self, secparam, p=None, q=None):
        raise NotImplementedError		

    def hash(self, pk, prefix, message, r):
        raise NotImplementedError