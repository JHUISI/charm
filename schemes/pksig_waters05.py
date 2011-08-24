'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:			06/2011
''' 

from charm.cryptobase import *
from toolbox.PKSig import *
from toolbox.bitstring import Bytes
from toolbox.conversion import Conversion
from toolbox.pairinggroup import *
from charm.engine import util
import hashlib, math

debug = False
class IBE_N04_Sig(PKSig):
    """Implementation of David Naccahe Identity Based Encryption"""
    def __init__(self, groupObj):
        PKSig.__init__(self)
        #PKSig.setProperty(self, secdef='IND_ID_CPA', assumption='DBDH', secmodel='Standard')
        #, other={'id':ZR}
        #message_space=[GT, 'KEM']
        global group, hashObj
        group = groupObj
        hashObj = hashlib.new('sha1') 
        
    def sha1(self, message):
        h = hashObj.copy()
        h.update(bytes(message))
        return Bytes(h.digest()) 
        
        
    def keygen(self, l=32):
        '''l is the security parameter
        with l = 32, and the hash function at 160 bits = n * l with n = 5'''
        g = group.random(G1)      # generator for group G of prime order p
        
        hLen = len(hashObj.digest()) * 8
        n = int(math.floor(hLen / l))
        #nprime = n * int(g).bit_length()
        #H = self.sha1 # Hash function H :{0,1}* -> {0,1}^{n'}      
        
        alpha = group.random()  #from Zp
        g1    = g ** alpha      # G1
        g2    = group.random(G2)    #G2
        uprime = group.random(G2)
        U = [group.random() for x in range(n)]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l, 'egg': pair(g, g2) ** alpha }
        
        # mk = pk.copy()
        mk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l, 'egg': pair(g, g2) ** alpha }
        mk['g2^alpha'] = g2 ** alpha #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
    
    def stringtoidentity(self, pk, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        hash = self.sha1(Bytes(strID)) # 'utf-8'
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header
        
        v=[]
        for i in range(pk['n']):  #n must be greater than or equal to 1
            binsubstr = bstr[pk['l']*i : pk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval) 
            v.append(intelement)
                     
        return v
    
    def sign(self, pk, sk, m):
        '''v = (v1, .., vn) is an identity'''
        r = group.random()
        
        d1 = sk['uPrime']
        for i in range(sk['n']):
            d1 *= sk['U'][i] ** m[i]
            
        d1 = sk['g2^alpha'] * (d1 ** r)
        d2 = sk['g'] ** r
        return {'d1': d1, 'd2':d2}

    def verify(self, pk, msg, sig):
        c3 = pk['uPrime']
        for i in range(pk['n']):
            c3 *= pk['U'][i] ** msg[i]
        
        num = pair(pk['g'], sig['d1'])
        dem = pair(sig['d2'], c3)
        return pk['egg'] == num / dem

    
def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('../param/a.param')
    ibe = IBE_N04_Sig(groupObj)
    (pk, sk) = ibe.keygen()

    # represents public identity
    M = "bob@mail.com"

    msg = ibe.stringtoidentity(pk, M)    
    sig = ibe.sign(pk, sk, msg)
    if debug: 
	print("original msg => '%s'" % M)
    	print("msg => '%s'" % msg)
    	print "sig => '%s'" % sig
    
    assert ibe.verify(pk, msg, sig)
    if debug: print("Successful Verification!!! msg => '%s'" % msg)

if __name__ == '__main__':
    debug = True
    main()
