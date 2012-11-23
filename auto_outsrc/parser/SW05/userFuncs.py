from builtInFuncs import *

groupUserFuncs = None

def recoverCoefficients(N):
    getUserGlobals()
    return

def genShares(mk0, dOver, n, q, wHash):
    getUserGlobals()
    return

def evalT(pk, n, loopVar):
    getUserGlobals()
    return

def intersection_subset(w, CT0, d):
    getUserGlobals()
    return

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
