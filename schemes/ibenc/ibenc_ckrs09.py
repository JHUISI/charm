'''
Jan Camenisch, Markulf Kohlweiss, Alfredo Rial, and Caroline Sheedy (Pairing-based)
 
| From: "Blind and Anonymous Identity-Based Encryption and 
Authorised Private Searches on Public Key Encrypted Data".
| Published in: PKC 2009
| Available from: http://www.iacr.org/archive/pkc2009/54430202/54430202.pdf
| Notes: section 4.1, first blind and anonymous IBE scheme
| Security Assumptions: 
|
| type:           identity-based encryption (public key)
| setting:        Pairing

:Authors:    J Ayo Akinyele/Mike Rushanan
:Date:       02/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import IBEnc
from charm.toolbox.conversion import Conversion
from charm.toolbox.bitstring import Bytes
from charm.toolbox.iterate import dotprod2
import hashlib

debug = False
class IBE_CKRS(IBEnc):
    def __init__(self, groupObj):
        global group,hashObj
        group = groupObj
        hashObj = hashlib.new('sha1') 

    
    def setup(self, n=5, l=32):
        """n integers with each size l""" 
        global lam_func
        lam_func = lambda i,x,y: x[i] ** y[i] 
        alpha, t1, t2, t3, t4 = group.random(ZR, 5)
        z = list(group.random(ZR, n))
        g = group.random(G1)
        h = group.random(G2)
        omega = pair(g, h) ** (t1 * t2 * alpha)
        g_l = [g ** i for i in z]
        h_l = [h ** i for i in z]
        v1, v2 = g ** t1, g ** t2
        v3, v4 = g ** t3, g ** t4
        msk = { 'alpha':alpha, 't1':t1, 't2':t2, 't3':t3, 't4':t4 }
        mpk = { 'omega':omega, 'g':g, 'h':h, 'g_l':g_l, 'h_l':h_l, 
               'v1':v1, 'v2':v2, 'v3':v3, 'v4':v4, 'n':n, 'l':l }
        return (mpk, msk)

    def sha1(self, message):
        h = hashObj.copy()
        h.update(bytes(message, 'utf-8'))
        return Bytes(h.digest())

    def strToId(self, pk, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        hash = self.sha1(strID)
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header

        v=[]
        for i in range(pk['n']):  #z must be greater than or equal to 1
            binsubstr = bstr[pk['l']*i : pk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        return v
    
    def extract(self, mpk, msk, ID):
        r1, r2 = group.random(ZR, 2) # should be params of extract
        hID = self.strToId(mpk, ID)
        hashID2 = mpk['h_l'][0] * dotprod2(range(1,mpk['n']), lam_func, mpk['h_l'], hID)        
        d = {}
        
        d[0] = mpk['h'] ** ((r1 * msk['t1'] * msk['t2']) + (r2 * msk['t3'] * msk['t4']))
        d[1] = (mpk['h'] ** (-msk['alpha'] * msk['t2'])) * (hashID2 ** (-r1 * msk['t2']))
        d[2] = (mpk['h'] ** (-msk['alpha'] * msk['t1'])) * (hashID2 ** (-r1 * msk['t1']))
        d[3] = hashID2 ** (-r2 * msk['t4'])
        d[4] = hashID2 ** (-r2 * msk['t3'])
        return { 'd':d }
    
    def encrypt(self, mpk, ID, msg):
        s, s1, s2 = group.random(ZR, 3)
        hID = self.strToId(mpk, ID)
        hashID1 = mpk['g_l'][0] * dotprod2(range(1,mpk['n']), lam_func, mpk['g_l'], hID)
        c = {}
        c_pr = (mpk['omega'] ** s) * msg
        c[0] = hashID1 ** s
        c[1] = mpk['v1'] ** (s - s1)
        c[2] = mpk['v2'] ** s1
        c[3] = mpk['v3'] ** (s - s2)
        c[4] = mpk['v4'] ** s2        
        return {'c':c, 'c_prime':c_pr }
    
    def decrypt(self, mpk, sk, ct):
        c, d = ct['c'], sk['d']
        msg = ct['c_prime'] * pair(c[0], d[0]) * pair(c[1], d[1]) * pair(c[2], d[2]) * pair(c[3], d[3]) * pair(c[4], d[4])        
        return msg
    
def main():
    groupObj = PairingGroup('SS512')
    ibe = IBE_CKRS(groupObj)
    (mpk, msk) = ibe.setup()

    # represents public identity
    ID = "bob@mail.com"
    sk = ibe.extract(mpk, msk, ID)

    M = groupObj.random(GT)
    ct = ibe.encrypt(mpk, ID, M)
    m = ibe.decrypt(mpk, sk, ct)
    if debug: print('m    =>', m)

    assert m == M, "FAILED Decryption!"
    if debug: print("Successful Decryption!!! m => '%s'" % m)
    
    
if __name__ == "__main__":
    debug = True
    main()
