from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

groupObjUserFuncs = None

def createPolicy(policy_str):
	getUserGlobals()
	return

def getAttributeList(policy):
	getUserGlobals()
	return

def DeriveKey(R):
	getUserGlobals()
	return

def calculateSharesDict(s, policy):
	getUserGlobals()
	return

def SymEnc(s_sesskey, M):
	getUserGlobals()
	return

def prune(policy, S):
	getUserGlobals()
	return

def getCoefficients(policy):
	getUserGlobals()
	return

def GetString(GetString_Arg):
	getUserGlobals()
	return GetString_Arg.getAttribute()

def lam_func1(y, attrs, Cr, coeff, Dj, Djp, Cpr):
	getUserGlobals()
	y = GetString(attrs[y])
	return (pair((Cr[y] ** -coeff[y]), Dj[y]) * pair((Djp[y] ** coeff[y]), Cpr[y]))

def getUserGlobals():
	global groupObjUserFuncs

	if (groupObjUserFuncs == None):
		groupObjUserFuncs = PairingGroup('SS512')
