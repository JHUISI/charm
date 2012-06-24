from builtInFuncs import *

groupUserFuncs = None

def calculateShares(s, policy):
	getUserGlobals()
	return

def GetString(GetString_Arg):
	getUserGlobals()
	return GetString_Arg.getAttribute()

def lam_func1(y, attrs, C1, coeff, h_gid, C3, K, C2):
	getUserGlobals()
	y = GetString(attrs[y])
	return (((C1[y] ** coeff[y]) * pair((h_gid ** coeff[y]), C3[y])) * pair((K[y] ** -coeff[y]), C2[y]))

def getUserGlobals():
	global groupUserFuncs

	if (groupUserFuncs == None):
		groupUserFuncs = PairingGroup(MNT160)
