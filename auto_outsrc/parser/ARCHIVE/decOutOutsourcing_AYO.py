from userFuncs import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

def decout(partCT, zz):
	input = [partCT, zz]
	output = M1
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(M1) = decout(sys.argv[1], sys.argv[2])
