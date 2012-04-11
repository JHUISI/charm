from userFuncs import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

def transform(ct, sk):
	input = [ct, sk]
	id, D, K, tag_k = sk
	C, E1, E2, tag_c, T1 = ct
	tag = (1 / (tag_c - tag_k))
	A1 = (pair(C[1], D[1]) * (pair(C[2], D[2]) * (pair(C[3], D[3]) * (pair(C[4], D[4]) * pair(C[5], D[5])))))
	A2 = (pair(C[6], D[6]) * pair(C[7], D[7]))
	A3 = (A1 / A2)
	A4 = (pair((E1 ** tag), D[7]) * pair((E2 ** -tag), K))
	T2 = (A3 / A4)
	T0 = C[0]
	partCT = [T0, T1, T2]
	output = partCT
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(partCT) = transform(sys.argv[1], sys.argv[2])
