from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, MNT160, SymEnc, SymDec

from charm.toolbox.secretutil import SecretUtil
from charm.pairing import pairing
from toolbox.iterate import dotprod2
from charm.pairing import hash as DeriveKey
from charm.engine.util import objectToBytes, bytesToObject
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hashlib

groupObjBuiltInFuncs = None
utilBuiltInFuncs = None

listIndexNoOfN_StrToId = 9
listIndexNoOfl_StrToId = 10

def objectOut(group, d):
	getUserGlobals()
	s = ""
	keys = d.keys()
	for i in keys:
		if type(d[i]) == pairing:
			s += str(i) + "=" + group.serialize(d[i]).decode() + "\n"
		else:
			s += str(i) + "=" + d[i].decode()
	return s

def writeToFile(name, s):
	getUserGlobals()
	fd = open(name, 'w')
	fd.write(s)
	fd.close()

def createPolicy(policy_str):
	getUserGlobals()
	return utilBuiltInFuncs.createPolicy(policy_str)

def getAttributeList(policy):
	getUserGlobals()
	return utilBuiltInFuncs.getAttributeList(policy)

def calculateSharesDict(s, policy):
	getUserGlobals()
	return utilBuiltInFuncs.calculateSharesDict(s, policy)

def calculateSharesList(s, policy):
	getUserGlobals()
	return utilBuiltInFuncs.calculateSharesList(s, policy)

def prune(policy, S):
	getUserGlobals()
	return utilBuiltInFuncs.prune(policy, S)

def getCoefficients(policy):
	getUserGlobals()
	return utilBuiltInFuncs.getCoefficients(policy)

def sha1(message):
	getUserGlobals()
	hashObj = hashlib.new('sha1') 
	h = hashObj.copy()
	h.update(bytes(message, 'utf-8'))
	return Bytes(h.digest())

def strToId(pk, strID):
	getUserGlobals()
	hash = sha1(strID)
	val = Conversion.OS2IP(hash)
	bstr = bin(val)[2:]

	v=[]

	for i in range(pk[listIndexNoOfN_StrToId]):
		binsubstr = bstr[pk[listIndexNoOfl_StrToId]*i : pk[listIndexNoOfl_StrToId]*(i+1)]
		print(binsubstr)
		intval = int(binsubstr, 2)
		intelement = groupObjBuiltInFuncs.init(ZR, intval)
		v.append(intelement)

	return v

def getUserGlobals():
	global groupObjBuiltInFuncs, utilBuiltInFuncs

	if (groupObjBuiltInFuncs == None):
		groupObjBuiltInFuncs = PairingGroup(MNT160)

	if (utilBuiltInFuncs == None):
		utilBuiltInFuncs = SecretUtil(groupObjBuiltInFuncs, verbose=False)
