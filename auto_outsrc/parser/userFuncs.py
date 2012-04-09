from charm import *
from toolbox import *
from toolbox.pairinggroup import *
from toolbox.secretutil import SecretUtil
from schemes import *
from math import *
from charm.pairing import hash as SHA1

groupObjUserFuncs = None
util = None

def createPolicy(policy_str):
	getUserGlobals()
	return util.createPolicy(policy_str)

def getAttributeList(policy):
	getUserGlobals()
	return util.getAttributeList(policy)

def calculateSharesDict(s, policy):
	getUserGlobals()
	return util.calculateSharesDict(s, policy)

def SymEnc(s_sesskey, M):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.encrypt(M) 

def prune(policy, S):
	getUserGlobals()
	return util.prune(policy, S)

def getCoefficients(policy):
	getUserGlobals()
	return util.getCoefficients(policy)

def SymDec(s_sesskey, T1):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.decrypt(T1)

def getUserGlobals():
	global groupObjUserFuncs, util

	if (groupObjUserFuncs == None):
		groupObjUserFuncs = PairingGroup('SS512')

	if (util == None):
		util = SecretUtil(groupObjUserFuncs, verbose=False)

