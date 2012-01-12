""" TODO: Description of Scheme here.
"""
from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string

bodyKey = 'Body'

debug = False

class CHP(PKSig):
    def __init__(self, groupObj):
        global group, H
        group = groupObj
        
    def setup(self):
        global H,H3
        H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
        H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)
        g = group.random(G2) 
        return { 'g' : g }
    
    def keygen(self, mpk):
        alpha = group.random(ZR)
        sk = alpha
        pk = mpk['g'] ** alpha
        return (pk, sk)
    
    def sign(self, pk, sk, M):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        sig = (a ** sk) * (h ** (sk * b))        
        return sig
    
    def verify(self, mpk, pk, M, sig):
        a = H(1, M['t1'])
        h = H(2, M['t2'])
        b = H3(M['str'], M['t3'])
        if pair(sig, mpk['g']) == (pair(a, pk) * (pair(h, pk) ** b)):
            return True
        return False

if __name__ == "__main__":
	if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")
   
	groupObj = pairing(80)
	chp = CHP(groupObj)
	mpk = chp.setup()

	(pk, sk) = chp.keygen(mpk)  
  
	M = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':'this is the message'}
	sig = chp.sign(pk, sk, M)

	assert chp.verify(mpk, pk, M, sig), "invalid signature!"
   
	numValidMessages = int(sys.argv[1])
	numInvalidMessages = int(sys.argv[2])
	messageSize = int(sys.argv[3])
	prefixName = sys.argv[4]
	validOutputDictName = sys.argv[5]
	invalidOutputDictName = sys.argv[6]

	f_mpk = open('mpkCHP.charmPickle', 'wb')
	pick_mpk = pickleObject(serializeDict(mpk, group))
	f_mpk.write(pick_mpk)
	f_mpk.close()

	f_pk = open('pkCHP.charmPickle', 'wb')
	pick_pk = pickleObject(serializeDict(pk, group))
	f_pk.write(pick_pk)
	f_pk.close()

	validOutputDict = {}
	validOutputDict[0] = {}
	validOutputDict[0]['mpk'] = 'mpkCHP.charmPickle'
	validOutputDict[0]['pk'] = 'pkCHP.charmPickle'

	invalidOutputDict = {}
	invalidOutputDict[0] = {}
	invalidOutputDict[0]['mpk'] = 'mpkCHP.charmPickle'
	invalidOutputDict[0]['pk'] = 'pkCHP.charmPickle'

	for index in range(0, numValidMessages):
		if (index != 0):
			validOutputDict[index] = {}
			validOutputDict[index]['mpk'] = 'mpkCHP.charmPickle'
			validOutputDict[index]['pk'] = 'pkCHP.charmPickle'

		message = ""
		for randomChar in range(0, messageSize):
			message += random.choice(string.printable)

		message = { 't1':'time_1', 't2':'time_2', 't3':'time_3', 'str':message}

		sig = chp.sign(pk, sk, message)
		assert chp.verify(mpk, pk, message, sig)

		f_message = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
		validOutputDict[index]['message'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

		f_sig = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
		validOutputDict[index]['sig'] = prefixName + str(index) + '_ValidSignature.charmPickle'

		pickle.dump(message, f_message)
		f_message.close()

		pick_sig = pickleObject(serializeDict(sig, group))

		f_sig.write(pick_sig)
		f_sig.close()

		del message
		del sig
		del f_message
		del f_sig
		del pick_sig

	dict_pickle = pickleObject(serializeDict(validOutputDict, group))
	f = open(validOutputDictName, 'wb')
	f.write(dict_pickle)
	f.close()
	del dict_pickle
	del f

