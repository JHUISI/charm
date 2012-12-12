from builtInFuncs import *

groupUserFuncs = None

def calculateShares(s, policy):
    getUserGlobals()
    return

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
