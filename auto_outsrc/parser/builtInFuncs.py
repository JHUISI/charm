from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, MNT160, SymEnc, SymDec

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
	return utilBuiltInFuncs.getAttributeList(policy)

def calculateSharesDict(s, policy):
	getUserGlobals()
	return utilBuiltInFuncs.calculateSharesDict(s, policy)

def prune(policy, S):
	getUserGlobals()
	return utilBuiltInFuncs.prune(policy, S)

def getCoefficients(policy):
	getUserGlobals()
	return utilBuiltInFuncs.getCoefficients(policy)

def getUserGlobals():
	global groupObjBuiltInFuncs, utilBuiltInFuncs

	if (groupObjBuiltInFuncs == None):
		groupObjBuiltInFuncs = PairingGroup(MNT160)

	if (utilBuiltInFuncs == None):
		utilBuiltInFuncs = SecretUtil(groupObjBuiltInFuncs, verbose=False)
