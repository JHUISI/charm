from builtInFuncs import *

groupUserFuncs = None

def GetString(GetString_Arg):
	getUserGlobals()
	return GetString_Arg.getAttribute()

def lam_func1(y, attrs, Cr, coeff, Dj, Djp, Cpr):
	getUserGlobals()
	y = GetString(attrs[y])
	return (pair((Cr[y] ** -coeff[y]), Dj[y]) * pair((Djp[y] ** coeff[y]), Cpr[y]))

def getUserGlobals():
	global groupUserFuncs

	if (groupUserFuncs == None):
		groupUserFuncs = PairingGroup(MNT160)
