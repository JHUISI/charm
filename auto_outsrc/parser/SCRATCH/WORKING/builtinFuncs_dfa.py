
groupUserFuncs = None
DFAObj = None

def hashToKey(T):
    return str(T)

def getString(wi):
    return str(wi)

def accept(dfaM, w):
    return DFAObj.accept(dfaM, w)

def getTransitions(dfaM, w):
    return DFAObj.getTransitions(dfaM, w)

def getAcceptState(Ti):
    return DFAObj.getAcceptState(Ti)

