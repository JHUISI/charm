
from charm.core.engine.protocol import Protocol
from charm.core.engine.util import *
from charm. toolbox.enum import Enum

#party = Enum('Prover', 'Verifier')

class Sigma(Protocol):
    def __init__(self, groupObj, common_input=None):        
        Protocol.__init__(self, None)  # think of something for handling errors      
        self.verifier_states = { 2:self.verifier_state2, 4:self.verifier_state4, 6:self.verifier_state6 }
        self.prover_states = { 1:self.prover_state1, 3:self.prover_state3, 5:self.prover_state5 }
        self.PROVER, self.VERIFIER = 1, 2  # PROVER = 1, VERIFIER = 2

        self.verifier_trans = { 2:4, 4:6 }
        self.prover_trans = { 1:3, 3:5 }
        # describe the parties involved and the valid transitions
        Protocol.addPartyType(self, self.VERIFIER, self.verifier_states, self.verifier_trans)
        Protocol.addPartyType(self, self.PROVER, self.prover_states, self.prover_trans, True)

        self.group = groupObj
        # proof parameter generation
        if common_input == None: # generate common parameters to P and V
            db = {}
        else: # can be used as a sub-protocol if common_input is specified by caller
            db = common_input            
        Protocol.setSubclassVars(self, self.group, db)      
    
    # must be implemented by sub class... 
    def prover_state1(self):
        pass
    
    def prover_state3(self, input):
        pass
    
    def prover_state5(self, input):
        pass
    
    def verifier_state2(self, input):
        pass

    def verifier_state4(self, input):
        pass
    
    def verifier_state6(self, input):
        pass
