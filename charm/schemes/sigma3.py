from charm.toolbox.sigmaprotocol import Sigma
from charm.toolbox.pairinggroup import ZR,G2,pair

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
        (g, V) = Sigma.get(self, ['g', 'V'])
        r = self.group.random(G2)
        a1 = pair(g, r)
        a2 = pair(V, r)
        print("send r =>", r)
        print("send a1 =>", a1)
        print("send a2 =>", a2)
        pk = Sigma.get(self, ['g','V','H'], dict)

        Sigma.store(self, ('r',r) )
        Sigma.setState(self, 3)
        return { 'a1':a1, 'a2':a2, 'pk':pk }
    
    def prover_state3(self, input):
        print("PROVER 3: ")
        (r, h, c) = Sigma.get(self, ['r', 'h', 'c'])
        print("input c =>", c)
        z = r * (h ** -c)
        Sigma.setState(self, 5)
        # need store and get functions for db        
        return {'z':z }
    
    def prover_state5(self, input):
        print("PROVER 5: result =>", input)
        Sigma.setState(self, None)
        Sigma.setErrorCode(self, input)
        return None
    
    def verifier_state2(self, input):
        print("VERIFIER 2: ")
        c = self.group.random(ZR)
        print("send c =>", c)
        Sigma.setState(self, 4)
        return {'c':c }

    def verifier_state4(self, input):
        print("VERIFIER 4: ")
        (a1, a2, c, W, z, pk) = Sigma.get(self, ['a1','a2','c','W','z','pk'])
        g, V, H = pk['g'], pk['V'], pk['H']
        if a1 == pair(g,z) * (H ** c) and a2 == pair(V,z) * (W ** c):
            print("SUCCESS!!!!!!!"); result = 'OK'
        else:
            print("Failed!!!"); result = 'FAIL'
        Sigma.setState(self, 6)
        Sigma.setErrorCode(self, result)
        return result
    
    def verifier_state6(self, input):
        print("VERIFIER 6: done.")
        Sigma.setState(self, None)
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
