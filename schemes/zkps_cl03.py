from charm.integer import *
from schemes.commit_cl03 import *
from schemes.pksig_cl03 import *

class ZKP_CL03(PKSig):
    def __init__(self, lmin=160, secparam=512):
        global ln, lm, le, l
        ln = 2 * secparam
        lm = lmin

    def inputCalc(self, pks, pkc, pkcx, Cx, x, rx, sig):
        w = integer(randomBits(ln))
        rs = integer(randomBits(ln))
        re = integer(randomBits(ln))
        rw = integer(randomBits(ln))
        rz = integer(randomBits(ln))
        r = integer(randomBits(ln))

        g = pkc['g']
        h = pkc['h']
        n = pks['N']

        Cs = ((g ** sig['s']) * (h ** rs)) % n
        Ce = ((g ** sig['e']) * (h ** re)) % n
        Cv = (sig['v'] * (g ** w)) % n
        Cw = ((g ** w) * (h ** rw))
        z = ((g ** sig['s']) * (h ** rs)) % n
        Cz = ((g ** z) * (h ** rz))
        C = ((Cv ** sig['e']) * (h ** r)) % n

        #Cv = (sig['v'] * (pks['g'] ** w)) % pks['N']
        #Cw = (pks['g'] ** w) * (pks['h'] ** rw)

        r2 = { 'w':w, 'rs':rs, 're':re, 'rw':rw, 'rz':rz, 'r':r, 'z':z }
        C2 = { 'Cs':Cs, 'Ce':Ce, 'Cv':Cv, 'Cw':Cw, 'Cz':Cz, 'C':C }

        return (r2, C2)      

    def verifier(self, pks, pkc, pkcx, Cx, x, rx, sig, C, r):
        #if(not (pks['c'] == (inputs['Cv'] ** sig['e']) * ((1/pks['a']) ** x) * ((1/pks['b']) ** sig['s']) * ((1/pkc['g']) ** inputs['w']))):
        #    return False
        #if(not (inputs['Cw'] == (pkc['g'] ** inputs['w']))):

        g = pkc['g']
        h = pkc['h']
        n = pks['N']

        if(not (C['C'] == ((C['Cv'] ** sig['e']) * (h ** r['r'])))):
            print("stmt 1")
            return False

        if(not (C['Ce'] == ((g ** sig['e']) * (h ** r['re'])))):
            print("stmt 2")
            return False

        if(not (C['C']/pks['c'] == (pks['a'] ** x) * (pks['b'] ** sig['s']) * (g ** r['z']) * (h ** r['r']))):
            print("stmt 3")
            return False

        if(not (Cx == (g ** x) * (h ** rx))):
            print("stmt 4")
            return False

        if(not (C['Cs'] == ((g ** sig['s']) * (h ** r['rs'])))):
            print("stmt 5")
            return False

        if(not (C['Cz'] == ((g ** r['z']) * (h ** r['rz'])))):
            print("stmt 6")
            return False

        if(not (C['C'] == ((C['Cv'] ** sig['e']) * (h ** r['r'])))):
            print("stmt 7")
            return False

        if(not (C['Cz'] == ((g ** r['z']) * (h ** r['rz'])))):
            print("stmt 8")
            return False

        if(not (C['Cw'] == ((g ** r['w']) * (h ** r['rw'])))):
            print("stmt 9")
            return False

        if(not (C['Ce'] == ((g ** sig['e']) * (h ** r['re'])))):
            print("stmt 10")
            return False

        if(not (C['Cz'] == (C['Cw'] ** sig['e']) *(h ** (r['rz'] - sig['e']*r['rw'])))):
            print("stmt 11")
            return False

        return True

if __name__ == "__main__":
    signature = Sig_CL03()
    commitment = CM_CL03()
    zkp = ZKP_CL03()

    (pks, sks) = signature.keygen(512)
    print("Public parameters...")
    print("pk =>", pks)
    print("sk =>", sks)
    
    m = integer(SHA1(b'this is the message I want to hash.'))
    sig = signature.sign(pks, sks, m)
    print("Signature...")
    print("sig =>", sig)

    pkc = commitment.setup(1024, sks['p'], sks['q'])
    print("Public parameters...")
    print("pk =>", pkc)
    
    r = integer(randomBits(1024)) % pkc['N']
    if debug: print("Commiting to => ", m, r)
    c = commitment.commit(pkc, m, r)

    (r2, C2) = zkp.inputCalc(pks, pkc, pkc, c, m, r, sig)

    assert zkp.verifier(pks, pkc, pkc, c, m, r, sig, C2, r2), "FAILED VERIFICATION!!!"
    print("ZKP Success!!!")

