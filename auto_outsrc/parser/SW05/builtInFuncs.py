import hashlib, sys

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.secretshare import SecretShare
from charm.core.math import pairing
from charm.toolbox.iterate import dotprod2
from charm.core.math.pairing import hashPair as DeriveKey
from charm.core.engine.util import objectToBytes, bytesToObject
#from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.conversion import Conversion
#from charm.toolbox.bitstring import Bytes
#import hashlib

groupObjBuiltInFuncs = None
utilBuiltInFuncs = None
shareBuiltInFuncs = None

listIndexNoOfN_StrToId = 9
listIndexNoOfl_StrToId = 10

MNT160 = 80

def isList(object):
    objectTypeName = None

    try:
        objectTypeName = type(object).__name__
    except:
        sys.exit("builtInFuncs.py:  could not obtain type/name of object passed in to isList.")

    if (objectTypeName == 'list'):
        return 1

    return 0

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

def strkeys(var):
	keys = []
	for i in range(len(var)):
	    keys.append( var[i][0] ) 
	return keys

def recoverCoefficientsDict(inputDict):
	getUserGlobals()
	newDict = {}
	_inputDict = {}
	if type(inputDict[0]) == int:
		for i,j in inputDict.items():
		    _inputDict[ i ] = groupObjBuiltInFuncs.init(ZR, j)
		resultDict = shareBuiltInFuncs.recoverCoefficientsDict(_inputDict)
		for i,j in resultDict.items():
		    newDict[ int(i) ] = j	
		return newDict

	length = len(inputDict)
	for i in range(length):
	    _inputDict[ inputDict[i][0] ] = inputDict[i][1]
	resultDict = shareBuiltInFuncs.recoverCoefficientsDict(_inputDict)
	for i in range(length):
	    key = inputDict[i][1] 
	    if resultDict.get(key) != None:
	       newDict[ inputDict[i][0] ] = resultDict[key]
	return newDict

def genShares(mk0, dOver, n, q, wHash):
	getUserGlobals()
	return shareBuiltInFuncs.genShares(mk0, dOver, n, q, wHash)

def genSharesForX(mk0, q, wHash):
	getUserGlobals()
	newX = []
	x = shareBuiltInFuncs.genShares(mk0, 1, 1, q, wHash) 
	for i in range(len(x)):
		newX.append(x[i][1])
	return newX
	#return utilBuiltInFuncs.genShares(mk0, q, wHash)

def intersectionSubset(w, wPrime, d):
    getUserGlobals()	
    SSub = {}
    S = {}

    wLen = len(w)
    wPrimeLen = len(wPrime)
    SIndex = 0
    for i in range(0, wLen):
        for j in range(0, wPrimeLen):
            if ( ( (w[i]) == (wPrime[j]) ) ):
                S[SIndex] = (w[i], groupObjBuiltInFuncs.hash(w[i]))
                SIndex = (SIndex + 1)
    #for k in range(0, d):
    #    SSub[k] = (S[k][0]], S[k][1])
    output = S
    return output

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
	global groupObjBuiltInFuncs, utilBuiltInFuncs, shareBuiltInFuncs

	if (groupObjBuiltInFuncs == None):
		groupObjBuiltInFuncs = PairingGroup("SS512")

	if (utilBuiltInFuncs == None):
		utilBuiltInFuncs = SecretUtil(groupObjBuiltInFuncs, verbose=False)

	if (shareBuiltInFuncs == None):
		shareBuiltInFuncs = SecretShare(groupObjBuiltInFuncs, False)
