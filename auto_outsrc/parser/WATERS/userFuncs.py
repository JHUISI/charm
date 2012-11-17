from builtInFuncs import *

groupUserFuncs = None

def GetString(GetString_Arg):
    getUserGlobals()
    return GetString_Arg.getAttribute()

def lam_func1(y, attrs, Cn, coeff, L, Kl, Dn):
    getUserGlobals()
    y = GetString(attrs[y])
    return (pair((Cn[y] ** coeff[y]), L) * pair((Kl[y] ** coeff[y]), Dn[y]))

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
