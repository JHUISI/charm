'''
   Marc Joye, Benoit Libert  (Aggregation Scheme)
    
   | From: "A Scalable Scheme for Privacy-Preserving Aggregation of Time-Series Data" 
   | Published in: Financial Crypto 2013
   | Available from: http://eprint.iacr.org/2009/309.pdf
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


