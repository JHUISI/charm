'''
   Marc Joye, Benoit Libert  (Aggregation Scheme)
    
   | From: "A Scalable Scheme for Privacy-Preserving Aggregation of Time-Series Data" 
   | Published in: Financial Crypto 2013
   | Available from: http://joye.site88.net/papers/JL13aggreg.pdf

   | Notes: 
   
   * type:           Plaintext Evaluation of the sum from encrypted values. 
   * setting:        Integer
  
  :Authors:    Iraklis Leontiadis
  :Date:            12/2013
'''
 
from charm.toolbox.integergroup import RSAGroup 
from charm.schemes.pkenc.pkenc_paillier99 import Pai99
from charm.toolbox.integergroup import lcm,integer
from charm.toolbox.PKEnc import PKEnc
from charm.core.engine.util import *

'''
Test script for two values
===========================
group = RSAGroup()
pai = Pai99(group)
(public_key, secret_key) = pai.keygen()
n=public_key['n']
n2=public_key['n2']
x1=3 #testing values for user 1
x2=2 #testing values for user 2
msg1 = pai.encode(n2, 1+x1*n)
msg2 = pai.encode(n2, 1+x2*n)
  
prod=pai.encode(n2,msg1*msg2)
print (integer(prod-integer(1)%n2)/n)
'''
class Joye():

    def __init__(self,users=2):
        global pai,group
        group=RSAGroup()
        pai=Pai99(group)
        self.users=users
        self.r=14 #this value act as the common hash output H(r) according to the protocol.

    def destruction_keys(self,pk):
        k={}
        for i in range(self.users):
            k['k'+str(i)]=integer(group.random(102))#exponentiation works only for small keys (needs investigation)
        k[0]=integer(-1)*(sum(k.values())) #inverse of the sum of all user keys. Acts as annihilation for keys.
        k[1]=(sum(k.values()))           
        #self.ak=integer(1)/integer(self.r)**integer(k[0])
        return k

    def encrypt(self,x,pk,sk):
        c1=self.encode(x,pk)%pk['n2']
        c2=pai.encode(pk['n2'],integer(self.r%pk['n2'])**integer(sk%pk['n2']))
        cipher=pai.encode(pk['n2'],c1*c2)
        return cipher

    '''def decrypt(self,c,pk,sk):
        c=pai.encode(pk['n2'],c)
        mul=pai.encode(pk['n2'],integer(self.r)**integer(sk))
        inter=pai.encode(pk['n2'],c*mul)
        result =pai.encode(pk['n'],integer(inter-integer(1)%pk['n2'])/pk['n'])
        return result
'''
    def keygen(self):
        public_key,secret_key = pai.keygen()
        return public_key

    def encode(self,x,pk):
        return integer(pai.encode(pk['n2'], 1+integer(x)*pk['n']))

    def sumfree(self,x1,x2,pk):
        '''Tests sum evaluations without encryption'''
        msg1 = self.encode(x1,pk)
        msg2 = self.encode(x2,pk)
        prod=pai.encode(pk['n2'],msg1*msg2)
        sumres=integer(prod%pk['n2']-integer(1)%pk['n2'])/pk['n']
        return sumres

    def sum(self,x1,x2,pk,k0):
        prod=pai.encode(pk['n2'],x1*x2)
        inter=pai.encode(pk['n2'],integer(self.r)**integer(integer(-1)*k0))
        inter2=(integer(prod)/integer(inter))
        sumres=integer(inter2%pk['n2']-integer(1)%pk['n2'])/pk['n']
        return sumres

if __name__=='__main__':
    joye = Joye()
    pk = joye.keygen()
    k = joye.destruction_keys(pk)

    c1 = joye.encrypt(2,pk,k['k0'])
    c2 = joye.encrypt(4,pk,k['k1'])
    
    print (joye.sum(c1,c2,pk,k[0]))
