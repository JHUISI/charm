from builtInFuncs import *

groupUserFuncs = None

def lam_func1(y, hl, hID):
    getUserGlobals()
    return (hl[y] ** hID[y])

def lam_func2(y, gl, hID1):
    getUserGlobals()
    return (gl[y] ** hID1[y])

