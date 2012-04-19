from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, MNT160
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction

groupObjUserFuncs = None
util = None

def createPolicy(policy_str):
	getUserGlobals()
	return util.createPolicy(policy_str)

def getAttributeList(policy):
	getUserGlobals()
	a_list = []
	util.getAttributeList(policy, a_list)
	return a_list

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
	z = {}
	util.getCoefficients(policy, z)
	return z

def SymDec(s_sesskey, T1):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s_sesskey)
	return cipher.decrypt(T1)

def getUserGlobals():
	global groupObjUserFuncs, util

	if (groupObjUserFuncs == None):
		groupObjUserFuncs = PairingGroup(MNT160)

	if (util == None):
		util = SecretUtil(groupObjUserFuncs, verbose=False)
