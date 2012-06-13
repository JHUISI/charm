from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.crypto.cryptobase import *
from charm.core.math.pairing import hash as sha1
from math import ceil
from schemes.dabenc.dabe_aw11 import *
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.toolbox.pairinggroup import *

debug = False
class HybridABEncMA(ABEncMultiAuth):
    """
    >>> group = PairingGroup('SS512')
    >>> dabe = Dabe(group)
    >>> hyb_abema = HybridABEncMA(dabe, group)
    >>> global_parameters = hyb_abema.setup()
    
    >>> jhu_attributes = ['jhu.professor', 'jhu.staff', 'jhu.student']
    >>> jhmi_attributes = ['jhmi.doctor', 'jhmi.nurse', 'jhmi.staff', 'jhmi.researcher']
    >>> (jhu_secret_key, jhu_public_key) = hyb_abema.authsetup(global_parameters, jhu_attributes)
    >>> (jhmi_secret_key, jhmi_public_key) = hyb_abema.authsetup(global_parameters, jhmi_attributes)
    >>> allAuth_private_key = {}; 
    >>> allAuth_private_key.update(jhu_public_key); 
    >>> allAuth_private_key.update(jhmi_public_key)
    
    >>> ID = "20110615 bob@gmail.com cryptokey"
    >>> K = {}
    >>> hyb_abema.keygen(global_parameters, jhu_secret_key,'jhu.professor', ID, K)
    >>> hyb_abema.keygen(global_parameters, jhmi_secret_key,'jhmi.researcher', ID, K)
    
    
    >>> msg = 'Hello World, I am a sensitive record!'
    >>> size = len(msg)
    >>> policy_str = "(jhmi.doctor or (jhmi.researcher and jhu.professor))"
    >>> cipher_text = hyb_abema.encrypt(allAuth_private_key, global_parameters, msg, policy_str)    

    >>> hyb_abema.decrypt(global_parameters, K, cipher_text)
    'Hello World, I am a sensitive record!'
    """
    def __init__(self, scheme, groupObj):
        global abencma, group
        # check properties (TODO)
        abencma = scheme
        group = groupObj

    def setup(self):
        return abencma.setup()
    
    def authsetup(self, gp, attributes):
        return abencma.authsetup(gp, attributes)
    
    def keygen(self, gp, sk, i, gid, pkey):
        return abencma.keygen(gp, sk, i, gid, pkey)

    def encrypt(self, pk, gp, M, policy_str):
        if type(M) != str and type(policy_str) != str: raise "message and policy not right type!"        
        key = group.random(GT)
        c1 = abencma.encrypt(pk, gp, key, policy_str)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha1(key)) 
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, gp, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = abencma.decrypt(gp, sk, c1)
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        return cipher.decrypt(c2)
        
