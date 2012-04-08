from charm import *
from toolbox import *
from schemes import *
from math import *
from charm.pairing import hash as SHA1

groupObj = None
util = None

def createPolicy(policy_str):
	getGlobals()
	return util.createPolicy(policy_str)

def getAttributeList(policy):
	getGlobals()
	return util.getAttributeList(policy)

def calculateSharesDict(s, policy):
	getGlobals()
	return util.calculateSharesDict(s, policy)

def SymEnc(s_sesskey, M):
	getGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.encrypt(M) 

def prune(policy, S):
	getGlobals()
	return util.prune(policy, S)

def getCoefficients(policy):
	getGlobals()
	return util.getCoefficients(policy)

def SymDec(s_sesskey, T1):
	getGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.decrypt(T1)

def getGlobals():
    global groupObj, util

    if (groupObj == None):
        groupObj = PairingGroup('SS512')

    if (util == None):
        util = SecretUtil(groupObj, verbose=False)
