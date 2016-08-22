from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import *

debug = False
class HashIDAdapter(IBEnc):
    """
    >>> from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
    >>> group = PairingGroup('SS512')
    >>> ibe = IBE_BB04(group)
    >>> hashID = HashIDAdapter(ibe, group)
    >>> (master_public_key, master_key) = hashID.setup()
    >>> ID = 'john.doe@example.com'
    >>> secret_key = hashID.extract(master_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = hashID.encrypt(master_public_key, ID, msg)
    >>> decrypted_msg = hashID.decrypt(master_public_key, secret_key, cipher_text)
    >>> msg == decrypted_msg
    True
    """
    def __init__(self, scheme, group):
        global ibe
        IBEnc.__init__(self)
        self.group = group
        ibe = None
        # validate that we have the appropriate object
        criteria = [('secDef', IND_sID_CPA), ('scheme', 'IBEnc'), ('secModel', SM), ('id',ZR)]
        if IBEnc.checkProperty(self, scheme, criteria):
            # change our property as well
            IBEnc.updateProperty(self, scheme, secDef=IND_ID_CPA, id=str, secModel=ROM)
            ibe = scheme
            #IBEnc.printProperties(self)
        else:
            assert False, "Input scheme does not satisfy adapter properties: %s" % criteria

    def setup(self):
        assert ibe != None, "IBEnc alg not set"
        return ibe.setup()

    def extract(self, mk, ID):
        assert ibe != None, "IBEnc alg not set"
        if type(ID) in [str, bytes]:
            ID2 = self.group.hash(ID)
            sk = ibe.extract(mk, ID2); sk['IDstr'] = ID
            return sk
        else:
            assert False, "invalid type on ID."
    
    def encrypt(self, pk, ID, msg):
        assert ibe != None, "IBEnc alg not set"        
        if type(ID) in [str, bytes]:
            ID2 = self.group.hash(ID)
            return ibe.encrypt(pk, ID2, msg)
        else:
            assert False, "invalid type on ID."

    def decrypt(self, pk, sk, ct):
        assert ibe != None, "IBEnc alg not set"        
        return ibe.decrypt(pk, sk, ct)

