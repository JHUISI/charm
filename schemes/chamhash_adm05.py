''' Ateneise-Medeiros (Schnorr group-based)
 
 | From: "Ateneise-Breno de Medeiros On the Key Exposure Problem in Chameleon Hashes", Section 4.
 | Published in: SCN 2004
 | Available from:
 | Notes: 

 * type:         hash function (chameleon)
 * setting:      Schnorr groups
 * assumption:   DL-Hard

:Authors: J Ayo Akinyele
:Date:    4/2011
'''

from toolbox.Hash import *
from toolbox.integergroup import *

debug = True
class Adm05(ChamHash):
    def __init__(self):
        ChamHash.__init__(self)
        global group; 
        group = IntegerGroupQ(0)
        self.group = group        
    
    def paramgen(self, secparam=1024):
        group.paramgen(secparam)
        g, x = group.randomGen(), group.random() # g, [1,q-1]
        y = g ** x
        
        if debug:
            print("Public params")
            print("g =>", g); print("y =>", y)
        
        pk = { 'g':g, 'y':y }
        sk = { 'x':x }        
        return (pk, sk)
    
    def hash(self, pk, m, r = 0):
        p,q = group.p, group.q
        if r == 0: r = group.random()
        s = group.random()        
        e = group.hash(m, r)
        
        C = r - (((pk['y'] ** e) * (pk['g'] ** s)) % p) % q
        return C

if __name__ == "__main__":    
    chamHash = Adm05()
    
    #TODO: how long is paramgen supposed to take?
    (pk, sk) = chamHash.paramgen()
    
    msg = "hello world this is the message"
    c = chamHash.hash(pk, msg)
    
    print("sig =>", c)