''' Base class for commitment schemes 
 
 Notes: This class implements an interface for a standard commitment scheme.
	 A commitment scheme consists of three algorithms: (setup, commit, decommit).
	 
 Allows one to commit to a value while keeping it hidden, with the ability
 to reveal the committed value later (wiki).
'''
from charm.toolbox.schemebase import *

class Commitment(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='Commitment')
        self.baseSecDefs = None
        
    def setup(self, securityparam):
        raise NotImplementedError		

    def commit(self, *args):
        raise NotImplementedError
    
    def decommit(self, *args):
        raise NotImplementedError
