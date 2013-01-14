
groupUserFuncs = None
DFAObj = None

def hashToInt(T):
    return str(T)

def string(wi):
    return str(wi)

def accept(dfaM, w):
    return DFAObj.accept(dfaM, w)

def getTransitions(dfaM, w):
    return DFAObj.getTransitions(dfaM, w)

def getAcceptState(Ti):
    return DFAObj.getAcceptState(Ti)

