from userFuncs_BSW import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

def decout(partCT, zz, egg):
	input = [partCT, zz, egg]
	T0, T1, T2 = partCT
	R = (T0 / (T2 ** zz))
	s_sesskey = SHA1(R)
	M = SymDec(s_sesskey, T1)
	s = groupObj.hash([R, M], ZR)
	output = M
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(M) = decout(sys.argv[1], sys.argv[2], sys.argv[3])
