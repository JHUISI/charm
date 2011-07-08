# Boneh-Franklin Identity Based Encryption (NEED TO REWRITE)
# 
# From: "D. Boneh, M. Franklin Identity-Based Encryption from the Weil Pairing", Section 4.2.
# Published in: Crypto 2003
# Available from: http://.../bfibe.pdf
# Notes: This is the IBE .
#
# type:           encryption (identity-based)
# setting:        bilinear groups (asymmetric)
#
# Implementer:    Joseph Ayo Akinyele
# Date:            2/2011

from toolbox.pairinggroup import *
from toolbox.hash_module import *
from toolbox.IBEnc import *
import binascii

debug = False
class IBE_BonehFranklin(IBEnc):
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        global group,h,ZN
        group = groupObj
        h = Hash('sha1', group.Pairing)
        ZN = -1
        
    def setup(self):
        s, P = group.random(), group.random(G2)
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
        k = { 'id':d_ID }
        if(debug):
            print("Key for id => '%s'" % ID)
            group.debug(k)
        return k
        
    
    def encrypt(self, pk, ID, M): # check length to make sure it is within n bits
        Q_id = group.hash(ID, G1) #standard
        g_id = pair(Q_id, pk['P2']) 
        #choose sig = {0,1}^n where n is # bits
        sig = group.random(ZN)
        r = h.hashToZr(sig, M) # hash Long, Str => not working yet. (DONE)


        enc_M = self.encodeToZn(M)
        if group.validSize(enc_M):
            C = { 'U':r * pk['P'], 'V':sig ^ h.hashToZn(g_id ** r) , 'W':enc_M ^ h.hashToZn(sig) }
        else:
            print("Message cannot be encoded.")
            return None

        if(debug):
            print('\nEncrypt...')
            print('r => %s' % r)
            print('sig => %s' % sig)
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
            print('r => %s' % r)
            print('sig => %s' % sig)
            if U == r * pk['P']:
                print("Decryption successful!!!")
                return M
            print("Decryption Failed!!!")
        return None

    #TODO: should encode be able to handle elements from GT or just strings?
    def encodeToZn(self, message):
        #print("Message =>", message)
        hex_val = binascii.b2a_hex(bytes(message, 'utf8'))
        #print("hex val =>", hex_val)
        # convert message to uint here
        return int(hex_val, 16)
    
    def decodeFromZn(self, element):
        if type(element) == int:
            val_hex = hex(element)
            str_hex = val_hex[2:].strip('L')
            return binascii.a2b_hex(str_hex)
        # take element and map it back to what? how?
        return None

def main():
    groupObj = PairingGroup('d224.param', 1024)    
    ibe = IBE_BonehFranklin(groupObj)
    
    (pk, sk) = ibe.setup()
    
    id = 'ayo@email.com'
    key = ibe.extract(sk, id)
    
    m = "hello world!!"
    ciphertext = ibe.encrypt(pk, id, m)

    msg = ibe.decrypt(pk, key, ciphertext)
    assert msg == m
        
if __name__ == "__main__":
    debug = True
    main()
