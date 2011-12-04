from toolbox.pairinggroup import *
from charm.integer import *
import hmac, hashlib, math
from toolbox.conversion import Conversion

debug = False
class EncapBCHK():
    def __init__(self):
        global H
        #H = md5.new()
        H = hashlib.sha1()

    def setup(self):
        pub = hashlib.md5()
        return pub

    def S(self, pub):
        print("In S")
        #x = random(448) #this should be 448 bits not (mod 448)
        #x = integer(randomBits(448))
        x = randomBits(448)
        x = str(x).zfill(135) 
        #x = int(str(x)[:56])
        print("x => ", x, type(x), str(x), len(str(x)))
        #xnew = group.init(ZR, x) #ish
        #xnew = serialize(x)
        #print("xnew => ", xnew)
        #pub.update(xnew)
        #r = pub.digest()
        r = hashlib.md5(x.encode('utf-8')).digest()
        #H.update(xnew)
        #com = H.digest()[:128]
        com = hashlib.sha1(x.encode('utf-8')).digest()[:128]
        #com = deserialize(com)
        dec = x
        #H.update(serialize(dec))
        #print(H.digest()[:128])
        print(r, com, dec)
        #return { 'r':r, 'com':com, 'dec':dec }
        return (r, com, dec)

    def R(self, pub, com, dec):
        print("In R")
        print(dec)
        #decnew = serialize(dec)
        print("decnew => ", dec, type(dec))
        #H.update(decnew)
        #x = H.digest()[:128]
        x = hashlib.sha1(str(dec).encode('utf-8')).digest()[:128]
        
        print(x, com)

        if(x == com):
            m = hashlib.md5(str(dec).encode('utf-8')).digest()
            #h.update(decnew)
            #m = h.digest()
            return m
        else:
            return b'FALSE'
    
def main():
    encap = EncapBCHK()

    hout = encap.setup()
    print("hout => ", hout)

    (r, com, dec) = encap.S(hout)
    print("sout => ", r, com, dec)

    rout = encap.R(hout, com, dec)
    
    if debug: print("recovered m =>", rout)

    assert r == rout
    if debug: print("Successful Decryption!!!")
    
if __name__ == "__main__":
    debug = True
    main()   
