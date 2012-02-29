from toolbox.pairinggroup import *
from toolbox.PKSig import *
from toolbox.iterate import dotprod
from charm.engine.util import *
import sys, random, string
from math import *

class CDH(PKSig):
    def __init__(self, groupObj):
        global group
        group = groupObj

    def ceilog(self, value):
        return group.init(ZR, ceil(log(value, 2)))
        
    def setup(self):
        s = 0
        g1, a = group.random(G1), group.random(ZR)
        g2 = group.random(G2)
        A = g2 ** a
        u, v, d = group.random(G1), group.random(G1), group.random(G1)
        U = pair(u, A)
        V = pair(v, A)
        D = pair(d, A)
        w, z, h = group.random(ZR), group.random(ZR), group.random(ZR)
        w1, w2 = g1 ** w, g2 ** w
        z1, z2 = g1 ** z, g2 ** z
        h1, h2 = g1 ** h, g2 ** h
        pk = {'U':U, 'V':V, 'D':D, 'g1':g1, 'g2':g2, 'A':A,  
              'w1':w1, 'w2':w2, 'z1':z1, 'z2':z2, 
              'h1':h1, 'h2':h2, 'u':u, 'v':v, 'd':d, 's':s }
        sk = {'a':a }
        return (pk, sk)
    
    def sign(self, pk, sk, s, msg):
        s += 1
        S = group.init(ZR, s)
        #print("S =>", S)
        M = group.hash(msg, ZR)
        r, t = group.random(ZR), group.random(ZR)
        sigma1a = ((pk['u'] ** M) * (pk['v'] ** r) * pk['d']) ** sk['a']
        sigma1b = ((pk['w1'] ** self.ceilog(s)) * (pk['z1'] ** S) * pk['h1']) ** t
        sigma1 =  sigma1a * sigma1b
        sigma2 = pk['g1'] ** t
        
        return { 1:sigma1, 2:sigma2, 'r':r, 'i':s }
        
    def verify(self, pk, msg, sig):
        M = group.hash(msg, ZR)
        sigma1, sigma2 = sig[1], sig[2]
        r, s = sig['r'], sig['i']
        S = group.init(ZR, s)        
        U, V, D = pk['U'], pk['V'], pk['D']
        rhs_pair = pair(sigma2, (pk['w2'] * self.ceilog(s)) * (pk['z2'] ** S) * pk['h2'])
        
        if( pair(sigma1, pk['g2']) == (U ** M) * (V ** r) * D * rhs_pair ):
            return True
        else:
            return False
        
if __name__ == "__main__":
    if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    groupObj = PairingGroup(MNT160)
    cdh = CDH(groupObj)
    
    (pk, sk) = cdh.setup()

    m = "please sign this message now please!"    

    sig = cdh.sign(pk, sk, pk['s'], m)
    assert cdh.verify(pk, m, sig), "invalid signature"


    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_pk = open('pk.charmPickle', 'wb')
    pick_pk = objectToBytes(pk, groupObj)
    f_pk.write(pick_pk)
    f_pk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['pk'] = 'pk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['pk'] = 'pk.charmPickle'
  
    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['pk'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cdh.sign(pk, sk, pk['s'], message)
        assert cdh.verify(pk, message, sig), "invalid signature"

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['msg'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

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
            invalidOutputDict[index]['pk'] = 'pk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = cdh.sign(pk, sk, pk['s'], message)
        assert cdh.verify(pk, message, sig), "invalid signature"

        f_message = open(prefixName + str(index) + '_InvalidMessage.pythonPickle', 'wb')
        invalidOutputDict[index]['msg'] = prefixName + str(index) + '_InvalidMessage.pythonPickle'
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
