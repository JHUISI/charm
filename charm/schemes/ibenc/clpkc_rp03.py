'''
Boneh-Boyen Identity Based Encryption
 
| From: "Certificateless Public Key Cryptography", Section 4.2
| Published in: Asiacrypt 2003
| Available from: https://eprint.iacr.org/2003/126.pdf
| Notes: T

* type:     encryption (identity-based)
* setting:  bilinear groups (symmetric)

:Authors:   Nikos Fotiou (https://www.fotiou.gr)
:Date:      7/2022
'''

from charm.toolbox.pairinggroup import PairingGroup, ZR,G1,G2,pair
from charm.core.math.integer import randomBits,integer,bitsize
from charm.toolbox.hash_module import Hash,int2Bytes,integer

debug = False
class CLPKC_RP03():

    def __init__(self, groupObj):
        
        global group, h
        group = groupObj
        h = Hash(group)
        
    def setup(self, secparam=None):
        P = group.random(G1)
        s = group.random(ZR)
        P0 = s*P
        params={'P':P, 'P0':P0}
        master_key = s
        return (params, master_key)
    
    def partial_private_key_extract(self, master_key, ID):
        QA = group.hash(ID, G1)
        DA = master_key * QA
        return DA

    '''
    DA = partial_private_key
    xA = secret_value
    '''
    def set_private_key(self, DA, xA):
        SA = xA*DA
        return SA
    '''
    xA = secret_value
    '''
    def set_public_key(self, params, xA):
        XA = xA*params['P']
        YA = xA*params['P0']
        PA = {'XA':XA, 'YA': YA}
        return PA

    def encrypt(self, params, M, ID, P): # check length to make sure it is within n bits
        QA = group.hash(ID, G1)
        g_id = pair(QA, P['YA']) 
        #choose σ = {0,1}^n where n is # bits
        sig = integer(randomBits(group.secparam))
        r = h.hashToZr(sig, M)
        enc_M = self.encodeToZn(M)
        if bitsize(enc_M) / 8 <= group.messageSize():
            C = { 'U':r * params['P'], 'V':sig ^ h.hashToZn(g_id ** r) , 'W':enc_M ^ h.hashToZn(sig) }
        else:
            print("Message cannot be encoded.")
            return None
        return C
    
    def decrypt(self, params, SA, C):
        U, V, W = C['U'], C['V'], C['W']
        sig = V ^ h.hashToZn(pair(SA, U))
        dec_M = W ^ h.hashToZn(sig)
        M = self.decodeFromZn(dec_M)

        r = h.hashToZr(sig, M)        
        if U == r * params['P']:
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


def main():
    group = PairingGroup('SS512', secparam=1024)
    clpkc = CLPKC_RP03(group)
    (params, master_key) = clpkc.setup()
    ID = 'user@email.com'
    partial_private_key = clpkc.partial_private_key_extract(master_key, ID)
    secret_value = group.random(ZR)
    private_key = clpkc.set_private_key(partial_private_key, secret_value)
    public_key = clpkc.set_public_key(params, secret_value)
    msg = b"hello world!!!!!"
    cipher_text = clpkc.encrypt(params, msg, ID, public_key)
    plain_text = clpkc.decrypt(params, private_key, cipher_text)
    print (plain_text)

if __name__=='__main__':
    main()