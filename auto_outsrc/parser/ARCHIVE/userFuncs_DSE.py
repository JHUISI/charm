from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

groupObjUserFuncs = None

def SHA1(R):
	getUserGlobals()
	return

def SymEnc(s2_sesskey, M):
	getUserGlobals()
	return

def SymDec(s2_sesskey, T1):
	getUserGlobals()
	return

def userErrorFunction(userErrorFunctionArgString):
	getUserGlobals()
	return

def getUserGlobals():
	global groupObjUserFuncs

	if (groupObjUserFuncs == None):
		groupObjUserFuncs = PairingGroup('SS512')
