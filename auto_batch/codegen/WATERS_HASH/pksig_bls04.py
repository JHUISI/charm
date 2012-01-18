from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from charm.engine.util import *
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import sys, random, string
import hashlib

debug = False
class IBSig():
    def __init__(self, groupObj):
        global group, debug, hashObj
        group = groupObj
        debug = False
        hashObj = hashlib.new('sha1')
        
    def dump(self, obj):
        ser_a = serializeDict(obj, group)
        return str(pickleObject(ser_a))

    def sha1(self, message):
        h = hashObj.copy()
        h.update(bytes(message, 'utf-8'))
        return Bytes(h.digest()) 
            
    def strToId(self, pk, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        hash = self.sha1(strID)
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header

        v=[]
        for i in range(pk['z']):  #z must be greater than or equal to 1
            binsubstr = bstr[pk['l']*i : pk['l']*(i+1)]
            intval = int(binsubstr, 2)
            intelement = group.init(ZR, intval)
            v.append(intelement)
        return v

    def setup(self, z=5, l=32):
        global lam_func
        lam_func = lambda i,a,b: a[i] ** b[i]
        g1 = group.random(G1)
        y = [group.random(ZR) for i in range(z)]
        u = [g1 ** y[i] for i in range(z)]
        mpk = { 'u0': g1, 'u':u, 'z':z, 'l':l }
        return mpk

    def keygen(self, secparam=None):
        g1 = group.random(G1)
        g, x = group.random(G2), group.random()
        g_x = g ** x
        pk = { 'g^x':g_x, 'g':g, 'identity':str(g_x), 'secparam':secparam }
        sk = { 'x':x }
        return (pk, sk)
        
    def sign(self, mpk, x, message):
        M = self.strToId(mpk, message)
        #print("M :=", M)
        #M = message
        #sig1 = group.hash(M, G1) ** x
        if debug: print("Message => '%s'" % M)
        sig1 = (mpk['u0'] * dotprod(1, -1, mpk['z'], lam_func, mpk['u'], M)) ** x
        #print("sig1 :=", sig1)
        sig2 = group.random()
        sig = {}
        sig['sig1'] = sig1
        sig['sig2'] = sig2
        return sig
        
    def verify(self, mpk, pk, sigDict, message):
        #M = message
        #h = group.hash(M, G1)
        M = self.strToId(mpk, message)
        #print("M :=", M)
        h = mpk['u0'] * dotprod(1, -1, mpk['z'], lam_func, mpk['u'], M)
        #print("h :=", h)
        sig = sigDict['sig1']
        t = sigDict['sig2']

        if pair(sig, (pk['g'] ** t)) == (pair(h, pk['g^x']) ** t):
            return True  
        return False 

def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    #groupObj = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
    groupObj = PairingGroup('d224.param')
    
    #m = { 'a':"hello world!!!" , 'b':"test message" }
    z = 5
    m = "rest"
    bls = IBSig(groupObj)

    mpk = bls.setup(z)
    
    (pk, sk) = bls.keygen(0)
    
    sig = bls.sign(mpk, sk['x'], m)
    
    if debug: print("Message: '%s'" % m)
    if debug: print("Signature: '%s'" % sig)     
    assert bls.verify(mpk, pk, sig, m), "Failure!!!"
    result = bls.verify(mpk, pk, sig, m)
    print(result)
    if debug: print('SUCCESS!!!')

    '''
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_mpk = open('mpk.charmPickle', 'wb')
    pick_mpk = pickleObject(serializeDict(pk, groupObj))
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

        sig = bls.sign(sk['x'], message)
        assert bls.verify(pk, sig, message)

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['message'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sigDict'] = prefixName + str(index) + '_ValidSignature.charmPickle'

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
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['pk'] = 'mpk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = bls.sign(sk['x'], message)
        assert bls.verify(pk, sig, message)

        f_message = open(prefixName + str(index) + '_InvalidMessage.pythonPickle', 'wb')
        invalidOutputDict[index]['message'] = prefixName + str(index) + '_InvalidMessage.pythonPickle'
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
        invalidOutputDict[index]['sigDict'] = prefixName + str(index) + '_InvalidSignature.charmPickle'

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
    '''

if __name__ == "__main__":
    debug = False
    main()
    
