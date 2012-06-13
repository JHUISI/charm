from schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.toolbox.IBEnc import IBEnc
from charm.toolbox.pairinggroup import *

debug = False
class HashIDAdapter(IBEnc):
    """
    >>> group = PairingGroup('SS512')
    >>> ibe = IBE_BB04(group)
    >>> hashID = HashIDAdapter(ibe, group)
    >>> (public_key, master_key) = hashID.setup()
    >>> ID = 'waldoayo@email.com'
    >>> secret_key = hashID.extract(master_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = hashID.encrypt(public_key, ID, msg)
    >>> orig_msg = hashID.decrypt(public_key, secret_key, cipher_text)
    >>> msg == orig_msg
    True
    """
    def __init__(self, scheme, group):
        IBEnc.__init__(self)
        self.group = group
        self.ibe_good = False
        # validate that we have the appropriate object
        
        if IBEnc.checkProperty(self, scheme, {'scheme':self.baseSchemeTypes.IBEnc, 
                                        'secdef':self.baseSecDefs.sIND_ID_CPA, 
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

