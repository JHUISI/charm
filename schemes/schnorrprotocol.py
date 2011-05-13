from charm.engine.protocol import *
from charm.engine.util import *
from toolbox.ecgroup import *
from socket import *
import sys
#error = {'OK':1, 'ERROR':2} 
PROVER,VERIFIER = 1,2
HOST, PORT = "", 8082

class SchnorrProtocol(Protocol):
    def __init__(self, builtin_cv=410):
        Protocol.__init__(self, None)        
        verifier_states = { 2:self.verifier_state2, 4:self.verifier_state4, 6:self.verifier_state6 }
        prover_states = { 1:self.prover_state1, 3:self.prover_state3, 5:self.prover_state5 }

        verifier_trans = { 2:4, 4:6 }
        prover_trans = { 1:3, 3:5 }
        # describe the parties involved and the valid transitions
        Protocol.addPartyType(self, VERIFIER, verifier_states, verifier_trans)
        Protocol.addPartyType(self, PROVER, prover_states, prover_trans, True)
#        Protocol.setSerializers(self, self.serialize, self.deserialize)
        self.group = ECGroup(builtin_cv)
        db = {}
        Protocol.setSubclassVars(self, self.group, db)
        
    def serialize(self, object):
        #print("input object... => ", object)
        bytes_object = serializeDict(object, self.group)
        #print("serializing... => ", bytes_object)
        return pickleObject(bytes_object)
    
    def deserialize(self, bytes_object):
        object = unpickleObject(bytes_object)

        if isinstance(object, dict):
            result = deserializeDict(object, self.group)        
            return result
        return object
    
    # PROVER states
    def prover_state1(self):
        x = self.group.random()
        r, g = self.group.random(), self.group.random(G)
        t = g ** r 
        print('prover: ',"hello to verifier.")
        self.db['r'], self.db['x'] = r, x
        self.db['t'], self.db['g'] = t, g
        Protocol.setState(self, 3)
        return {'t':t, 'g':g, 'y':g ** x } # output goes to the next state.
     
    def prover_state3( self, input):
        print("state3 input => ", input)
        c = input['c']
        s = self.db['r'] + c * self.db['x']
        print("s => '%s'" % s)
        output = "prover: message 1"
        Protocol.setState(self, 5)
        return {'s':s}

    def prover_state5( self, input ):
        print("state5 input => ", input)
        output = "prover: End state."
        Protocol.setState(self, None)
        return None

    # VERIFIER states
    def verifier_state2( self, input ):
        print("state2 input => ", input)
        # save the protocol values
        self.db['t'], self.db['g'] = input['t'], input['g']
        self.db['y'] = input['y']
        # compute challenge c and send to prover
        c = self.group.random()
        self.db['c'] = c
        Protocol.setState(self, 4)        
        return {'c':c}

    def verifier_state4( self, input ):
        print("state4 input => ", input) # read input off of socket, right?
        t, g, y, c = self.db['t'], self.db['g'], self.db['y'], self.db['c']
        s = input['s']
        
        print("s => '%s'" % s)
        if (g ** s == t * (y ** c)):
           print("SUCCESSFUL VERIFICATION!!!")
           output = "verifier: ACCEPTED!"
        else:
            print("FAILED TO VERIFY!!!")            
            output = "verifier: FAILED!"
        Protocol.setState(self, 6)
        return output
    
    def verifier_state6(self, input ):
        print("state6 input => ", input)
#        output = "verifier: Ack End state."        
        Protocol.setState(self, None)
        return None
    
if __name__ == "__main__":
    sp = SchnorrProtocol()

    if sys.argv[1] == "-v":
        print("Operating as verifier...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.bind((HOST, PORT))
        svr.listen(1)
        svr_sock, addr = svr.accept()
        print("Connected by ", addr)
        _name, _type, _sock = "verifier", VERIFIER, svr_sock
#       sp.setup( {'name':"verifier", 'type':_type, 'socket':svr_sock} )
    elif sys.argv[1] == "-p":
        print("Operating as prover...")
        clt = socket(AF_INET, SOCK_STREAM)
        clt.connect((HOST, PORT))
        clt.settimeout(15)
        _name, _type, _sock = "prover", PROVER, clt
    else:
        print("Usage: %s [-v or -p]" % sys.argv[0])
        exit(-1)
    sp.setup( {'name':_name, 'type':_type, 'socket':_sock} )
    # run as a thread...
    sp.execute(_type)
