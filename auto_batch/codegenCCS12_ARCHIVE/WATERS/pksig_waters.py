""" 
Waters - Identity-based signatures

| From: "B. Waters - Efficient identity-based encryption without random oracles"
| Published in: EUROCRYPT 2005
| Available from: Vol 3494 of LNCS, pages 320-329
| Notes: 

* type:           signature (ID-based)
* setting:        bilinear groups (asymmetric)

:Authors:    J. Ayo Akinyele
:Date:       11/2011
"""
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *

from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hashlib
import sys, random, string

debug = False

class WatersSig:
    def __init__(self, groupObj):
        global group,lam_func,hashObj,debug
        debug = False
        group = groupObj
        lam_func = lambda i,a,b: a[i] ** b[i]
        hashObj = hashlib.new('sha1')

    def sha1(self, message):
        h = hashObj.copy()
        h.update(bytes(message, 'utf-8'))
        return Bytes(h.digest())    

    def setup(self, z, l=32):
        alpha, h = group.random(ZR), group.random(G1)
        g1, g2 = group.random(G1), group.random(G2)
        A = pair(h, g2) ** alpha
        y = [group.random(ZR) for i in range(z)]
        y1t,y2t = group.random(ZR), group.random(ZR)

        u1t = g1 ** y1t; u2t = g1 ** y2t
        u = [g1 ** y[i] for i in range(z)]

        u1b = g2 ** y1t; u2b = g2 ** y2t
        ub =[g2 ** y[i] for i in range(z)]

        msk = h ** alpha
        mpk = {'g1':g1, 'g2':g2, 'A':A, 'u1t':u1t, 'u2t':u2t, 'u':u, 'u1b':u1b, 'u2b':u2b, 'ub':ub, 'z':z, 'l':l } 
        return (mpk, msk) 

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
    
    def keygen(self, mpk, msk, ID):
        if debug: print("Keygen alg...")
        k = self.strToId(mpk, ID) # return list from k1,...,kz
        if debug: print("k =>", k)
        r = group.random(ZR)
        k1 = msk * ((mpk['u1t'] * dotprod(group.init(G1), -1, mpk['z'], lam_func, mpk['u'], k)) ** r)  
        k2 = mpk['g1'] ** -r
        return (k1, k2)
    
    def sign(self, mpk, sk, M):
        if debug: print("Sign alg...")
        m = self.strToId(mpk, M) # return list from m1,...,mz
        if debug: print("m =>", m)
        (k1, k2) = sk
        s  = group.random(ZR)
        S1 = k1 * ((mpk['u2t'] * dotprod(group.init(G1), -1, mpk['z'], lam_func, mpk['u'], m)) ** s)
        S2 = k2
        S3 = mpk['g1'] ** -s
        return {'S1':S1, 'S2':S2, 'S3':S3}
    
    def verify(self, mpk, ID, M, sig):
        if debug: print("Verify...")
        k = self.strToId(mpk, ID)
        m = self.strToId(mpk, M)
        (S1, S2, S3) = sig['S1'], sig['S2'], sig['S3']
        A, g2 = mpk['A'], mpk['g2']
        comp1 = dotprod(group.init(G2), -1, mpk['z'], lam_func, mpk['ub'], k)
        comp2 = dotprod(group.init(G2), -1, mpk['z'], lam_func, mpk['ub'], m)
        if (pair(S1, g2) * pair(S2, mpk['u1b'] * comp1) * pair(S3, mpk['u2b'] * comp2)) == A: 
            return True
        return False

def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    #print("test")

    l = 5
    z = 5
    groupObj = PairingGroup(MNT160)

    waters = WatersSig(groupObj)
    (mpk, msk) = waters.setup(z)

    ID = 'janedoe@email.com'
    sk = waters.keygen(mpk, msk, ID)  
    if debug:
        print("Keygen...")
        print("sk =>", sk)
 
    M = 'please sign this new message!'
    sig = waters.sign(mpk, sk, M)
    if debug: print("Signature...")

    assert waters.verify(mpk, ID, M, sig), "invalid signature!"
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

    f_pk = open('ID.pythonPickle', 'wb')
    pickle.dump(ID, f_pk)
    f_pk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['mpk'] = 'mpk.charmPickle'
    validOutputDict[0]['ID'] = 'ID.pythonPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['mpk'] = 'mpk.charmPickle'
    invalidOutputDict[0]['ID'] = 'ID.pythonPickle'

    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['mpk'] = 'mpk.charmPickle'
            validOutputDict[index]['ID'] = 'ID.pythonPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = waters.sign(mpk, sk, message)
        assert waters.verify(mpk, ID, message, sig)

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
            invalidOutputDict[index]['ID'] = 'ID.pythonPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        sig = waters.sign(mpk, sk, message)
        assert waters.verify(mpk, ID, message, sig)

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
