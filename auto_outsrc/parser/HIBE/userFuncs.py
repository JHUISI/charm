from builtInFuncs import *

groupUserFuncs = None

'''
def stringToID(z, 5, id):
    getUserGlobals()
    return
'''

def lam_func1(y, g1b, Id, hb, r):
    getUserGlobals()
    return (((g1b ** Id[y]) * hb[y]) ** r[y])

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
