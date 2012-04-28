'''
Identity Based Signature
 
| From: "J. Camenisch, A. Lysyanskaya. Signature Schemes and Anonymous Credentials from Bilinear Maps"
| Published in: 2004
| Available from: http://www.cs.brown.edu/~anna/papers/cl04.pdf
| Notes: Scheme A on page 5 section 3.1.

* type:           signature (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       1/2012
'''
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string

debug = False

class CL04(PKSig):
    def __init__(self, groupObj):
        global group, debug
        group = groupObj
        debug = False
        
    def setup(self):
        g = group.random(G1)
        mpk = { 'g': g }
        return mpk
        
    def keygen(self, mpk):
        x, y = group.random(ZR), group.random(ZR)
        sk = { 'x':x, 'y':y }
        pk = { 'X':mpk['g'] ** x, 'Y': mpk['g'] ** y, 'g':mpk['g'] }        
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = group.random(G2)
        m = group.hash(M, ZR)
        sig = {'a':a, 'a_y':a ** sk['y'], 'a_xy':a ** (sk['x'] + (m * sk['x'] * sk['y'])) }
        return sig
    
    def verify(self, pk, M, sig):
        (a, b, c) = sig['a'], sig['a_y'], sig['a_xy']
        m = group.hash(M, ZR)
        if pair(pk['Y'], a) == pair(pk['g'], b) and (pair(pk['X'], a) * (pair(pk['X'], b) ** m)) == pair(pk['g'], c):
            return True
        return False
    
def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    #print("test")

    grp = PairingGroup(MNT160)
    cl = CL04(grp)
    
    mpk = cl.setup()
    
    (pk, sk) = cl.keygen(mpk)
    
    M = "Please sign this stupid message!"
    sig = cl.sign(pk, sk, M)
    
    result = cl.verify(pk, M, sig)
    assert result, "INVALID signature!"

    '''
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_mpk = open('mpk.charmPickle', 'wb')
    pick_mpk = objectToBytes(pk, grp)
    f_mpk.write(pick_mpk)
    f_mpk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['pk'] = 'mpk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['pk'] = 'mpk.charmPickle'

    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['pk'] = 'mpk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cl.sign(pk, sk, message)
        assert cl.verify(pk, message, sig)

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['M'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sig'] = prefixName + str(index) + '_ValidSignature.charmPickle'

        pickle.dump(message, f_message)
        f_message.close()

        pick_sig = objectToBytes(sig, grp)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig

    dict_pickle = objectToBytes(validOutputDict, grp)
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f

    for index in range(0, numInvalidMessages):
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['pk'] = 'mpk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cl.sign(pk, sk, message)
        assert cl.verify(pk, message, sig)

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

        pick_sig = objectToBytes(sig, grp)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del sig
        del f_message
        del f_sig
        del pick_sig

    dict_pickle = objectToBytes(invalidOutputDict, grp)
    f = open(invalidOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f
    '''

if __name__ == "__main__":
    main()
    
