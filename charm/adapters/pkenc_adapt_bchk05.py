'''
Boneh-Canetti-Halevi-Katz Public Key Encryption, IBE-to-PKE transform

| From: "Improved Efficiency for CCA-Secure Cryptosystems Built Using Identity-Based Encryption", Section 4
| Published In: Topics in Cryptology in CTRSA 2005
| Available From: eprint.iacr.org/2004/261.pdf

:Author: Christina Garman
:Date: 12/2011
'''
from charm.core.engine.util import pickleObject, serializeObject 
import hmac, hashlib, math
from charm.schemes.ibenc.ibenc_bb03 import IBEnc, ZR, GT, sha2

debug = False
class BCHKIBEnc(IBEnc):
    """
    >>> from charm.schemes.encap_bchk05 import EncapBCHK 
    >>> from charm.schemes.ibenc.ibenc_bb03 import PairingGroup, IBE_BB04
    >>> group = PairingGroup('SS512')
    >>> ibe = IBE_BB04(group)
    >>> encap = EncapBCHK()
    >>> hyb_ibe = BCHKIBEnc(ibe, group, encap)
    >>> (public_key, secret_key) = hyb_ibe.keygen()
    >>> msg = b"Hello World!"
    >>> cipher_text = hyb_ibe.encrypt(public_key, msg)
    >>> decrypted_msg = hyb_ibe.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
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
            gStr += sha2(g, i)
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
        if type(m) != bytes:
           m = bytes(m, 'utf8')	
        if type(x) != bytes:
           x = bytes(x, 'utf8')	

        ID2 = group.hash(ID, ZR)

        m2 = m + b':' + x

        kprime = group.random(GT)
        kprimeStr = self.elmtToString(kprime, len(m2))

        C1 = ibenc.encrypt(pk['PK'], ID2, kprime)

        C2 = self.str_XOR(m2, kprimeStr)
        C2 = C2.encode('utf8')
        
        C1prime = pickleObject(serializeObject(C1, group))
        
        tag = hmac.new(k, C1prime+C2, hashlib.sha256).digest()
        
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

        C1prime = pickleObject(serializeObject(c['C1'], group))
        
        if(c['tag'] == hmac.new(k, C1prime+c['C2'], hashlib.sha256).digest()):
            return bytes(m2.split(':')[0], 'utf8')
        else:
            return b'FALSE'
   
