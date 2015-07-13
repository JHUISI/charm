'''
Xuanxia Yao, Zhi Chen, Ye Tian
 
| From: A lightweight attribute-based encryption scheme for the Internet of things
| Published in: Future Generation Computer Systems
| Available From: http://www.sciencedirect.com/science/article/pii/S0167739X14002039
| Notes: 

* type:           key-policy attribute-based encryption (public key)
* setting:        No Pairing

:Authors:    artjomb
:Date:       10/2014
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_lsw08 import KPabe
from charm.core.math.pairing import hashPair as extractor

from time import clock

debug = False
class EKPabe(ABEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> group = PairingGroup('MNT224')
    >>> kpabe = EKPabe(group)
    >>> attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]
    >>> (master_public_key, master_key) = kpabe.setup(attributes)
    >>> policy = '(ONE or THREE) and (THREE or TWO)'
    >>> secret_key = kpabe.keygen(master_public_key, master_key, policy)
    >>> msg = b"Some Random Message"
    >>> cipher_text = kpabe.encrypt(master_public_key, msg, attributes)
    >>> decrypted_msg = kpabe.decrypt(cipher_text, secret_key)
    >>> decrypted_msg == msg
    True
    """

    def __init__(self, groupObj, verbose=False):
        ABEnc.__init__(self)
        global group, util
        group = groupObj
        util = SecretUtil(group, verbose)        

    def setup(self, attributes):
        s = group.random(ZR)
        g = group.random(G1)
        
        self.attributeSecrets = {}
        self.attribute = {}
        for attr in attributes:
            si = group.random(ZR)
            self.attributeSecrets[attr] = si
            self.attribute[attr] = g**si
        return (g**s, s) # (pk, mk)
    
    def keygen(self, pk, mk, policy_str):
        policy = util.createPolicy(policy_str)
        attr_list = util.getAttributeList(policy)
        
        s = mk
        shares = util.calculateSharesDict(s, policy)
        
        d = {}
        D = { 'policy': policy_str, 'Du': d }
        for x in attr_list:
            y = util.strip_index(x)
            d[y] = shares[x]/self.attributeSecrets[y]
            if debug: print(str(y) + " d[y] " + str(d[y]))
        if debug: print("Access Policy for key: %s" % policy)
        if debug: print("Attribute list: %s" % attr_list)
        return D
    
    def encrypt(self, pk, M, attr_list): 
        if debug: print('Encryption Algorithm...')
        k = group.random(ZR);
        Cs = pk ** k
        
        Ci = {}
        for attr in attr_list:
            Ci[attr] = self.attribute[attr] ** k
        
        symcrypt = SymmetricCryptoAbstraction(extractor(Cs))
        C = symcrypt.encrypt(M)
        
        return { 'C': C, 'Ci': Ci, 'attributes': attr_list }
    
    def decrypt(self, C, D):
        policy = util.createPolicy(D['policy'])
        attrs = util.prune(policy, C['attributes'])
        if attrs == False:
            return False
        coeff = util.getCoefficients(policy)
        
        Z = {}
        prodT = 1
        for i in range(len(attrs)):
            x = attrs[i].getAttribute()
            y = attrs[i].getAttributeAndIndex()
            Z[y] = C['Ci'][x] ** D['Du'][x]
            prodT *= Z[y] ** coeff[y]
        
        symcrypt = SymmetricCryptoAbstraction(extractor(prodT))
        
        return symcrypt.decrypt(C['C'])

def main():
    groupObj = PairingGroup('MNT224')
    kpabe = EKPabe(groupObj)

    attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]

    (pk, mk) = kpabe.setup(attributes)

    # policy = '(ONE or THREE) and (THREE or TWO)'
    policy = 'THREE and (ONE or TWO)'
    msg = b"Some Random Message"

    mykey = kpabe.keygen(pk, mk, policy)

    if debug: print("Encrypt under these attributes: ", attributes)
    ciphertext = kpabe.encrypt(pk, msg, attributes)
    if debug: print(ciphertext)

    rec_msg = kpabe.decrypt(ciphertext, mykey)
    assert rec_msg
    if debug: print("rec_msg=%s" % str(rec_msg))

    assert msg == rec_msg
    if debug: print("Successful Decryption!")

def benchmark():
    groupObj1 = PairingGroup('MNT224')
    groupObj2 = PairingGroup('MNT224')
    ekpabe = EKPabe(groupObj1)
    kpabe = KPabe(groupObj2)
    
    t1_s = 0
    t1_k = 0
    t1_e = 0
    t1_d = 0
    t2_s = 0
    t2_k = 0
    t2_e = 0
    t2_d = 0

    attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]
    policy = 'THREE and (ONE or TWO)'
    msg1 = b"Some Random Message"
    msg2 = groupObj2.random(GT)

    for b in range(4):
        start = clock()
        (epk, emk) = ekpabe.setup(attributes)
        t1_s += clock() - start
        
        start = clock()
        (pk, mk) = kpabe.setup()
        t2_s += clock() - start

        start = clock()
        emykey = ekpabe.keygen(epk, emk, policy)
        t1_k += clock() - start
        
        start = clock()
        mykey = kpabe.keygen(pk, mk, policy)
        t2_k += clock() - start
        
        for i in range(50):
            start = clock()
            eciphertext = ekpabe.encrypt(epk, msg1, attributes)
            t1_e += clock() - start
            
            start = clock()
            ciphertext = kpabe.encrypt(pk, msg2, attributes)
            t2_e += clock() - start
            
            start = clock()
            erec_msg = ekpabe.decrypt(eciphertext, emykey)
            t1_d += clock() - start
            
            start = clock()
            rec_msg = kpabe.decrypt(ciphertext, mykey)
            t2_d += clock() - start

            assert msg1 == erec_msg
            assert msg2 == rec_msg
    
    print ("yct14 s=%s k=%s e=%s d=%s" % (t1_s, t1_k, t1_e, t1_d))
    print ("lsw08 s=%s k=%s e=%s d=%s" % (t2_s, t2_k, t2_e, t2_d))
    
    # Result in VM:
    # yct14 s=0.1 k=0.02 e=3.44 d=2.91
    # lsw08 s=0.42 k=0.41 e=10.32 d=21.25

if __name__ == "__main__":
    # debug = True
    # main()
    benchmark()
