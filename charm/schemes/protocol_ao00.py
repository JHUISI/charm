'''
:Partially Blind Signature Scheme
 
| From: "M. Abe, T. Okamoto Provably Secure Partially Blind Signatures"
| Published in: CRYPTO 2000
| Available from: http://www.iacr.org/archive/crypto2000/18800272/18800272.pdf

* type:           signature (partially blind)
* setting:        integer groups

:Authors:    Antonio de la Piedra
:Date:       12/2013
 '''
from charm.toolbox.integergroup import integer, IntegerGroupQ
from charm.core.engine.protocol import *
from charm.toolbox.enum import Enum
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
import hashlib
import sys

party = Enum('Signer', 'User')
SIGNER, USER = party.Signer, party.User
HOST, PORT = "", 8082

def SHA2(bytes1):
    s1 = hashlib.new('sha256')
    s1.update(bytes1)
    return s1.digest()

debug = False
class AOSig(Protocol):    
    def __init__(self, groupObj, p=0, q=0, secparam=0):
        Protocol.__init__(self, None)        

        signer_states = { 1:self.signer_state1, 3:self.signer_state3, 5:self.signer_state5 }
        user_states = { 2:self.user_state2, 4:self.user_state4, 6:self.user_state6 }

        signer_trans = { 1:3, 3:5 }
        user_trans = { 2:4, 4:6 }

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

        p = self.group.p
        q = self.group.q
                
        x, g, = self.group.random(), self.group.randomGen()
        
        y = g ** x 
                        
        Protocol.store(self, ('g', g), ('y', y), ('x', x))
        Protocol.setState(self, 3)
        
        return { 'g':g, 'y':y }

    def user_state2(self, input):
        print("USER state #2")
        
        g = input.get('g')
        y = input.get('y')
                
        Protocol.store(self, ('g', g), ('y', y))
        Protocol.setState(self, 4)
        return { 'g':g, 'y':y }

    def signer_state3(self, input):
        print("SIGNER state #3")

        u = self.group.random()        
        s = self.group.random()        
        d = self.group.random()        

        g = input.get('g')
        y = input.get('y')
        
        str = "info"

        msg = integer(SHA2(str))
        z = (msg ** ((p - 1)/q)) % p
                
        a = g ** u
        b = (g ** s) * (z ** d) 
        
        Protocol.store(self, ('u', u), ('s', s), ('d', d))
        Protocol.setState(self, 5)

        return { 'a':a, 'b':b, 's':s }

    def user_state4(self, input):
        print("USER state #4")
        
        p = self.group.p
        q = self.group.q
                        
        a = input.get('a')
        b = input.get('b')
        s = input.get('s')
        
        g, y = Protocol.get(self, ['g', 'y'])
         
        t1 = self.group.random()        
        t2 = self.group.random()        
        t3 = self.group.random()        
        t4 = self.group.random()        
        
        str = "info"
                
        msg = integer(SHA2(str))
        z = (msg ** ((p - 1)/q)) % p
                
        alpha = a * (g ** t1) * (y ** t2) % p
        beta  = b * (g ** t3) * (z ** t4) % p
        
        epsilon = self.group.hash(alpha, beta, z, "msg")
        e = epsilon - t2 - t4
                
        Protocol.store(self, ('z', z), ('s', s), ('t1', t1), ('t2', t2), ('t3', t3), ('t4', t4), ('alpha', alpha), ('beta', beta))
        Protocol.setState(self, 6)        

        return { 'e':e }        
        
    def signer_state5(self, input):
        print("SIGNER state #5")

        e = input.get('e')
        (d, u, x, s) = Protocol.get(self, ['d', 'u', 'x', 's'])
        
        c = e - d
        r = u - c*x
                
        Protocol.setState(self, None)
        
        return { 'r':r, 'c':c, 'd':d }

    def user_state6(self, input):
        print("USER state #6")

        r = input.get('r')
        c = input.get('c')
        d = input.get('d')
        
        (t1, t2, t3, t4, s) = Protocol.get(self, ['t1', 't2', 't3', 't4', 's'])
        (alpha, beta, g, y, z) = Protocol.get(self, ['alpha', 'beta', 'g', 'y', 'z'])
        
        rho = r + t1
        omega = c + t2
        sigma = s + t3
        delta = d + t4

        # Verification

        tmp1 = (g ** rho) * (y ** omega) % p
        tmp2 = (g ** sigma) * (z ** delta) % p
        
        p1 = (omega + delta) % q
        p2 = self.group.hash(tmp1, tmp2, z, "msg")
        
        print("Verification OK:", p1 == p2)

        Protocol.setState(self, None)
        return None
                
if __name__ == "__main__":

    p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
    q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)

    groupObj = IntegerGroupQ()
    sp = AOSig(groupObj, p, q, 1024)

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
    
