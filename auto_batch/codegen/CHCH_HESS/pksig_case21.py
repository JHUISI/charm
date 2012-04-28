""" 
Hess and ChCh - Identity-based Signatures

| From: "Hess - Efficient identity based signature schemes based on pairings."
| Published in: Selected Areas in Cryptography
| Available from: Vol. 2595. LNCS, pages 310-324
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from schemes.pksig_hess import Hess
from schemes.pksig_chch import CHCH

debug = False

class ComboScheme(PKSig):
    def __init__(self, groupObj):
        global H2, group, debug
        group = groupObj
        debug = False
        H2 = lambda x,y: group.hash((x,y), ZR)
            
    def verify(self, mpk, pk, M, sig):
        sig1, sig2 = sig['sig_hess'], sig['sig_chch']
        S1h, S2h = sig1['S1'], sig1['S2']
        S1c, S2c = sig2['S1'], sig2['S2']
        ah = H2(M, S1h)
        ac = H2(M, S1c)
        if pair(S2h, mpk['g2']) == (pair(pk, mpk['P']) ** ah) * S1h and pair(S2c, mpk['g2']) == pair(S1c * (pk ** ac), mpk['P']):                 
            return True
        return False
        
def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")
   
    groupObj = PairingGroup(MNT160)
    hess = Hess(groupObj)
    chch = CHCH(groupObj)
    combo = ComboScheme(groupObj)
   
    (mpk, msk) = chch.setup()

    _id = "janedoe@email.com"
    (pk, sk) = chch.keygen(msk, _id)
 
    M = "this is a message! twice!" 
    sig1 = hess.sign(mpk, sk, M)
    sig2 = chch.sign(pk, sk, M)
    sig = { 'sig_hess':sig1, 'sig_chch':sig2 }
   
    result = combo.verify(mpk, pk, M, sig)

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

        sig1 = hess.sign(mpk, sk, message)
        sig2 = chch.sign(pk, sk, message)
        sig = { 'sig_hess':sig1, 'sig_chch':sig2 }
        assert combo.verify(mpk, pk, message, sig)

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

        sig1 = hess.sign(mpk, sk, message)
        sig2 = chch.sign(pk, sk, message)
        sig = { 'sig_hess':sig1, 'sig_chch':sig2 }
        assert combo.verify(mpk, pk, message, sig)

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
    debug = False
    main()
