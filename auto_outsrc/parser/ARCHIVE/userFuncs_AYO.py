from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

groupObjUserFuncs = None

def getUserGlobals():
	global groupObjUserFuncs

	if (groupObjUserFuncs == None):
		groupObjUserFuncs = PairingGroup('SS512')
