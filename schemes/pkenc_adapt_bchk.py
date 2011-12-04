'''
| From: "Improved Efficiency for CCA-Secure Cryptosystems Built Using Identity-Based Encryption", Section 4
| Available From: eprint.iacr.org/2004/261.pdf

:Author: Christina Garman
:Date: 12/2011
'''
from charm.engine.util import *
from toolbox.pairinggroup import *
from charm.integer import *
import hmac, hashlib, math
from toolbox.IBEnc import *
from charm.cryptobase import *
from schemes.encap_bchk import *
from schemes.ibenc_bb03 import *

debug = False
class BCHKIBEnc(IBEnc):
    def __init__(self, scheme, groupObj, encscheme):
        global ibenc, group, encap
        ibenc = scheme
        group = groupObj
        encap = encscheme
        #mac = macscheme

    def keygen(self):
        (PK, msk) = ibenc.setup()
        pub = encap.setup()
        pk = { 'PK':PK, 'pub':pub }
        sk = { 'msk': msk }
        return (pk, sk)

    def encrypt(self, pk, m):
        (k, ID, x) = encap.S(pk['pub'])
        print("m => ", m, m+str(x), len(m+str(x)))
        print("x => ", x)
        print("ID => ", ID, type(ID))
        ID2 = group.hash(ID, ZR)

        m2 = m+x

        kprime = group.random(GT)
        kprimeStr = group.serialize(kprime)

        print("kprimeStr => ", kprimeStr, len(kprimeStr))

        #kprimeInt = randomBits(len(m2)*8)
        #kprime = str(kprimeInt).encode('utf-8')[:len(m2)]
        #test = group.deserialize(kprime)
        print("kprime => ", kprime, type(kprime))
        #kprime2 = group.hash(kprime, G1)

        C1 = ibenc.encrypt(pk['PK'], ID2, kprime)
        print("C1 => ", C1)

        C2 = ""
        for character in m2:
            for letter in kprimeStr:
                #print(character, type(character))
                #print(letter, type(letter))
                if(not type(character) == int):
                    character = ord(character)
                elif(not type(letter) == int):
                    letter = ord(letter)

                character = chr(character ^ letter)
            C2 += character

        #C2 = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in (kprime, (m+str(x))))

        #C2 = int(kprime) ^ int(m+str(x))
        C2 = C2.encode('utf-8')
        print("C2 => ", C2, type(C2), len(C2))
        #print(C2.encode('utf-8'))

        C1prime = pickleObject(serializeDict(C1, group))
        print("Cprime => ", C1prime)
        tag = hmac.new(k, C1prime+C2, hashlib.sha1).digest()
        print("tag => ", tag)
        cipher = { 'ID':ID, 'C1':C1, 'C2':C2, 'tag':tag }

        return cipher

    def decrypt(self, pk, sk, c):
        ID2 = group.hash(c['ID'], ZR)
        SK = ibenc.extract(sk['msk'], ID2)
        print("SK => ", SK)
        kprime = ibenc.decrypt(pk, SK, c['C1'])
        print("kprime => ", kprime)

        kprimeStr = group.serialize(kprime)

        #m2 = c['C2'] ^ kprime

        m2 = ""
        for character in c['C2']:
            for letter in kprimeStr:
                #print(character, type(character))
                #print(letter, type(letter))
                if(not type(character) == int):
                    character = ord(character)
                elif(not type(letter) == int):
                    letter = ord(letter)

                character = chr(character ^ letter)
            m2 += character

        print("m2 => ", m2)

        x = m2[-135:]
        print("x => ", x)

        k = encap.R(pk['pub'], c['ID'], x) # does SK = dec???
        print("k => ", k)

        C1prime = pickleObject(serializeDict(c['C1'], group))
        print("C1prime => ", C1prime)
        if(c['tag'] == hmac.new(k, C1prime+c['C2'], hashlib.sha1).digest()):
            return m2[:-135]
        else:
            return b'FALSE'
   
def main():
    groupObj = PairingGroup('../param/a.param')
    ibe = IBE_BB04(groupObj)
    encap = EncapBCHK()
    
    hyb_ibe = BCHKIBEnc(ibe, groupObj, encap)
    
    (pk, sk) = hyb_ibe.keygen()

    msg = "Hello World!"
    
    ct = hyb_ibe.encrypt(pk, msg)
    if debug:
        print("Ciphertext")
        print("c1 =>", ct['C1'])
        print("c2 =>", ct['C2'])
        print("tag =>", ct['tag'])

    print(ct['C2'], type(ct['C2']))
    
    orig_msg = hyb_ibe.decrypt(pk, sk, ct)
    assert orig_msg == msg
    if debug: print("Successful Decryption!!! =>", orig_msg)
    print(msg)
    del groupObj

if __name__ == "__main__":
    debug = True
    main()
