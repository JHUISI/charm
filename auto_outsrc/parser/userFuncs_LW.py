from builtInFuncs import *

groupUserFuncs = None

def GetString(GetString_Arg):
	getUserGlobals()
	return GetString_Arg.getAttribute()

def lam_func1(y, attrs, C1, h_gid, C3, K, C2, coeff):
	getUserGlobals()
	y = GetString(attrs[y])
	return (((C1[y] * pair(h_gid, C3[y])) / pair(K[y], C2[y])) ** coeff[y])

def getUserGlobals():
	global groupUserFuncs

	if (groupUserFuncs == None):
		groupUserFuncs = PairingGroup(MNT160)
