from charm.integer import randomBits
import hmac, hashlib, math
from toolbox.conversion import Conversion

debug = False
class EncapBCHK():
    def __init__(self):
        global H
        H = hashlib.sha1()

    def setup(self):
        pub = hashlib.md5()
        return pub

    def S(self, pub):
        x = randomBits(448)
        x = str(x).zfill(135) 

        r = hashlib.md5(x.encode('utf-8')).digest()

        com = hashlib.sha1(x.encode('utf-8')).digest()[:128]

        dec = x

        return (r, com, dec)

    def R(self, pub, com, dec):
        x = hashlib.sha1(str(dec).encode('utf-8')).digest()[:128]
        
        if(x == com):
            m = hashlib.md5(str(dec).encode('utf-8')).digest()
            return m
        else:
            return b'FALSE'
    
def main():
    encap = EncapBCHK()

    hout = encap.setup()

    (r, com, dec) = encap.S(hout)

    rout = encap.R(hout, com, dec)
    
    if debug: print("recovered m =>", rout)

    assert r == rout
    if debug: print("Successful Decryption!!!")
    
if __name__ == "__main__":
    debug = True
    main()   
