from toolbox.sigmaprotocol import *
from toolbox.pairinggroup import *
#from socket import *
import sys

HOST, PORT = "", 8082

# Proof of Membership {(h): H = e(g,h) /and/ W = e(h,V)}
class SigmaProtocol3(Sigma):
    def __init__(self, groupObj=None, common_input=None):        
        Sigma.__init__(self, groupObj, common_input)
        # dict to hold variables from interaction        
        
#    def gen_common(self):
#        if self.__gen_setup:
#            x = self.group.random(ZR)
#            v = self.group.random(ZR) 
#            g = self.group.random(G1) # , self.group.random(G2)
#            index = self.group.init(ZR, 1) # testing message 0 at index 1
#            V = (g ** ~(x+index)) ** v
#            y = g ** x
#            print("check: lhs = e(V,y) =>", pair(V,y))
#            print("check: rhs = e(V,g)^-o * e(g,g)^v =>", (pair(V,g) ** -index) * (pair(g,g) ** v))
#            Protocol.store(self, ('g', g), ('V', V), ('v',v), ('y',y), ('sigma', index) )
#            return None
        
    def prover_state1(self):
        print("PROVER 1: ")
        (g, V) = Protocol.get(self, ['g', 'V'])
        r = self.group.random(G1)
#        a = (pair(V, g2) ** -r1) * (pair(g, g2) ** r2)
        a1 = pair(g, r); a2 = pair(V, r)
        print("send r =>", r)
        print("send a1 =>", a1)
        print("send a2 =>", a2)

        Protocol.store(self, ('r',r), ('a1',a1), ('a2',a2) )
        Protocol.setState(self, 3)

        pk = Protocol.get(self, ['g','V','H'], dict)
        return { 'a1':a1, 'a2':a2, 'pk':pk }
    
    def prover_state3(self, input):
        print("PROVER 3: ")
        (r, h) = Protocol.get(self, ['r', 'h'])
        c = input['c']
        print("input c =>", c)
        z = r * (h ** -c)
        Protocol.setState(self, 5)
        # need store and get functions for db        
        return {'z':z }
    
    def prover_state5(self, input):
        print("PROVER 5: result =>", input)
        Protocol.setState(self, None)
        Protocol.setErrorCode(self, input)
        return None
    
    def verifier_state2(self, input):
        print("VERIFIER 2: ")
        print("input pk =>", input['pk'])
        print("input a1 =>", input['a1'])
        print("input a2 =>", input['a2'])
        pk = input['pk']
    
        c = self.group.random(ZR)
        print("send c =>", c)
        Protocol.store(self, ('c',c),('g',pk['g']),('V',pk['V']),('H',pk['H']), 
            ('a1', input['a1']), ('a2', input['a2']) ) 
        Protocol.setState(self, 4)
        return {'c':c }

    def verifier_state4(self, input):
        print("VERIFIER 4: ")
        z = input['z']
        (a1, a2, g, H, c, V, W) = Protocol.get(self, ['a1','a2','g','H','c','V','W'])
        print("get a1 =>", a1)
        _a1 = pair(g,z) * (H ** c)
        _a2 = pair(V,z) * (W ** c)
        print("test a1 =>", _a1)
        print("get a2 =>", a2)
        print("test a2 =>", _a2)
        if a1 == _a1 and a2 == _a2:
            print("SUCCESS!!!!!!!"); result = 'OK'
        else:
            print("Failed!!!"); result = 'FAIL'
        Protocol.setState(self, 6)
        Protocol.setErrorCode(self, result)
        return result
    
    def verifier_state6(self, input):
        print("VERIFIER 6: done.")
        Protocol.setState(self, None)
        return None

#if __name__ == "__main__":
#    if len(sys.argv) != 2:
#        print("Usage: %s [-v or -p]" % sys.argv[0])
#        exit(-1)
#
#    if sys.argv[1] == "-v":
#        print("Operating as verifier...")
#        svr = socket(AF_INET, SOCK_STREAM)
#        svr.bind((HOST, PORT))
#        svr.listen(1)
#        svr_sock, addr = svr.accept()
#        print("Connected by ", addr)
#        _name, _type, _sock = "verifier", VERIFIER, svr_sock
#    elif sys.argv[1] == "-p":
#        print("Operating as prover...")
#        clt = socket(AF_INET, SOCK_STREAM)
#        clt.connect((HOST, PORT))
#        clt.settimeout(15)
#        _name, _type, _sock = "prover", PROVER, clt
#    else:
#        print("Usage: %s -v or -p" % sys.argv[0])
#        exit(-1)
#    
#    group = PairingGroup('a.param')
#    sp = SigmaProtocol3(group)
#    sp.setup( {'name':_name, 'type':_type, 'socket':_sock} )
#    # run as a thread...
#    sp.execute(_type)
#    print("Result of protocol =>", sp.result)
#    