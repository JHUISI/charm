#from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, MNT160, SymEnc, SymDec
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair

from toolbox.secretutil import SecretUtil
from charm.pairing import pairing
from toolbox.iterate import dotprod2
from charm.pairing import hash as DeriveKey
from charm.engine.util import objectToBytes, bytesToObject
from toolbox.symcrypto import AuthenticatedCryptoAbstraction

groupObjBuiltInFuncs = None
utilBuiltInFuncs = None

def objectOut(group, d):
	s = ""
	keys = d.keys()
	for i in keys:
		if type(d[i]) == pairing:
			s += str(i) + "=" + group.serialize(d[i]).decode() + "\n"
		else:
			s += str(i) + "=" + d[i].decode()
	return s

def writeToFile(name, s):
	fd = open(name, 'w')
	fd.write(s)
	fd.close()

def createPolicy(policy_str):
	getUserGlobals()
	return utilBuiltInFuncs.createPolicy(policy_str)

def getAttributeList(policy):
	getUserGlobals()
	a_list = []
	utilBuiltInFuncs.getAttributeList(policy, a_list)
	return a_list

def calculateSharesDict(s, policy):
	getUserGlobals()
	return utilBuiltInFuncs.calculateSharesDict(s, policy)

def SymEnc(s_sesskey, M):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.encrypt(M)

def prune(policy, S):
	getUserGlobals()
	return utilBuiltInFuncs.prune(policy, S)

def getCoefficients(policy):
	getUserGlobals()
	z = {}
	utilBuiltInFuncs.getCoefficients(policy, z)
	return z

def SymDec(s_sesskey, T1):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.decrypt(T1)

def getUserGlobals():
	global groupObjBuiltInFuncs, utilBuiltInFuncs

	if (groupObjBuiltInFuncs == None):
		groupObjBuiltInFuncs = PairingGroup('SS512')

	if (utilBuiltInFuncs == None):
		utilBuiltInFuncs = SecretUtil(groupObjBuiltInFuncs, verbose=False)
