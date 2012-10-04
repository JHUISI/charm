""" 
Jae Choon Cha and Jung Hee Cheon - Identity-based Signatures

| From: "J. Cha and J. Choen - An identity-based signature from gap Diffie-Hellman groups."
| Published in: PKC 2003
| Available from: Vol. 2567. LNCS, pages 18-30
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from charm.toolbox.pairinggroup import *
from charm.toolbox.PKSig import PKSig
from charm.core.engine.util import *
import sys, random, string

debug = False

class CHCH(PKSig):
    def __init__(self, groupObj):
        global group, debug
        group = groupObj
        debug = False
        
    def setup(self):
        #global H1,H2
        #H1 = lambda x,t: group.hash(x, G1)
        #H2 = lambda x,y,t: group.hash((x,y), ZR)
        g2 = group.random(G2)
        alpha = group.random(ZR)
        P = g2 ** alpha 
        mpk = {'P':P, 'g2':g2}
        return (mpk, alpha)

    def keygen(self, alpha, ID):
        sk = group.hash(ID, G1) ** alpha
        pk = group.hash(ID, G1)
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        if debug: print("sign...")
        s = group.random(ZR)
        S1 = pk ** s
        a = group.hash((M, S1), ZR)
        S2 = sk ** (s + a)
        sig = {'S1':S1, 'S2':S2}
        return sig
    
    def verify(self, mpk, pk, M, sig):
        if debug: print("verify...")
        a = group.hash((M, sig['S1']), ZR)
        if pair(sig['S2'], mpk['g2']) == pair(sig['S1'] * (pk ** a), mpk['P']): 
            return True
        return False

def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    groupObj = PairingGroup('MNT224') #MNT160)
    N = 100
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

    '''
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
    pick_pk = objectToBytes(pk, groupObj)
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

        sig = chch.sign(pk, sk, message)
        assert chch.verify(mpk, pk, message, sig)

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
            invalidOutputDict[index]['pk'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = chch.sign(pk, sk, message)
        assert chch.verify(mpk, pk, message, sig)

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
    '''

if __name__ == "__main__":
    debug = True
    main()
   
