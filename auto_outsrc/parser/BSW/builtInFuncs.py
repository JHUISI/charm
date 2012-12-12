import hashlib, sys

from charm.toolbox.pairinggroup import *

from charm.toolbox.secretutil import SecretUtil
from charm.core.math import pairing
from charm.toolbox.iterate import dotprod2
from charm.core.math.pairing import hashPair as DeriveKey
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.conversion import Conversion
from charm.toolbox.bitstring import Bytes
#import hashlib

groupObj = None
util = None

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
	#getUserGlobals()
	s = ""
	keys = d.keys()
	for i in keys:
		if type(d[i]) == pairing:
			s += str(i) + "=" + group.serialize(d[i]).decode() + "\n"
		else:
			s += str(i) + "=" + d[i].decode()
	return s

def writeToFile(name, s):
	#getUserGlobals()
	fd = open(name, 'w')
	fd.write(s)
	fd.close()

def createPolicy(policy_str):
	#getUserGlobals()
	return util.createPolicy(policy_str)

def getAttributeList(policy):
	#getUserGlobals()
	return util.getAttributeList(policy)

def calculateSharesDict(s, policy):
	#getUserGlobals()
	return util.calculateSharesDict(s, policy)

def calculateSharesList(s, policy):
	#getUserGlobals()
	return util.calculateSharesList(s, policy)

def prune(policy, S):
	#getUserGlobals()
	return util.prune(policy, S)

def getCoefficients(policy):
	#getUserGlobals()
	return util.getCoefficients(policy)

def sha1(message):
	#getUserGlobals()
	hashObj = hashlib.new('sha1') 
	h = hashObj.copy()
	h.update(bytes(message, 'utf-8'))
	return Bytes(h.digest())

def stringToId(strID, length, size):
	#getUserGlobals()
	hash = sha1(strID)
	val = Conversion.OS2IP(hash)
	bstr = bin(val)[2:]

	v=[]

	for i in range(length):
		binsubstr = bstr[size*i : size*(i+1)]
		print(binsubstr)
		intval = int(binsubstr, 2)
		intelement = groupObj.init(ZR, intval)
		v.append(intelement)

	return v

#def getUserGlobals():
#	global groupObjBuiltInFuncs, utilBuiltInFuncs
#
#	if (groupObjBuiltInFuncs == None):
#		groupObjBuiltInFuncs = PairingGroup(MNT160)
#
#	if (utilBuiltInFuncs == None):
#		utilBuiltInFuncs = SecretUtil(groupObjBuiltInFuncs, verbose=False)
