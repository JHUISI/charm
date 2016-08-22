'''
:Blind Signature Scheme
 
| From: "M. Abe A Secure Three-move Blind Signature Scheme for Polynomially 
| 	Many Signatures"
| Published in: EUROCRYPT 2001
| Available from: http://www.iacr.org/archive/eurocrypt2001/20450135.pdf

* type:           signature 
* setting:        integer groups

:Authors:    Antonio de la Piedra
:Date:       12/2013
 '''
from charm.toolbox.integergroup import integer, IntegerGroupQ, randomBits
from charm.toolbox.conversion import Conversion
from charm.core.engine.protocol import *
from charm.toolbox.enum import Enum
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
import hashlib
import sys

party = Enum('Signer', 'User')
SIGNER, USER = party.Signer, party.User
HOST, PORT = "", 8082

def SHA1(bytes1):
    s1 = hashlib.new('sha256')
    s1.update(bytes1)
    return s1.digest()

debug = False
class Asig(Protocol):    
    def __init__(self, groupObj, p=0, q=0, secparam=0):
        Protocol.__init__(self, None)        

        signer_states = { 1:self.signer_state1, 3:self.signer_state3, 5:self.signer_state5, 7:self.signer_state7 }
        user_states = { 2:self.user_state2, 4:self.user_state4, 6:self.user_state6, 8:self.user_state8 }

        signer_trans = { 1:3, 3:5, 5:7 }
        user_trans = { 2:4, 4:6, 6:8 }

        Protocol.addPartyType(self, SIGNER, signer_states, signer_trans, True)
        Protocol.addPartyType(self, USER, user_states, user_trans)

        self.group = groupObj
        Protocol.setSubclassVars(self, self.group) 
                        
        group = groupObj
        group.p, group.q, group.r = p, q, 2
              
        if group.p == 0 or group.q == 0:
            group.paramgen(secparam)
            p = group.p

        p = group.p
        q = group.q
           
    def signer_state1(self):
        print("SIGNER state #1")

        x, g, = self.group.random(), self.group.randomGen()
        z, h, = self.group.randomGen(), self.group.randomGen()
        
        y = g ** x 

        hs1 = hashlib.new('sha256')
        hs1.update(Conversion.IP2OS(integer(p)))
        hs1.update(Conversion.IP2OS(integer(q)))
        hs1.update(Conversion.IP2OS(integer(g)))
        hs1.update(Conversion.IP2OS(integer(h)))
        hs1.update(Conversion.IP2OS(integer(y)))
        
        msg = integer(hs1.digest())
        z = (msg ** ((p - 1)/q)) % p
                                
        Protocol.store(self, ('g', g), ('y', y), ('x', x), ('h', h), ('z', z))
        Protocol.setState(self, 3)
        
        return { 'g':g, 'y':y, 'h':h, 'z':z  }

    def user_state2(self, input):
        print("USER state #2")
        
        g = input.get('g')
        y = input.get('y')
        h = input.get('h')
        z = input.get('z')
                
        Protocol.store(self, ('g', g), ('y', y), ('h', h), ('z', z))
        Protocol.setState(self, 4)
        return { 'g':g, 'y':y }

    def signer_state3(self, input):
        print("SIGNER state #3")

        rnd = (integer(randomBits(80)))

        msg = integer(SHA1(Conversion.IP2OS(rnd)))
        z1 = (msg ** ((p - 1)/q)) % p
                        
        (g, y, h ,z) = Protocol.get(self,  ['g', 'y', 'h', 'z'])
        
        z2 = z/z1
        
        u = self.group.random()        
        s1 = self.group.random()                
        s2 = self.group.random()        
        d = self.group.random()        

        a = g ** u
        
        b1 = (g ** s1) * (z1 ** d)         
        b2 = (h ** s2) * (z2 ** d) 
        
        Protocol.store(self, ('u', u), ('s1', s1), ('s2', s2), ('d', d))
        Protocol.setState(self, 5)

        return { 'rnd':rnd, 'a':a, 'b1':b1, 'b2':b2  }

    def user_state4(self, input):
        print("USER state #4")

        (g, y, h ,z) = Protocol.get(self,  ['g', 'y', 'h', 'z'])
        
        rnd = input.get('rnd')
        a = input.get('a')
        b1 = input.get('b1')
        b2 = input.get('b2')
        
        msg = integer(SHA1(Conversion.IP2OS(rnd)))
        z1 = (msg ** ((p - 1)/q)) % p

        gamma = self.group.random()
        
        tau = self.group.random()

        t1 = self.group.random()        
        t2 = self.group.random()        
        t3 = self.group.random()        
        t4 = self.group.random()        
        t5 = self.group.random()        

        zeta = z ** gamma
        zeta1 = z1 ** gamma
        zeta2 = zeta/zeta1
                                                         
        alpha = a * (g ** t1) * (y ** t2) % p
        beta1 = (b1 ** gamma) * (g ** t3) * (zeta1 ** t4) % p
        beta2 = (b2 ** gamma) * (h ** t5) * (zeta2 ** t4) % p        
        eta = z ** tau
                
        epsilon = self.group.hash(zeta, zeta1, alpha, beta1, beta2, eta, "msg")
        e = epsilon - t2 - t4
                
        Protocol.store(self, ('z', z), ('z1', z1), ('zeta', zeta), ('zeta1', zeta1))
        Protocol.store(self, ('zeta2', zeta2), ('alpha', alpha), ('beta1', beta1), ('beta2', beta2))
        Protocol.store(self, ('t1', t1), ('t2', t2), ('t3', t3), ('t4', t4), ('t5', t5))
        Protocol.store(self, ('gamma', gamma), ('tau', tau), ('eta', eta))

        Protocol.setState(self, 6)        

        return { 'e':e }        
        
    def signer_state5(self, input):
        print("SIGNER state #5")

        e = input.get('e')
        (d, u, x) = Protocol.get(self, ['d', 'u', 'x'])
        
        c = e - d
        r = u - c*x
                
        Protocol.setState(self, 7)
        
        return { 'r':r, 'c':c, 'd':d }

    def user_state6(self, input):
        print("USER state #6")

        r = input.get('r')
        c = input.get('c')
        d = input.get('d')
        
        Protocol.store(self, ('r', r), ('c', c), ('d', d))
        
        Protocol.setState(self, 8)
        return { 'r':r }

    def signer_state7(self, input):
        print("SIGNER state #7")

        (s1, s2) = Protocol.get(self, ['s1', 's2'])
                        
        Protocol.setState(self, None)
        
        return { 's1':s1, 's2':s2 }

    def user_state8(self, input):
        print("USER state #8")

        s1 = input.get('s1')
        s2 = input.get('s2')
        
        (r, c, d) = Protocol.get(self, ['r', 'c', 'd'])

        (alpha, beta1, beta2, g, y, z, h) = Protocol.get(self, ['alpha', 'beta1', 'beta2', 'g', 'y', 'z', 'h'])
        (zeta, zeta1, zeta2, z, z1) = Protocol.get(self, ['zeta', 'zeta1', 'zeta2', 'z', 'z1'])
        (t1, t2, t3, t4, t5) = Protocol.get(self, ['t1', 't2', 't3', 't4', 't5'])
        (gamma, tau, eta) = Protocol.get(self, ['gamma', 'tau', 'eta'])
        
        rho = r + t1
        omega = c + t2
        
        sigma1 = (gamma*s1) + t3
        sigma2 = (gamma*s2) + t5
        
        delta = d + t4

        mu = tau - (delta * gamma)

        # Verification

        tmp1 = (g ** rho) * (y ** omega) % p
        tmp2 = (g ** sigma1) * (zeta1 ** delta) % p
        tmp3 = (h ** sigma2) * (zeta2 ** delta) % p
        tmp4 = (z ** mu) * (zeta ** delta) % p
        
        p1 = (omega + delta) % q
        p2 = self.group.hash(zeta, zeta1, tmp1, tmp2, tmp3, tmp4, "msg")        
        
        print("Verification OK:", p1 == p2)
        
        Protocol.setState(self, None)
        return None
         
if __name__ == "__main__":

    p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
    q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)

    groupObj = IntegerGroupQ()
    sp = Asig(groupObj, p, q, 1024)

    if sys.argv[1] == "-s":
        print("Operating as signer...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        svr.bind((HOST, PORT))
        svr.listen(1)
        svr_sock, addr = svr.accept()
        print("Connected by ", addr)
        _name, _type, _sock = "signer", SIGNER, svr_sock
    elif sys.argv[1] == "-u":
        print("Operating as user...")
        clt = socket(AF_INET, SOCK_STREAM)
        clt.connect((HOST, PORT))
        clt.settimeout(15)
        _name, _type, _sock = "user", USER, clt
    else:
        print("Usage: %s [-s or -u]" % sys.argv[0])
        exit(-1)
    sp.setup( {'name':_name, 'type':_type, 'socket':_sock} )
    sp.execute(_type)
    
