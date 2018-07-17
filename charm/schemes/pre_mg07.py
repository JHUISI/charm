'''
Identity-Based Proxy Re-Encryption

| From: "M. Green, G. Ateniese Identity-Based Proxy Re-Encryption", Section 4.3.
| Published in: Applied Cryptography and Network Security. Springer Berlin/Heidelberg, 2007
| Available from: http://link.springer.com/chapter/10.1007%2F978-3-540-72738-5_19

* type:           proxy encryption (identity-based)
* setting:        bilinear groups (symmetric)

:Authors:    N. Fotiou
:Date:       11/2012
'''
from charm.toolbox.pairinggroup import pc_element,ZR,G1,G2,GT,pair
from charm.core.math.integer import integer,bitsize, int2Bytes, randomBits
from charm.toolbox.hash_module import Hash
from charm.core.engine.util import objectToBytes

debug = False
class PreGA:
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,pc_element  
    >>> ID = "nikos fotiou"
    >>> ID2 = "test user"
    >>> msg = "hello world!!!!!"
    >>> group = PairingGroup('SS512', secparam=1024)  
    >>> pre = PreGA(group)
    >>> (master_secret_key, params) = pre.setup()
    >>> id_secret_key = pre.keyGen(master_secret_key, ID)
    >>> id2_secret_key = pre.keyGen(master_secret_key, ID2)
    >>> ciphertext = pre.encrypt(params, ID, msg);
    >>> pre.decryptFirstLevel(params,id_secret_key, ciphertext, ID)
    b'hello world!!!!!'
    >>> re_encryption_key = pre.rkGen(params,id_secret_key, ID, ID2)
    >>> ciphertext2 = pre.reEncrypt(params, ID, re_encryption_key, ciphertext)
    >>> pre.decryptSecondLevel(params,id2_secret_key,ID, ID2, ciphertext2)
    b'hello world!!!!!'
    """
    def __init__(self, groupObj):
        global group,h
        group = groupObj
        h = Hash(group) # use the default
        
    def setup(self):
        s = group.random(ZR) 
        g =  group.random(G1)
        # choose H1-H6 hash functions
        msk = { 's':s }
        params = { 'g':g, 'g_s':g**s}
        if(debug):
            print("Public parameters...")
            group.debug(params)
            print("Master secret key...")
            group.debug(msk)
        return (msk, params)

    def keyGen(self, msk, ID):
        k = group.hash(ID,G1) ** msk['s']
        skid = { 'skid':k }        
        if(debug):
            print("Key for id => '%s'" % ID)
            group.debug(skid)
        return skid

    def encrypt(self, params, ID, M):
        enc_M = integer(M)
        if bitsize(enc_M)/8 > group.messageSize():
            print("Message cannot be encoded.")
            return None
        sigma = group.random(GT)
        r = h.hashToZr(sigma,enc_M)
        A = params['g'] ** r 
        B = sigma * pair(params['g_s'], group.hash(ID, G1) ** r)
        C = enc_M ^ h.hashToZn(sigma)      
        C_ = {'A':A, 'B':B, 'C':C}
        S = group.hash((ID, C_),G1) ** r        
        ciphertext = {'S':S,'C':C_}           
        if(debug):
            print('\nEncrypt...')
            print('r => %s' % r)
            print('sigma => %s' % sigma)
            print('enc_M => %s' % enc_M)
            group.debug(ciphertext)
        return ciphertext
        
    def decryptFirstLevel(self, params, skid, cid, ID):
        H = group.hash((ID, cid['C']), G1)
        t = group.random(ZR)
        sigma =  cid['C']['B'] / (pair(cid['C']['A'], skid['skid'] * H ** t)/pair(params['g'] ** t, cid['S']))
        m =  cid['C']['C'] ^ h.hashToZn(sigma)
        r = h.hashToZr(sigma,m)
        if (cid['S'] != H**r) or (cid['C']['A'] != params['g'] ** r):
            if debug: print("Decryption Failed")
            return None 
        if(debug):
            print('\nDecrypting...')
            print('H => %s' % H)
            print('t => %s' % t)
            print('r => %s' % r)
            print('sigma => %s' % sigma)
            print(int2Bytes(m))
        return int2Bytes(m)
    
    def rkGen(self, params, skid, IDsrc, IDdest):
        N = integer(randomBits(group.secparam))
        K = pair(skid['skid'], group.hash(IDdest, G1))
        if(debug):
            print("\nRe-encryption key for id1 => '%s' to id2 => '%s'" % (IDsrc,IDdest))
            group.debug(skid)
            print('N => %s' % N)
            print('K => %s' % K)
        return  {'N':N, 'R':group.hash((K, IDsrc, IDdest, N), G1) * skid['skid']}
        
    def reEncrypt(self, params, IDsrc, rk, cid):
        H = group.hash((IDsrc, cid['C']), G1)
        if pair(params['g'], cid['S']) != pair(H, cid['C']['A']):
            if debug: print("Re-encryption Failed")
            return None                
        t = group.random(ZR)
        B_ = cid['C']['B'] / (pair(cid['C']['A'], rk['R'] * H ** t)/pair(params['g'] ** t, cid['S']))
        if(debug):
            print('\nRe-ncrypt...')
            print('H => %s' % H)
            print('t => %s' % t)
            print('B\' => %s' % B_)
        return {'A':cid['C']['A'], 'B':B_, 'C':cid['C']['C'], 'IDsrc':IDsrc, 'N':rk['N']}
        
    def decryptSecondLevel(self, params, skid, IDsrc, ID, cid):
        K = pair(group.hash(IDsrc, G1), skid['skid'])
        sigma = cid['B'] * pair(cid['A'], group.hash((K, IDsrc, ID, cid['N']), G1))
        m = cid['C'] ^ h.hashToZn(sigma)
        r = h.hashToZr(sigma,m)
        if (cid['A'] != params['g'] ** r):
            if debug: print("Decryption second level Failed")
            return None 
        if(debug):
            print('\nDecrypting Second Level...')
            print('K => %s' % K)
            print('sigma => %s' % sigma)
            print(int2Bytes(m)) 
        return int2Bytes(m) 

