'''David Naccache based Identity-Based Encryption
 
| From: "David Naccache Secure and Practical Identity-Based Encryption Section 4"
| Available from: http://eprint.iacr.org/2005/369.pdf

* type:			encryption (identity-based)
* setting:		bilinear groups (asymmetric)

:Authors:	Gary Belvin
:Date:			06/2011
''' 

from charm.cryptobase import *
from toolbox.IBEnc import *
from toolbox.bitstring import Bytes
from toolbox.conversion import Conversion
from toolbox.pairinggroup import *
import hashlib, math

debug = False
class IBE_N04(IBEnc):
    """Implementation of David Naccahe Identity Based Encryption"""
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        IBEnc.setProperty(self, secdef='IND_ID_CPA', assumption='DBDH', secmodel='Standard')
        #, other={'id':ZR}
        #message_space=[GT, 'KEM']
        global group, hashObj
        group = groupObj
        hashObj = hashlib.new('sha1') 
        
    def sha1(self, message:Bytes):
        h = hashObj.copy()
        h.update(bytes(message))
        return Bytes(h.digest()) 
        
        
    def setup(self, l=32):
        '''l is the security parameter
        with l = 32, and the hash function at 160 bits = n * l with n = 5'''
        g = group.random(G1)      # generator for group G of prime order p
        
        hLen = len(hashObj.digest()) * 8
        n = math.floor(hLen / l)
        
        #nprime = n * int(g).bit_length()
        #H = self.sha1 # Hash function H :{0,1}* -> {0,1}^{n'}      
        
        alpha = group.random()  #from Zp
        g1    = g ** alpha      # G1
        g2    = group.random(G2)    #G2
        uprime = group.random(G2)
        U = [group.random() for x in range(n)]
        
        pk = {'g':g, 'g1':g1, 'g2': g2, 'uPrime':uprime, 'U': U, 
              'n':n, 'l':l}
        
        mk = pk.copy()
        mk['g2^alpha'] = g2 ** alpha #master secret
        if debug: 
            print(mk)
        
        return (pk, mk)
    
    def stringtoidentity(self, pk, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        hash = self.sha1(Bytes(strID, 'utf-8'))
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header
        
        v=[]
        for i in range(pk['n']):  #n must be greater than or equal to 1
            binsubstr = bstr[pk['l']*i : pk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval) 
            v.append(intelement)
                     
        return v
    
    def extract(self, mk, v):
        '''v = (v1, .., vn) is an identity'''
        r = group.random()
        
        d1 = mk['uPrime']
        for i in range(mk['n']):
            d1 *= mk['U'][i] ** v[i]
            
        d1 = mk['g2^alpha'] * (d1 ** r)
        d2 = mk['g'] ** r
        
        if debug:
            print("D1    =>", d1)
            print("D2    =>", d2)
        return {'d1': d1, 'd2':d2}

    def encrypt(self, pk, ID, M:GT):
        t = group.random()
        c1 = (pair(pk['g1'], pk['g2']) ** t) * M
        c2 = pk['g'] ** t
        c3 = pk['uPrime']
        for i in range(pk['n']):
            c3 *= pk['U'][i] ** ID[i]
        c3 = c3 ** t
        
        if debug:
            print("Encrypting")
            print("C1    =>", c1)
            print("C2    =>", c2)
            print("C3    =>", c3)
        return {'c1':c1, 'c2': c2, 'c3':c3}

    def decrypt(self, pk, sID, ct):
        num = pair(sID['d2'], ct['c3'])
        dem = pair(ct['c2'], sID['d1'])
        if debug:
            print("Decrypting")    
            print("arg1    =>", sID['d2'].type)
            print("arg2    =>", ct['c3'].type)
            print("Num:    =>", num)
            print("Dem:    =>", dem)
            
        return ct['c1'] *  num / dem

    
def main():
    # initialize the element object so that object references have global scope
    groupObj = PairingGroup('a.param')
    ibe = IBE_N04(groupObj)
    (pk, mk) = ibe.setup()

    # represents public identity
    ID = "bob@mail.com"
    kID = ibe.stringtoidentity(pk, ID)
    if debug: print("Bob's key  =>", kID)
    key = ibe.extract(mk, kID)

    M = groupObj.random(GT)
    cipher = ibe.encrypt(pk, kID, M)
    m = ibe.decrypt(pk, key, cipher)
    #print('m    =>', m)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!!! m => '%s'" % m)
    del groupObj
if __name__ == '__main__':
    debug = True
    main()
