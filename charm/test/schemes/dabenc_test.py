from charm.schemes.dabe_aw11 import Dabe
from charm.adapters.dabenc_adapt_hybrid import HybridABEncMA
from charm.toolbox.pairinggroup import PairingGroup, GT
import unittest

debug = False

class DabeTest(unittest.TestCase):
    def testDabe(self):
        groupObj = PairingGroup('SS512')

        dabe = Dabe(groupObj)
        GP = dabe.setup()

        #Setup an authority
        auth_attrs= ['ONE', 'TWO', 'THREE', 'FOUR']
        (SK, PK) = dabe.authsetup(GP, auth_attrs)
        if debug: print("Authority SK")
        if debug: print(SK)

        #Setup a user and give him some keys
        gid, K = "bob", {}
        usr_attrs = ['THREE', 'ONE', 'TWO']
        for i in usr_attrs: dabe.keygen(GP, SK, i, gid, K)
        if debug: print('User credential list: %s' % usr_attrs)    
        if debug: print("\nSecret key:")
        if debug: groupObj.debug(K)

        #Encrypt a random element in GT
        m = groupObj.random(GT)
        policy = '((one or three) and (TWO or FOUR))'
        if debug: print('Acces Policy: %s' % policy)
        CT = dabe.encrypt(PK, GP, m, policy)
        if debug: print("\nCiphertext...")
        if debug: groupObj.debug(CT)    
        
        orig_m = dabe.decrypt(GP, K, CT)
       
        assert m == orig_m, 'FAILED Decryption!!!' 
        if debug: print('Successful Decryption!')

class HybridABEncMATest(unittest.TestCase):
    def testHybridABEncMA(self):
        groupObj = PairingGroup('SS512')
        dabe = Dabe(groupObj)
            
        hyb_abema = HybridABEncMA(dabe, groupObj)
        
        #Setup global parameters for all new authorities
        gp = hyb_abema.setup()
        
        #Instantiate a few authorities 
        #Attribute names must be globally unique.  HybridABEncMA
        #Two authorities may not issue keys for the same attribute. 
        #Otherwise, the decryption algorithm will not know which private key to use   
        jhu_attributes = ['jhu.professor', 'jhu.staff', 'jhu.student']
        jhmi_attributes = ['jhmi.doctor', 'jhmi.nurse', 'jhmi.staff', 'jhmi.researcher']
        (jhuSK, jhuPK) = hyb_abema.authsetup(gp, jhu_attributes)
        (jhmiSK, jhmiPK) = hyb_abema.authsetup(gp, jhmi_attributes)
        allAuthPK = {}; allAuthPK.update(jhuPK); allAuthPK.update(jhmiPK)
        
        #Setup a user with a few keys
        bobs_gid = "20110615 bob@gmail.com cryptokey"
        K = {}
        hyb_abema.keygen(gp, jhuSK,'jhu.professor', bobs_gid, K)
        hyb_abema.keygen(gp, jhmiSK,'jhmi.researcher', bobs_gid, K)
        
        
        msg = b'Hello World, I am a sensitive record!'
        size = len(msg)
        policy_str = "(jhmi.doctor or (jhmi.researcher and jhu.professor))"
        ct = hyb_abema.encrypt(allAuthPK, gp, msg, policy_str)    

        if debug:
            print("Ciphertext")
            print("c1 =>", ct['c1'])
            print("c2 =>", ct['c2'])
        
        decrypted_msg = hyb_abema.decrypt(gp, K, ct)
        if debug: print("Result =>", decrypted_msg)
        assert decrypted_msg == msg, "Failed Decryption!!!"
        if debug: print("Successful Decryption!!!")
        del groupObj

if __name__ == "__main__":
    unittest.main()
