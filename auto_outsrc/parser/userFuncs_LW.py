from builtInFuncs import *

groupUserFuncs = None

def getUserGlobals():
    global groupUserFuncs

    if (groupUserFuncs == None):
        groupUserFuncs = PairingGroup(MNT160)
