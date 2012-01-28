'''
Boneh-Gentry-Lynn-Shacham Aggregate Signature
 
| From: "D. Boneh, C. Gentry, B. Lynn, H. Shacham Aggregate and Verifiably Encrypted Signatures From Bilinear Maps"
| Published in: EUROCRYPT 2003
| Available from: http://

* type:           signature (aggregate)
* setting:        bilinear groups (asymmetric)

:Authors:    Matthew W. Pagano, building upon the BLS scheme authored by J. Ayo Akinyele
:Date:       1/2012
'''
from charm.engine.util import *
from toolbox.pairinggroup import *
import sys, random, string

debug = False
class BGLS():
    def __init__(self, groupObj):
        global group, g2, debug
        group = groupObj
        g2 = group.random(G2)
        debug = False
            
    def keygen(self, secparam=None):
        x = group.random()
        g_x = g2 ** x
        pk = { 'g^x':g_x, 'g2':g2, 'identity':str(g_x), 'secparam':secparam }
        sk = { 'x':x }
        return (pk, sk)
        
    def sign(self, x, message):
        return group.hash(message, G1) ** x

    def aggregate(self, sigList):
        sig = group.init(G1, 1)

        for index in range(0, len(sigList)):
            sig = sig * sigList[index]

        return sig

    def verifyIndividual(self, pk, sig, message):
        h = group.hash(message, G1)
        if pair(sig, pk['g2']) == pair(h, pk['g^x']):
            return True  
        return False 

    def verify(self, pk, sig, M):
        rightSideProduct = group.init(GT, 1)

        for index in range(0, len(M)):
            h = group.hash(M[index], G1)
            rightSideProduct = rightSideProduct * pair(h, pk[index]['g^x'])

        if pair(sig, pk[0]['g2']) == rightSideProduct:
            return True
        return False

def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    groupObj = PairingGroup('/Users/matt/Documents/charm/param/d224.param')

    l = 5

    bgls = BGLS(groupObj)

    '''
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    validOutputDict = {}

    for i in range(0, numValidMessages):
        pk = []
        message = []
        sigList = []

        for j in range(0, l):
            (pkTemp, skTemp) = bgls.keygen(0)
            pk.append(pkTemp)

            messageTemp = ""

            for randomChar in range(0, messageSize):
                messageTemp = messageTemp + random.choice(string.printable)

            message.append(messageTemp)

            sigTemp = bgls.sign(skTemp['x'], message[j])
            sigList.append(sigTemp)
            assert bgls.verifyIndividual(pk[j], sigList[j], message[j])

        sig = bgls.aggregate(sigList)
        assert bgls.verify(pk, sig, message)

        f_pk = open(prefixName + str(i) + '_ValidPK.charmPickle', 'wb')
        pick_pk = objectToBytes(pk, groupObj)
        f_pk.write(pick_pk)
        f_pk.close()

        validOutputDict[i] = {}

        validOutputDict[i]['pk'] = prefixName + str(i) + '_ValidPK.charmPickle'

        f_sig = open(prefixName + str(i) + '_ValidSignature.charmPickle', 'wb')
        pick_sig = objectToBytes(sig, groupObj)
        f_sig.write(pick_sig)
        f_sig.close()

        validOutputDict[i]['sig'] = prefixName + str(i) + '_ValidSignature.charmPickle'

        f_M = open(prefixName + str(i) + '_ValidMessage.pythonPickle', 'wb')
        pickle.dump(message, f_M)
        f_M.close()

        validOutputDict[i]['M'] = prefixName + str(i) + '_ValidMessage.pythonPickle'

    dict_pickle = objectToBytes(validOutputDict, groupObj)
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()

    invalidOutputDict = {}

    for i in range(0, numInvalidMessages):
        pk = []
        message = []
        sigList = []

        for j in range(0, l):
            (pkTemp, skTemp) = bgls.keygen(0)
            pk.append(pkTemp)

            messageTemp = ""

            for randomChar in range(0, messageSize):
                messageTemp = messageTemp + random.choice(string.printable)

            message.append(messageTemp)

            sigTemp = bgls.sign(skTemp['x'], message[j])
            sigList.append(sigTemp)
            assert bgls.verifyIndividual(pk[j], sigList[j], message[j])

        sig = bgls.aggregate(sigList)
        assert bgls.verify(pk, sig, message)

        f_pk = open(prefixName + str(i) + '_InvalidPK.charmPickle', 'wb')
        pick_pk = objectToBytes(pk, groupObj)
        f_pk.write(pick_pk)
        f_pk.close()

        invalidOutputDict[i] = {}

        invalidOutputDict[i]['pk'] = prefixName + str(i) + '_invalidPK.charmPickle'

        f_sig = open(prefixName + str(i) + '_invalidSignature.charmPickle', 'wb')
        pick_sig = objectToBytes(sig, groupObj)
        f_sig.write(pick_sig)
        f_sig.close()

        invalidOutputDict[i]['sig'] = prefixName + str(i) + '_invalidSignature.charmPickle'

        randomListIndex = random.randint(0, (l - 1) )
        randomIndex = random.randint(0, (messageSize - 1))
        oldValue = message[randomListIndex][randomIndex]
        newValue = random.choice(string.printable)
        while (newValue == oldValue):
            newValue = random.choice(string.printable)

        if (messageSize == 1):
            message[randomListIndex] = newValue
        elif (randomIndex != (messageSize -1) ):
            message[randomListIndex] = message[randomListIndex][0:randomIndex] + newValue + message[randomListIndex][(randomIndex + 1):messageSize]
        else:
            message[randomListIndex] = message[randomListIndex][0:randomIndex] + newValue

        f_M = open(prefixName + str(i) + '_invalidMessage.pythonPickle', 'wb')
        pickle.dump(message, f_M)
        f_M.close()

        invalidOutputDict[i]['M'] = prefixName + str(i) + '_invalidMessage.pythonPickle'

    dict_pickle = objectToBytes(invalidOutputDict, groupObj)
    f = open(invalidOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    '''
    
if __name__ == "__main__":
    debug = False
    main()
    
