
from toolbox.sigmaprotocol import *
from toolbox.pairinggroup import *

class SigmaProtocol2(Sigma):
    def __init__(self, groupObj, common_input=None):
        Sigma.__init__(self, groupObj, common_input)
        self.__gen_setup = False
        # dict to hold variables from interaction        
        
    def gen_common(self):
        if self.__gen_setup:
            x = self.group.random(ZR)
            v = self.group.random(ZR) 
            g = self.group.random(G1) # , self.group.random(G2)
            index = self.group.init(ZR, 1) # testing message 0 at index 1
            V = (g ** ~(x+index)) ** v
            y = g ** x
            print("check: lhs = e(V,y) =>", pair(V,y))
            print("check: rhs = e(V,g)^-o * e(g,g)^v =>", (pair(V,g) ** -index) * (pair(g,g) ** v))
            Protocol.store(self, ('g', g), ('V', V), ('v',v), ('y',y), ('sigma', index) )
            return None
        
    def prover_state1(self):
        print("PROVER 1: ")
        self.gen_common()
#        (g, g2, V) = Protocol.get(self, ['g', 'g2', 'V'])
        (g, V) = Protocol.get(self, ['g', 'V'])
        r1, r2 = self.group.random(ZR), self.group.random(ZR)
#        a = (pair(V, g2) ** -r1) * (pair(g, g2) ** r2)
        a = (pair(V, g) ** -r1) * (pair(g, g) ** r2)
        print("send g =>", g)
        print("send V =>", V)
        print("send r1 =>", r1)
        print("send r2 =>", r2)
        print("send a =>", a)

        Protocol.store(self, ('r1',r1), ('r2',r2) )
        Protocol.setState(self, 3)
#        pk = Protocol.get(self, ['g','g2','V','y'], dict)
        pk = Protocol.get(self, ['g','V','y'], dict)
        return { 'a':a, 'pk':pk }
    
    def prover_state3(self, input):
        print("PROVER 3: ")
        (r1, r2, v, sigma) = Protocol.get(self, ['r1','r2','v','sigma'])
        c = input['c']
        print("input c =>", c)
        z1 = r1 - sigma * c # need a way to get sigma index as part of init index (1..N)
        z2 = r2 - v * c 
        print("send z1 =>", z1)
        print("send z2 =>", z2)
        Protocol.setState(self, 5)
        # need store and get functions for db        
        return {'z1':z1, 'z2':z2 }
    
    def prover_state5(self, input):
        print("PROVER 5: result =>", input)
        Protocol.setState(self, None)
        Protocol.setErrorCode(self, input)
        return None
    
    def verifier_state2(self, input):
        print("VERIFIER 2: ")
        print("input pk =>", input['pk'])
        print("input a =>", input['a'])
        pk = input['pk']
    
        c = self.group.random(ZR)
        print("send c =>", c)
        Protocol.store(self, ('c',c),('g',pk['g']),('V',pk['V']), ('y',pk['y']), ('a', input['a']) ) 
        Protocol.setState(self, 4)
        return {'c':c }

    def verifier_state4(self, input):
        print("VERIFIER 4: ")
        z1,z2 = input['z1'],input['z2']
        (V, y, g, a, c) = Protocol.get(self, ['V','y','g','a','c'])
        print("get a =>", a)
        test = (pair(V,y) ** c) * (pair(V,g) ** -z1) * (pair(g,g) ** z2)
        print("test =>", test)
        if a == test:
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
#    group = PairingGroup('library/a.param')
#    sp = SigmaProtocol2(group)
#    sp.setup( {'name':_name, 'type':_type, 'socket':_sock} )
#    # run as a thread...
#    sp.execute(_type)
#    print("Result of protocol =>", sp.result)
#    