""" 
Camenisch-Hohenberger-Pedersen - Identity-based Signatures

| From: "Camenisch, S. Hohenberger, M. Pedersen - Batch Verification of short signatures."
| Published in: EUROCRYPT 2007
| Available from: http://epring.iacr.org/2007/172.pdf
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

class CHP(PKSig):
    def __init__(self, groupObj):
        global group, H, debug
        group = groupObj
        debug = False
        
    def setup(self):
        global H,H3
        H = lambda prefix,x,t: group.hash( (str(prefix), str(x)), G1 )
        H3 = lambda a,b,t: group.hash( ('3', str(a), str(b)), ZR )
        g = group.random(G2) 
        mpk = { 'g' : g }
        return mpk
    
    def keygen(self, mpk):
        alpha = group.random(ZR)
        sk = alpha
        pk = mpk['g'] ** alpha
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H(1, M['t1'], G1)
        h = H(2, M['t2'], G1)
        b = H3(M['str'], M['t3'], ZR)
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, mpk, pk, M, sig):
        a = H(1, M['t1'], G1)
        h = H(2, M['t2'], G1)
        b = H3(M['str'], M['t3'], ZR)
        if pair(sig, mpk['g']) == (pair(a, pk) * (pair(h, pk) ** b)):
            return True
        return False

def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")
   
    groupObj = PairingGroup('MNT224') #MNT160)
    N = 100
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

        M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':message}

        sig = chp.sign(pk, sk, M)
        assert chp.verify(mpk, pk, M, sig), "invalid signature!"
       
        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['M'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sig'] = prefixName + str(index) + '_ValidSignature.charmPickle'
        
        pickle.dump(M, f_message)
        f_message.close()

        pick_sig = objectToBytes(sig, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del M
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

        M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':message}

        sig = chp.sign(pk, sk, M)
        assert chp.verify(mpk, pk, M, sig), "invalid signature!"

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

        M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':message}

        pickle.dump(M, f_message)
        f_message.close()

        pick_sig = objectToBytes(sig, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del M
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
    debug = False
    main()
