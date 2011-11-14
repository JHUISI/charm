from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string

debug = False

class IBSig():
    def __init__(self):
        global group
        group = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
  
    def keygen(self, secparam=None):
        g = group.random(G2)
        x = group.random()
        g_x = g ** x
        pk = { 'g^x':g_x, 'g':g, 'identity':str(g_x), 'secparam':secparam }
        sk = { 'x':x }
        return (pk, sk)
        
    def sign(self, x, message):
        sig = group.hash(message, G1) ** x
        return sig
        
    def verify(self, pk, sig, message):
        A, B = pk, sig
        h = group.hash(message, G1)
        if pair(sig, pk['g']) == pair(h, pk['g^x']):
            return True  
        return False 

if __name__ == "__main__":
	if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

	numValidMessages = int(sys.argv[1])
	numInvalidMessages = int(sys.argv[2])
	messageSize = int(sys.argv[3])
	prefixName = sys.argv[4]
	validOutputDictName = sys.argv[5]
	invalidOutputDictName = sys.argv[6]

	bls = IBSig()
	(pk, sk) = bls.keygen(0)

	#print(pk)

	f_pk = open('pkBLS.charmPickle', 'wb')
	pick_pk = pickleObject(serializeDict(pk, group))
	f_pk.write(pick_pk)
	f_pk.close()

	validOutputDict = {}
	validOutputDict[0] = {}
	validOutputDict[0]['pk'] = 'pkBLS.charmPickle'

	invalidOutputDict = {}
	invalidOutputDict[0] = {}
	invalidOutputDict[0]['pk'] = 'pkBLS.charmPickle'

	for index in range(0, numValidMessages):
		if (index != 0):
			validOutputDict[index] = {}
			validOutputDict[index]['pk'] = 'pkBLS.charmPickle'

		message = ""
		for randomChar in range(0, messageSize):
			message += random.choice(string.printable)
		#print(message)
		sig = bls.sign(sk['x'], message)
		#print(sig)
		assert bls.verify(pk, sig, message)

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

	for index in range(0, numInvalidMessages):
		if (index != 0):
			invalidOutputDict[index] = {}
			invalidOutputDict[index]['pk'] = 'pkBLS.charmPickle'

		message = ""
		for randomChar in range(0, messageSize):
			message += random.choice(string.printable)
		sig = bls.sign(sk['x'], message)
		#print(sig)
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

		#print(message)

		f_sig = open(prefixName + str(index) + '_InvalidSignature.charmPickle', 'wb')
		invalidOutputDict[index]['sig'] = prefixName + str(index) + '_InvalidSignature.charmPickle'

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

	dict_pickle = pickleObject(serializeDict(invalidOutputDict, group))
	f = open(invalidOutputDictName, 'wb')
	f.write(dict_pickle)
	f.close()
	del dict_pickle
	del f
