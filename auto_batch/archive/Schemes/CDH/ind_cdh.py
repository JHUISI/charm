from charm.pairing import *
from pksig_cdh import *
import random, string

messageSize = 80
numSigs = 20 # generate this many sig + msg pairs

def randomMessages(count):
    msgList = []
    for i in range(0, count):
        msg = ""
        for index in range(0, messageSize):
            msg += random.choice(string.printable)
        msgList.append(msg)
    return msgList
    
def generateSigs(pk, sk, cdhObj, num_sigs):
    m = randomMessages(num_sigs)
    sig = []
    c = pk['s'] # set state counter from pk (needs to be consistent, right?)
    for i in range(num_sigs):
        sig.append( cdhObj.sign(pk, sk, c, m[i]) )
        c += 1
    
    pk['s'] = c # update the state counter
    return (m, sig)

# does timings, group membership check, verification
def individualVerification(group, cdhObj,  pk, msgs, sigs, N):
    failed = []
    success = []
    trials = 10
    
    bId = InitBenchmark()
    # Start Time?
    StartBenchmark(bID, [RealTime])
    for i in range(N):
        if groupCheck(pk, sigs[i]) == False:
            failed.append(i)
            break
        if cdhObj.verify(pk, msgs[i], sigs[i]):
            continue
    EndBenchmark(bID)
    return (failed, success)
        

def printAll(m, sig, count):
    for i in range(count):
        print("m =>", m[i])
        print("sig =>", sig[i])
    

def batchVerification(group, cdhObj):
    pass

if __name__ == "__main__":
    groupObj = pairing(80)
    cdh = CDH(groupObj)
    N = numSigs
    
    (pk, sk) = cdh.setup()
    
    (mList, sigList) = generateSigs(pk, sk, cdh, N)
    
    printAll(mList, sigList, N)

