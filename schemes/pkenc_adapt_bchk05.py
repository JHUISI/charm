'''
Boneh-Canetti-Halevi-Katz Public Key Encryption, IBE-to-PKE transform

| From: "Improved Efficiency for CCA-Secure Cryptosystems Built Using Identity-Based Encryption", Section 4
| Published In: Topics in Cryptology in CTRSA 2005
| Available From: eprint.iacr.org/2004/261.pdf

:Author: Christina Garman
:Date: 12/2011
'''
from charm.engine.util import *
from toolbox.pairinggroup import *
from charm.pairing import hash as sha1
import hmac, hashlib, math
from toolbox.IBEnc import *
from schemes.encap_bchk05 import *
from schemes.ibenc_bb03 import *

debug = False
class BCHKIBEnc(IBEnc):
    def str_XOR(self, m, k):
        output = ""
        for character in m:
            for letter in k:
                if(not type(character) == int):
                    character = ord(character)
                if(not type(letter) == int):
                    letter = ord(letter)

                character = chr(character ^ letter)
            output += character
        return output

    def elmtToString(self, g, length):
        hash_len = 20
        b = math.ceil(length / hash_len)
        gStr = b''
        for i in range(1, b+1):
            gStr += sha1(g, i)
        return gStr[:length]
    
    def __init__(self, scheme, groupObj, encscheme):
        global ibenc, group, encap
        ibenc = scheme
        group = groupObj
        encap = encscheme

    def keygen(self):
        (PK, msk) = ibenc.setup()
        pub = encap.setup()
        pk = { 'PK':PK, 'pub':pub }
        sk = { 'msk': msk }
        return (pk, sk)

    def encrypt(self, pk, m):
        (k, ID, x) = encap.S(pk['pub'])

        ID2 = group.hash(ID, ZR)

        m2 = m + ':' + x

        kprime = group.random(GT)
        kprimeStr = self.elmtToString(kprime, len(m2))

        C1 = ibenc.encrypt(pk['PK'], ID2, kprime)

        C2 = self.str_XOR(m2, kprimeStr)
        C2 = C2.encode('utf-8')

        C1prime = pickleObject(serialize(C1, group))
        
        tag = hmac.new(k, C1prime+C2, hashlib.sha1).digest()
        
        cipher = { 'ID':ID, 'C1':C1, 'C2':C2, 'tag':tag }
        return cipher

    def decrypt(self, pk, sk, c):
        ID2 = group.hash(c['ID'], ZR)
        SK = ibenc.extract(sk['msk'], ID2)
        kprime = ibenc.decrypt(pk, SK, c['C1'])

        kprimeStr = self.elmtToString(kprime, len(c['C2']))

        m2 = self.str_XOR(c['C2'], kprimeStr)

        x = m2.split(':')[1]
        k = encap.R(pk['pub'], c['ID'], x)

        C1prime = pickleObject(serialize(c['C1'], group))
        
        if(c['tag'] == hmac.new(k, C1prime+c['C2'], hashlib.sha1).digest()):
            return m2.split(':')[0]
        else:
            return b'FALSE'
   
def main():
    groupObj = PairingGroup('../param/a.param')
    ibe = IBE_BB04(groupObj)
    encap = EncapBCHK()
    
    hyb_ibe = BCHKIBEnc(ibe, groupObj, encap)
    
    (pk, sk) = hyb_ibe.keygen()
    if debug:
        print("pk => ", pk)
        print("sk => ", sk)

    msg = "Hello World!"
    
    ct = hyb_ibe.encrypt(pk, msg)
    if debug:
        print("\nCiphertext")
        print("C1 =>", ct['C1'])
        print("C2 =>", ct['C2'])
        print("tag =>", ct['tag'])

    orig_msg = hyb_ibe.decrypt(pk, sk, ct)
    assert orig_msg == msg
    if debug: print("Successful Decryption!!! =>", orig_msg)
    del groupObj

if __name__ == "__main__":
    debug = True
    main()
