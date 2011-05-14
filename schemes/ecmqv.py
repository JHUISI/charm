# EC-MQV authenticated key agreement protocol
from modules.engine.protocol import *
from modules.engine.util import *
from ecgroup import *

# UNTESTED CODE
class ECMQV(Protocol):
    def __init__(self, builtin_cv=410):
        Protocol.__init__(self, None)        
        receiver_states = { 2:self.receiver_state2, 4:self.receiver_state4, 6:self.receiver_state6 }
        sender_states = { 1:self.sender_state1, 3:self.sender_state3, 5:self.sender_state5 }

        receiver_trans = { 2:4, 4:6 }
        sender_trans = { 1:3, 3:5 }
        # describe the parties involved and the valid transitions
        Protocol.addPartyType(self, RECEIVER, receiver_states, receiver_trans)
        Protocol.addPartyType(self, SENDER, sender_states, sender_trans, True)

        self.group = ECGroup(builtin_cv)
        db = {}; Protocol.setSubclassVars(self, self.group, db)
    
    def sender_state1(self):
        # generate private key
        a,g = self.group.random(ZR),self.group.random(G)
        k = self.group.random(ZR)
        A = g**a; Ra = g**k
        Protocol.store(self, ('k',k),('a',a),('A',A),('Ra',Ra))
        Protocol.setState(self, 3)
        return {'A':A, 'Ra':Ra, 'g':g}
    
    def receiver_state2(self, input):
        # generate private key
        g, A, Ra = input['g'], input['A'], input['Ra'] 
        b,k = self.group.random(ZR), self.group.random(ZR)
        B = g ** b
        Rb = g ** k
        sb = k + (self.group.zr(Rb) * b)
        Z = (Ra * (Ra * A)) ** sb
        
        key = self.group.hash(Z, G) 
        (k1, k2) = self.group.coordinates(key) # need to implement this
        tb = self.mac((2, B, A, Rb, Ra), k1) # need to implement this
        Protocol.setState(self, 4)
        Protocol.store(self, ('A',A),('Ra',Ra),('B',B),('Rb',Rb) )
        Protocol.store(self, ('k1',k1),('k2',k2) )
        return {'B':B, 'Rb':Rb, 'tb':tb}
        
    def sender_state3(self, input):
        B, Rb, tb = input['B'], input['Rb'], input['tb']
        (k, Ra, A, a) = Protocol.get(self, ['k','Ra','A','a'])
        sa = (k + self.group.zr(Ra) * a)
        Z = (Rb * (Rb * B)) ** sa
        
        key = self.group.hash(Z, G)
        (k1, k2) = self.group.coordinates(key)
        t = self.hmac((2, B, A, Rb, Ra), k1)
        if t == tb:
            print("Good so far.")
            ta = self.mac((3, A, B, Ra, Rb), k1)
            Protocol.setState(self, 5)
            return { 'ta':ta }
    
    def receiver_state4(self, input):
        ta = input['ta']
        (A, B, Ra, Rb, k1) = Protocol.get(self, ['A','B','Ra','Rb','k1'])
        t = self.mac((3, A, B, Ra, Rb), k1)
        if t == ta:
            print("Signature verified and key agreed.")
            print("k1 =>", k1)
            result = 'OK'
        else:
            result = 'FAIL'
        Protocol.setState(self, 6)
        return result
    
    def sender_state5(self, input):
        Protocol.setState(self, None)
        return None

    def receiver_state6(self, input):
        print("Result =>", input)
        Protocol.setState(self, None)
        return None
    
    # key is an element of ZR
    # data is a tuple of various elements
    def mac(self, data, key):
        pass