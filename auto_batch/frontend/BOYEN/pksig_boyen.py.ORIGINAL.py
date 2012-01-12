""" 
Xavier Boyen - Anonymous Ring Signatures

| From: "X. Boyen. Mesh Signatures: How to Leak a Secret with Unwitting and Unwilling Participants"
| Published in: EUROCRYPT 2007
| Available from: http://eprint.iacr.org/2007/094.pdf
| Notes: 

* type:           signature (ring-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011

"""
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string

debug = False

# need RingSig
class Boyen(PKSig):
    def __init__(self, groupObj):
        global group, debug
        group = groupObj
        debug = False
    
    def setup(self):
        global H
        H = lambda a: group.hash(('1', str(a)), ZR)
        g1, g2 = group.random(G1), group.random(G2)
        a = [group.random(ZR) for i in range(3)]
        A = []; At = [];
        for i in range(3):
            A.append(g1 ** a[i])
            At.append(g2 ** a[i])
        # public verification key "in the sky" for all users
        return {'g1':g1, 'g2':g2, 'A':A[0],    'B':A[1],   'C':A[2], 'At':At[0], 'Bt':At[1], 'Ct':At[2]}
    
    def keygen(self, mpk):
        a, b, c = group.random(ZR), group.random(ZR), group.random(ZR)
        A = mpk['g1'] ** a; B = mpk['g1'] ** b; C = mpk['g1'] ** c 
        At = mpk['g2'] ** a; Bt = mpk['g2'] ** b; Ct = mpk['g2'] ** c
        sk = {'a':a, 'b':b, 'c':c}
        pk = {'A':A, 'B':B, 'C':C, 'At':At, 'Bt':Bt, 'Ct':Ct}
        return (pk, sk)

    def getPKdict(self, mpk, pk, k):
        A_pk, B_pk, C_pk = {}, {}, {}
        A_pk[ 0 ] = mpk[ k[0] ]
        B_pk[ 0 ] = mpk[ k[1] ]
        C_pk[ 0 ] = mpk[ k[2] ]
        for i in pk.keys():
            A_pk[ i ] = pk[ i ][ k[0] ]
            B_pk[ i ] = pk[ i ][ k[1] ]
            C_pk[ i ] = pk[ i ][ k[2] ]        
        return A_pk, B_pk, C_pk
    
    def sign(self, mpk, pk, sk, M):
        if debug: print("Signing....")
        if debug: print("pk =>", pk.keys())
        (A_pk, B_pk, C_pk) = self.getPKdict(mpk, pk, ['A', 'B', 'C'])
        m = H(M)
        l = len(A_pk.keys())
        if debug: print("l defined as =>", l)        
        s = [group.random(ZR) for i in range(l-1)] # 0:l-1
        t = [group.random(ZR) for i in range(l)]
        S = {}
        for i in range(l-1):
            S[ i ] = mpk['g1'] ** s[i]
            #print("S[", i, "] :=", S[i])         
        # index=0
        (A, B, C) = A_pk[ 0 ], B_pk[ 0 ], C_pk[ 0 ]
        prod = (A * (B ** m) * (C ** t[0])) ** -s[0]
        
        # 1 -> l-1
        for i in range(1, l-1):
            (A, B, C) = A_pk[i], B_pk[i], C_pk[i]
            prod *= ((A * (B ** m) * (C ** t[i])) ** -s[i])            

        final = l-1
        d = (sk['a'] + (sk['b'] * m) + (sk['c'] * t[final]))  # s[l]
        S[final] = (mpk['g1'] * prod) ** ~d # S[l]
        if debug: print("S[", final, "] :=", S[final])
        sig = { 'S':S, 't':t }
        return sig
    
    def verify(self, mpk, pk, M, sig):
        if debug: print("Verifying...")
        At_pk, Bt_pk, Ct_pk = self.getPKdict(mpk, pk, ['At', 'Bt', 'Ct'])
        l = len(At_pk.keys())
        if debug: print("Length =>", l)
        D = pair(mpk['g1'], mpk['g2'])
        S, t = sig['S'], sig['t']
        m = H(M)
        prod_result = group.init(GT, 1)
        for i in range(l):
            prod_result *= pair(S[i], At_pk[i] * (Bt_pk[i] ** m) * (Ct_pk[i] ** t[i]))
        if debug: print("final result =>", prod_result)
        if debug: print("D =>", D )
        if prod_result == D:
            return True
        return False

def main():
    if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")


    groupObj = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
    boyen = Boyen(groupObj)
    mpk = boyen.setup()
    if debug: print("Pub parameters")
    if debug: print(mpk, "\n\n")
   
    num_signers = 3
    l = 3
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
    sig = boyen.sign(mpk, L_pk, sk, M)
    if debug: print("\nSignature...")
    if debug: print("sig =>", sig)

    assert boyen.verify(mpk, L_pk, M, sig), "invalid signature!"
    if debug: print("Verification successful!")


    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_mpk = open('mpk.charmPickle', 'wb')
    pick_mpk = pickleObject(serializeDict(mpk, groupObj))
    f_mpk.write(pick_mpk)
    f_mpk.close()

    f_pk = open('pk.charmPickle', 'wb')
    pick_pk = pickleObject(serializeDict(L_pk, groupObj))
    f_pk.write(pick_pk)
    f_pk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['mpk'] = 'mpk.charmPickle'
    validOutputDict[0]['pk'] = 'pk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['mpk'] = 'mpk.charmPickle'
    invalidOutputDict[0]['pk'] = 'pk.charmPickle'

    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['mpk'] = 'mpk.charmPickle'
            validOutputDict[index]['pk'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = boyen.sign(mpk, L_pk, sk, message)
        assert boyen.verify(mpk, L_pk, message, sig), "invalid signature!"

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['M'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sig'] = prefixName + str(index) + '_ValidSignature.charmPickle'

        pickle.dump(message, f_message)
        f_message.close()

        pick_sig = pickleObject(serializeDict(sig, groupObj))

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig

    dict_pickle = pickleObject(serializeDict(validOutputDict, groupObj))
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f

    for index in range(0, numInvalidMessages):
        print("here")
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['mpk'] = 'mpk.charmPickle'
            invalidOutputDict[index]['pk'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = boyen.sign(mpk, L_pk, sk, message)
        assert boyen.verify(mpk, L_pk, message, sig), "invalid signature!"

        f_message = open(prefixName + str(index) + '_InvalidMessage.pythonPickle', 'wb')
        invalidOutputDict[index]['M'] = prefixName + str(index) + '_InvalidMessage.pythonPickle'
        randomIndex = random.randint(0, (messageSize - 1))
        oldValue = message[randomIndex]
        newValue = random.choice(string.printable)
        while (newValue == oldValue):
            newValue = random.choice(string.printable)

        if (messageSize == 1):
            message = newValue
        elif (randomIndex != (messageSize -1) ):
            message = message[0:randomIndex] + newValue + message[(randomIndex + 1):messageSize]
        else:
            message = message[0:randomIndex] + newValue

        f_sig = open(prefixName + str(index) + '_InvalidSignature.charmPickle', 'wb')
        invalidOutputDict[index]['sig'] = prefixName + str(index) + '_InvalidSignature.charmPickle'

        pickle.dump(message, f_message)
        f_message.close()

        pick_sig = pickleObject(serializeDict(sig, groupObj))

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig

    dict_pickle = pickleObject(serializeDict(invalidOutputDict, groupObj))
    f = open(invalidOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f


if __name__ == "__main__":
    debug = True
    main()   
