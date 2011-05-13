from toolbox.pairinggroup import *
from toolbox.IBEnc import *
from ibe_bb03 import *

class HashIDAdapter(IBEnc):
    def __init__(self, scheme, group):
        IBEnc.__init__(self)
        self.group = group
        self.ibe_good = False
        # validate that we have the appropriate object
        
        if IBEnc.checkProperty(self, scheme, {'scheme':self.baseSchemeTypes.IBEnc, 
                                        'secdef':self.baseSecDefs.IND_sID_CPA, 
                                        'id':ZR}):
            self.ibenc = scheme
            # change our property as well
            IBEnc.setProperty(self, secdef='IND_ID_CPA', other={'id':str}, secmodel='ROM')
            # check message space?
            self.ibe_good = True

        if not self.ibe_good:
            assert False, "ibe object does not satisfy requirements."

    def setup(self):
        if not self.ibe_good: return IBEnc.setup(self)
        return self.ibenc.setup()

    def extract(self, mk, ID):
        if not self.ibe_good: return IBEnc.extract(self, mk, ID)
        if type(ID) == str:
            ID2 = self.group.hash(ID)
            return self.ibenc.extract(mk, ID2)
        else:
            assert False, "invalid type on ID."
    
    def encrypt(self, pk, ID, msg):
        if not self.ibe_good: return IBEnc.encrypt(self, pk, ID, msg)
        return self.ibenc.encrypt(pk, ID, msg)

    def decrypt(self, pk, sk, ct):
        if not self.ibe_good: return IBEnc.decrypt(self, pk, sk, ct)
        return self.ibenc.decrypt(pk, sk, ct)
    
if __name__ == "__main__":
    group = PairingGroup('a.param')
    
    ibe = IBE_BB04(group)
    
    hashID = HashIDAdapter(ibe, group)
    
    (pk, mk) = hashID.setup()
    
    kID = 'waldoayo@email.com'
    sk = hashID.extract(mk, kID)
    print("Keygen for %s" % kID)
    print(sk)
    
    m = group.random(GT)
    ct = hashID.encrypt(pk, sk['id'], m)
    
    orig_m = hashID.decrypt(pk, sk, ct)
    
    if m == orig_m:
        print("Successful Decryption!!!")
        print("Result =>", orig_m)
    else:
        print("FAILED Decryption!")
    
        
