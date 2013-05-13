from charm.adapters.pksig_adapt_naor01 import Sig_Generic_ibetosig_Naor01
from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.schemes.pksig.pksig_bls04 import BLS01
from charm.schemes.pksig.pksig_boyen import Boyen
from charm.schemes.pksig.pksig_chch import CHCH
from charm.schemes.pksig.pksig_chp import CHP
from charm.schemes.pksig.pksig_cl03 import Sig_CL03, SHA1
from charm.schemes.pksig.pksig_cl04 import CL04
from charm.schemes.pksig.pksig_cyh import CYH
from charm.schemes.pksig.pksig_dsa import DSA
from charm.schemes.pksig.pksig_ecdsa import ECDSA
from charm.schemes.pksig.pksig_hess import Hess
from charm.schemes.pksig.pksig_hw import HW
from charm.schemes.pksig.pksig_rsa_hw09 import Sig_RSA_Stateless_HW09
from charm.schemes.pksig.pksig_schnorr91 import SchnorrSig
from charm.schemes.pksig.pksig_waters05 import IBE_N04_Sig
from charm.schemes.pksig.pksig_waters09 import IBEWaters09
from charm.schemes.pksig.pksig_waters import WatersSig
from charm.toolbox.pairinggroup import PairingGroup, ZR
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import prime192v2
from charm.toolbox.integergroup import integer
from charm.toolbox.hash_module import Waters
import unittest
#import pytest
debug = False

class PKSig_Naor01Test(unittest.TestCase):
    def testPKSig_Naor01(self):
        groupObj = PairingGroup('MNT224')
        
        ibe = IBE_BB04(groupObj)
        
        hashID = HashIDAdapter(ibe, groupObj)
        ibsig = Sig_Generic_ibetosig_Naor01(hashID, groupObj)

        (mpk, msk) = ibsig.keygen()
        
        M = "I want a signature on this message!"

        sigma = ibsig.sign(msk, M)
        if debug: print("\nMessage =>", M)
        if debug: print("Sigma =>", sigma)
        
        assert ibsig.verify(mpk, M, sigma), "Failed Verification!!!"
        if debug: print("Successful Verification!!!")
        del groupObj

class BLS01Test(unittest.TestCase):
    def testBLS04(self):
        groupObj = PairingGroup('MNT224')
        
        m = { 'a':"hello world!!!" , 'b':"test message" }
        bls = BLS01(groupObj)
        
        (pk, sk) = bls.keygen(0)
        
        sig = bls.sign(sk['x'], m)
        
        if debug: print("Message: '%s'" % m)
        if debug: print("Signature: '%s'" % sig)     
        assert bls.verify(pk, sig, m), "Failure!!!"
        if debug: print('SUCCESS!!!')

class BoyenTest(unittest.TestCase):
    def testBoyen(self):
       groupObj = PairingGroup('MNT224')
       #groupObj = PairingGroup(MNT160)
       boyen = Boyen(groupObj)
       mpk = boyen.setup()
       if debug: print("Pub parameters")
       if debug: print(mpk, "\n\n")
       
       num_signers = 3
       L_keys = [ boyen.keygen(mpk) for i in range(num_signers)]     
       L_pk = {}; L_sk = {}
       for i in range(len(L_keys)):
           L_pk[ i+1 ] = L_keys[ i ][ 0 ] # pk
           L_sk[ i+1 ] = L_keys[ i ][ 1 ]

       if debug: print("Keygen...")
       if debug: print("sec keys =>", L_sk.keys(),"\n", L_sk) 

       signer = 3
       sk = L_sk[signer] 
       M = 'please sign this new message!'
       sig = boyen.sign(signer, mpk, L_pk, sk, M)
       if debug: print("\nSignature...")
       if debug: print("sig =>", sig)

       assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

class CHCHTest(unittest.TestCase):
    def testCHCH(self):
       groupObj = PairingGroup('SS512')
       chch = CHCH(groupObj)
       (mpk, msk) = chch.setup()

       _id = "janedoe@email.com"
       (pk, sk) = chch.keygen(msk, _id)  
       if debug:
        print("Keygen...")
        print("pk =>", pk)
        print("sk =>", sk)
     
       M = "this is a message!" 
       sig = chch.sign(pk, sk, M)
       if debug:
        print("Signature...")
        print("sig =>", sig)

       assert chch.verify(mpk, pk, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

class CHPTest(unittest.TestCase):
    def testCHP(self):
       groupObj = PairingGroup('SS512')
       chp = CHP(groupObj)
       mpk = chp.setup()

       (pk, sk) = chp.keygen(mpk) 
       if debug: 
        print("Keygen...")
        print("pk =>", pk)
        print("sk =>", sk)
      
       M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message'}
       sig = chp.sign(pk, sk, M)
       if debug:
        print("Signature...")
        print("sig =>", sig)

       assert chp.verify(mpk, pk, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

class CL03Test(unittest.TestCase):
    def testCL03(self):
        pksig = Sig_CL03() 

        p = integer(21281327767482252741932894893985715222965623124768085901716557791820905647984944443933101657552322341359898014680608292582311911954091137905079983298534519)
        q = integer(25806791860198780216123533220157510131833627659100364815258741328806284055493647951841418122944864389129382151632630375439181728665686745203837140362092027)

        (pk, sk) = pksig.keygen(1024, p, q)
        if debug:
            print("Public parameters...")
            print("pk =>", pk)
            print("sk =>", sk)
        
        m = integer(SHA1(b'This is the message I want to hash.'))
        sig = pksig.sign(pk, sk, m)
        if debug:
            print("Signature...")
            print("sig =>", sig)
        
        assert pksig.verify(pk, m, sig), "FAILED VERIFICATION!!!"
        if debug: print("Successful Verification!!!")

class CL04Test(unittest.TestCase):
    def testCL04(self):
        grp = PairingGroup('MNT224')
        cl = CL04(grp)
        
        mpk = cl.setup()
        
        (pk, sk) = cl.keygen(mpk)
        if debug:
            print("Keygen...")
            print("pk :=", pk)
            print("sk :=", sk)
        
        M = "Please sign this stupid message!"
        sig = cl.sign(pk, sk, M)
        if debug: print("Signature: ", sig)
        
        result = cl.verify(pk, M, sig)
        assert result, "INVALID signature!"
        if debug: print("Successful Verification!!!")

class CYHTest(unittest.TestCase):
    def testCYH(self):
       L = [ "alice", "bob", "carlos", "dexter", "eddie"] 
       ID = "bob"
       groupObj = PairingGroup('SS512')
       cyh = CYH(groupObj)
       (mpk, msk) = cyh.setup()

       (ID, Pk, Sk) = cyh.keygen(msk, ID)  
       sk = (ID, Pk, Sk)
       if debug:
        print("Keygen...")
        print("sk =>", sk)
      
       M = 'please sign this new message!'
       sig = cyh.sign(sk, L, M)
       if debug:
        print("Signature...")
        print("sig =>", sig)

       assert cyh.verify(mpk, L, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

class DSATest(unittest.TestCase):
    def testDSA(self):
        p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
        q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)    
        dsa = DSA(p, q)

        (pk, sk) = dsa.keygen(1024)
        m = "hello world test message!!!"
        sig = dsa.sign(pk, sk, m)

        assert dsa.verify(pk, sig, m), "Failed verification!"
        if debug: print("Signature Verified!!!")

class ECDSATest(unittest.TestCase):
    def testECDSA(self):
        groupObj = ECGroup(prime192v2)
        ecdsa = ECDSA(groupObj)
        
        (pk, sk) = ecdsa.keygen(0)
        m = "hello world! this is a test message."

        sig = ecdsa.sign(pk, sk, m)
        assert ecdsa.verify(pk, sig, m), "Failed verification!"
        if debug: print("Signature Verified!!!")

class HessTest(unittest.TestCase):
    def testHess(self):
       groupObj = PairingGroup('SS512')
       chch = Hess(groupObj)
       (mpk, msk) = chch.setup()

       _id = "janedoe@email.com"
       (pk, sk) = chch.keygen(msk, _id)
       if debug:  
        print("Keygen...")
        print("pk =>", pk)
        print("sk =>", sk)
     
       M = "this is a message!" 
       sig = chch.sign(mpk, sk, M)
       if debug:
        print("Signature...")
        print("sig =>", sig)

       assert chch.verify(mpk, pk, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

class HWTest(unittest.TestCase):
    def testHW(self):
        #AES_SECURITY = 80
        groupObj = PairingGroup('SS512')
        hw = HW(groupObj)
        
        (pk, sk) = hw.setup()
        if debug:
            print("Public parameters")
            print("pk =>", pk)

        m = "please sign this message now please!"    
        sig = hw.sign(pk, sk, pk['s'], m)
        if debug:
            print("Signature...")
            print("sig =>", sig)

        assert hw.verify(pk, m, sig), "invalid signature"
        if debug: print("Verification Successful!!")

#@pytest.mark.skpifif("1=1")
#class RSA_HW09Test(unittest.TestCase):
#    def testRSA_HW09(self):
#        pksig = Sig_RSA_Stateless_HW09() 
#        # fixed params for unit tests
#        p = integer(13075790812874903063868976368194105132206964291400106069285054021531242344673657224376055832139406140158530256050580761865568307154219348003780027259560207)
#        q = integer(12220150399144091059083151334113293594120344494042436487743750419696868216757186059428173175925369884682105191510729093971051869295857706815002710593321543)
#        (pk, sk) = pksig.keygen(1024, p, q)
#        if debug:
#            print("Public parameters...")
#            print("pk =>", pk)
#            print("sk =>", sk)
#        
#        m = SHA1(b'this is the message I want to hash.')
#        m2 = SHA1(b'please sign this message too!')
#        #m = b'This is a message to hash'
#        sig = pksig.sign(pk, sk, m)
#        if debug:
#            print("Signature...")
#            print("sig =>", sig)
#        sig2 = pksig.sign(pk, sk, m2)
#        if debug:
#            print("Signature 2...")
#            print("sig2 =>", sig2)
#        
#        assert pksig.verify(pk, m, sig), "FAILED VERIFICATION!!!"
#        assert pksig.verify(pk, m2, sig2), "FAILED VERIFICATION!!!"
#        if debug: print("Successful Verification!!!")

class SchnorrSigTest(unittest.TestCase):
    def testSchnorrSig(self):
        # test only parameters for p,q
        p = integer(156816585111264668689583680968857341596876961491501655859473581156994765485015490912709775771877391134974110808285244016265856659644360836326566918061490651852930016078015163968109160397122004869749553669499102243382571334855815358562585736488447912605222780091120196023676916968821094827532746274593222577067)
        q = integer(78408292555632334344791840484428670798438480745750827929736790578497382742507745456354887885938695567487055404142622008132928329822180418163283459030745325926465008039007581984054580198561002434874776834749551121691285667427907679281292868244223956302611390045560098011838458484410547413766373137296611288533)    
        pksig = SchnorrSig()
        
        pksig.params(p, q)
        
        (pk, sk) = pksig.keygen()
        
        M = "hello world."
        sig = pksig.sign(pk, sk, M)
        
        assert pksig.verify(pk, sig, M), "Failed verification!"
        if debug: print("Signature verified!!!!")

class IBE_N04_SigTest(unittest.TestCase):
    def testIBE_N04_Sig(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('SS512')
        waters = Waters(groupObj)
        ibe = IBE_N04_Sig(groupObj)
        (pk, sk) = ibe.keygen()

        # represents public identity
        M = "bob@mail.com"

        msg = waters.hash(M)
        sig = ibe.sign(pk, sk, msg)
        if debug:
            print("original msg => '%s'" % M)
            print("msg => '%s'" % msg)
            print("sig => '%s'" % sig)

        assert ibe.verify(pk, msg, sig), "Failed verification!"
        if debug: print("Successful Verification!!! msg => '%s'" % msg)

class IBEWaters09Test(unittest.TestCase):
    def testIBEWaters09(self):
        # scheme designed for symmetric billinear groups
        grp = PairingGroup('MNT224')
        
        ibe = IBEWaters09(grp)
        
        (mpk, msk) = ibe.keygen()
        
        m = "plese sign this message!!!!"
        sigma = ibe.sign(mpk, msk, m)
        if debug: print("Signature :=", sigma)
            
        assert ibe.verify(mpk, sigma, m), "Invalid Verification!!!!"
        if debug: print("Successful Individual Verification!")

class WatersSigTest(unittest.TestCase):
    def testWatersSig(self):
       z = 5
       groupObj = PairingGroup('SS512')

       waters = WatersSig(groupObj)
       (mpk, msk) = waters.setup(z)

       ID = 'janedoe@email.com'
       sk = waters.keygen(mpk, msk, ID)  
       if debug:
        print("Keygen...")
        print("sk =>", sk)
     
       M = 'please sign this new message!'
       sig = waters.sign(mpk, sk, M)
       if debug: print("Signature...")

       assert waters.verify(mpk, ID, M, sig), "invalid signature!"
       if debug: print("Verification successful!")

if __name__ == "__main__":
    unittest.main()
