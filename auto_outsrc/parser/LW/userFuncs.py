from builtInFuncs import *

groupUserFuncs = None

def GetString(attrsy):
    getUserGlobals()
    return

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
