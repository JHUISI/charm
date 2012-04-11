from userFuncs import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

def decout(partCT, zz, egga):
	input = [partCT, zz, egga]
	T0, T1, T2 = partCT
	R = (T0 / (T2 ** zz))
	s2_sesskey = SHA1(R)
	M = SymDec(s2_sesskey, T1)
	s2 = groupObj.hash([R, M], ZR)
	output = M
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(M) = decout(sys.argv[1], sys.argv[2], sys.argv[3])
