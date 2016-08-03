'''
Boneh-Franklin Identity Based Encryption
  
| From: "D. Boneh, M. Franklin Identity-Based Encryption from the Weil Pairing", Section 4.2.
| Published in: Crypto 2003
| Available from: http://.../bfibe.pdf
| Notes: This is the IBE .

* type:           encryption (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       2/2011
'''
from charm.toolbox.pairinggroup import ZR,G1,G2,pair
from charm.core.math.integer import randomBits,integer,bitsize
from charm.toolbox.hash_module import Hash,int2Bytes,integer
from charm.toolbox.IBEnc import IBEnc

debug = False
class IBE_BonehFranklin(IBEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> group = PairingGroup('MNT224', secparam=1024)    
    >>> ibe = IBE_BonehFranklin(group)
    >>> (master_public_key, master_secret_key) = ibe.setup()
    >>> ID = 'user@email.com'
    >>> private_key = ibe.extract(master_secret_key, ID)
    >>> msg = b"hello world!!!!!"
    >>> cipher_text = ibe.encrypt(master_public_key, ID, msg)
    >>> ibe.decrypt(master_public_key, private_key, cipher_text)
    b'hello world!!!!!'
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group,h
        group = groupObj
        h = Hash(group)
        
    def setup(self):
        s, P = group.random(ZR), group.random(G2)
        P2 = s * P
        # choose H1, H2 hash functions
        pk = { 'P':P, 'P2':P2 }
        sk = { 's':s }
        if(debug):
            print("Public parameters...")
            group.debug(pk)
            print("Secret parameters...")
            group.debug(sk)
        return (pk, sk)
    
    def extract(self, sk, ID):        
        d_ID = sk['s'] * group.hash(ID, G1)
        k = { 'id':d_ID, 'IDstr':ID }
        if(debug):
            print("Key for id => '%s'" % ID)
            group.debug(k)
        return k
        
    
    def encrypt(self, pk, ID, M): # check length to make sure it is within n bits
        Q_id = group.hash(ID, G1) #standard
        g_id = pair(Q_id, pk['P2']) 
        #choose sig = {0,1}^n where n is # bits
        sig = integer(randomBits(group.secparam))
        r = h.hashToZr(sig, M)

        enc_M = self.encodeToZn(M)
        if bitsize(enc_M) / 8 <= group.messageSize():
            C = { 'U':r * pk['P'], 'V':sig ^ h.hashToZn(g_id ** r) , 'W':enc_M ^ h.hashToZn(sig) }
        else:
            print("Message cannot be encoded.")
            return None

        if(debug):
            print('\nEncrypt...')
            print('r => %s' % r)
            print('sig => %s' % sig)
            print("V'  =>", g_id ** r)
            print('enc_M => %s' % enc_M)
            group.debug(C)
        return C
    
    def decrypt(self, pk, sk, ct):
        U, V, W = ct['U'], ct['V'], ct['W']
        sig = V ^ h.hashToZn(pair(sk['id'], U))
        dec_M = W ^ h.hashToZn(sig)
        M = self.decodeFromZn(dec_M)

        r = h.hashToZr(sig, M)
        if(debug):
            print('\nDecrypt....')
            print('V   =>', V)
            print("V'  =>", pair(sk['id'], U))
            print('sig => %s' % sig)
            print('r => %s' % r)
        if U == r * pk['P']:
            if debug: print("Successful Decryption!!!")
            return M
        if debug: print("Decryption Failed!!!")
        return None

    def encodeToZn(self, message):
        assert type(message) == bytes, "Input must be of type bytes"
        return integer(message)
        
    def decodeFromZn(self, element):
        if type(element) == integer:
            msg = int2Bytes(element)
            return msg
        return None
     

