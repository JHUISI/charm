from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

def SymEnc(s2_sesskey, M):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s2_sesskey)
	return cipher.encrypt(M) 

def SymDec(s2_sesskey, T1):
	getUserGlobals()
	cipher = AuthenticatedCryptoAbstraction(s2_sesskey)
	return cipher.decrypt(T1)

def getUserGlobals():
	pass
