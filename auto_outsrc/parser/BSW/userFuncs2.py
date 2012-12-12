from builtInFuncs import *

groupUserFuncs = None

def GetString(GetString_Arg):
    #getUserGlobals()
    return GetString_Arg.getAttribute()

def lam_func1(y, attrs, Cr, Dj, Djp, Cpr, coeff):
    #getUserGlobals()
    y = GetString(attrs[y])
    return ((pair(Cr[y], Dj[y]) / pair(Djp[y], Cpr[y])) ** coeff[y])

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
