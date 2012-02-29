""" 
Chow-Yiu-Hui - Identity-based ring signatures

| From: "S. Chow, S. Yiu and L. Hui - Efficient identity based ring signature."
| Published in: ACNS 2005
| Available from: Vol 3531 of LNCS, pages 499-512
| Notes: 

* type:           signature (ring-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from charm.engine.util import *
import sys, random, string

debug = False

class CYH(PKSig):
    def __init__(self, groupObj):
        global group, debug
        group = groupObj
        debug = False
    
    def concat(self, L_id):
        result = ""
        for i in L_id:
            result += ":"+i 
        return result

    def setup(self):
        global H1,H2,lam_func
        H1 = lambda x: group.hash(('1', str(x)), G1)
        H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
        lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
        g, alpha = group.random(G2), group.random(ZR)
        P = g ** alpha
        msk = alpha
        mpk = {'Pub':P, 'g':g }
        return (mpk, msk) 
    
    def keygen(self, msk, ID):
        sk = H1(ID) ** msk
        pk = H1(ID)
        return (ID, pk, sk)
    
    def sign(self, sk, L, M):
        (IDs, IDpk, IDsk) = sk
        assert IDs in L, "signer should be an element in L"
        Lt = self.concat(L) 
        l = len(L)
 
        u = [group.init(G1) for i in range(l)]
        h = [group.init(ZR, 1) for i in range(l)]
        for i in range(l):
            if IDs != L[i]:
                u[i] = group.random(G1)
                h[i] = H2(M, Lt, u[i])
            else:
                s = i
        
        r = group.random(ZR)
        pk = [ H1(i) for i in L] # get all signers pub keys
        u[s] = (IDpk ** r) * ~dotprod(group.init(G1), s, l, lam_func, u, pk, h)
        h[s] = H2(M, Lt, u[s])
        S = IDsk ** (h[s] + r)
        sig = { 'u':u, 'S':S }
        return sig
    
    def verify(self, mpk, L, M, sig):
        u, S = sig['u'], sig['S']
        Lt = self.concat(L) 
        l = len(L)
        h = [group.init(ZR, 1) for i in range(l)]
        for i in range(l):
            h[i] = H2(M, Lt, u[i])

        pk = [ H1(i) for i in L] # get all signers pub keys
        result = dotprod(group.init(G1), -1, l, lam_func, u, pk, h) 
        if pair(result, mpk['Pub']) == pair(S, mpk['g']):
            return True
        return False

def main():
    if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    L = [ "alice", "bob", "carlos", "dexter", "eddie"] 

    ID = "bob"
    groupObj = PairingGroup(MNT160)
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



    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_mpk = open('mpk.charmPickle', 'wb')
    pick_mpk = objectToBytes(mpk, groupObj)
    f_mpk.write(pick_mpk)
    f_mpk.close()

    f_pk = open('pk.charmPickle', 'wb')
    pick_pk = objectToBytes(L, groupObj)
    f_pk.write(pick_pk)
    f_pk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['mpk'] = 'mpk.charmPickle'
    validOutputDict[0]['L'] = 'pk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['mpk'] = 'mpk.charmPickle'
    invalidOutputDict[0]['L'] = 'pk.charmPickle'
  
    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['mpk'] = 'mpk.charmPickle'
            validOutputDict[index]['L'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cyh.sign(sk, L, message)
        assert cyh.verify(mpk, L, message, sig), "invalid signature!"

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['M'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sig'] = prefixName + str(index) + '_ValidSignature.charmPickle'
        
        pickle.dump(message, f_message)
        f_message.close()
        pick_sig = objectToBytes(sig, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig

    dict_pickle = objectToBytes(validOutputDict, groupObj)
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f


    for index in range(0, numInvalidMessages):
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['mpk'] = 'mpk.charmPickle'
            invalidOutputDict[index]['L'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cyh.sign(sk, L, message)
        assert cyh.verify(mpk, L, message, sig), "invalid signature!"

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

        pick_sig = objectToBytes(sig, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig
    
    dict_pickle = objectToBytes(invalidOutputDict, groupObj)
    f = open(invalidOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f


if __name__ == "__main__":
    debug = True
    main()
   
