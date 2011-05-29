# EC-MQV authenticated key agreement protocol
from toolbox.ecgroup import *
from charm.engine.protocol import *
from charm.engine.util import *
from socket import *
import hmac, sys

SENDER, RECEIVER = 1,2
HOST, PORT = "", 8090

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
        print("Sender state 1 =>")
        a,g = self.group.random(ZR),self.group.random(G)
        k = self.group.random(ZR)
        A = g**a; Ra = g**k
        print("A =>", A); print("Ra =>", Ra); 
        Protocol.store(self, ('k',k),('a',a),('A',A),('Ra',Ra))
        Protocol.setState(self, 3)
        return {'A':A, 'Ra':Ra, 'g':g}
    
    def receiver_state2(self, input):
        # generate private key
        print("Receiver state 2 =>")
        g, A, Ra = input['g'], input['A'], input['Ra'] 
        b,k = self.group.random(ZR), self.group.random(ZR)
        B = g ** b
        Rb = g ** k
        sb = k + (self.group.zr(-Rb) * b)
        print("sb =>", sb)
        Z = (Ra * A) ** sb
        print("receiver Z =>", Z)
        key = self.group.hash(Z, G)
        print("key =>", key) 
        (k1, k2) = self.group.coordinates(key)
        print("k1 =>", k1); print("k2 =>", k2)
        tb = self.mac((2, B, A, Rb, Ra), k1)
        print("tb =>", tb)
        Protocol.setState(self, 4)
        Protocol.store(self, ('A',A),('Ra',Ra),('B',B),('Rb',Rb) )
        Protocol.store(self, ('k1',k1),('k2',k2) )
        return {'B':B, 'Rb':Rb, 'tb':tb}
        
    def sender_state3(self, input):
        print("Sender state 2 =>")
        B, Rb, tb = input['B'], input['Rb'], input['tb']
        (k, Ra, A, a) = Protocol.get(self, ['k','Ra','A','a'])
        sa = (k + self.group.zr(-Ra) * a)
        Z = (Rb * B) ** sa
        print("sender Z =>", Z)
        key = self.group.hash(Z, G)
        print("recovered key? =>", key)
        (k1, k2) = self.group.coordinates(key)
        print("k1 =>", k1); print("k2 =>", k2)
        t = self.mac((2, B, A, Rb, Ra), k1)
        print("t =>", t)
        print("tb =>", tb)
        if t == tb:
            print("Good so far.")
            ta = self.mac((3, A, B, Ra, Rb), k1)
            Protocol.setState(self, 5)
            return { 'ta':ta }
        Protocol.setState(self, None)
        return None            
    
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
    def mac(self, tupl_arg, key):
        h = hmac.new(self.group.serialize(key))
        for i in tupl_arg:
            if type(i) == int: b = bytes(i)
            else: b = self.group.serialize(i)
        h.update(b)
        result = h.hexdigest()
        return self.group.hash(result, ZR)

if __name__ == "__main__":
    if sys.argv[1] == "-r":
        print("Operating as receiver...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.bind((HOST, PORT))
        svr.listen(1)
        svr_sock, addr = svr.accept()
        print("Connected by ", addr)
        _name, _type, _sock = "receiver", RECEIVER, svr_sock
    elif sys.argv[1] == "-s":
        print("Operating as sender...")
        clt = socket(AF_INET, SOCK_STREAM)
        clt.connect((HOST, PORT))
        clt.settimeout(15)
        _name, _type, _sock = "sender", SENDER, clt
    else:
        print("Usage: %s [-v or -p]" % sys.argv[0])
        exit(-1)
        
    mqv = ECMQV()        
    mqv.setup( {'name':_name, 'type':_type, 'socket':_sock} )
    # run as a thread...
    mqv.execute(_type)
    