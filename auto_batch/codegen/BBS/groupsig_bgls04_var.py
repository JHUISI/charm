'''
Dan Boneh, Xavier Boyen, and Hovav Shacham

| From: "Short Group Signatures
| Published in: CRYPTO 2004
| Available from: n/a
| Notes: An extended abstract of this paper appeared in Advances in Cryptology (2004)

* type:           digital signature scheme
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:           12/2010
'''
from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string

debug=False
class ShortSig(PKSig):
    def __init__(self, groupObj):
        PKSig.__init__(self)
        global group, debug
        group = groupObj
        debug = False
        
    def keygen(self, n):
        g1, g2 = group.random(G1), group.random(G2)
        h = group.random(G1)
        xi1, xi2 = group.random(), group.random()

        u,v = h ** ~xi1, h ** ~xi2
        gamma = group.random(ZR)
        w = g2 ** gamma
        gpk = { 'g1':g1, 'g2':g2, 'h':h, 'u':u, 'v':v, 'w':w }
        gmsk = { 'xi1':xi1, 'xi2':xi2 }
                
        x = [group.random(ZR) for i in range(n)]
        A = [gpk['g1'] ** ~(gamma + x[i]) for i in range(n)]
        gsk = {}
        if debug: print("\nSecret keys...")
        for i in range(n):
            if debug: print("User %d: A = %s, x = %s" % (i, A[i], x[i]))
            gsk[i] = (A[i], x[i]) 
        return (gpk, gmsk, gsk)
    
    def sign(self, gpk, gsk, M):
        alpha, beta = group.random(), group.random()
        A, x = gsk[0], gsk[1]
        T1 = gpk['u'] ** alpha
        T2 = gpk['v'] ** beta
        T3 = A * (gpk['h'] ** (alpha + beta))
        
        gamma1 = x * alpha
        gamma2 = x * beta
        r = [group.random() for i in range(5)]
         
        R1 = gpk['u'] ** r[0]
        R2 = gpk['v'] ** r[1]
        R3 = (pair(T3, gpk['g2']) ** r[2]) * (pair(gpk['h'], gpk['w']) ** (-r[0] - r[1])) * (pair(gpk['h'], gpk['g2']) ** (-r[3] - r[4]))
        R4 = (T1 ** r[2]) * (gpk['u'] ** -r[3])
        R5 = (T2 ** r[2]) * (gpk['v'] ** -r[4])
        
        c = group.hash((M, T1, T2, T3, R1, R2, R3, R4, R5), ZR)
        s1, s2 = r[0] + c * alpha, r[1] + c * beta
        s3, s4 = r[2] + c * x, r[3] + c * gamma1
        s5 = r[4] + c * gamma2
        return { 'T1':T1, 'T2':T2, 'T3':T3, 'R3':R3,'c':c, 's_alpha':s1, 's_beta':s2, 's_x':s3, 's_gamma1':s4, 's_gamma2':s5 }
    
    def verify(self, gpk, M, sigma):        
        """alternative verification check for BGLS04 which allows it to be batched"""
        c, T1, T2, T3 = sigma['c'], sigma['T1'], sigma['T2'], sigma['T3']
        salpha, sbeta = sigma['s_alpha'], sigma['s_beta']
        sx, sgamma1, sgamma2 = sigma['s_x'], sigma['s_gamma1'], sigma['s_gamma2']
        R3 = sigma['R3']
        
        R1 = (gpk['u'] ** salpha) * (T1 ** -c)
        R2 = (gpk['v'] ** sbeta) * (T2 ** -c)
        R4 = (T1 ** sx) * (gpk['u'] ** -sgamma1)
        R5 = (T2 ** sx) * (gpk['v'] ** -sgamma2)
        if c == group.hash((M, T1, T2, T3, R1, R2, R3, R4, R5), ZR):
            if debug: print("c => '%s'" % c)
            if debug: print("Valid Group Signature for message: '%s'" % M)
            pass
        else:
            if debug: print("Not a valid signature for message!!!")
            return False
        
        if ((pair(T3, gpk['g2']) ** sx) * (pair(gpk['h'],gpk['w']) ** (-salpha - sbeta)) * (pair(gpk['h'], gpk['g2']) ** (-sgamma1 - sgamma2)) * (pair(T3, gpk['w']) ** c) * (pair(gpk['g1'], gpk['g2']) ** -c) ) == R3: 
            return True
        else:
            return False
    
    def open(self, gpk, gmsk, M, sigma):
        t1, t2, t3, xi1, xi2 = sigma['T1'], sigma['T2'], sigma['T3'], gmsk['xi1'], gmsk['xi2']
        
        A_prime = t3 / ((t1 ** xi1) * (t2 ** xi2))
        return A_prime
        
def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    groupObj = PairingGroup(MNT160)
    n = 3    # how manu users in the group
    user = 1 # which user's key to sign a message with
    
    sigTest = ShortSig(groupObj)
    
    (gpk, gmsk, gsk) = sigTest.keygen(n)

    message = 'Hello World this is a message!'
    if debug: print("\n\nSign the following M: '%s'" % (message))
    
    signature = sigTest.sign(gpk, gsk[user], message)
    
    result = sigTest.verify(gpk, message, signature)
    #if result:
    #    print("Verify signers identity...")
    #    index = sigTest.open(gpk, gmsk, message, signature)
    #    i = 0
    #    while i < n:
    #        if gsk[i][0] == index:
    #            print('Found index of signer: %d' % i)
    #            print('A = %s' % index)
    #        i += 1
    assert result, "Signature Failed"
    if debug: print('Successful Verification!')

    '''
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_gpk = open('gpk.charmPickle', 'wb')
    pick_gpk = objectToBytes(gpk, groupObj)
    f_gpk.write(pick_gpk)
    f_gpk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['gpk'] = 'gpk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['gpk'] = 'gpk.charmPickle'

    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['gpk'] = 'gpk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        signature = sigTest.sign(gpk, gsk[user], message)
        assert sigTest.verify(gpk, message, signature)

        f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['M'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['sigma'] = prefixName + str(index) + '_ValidSignature.charmPickle'

        pickle.dump(message, f_message)
        f_message.close()

        pick_sig = objectToBytes(signature, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del signature
        del f_message
        del f_sig
        del pick_sig

    #print(validOutputDict)

    dict_pickle = objectToBytes(validOutputDict, groupObj)
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f

    for index in range(0, numInvalidMessages):
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['gpk'] = 'gpk.charmPickle'

        message = ""
        for randomChar in range(0, messageSize):
            message += random.choice(string.printable)

        signature = sigTest.sign(gpk, gsk[user], message)
        assert sigTest.verify(gpk, message, signature)

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
        invalidOutputDict[index]['sigma'] = prefixName + str(index) + '_InvalidSignature.charmPickle'

        pickle.dump(message, f_message)
        f_message.close()

        pick_sig = objectToBytes(signature, groupObj)

        f_sig.write(pick_sig)
        f_sig.close()

        del message
        del signature
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
