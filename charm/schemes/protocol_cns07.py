""" 
Camenisch-Neven-shelat - Oblivious Transfer

| From: "J. Camenisch, G. Neven, a. shelat - Simulatable Adaptive Oblivious Transfer"
| Published in: EUROCRYPT 2007
| Available from: http://eprint.iacr.org/2008/014
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       2/2012
"""
from charm.core.engine.protocol import *
from charm.core.engine.util import *
from socket import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.schemes.sigma1 import *
from charm.schemes.sigma2 import *
from charm.schemes.sigma3 import *
import sys

SENDER,RECEIVER = 1,2
HOST, PORT = "", 8083

class ObliviousTransfer(Protocol):
    def __init__(self, messages=None, groupObj=None, common_input=None):        
        Protocol.__init__(self, None)        
        receiver_states = { 2:self.receiver_init2, 4:self.receiver_transfer4, 6:self.receiver_transfer6, 8:self.receiver_transfer8 }
        sender_states = { 1:self.sender_init1, 3:self.sender_init3, 5:self.sender_transfer5, 7:self.sender_transfer7, 9:self.sender_transfer9 }

        receiver_trans = { 2:4, 4:6, 6:8 }
        sender_trans = { 1:3, 3:[3,5], 5:7, 7:9 }
        # describe the parties involved and the valid transitions
        Protocol.addPartyType(self, RECEIVER, receiver_states, receiver_trans)
        Protocol.addPartyType(self, SENDER, sender_states, sender_trans, True)
#        Protocol.setSerializers(self, self.serialize, self.deserialize)
        # make sure 
        if groupObj == None:
            self.group = PairingGroup('SS512')
        else:
            self.group = groupObj
        # proof parameter generation
        if common_input == None: # generate common parameters to P and V
            db = {}
            self.__gen_setup = True
        else: # can be used as a sub-protocol if common_input is specified by caller
            db = common_input
            self.__gen_setup = False
        Protocol.setSubclassVars(self, self.group, db) 
        if messages != None:
            self.M, self.sig = [], []
            for i in range(0, len(messages)):
                self.M.append( bytes(messages[i], 'utf8') )
                print("bytes =>", self.M[i],", message =>", messages[i])                
#                self.M.append(self.group.hash(messages[i], ZR))
#                self.sig.append(messages[i])
        # dict to hold variables from interaction        

    def get_common(self):
        if self.__gen_setup:
            g, h = self.group.random(G1), self.group.random(G2)
            H = pair(g, h)
            Protocol.store(self, ('g', g), ('h', h), ('H', H) )
            return (g, h, H)
        else: # common parameters generated already
            return Protocol.get(self, ['g', 'h', 'H'])
    
    # msgs => dict of M -> H(M)
    def sender_init1(self):
        M = self.M
        print("SENDER 1: ")
        (g, h, H) = self.get_common()  
        x = self.group.random(ZR)
        y = g ** x
        print("send g =>", g)
        print("send h =>", h)
        print("send H =>", H)
        print("send x =>", x)
        print("send y =>", y)
        A, B, C = {}, {}, {}
        for i in range(0, len(self.M)):
            j = self.group.init(ZR, i+1)
            print("j =>", j)
            A[i] = g ** ~(x + j)
            B[i] = pair(A[i], h)  #, M[i])
            C[i] = { 'A':A[i], 'B':B[i] }
        
        S = { 'g':g, 'h':h, 'H':H, 'y':y }        
        Protocol.store(self, ('x', y), ('y',y), ('C', C) )
        Protocol.setState(self, 3)
        return { 'S':S, 'C':C , 'PoK':'SigmaProtocol1' }
    
    def sender_init3(self, input):
        print("SENDER 3: ", input)
        result = 'FAIL'
        pk = Protocol.get(self, ['g', 'H', 'h'], dict)
        if input == 'GO':
            PoK1 = SigmaProtocol1(self.group, pk)
            PoK1.setup( {'name':'prover', 'type':PoK1.PROVER, 'socket':self._socket} )
            PoK1.execute(PoK1.PROVER, close_sock=False)
#            print("PoK1 prover result =>", PoK1.result)

            if PoK1.result == 'OK':
           # transition to transfer phase
                Protocol.setState(self, 5)
                result = PoK1.result
#        else: # JAA - something to this effect (Error case doesn't work yet)
#           Protocol.setState(self, 3); return {'PoK': 'REDO' }
        # need store and get functions for db        
        return {'PoK': result }
    
    def sender_transfer5(self, input):
        print("SENDER 5: query =>", input)
        
        if input.get('PoK') != None: # continue
            Protocol.setState(self, 7)
            return 'OK'    
        Protocol.setState(self, None)
        return None
    
    def sender_transfer7(self, input):
#        print("SENDER 7: input =>", input)
        if input.get('PoK2') != None: 
#            pk = Protocol.get(self, ['g','g2','y'], dict)           
            V = Protocol.get(self, ['V'])
            pk = { 'V':V }
            PoK2 = SigmaProtocol2(self.group, pk)
            PoK2.setup( {'name':'verifier', 'type':PoK2.VERIFIER, 'socket':self._socket} )
            Protocol.send_msg(self, 'GO')
            PoK2.execute(PoK2.VERIFIER, close_sock=False)
#            print("PoK2 verifier result =>", PoK2.result)
            result = PoK2.result

        if result == 'OK':
#           print("transitioning to transfer9 result =>", result)
           h, V = Protocol.get(self, ['h','V'])             
           W = pair(V, h)
           Protocol.setState(self, 9)
           return { 'PoK2':result, 'W':W, 'PoM':'SigmaProtocol3' }
        Protocol.setState(self, None)
        return None
    
    def sender_transfer9(self, input):
#        print("SENDER 9: PoM init =>", input)           
        
        if input == 'GO':    
#           print("Executing the PoM interactive proof.")
           pk = Protocol.get(self, ['h','g','H','V'], dict) 
           PoM = SigmaProtocol3(self.group, pk)
           PoM.setup( {'name':'prover', 'type':PoM.PROVER, 'socket':self._socket} )
           PoM.execute(PoM.PROVER)
           print("PoM prover result =>", PoM.result)
            
        Protocol.setState(self, None)
        return None
#################################    
# END of SENDER state functions #
#################################    
    
    def receiver_init2(self, input):
        print("RECEIVER 2: ")
        pk = Sigma.get(self, ['S'])
        if input['PoK'] == 'SigmaProtocol1':
            PoK1 = SigmaProtocol1(self.group, pk)
            PoK1.setup( {'name':'verifier', 'type':PoK1.VERIFIER, 'socket': self._socket} )
            Protocol.send_msg(self, 'GO') # important: 1. acknowledges sub-protocol transition, 2. sends a short message using this socket
            PoK1.execute(PoK1.VERIFIER, close_sock=False)
            print("PoK1 verifier result =>", PoK1.result)
            result = PoK1.result

        if result == 'OK':            
            Protocol.setState(self, 4) # desired: 4 (TBD)
        return {'PoK': result } # result should be R0 (state info) for Receiver
        # let sender know to expect a PoK2 interaction next

    def receiver_transfer4(self, input): # rec_tran4 -> sender_tran5
        print("RECEIVER 4: Get query from end user.")
        index = 0 # maps to position 0 in array (+1 indexed)
        C = Protocol.get(self, ['C'])[0]
        v = self.group.random(ZR) # secret for Receiver
        V = C[index]['A'] ** v # public value
        Protocol.setState(self, 6)
        Protocol.store( self, ('v',v), ('V',V), ('query', index+1) )
        return { 'V':V, 'PoK2':'SigmaProtocol2' }
    
    def receiver_transfer6(self, input):
        print("RECEIVER 6: input =>",input)
        if input == 'GO':
            (pk, V, v, query) = Protocol.get(self, ['S','V','v','query'])
            pk['V'], pk['v'], pk['sigma'] = V, v, query
            # set up client end of PoK2
            PoK2 = SigmaProtocol2(self.group, pk)
            PoK2.setup( {'name':'prover', 'type':PoK2.PROVER, 'socket':self._socket} )
            PoK2.execute(PoK2.PROVER, close_sock=False)
            print("PoK2 prover result =>", PoK2.result)
            result = PoK2.result            
            Protocol.setState(self, 8)
            return {'Pok2':result}
        
        Protocol.setState(self, None)            
        return None

    def receiver_transfer8(self, input):
        print("RECEIVER 8:")
        if input['PoK2'] != 'OK':
            Protocol.setState(self, None)
            return None
        
        if input.get('PoM') != None:    
#            print("Executing the PoM interactive proof.")
            pk = Protocol.get(self, ['W'], dict)
            PoM = SigmaProtocol3(self.group, pk)
            PoM.setup( {'name':'verifier', 'type':PoM.VERIFIER, 'socket': self._socket} )
            Protocol.send_msg(self, 'GO') # important: 1. acknowledges sub-protocol transition, 2. sends a short message using this socket
            PoM.execute(PoM.VERIFIER, close_sock=False)
            result = PoM.result
            print("PoM verifier result =>", result)
        
        if result == 'OK':
#            print("Now we recover ")
            # W allows us to unlock the appropriate keyword, right?
            # get query, B_query, and v
            (W, v, C) = Protocol.get(self, ['W','v','C'])
            index = 0
            B = C[index]['B']
            w = W ** ~v
            # m = self.xor(B, w)
            print("Query =>", index)
            print("Corresponding B =>", B)
            print("Original message key =>", w)
            print("Search complete!!!")
        Protocol.setState(self, None)
        return None    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s [-r or -s]" % sys.argv[0])
        exit(-1)

    if sys.argv[1] == "-r":
        print("Operating as receiver...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.bind((HOST, PORT))
        svr.listen(1)
        svr_sock, addr = svr.accept()
        print("Connected by ", addr)
        msgs = None
        _name, _type, _sock = "receiver", RECEIVER, svr_sock
#       sp.setup( {'name':"receiver", 'type':_type, 'socket':svr_sock} )
    elif sys.argv[1] == "-s":
        print("Operating as sender...")
        clt = socket(AF_INET, SOCK_STREAM)
        clt.connect((HOST, PORT))
        clt.settimeout(15)
        msgs = ['one', 'two', 'three']
        _name, _type, _sock = "sender", SENDER, clt
    else:
        print("Usage: %s -r or -s" % sys.argv[0])
        exit(-1)
    
#    group = PairingGroup('library/a.param')
    sp = ObliviousTransfer(msgs)
    sp.setup( {'name':_name, 'type':_type, 'socket':_sock} )
    # run as a thread...
    sp.execute(_type)
