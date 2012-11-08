from charm.pairing import *
from pksig_cdh import *
import random, string

messageSize = 80
numSigs = 100 # generate this many sig + msg pairs

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

def groupMembershipCheck(group, obj):
    if type(obj) == dict:
        for i in obj.keys():
            if type(obj[i]) == int:
                pass
            else: 
                if group.ismember(obj[i]) == False: 
                    return False
        return True
    elif type(obj) in [tuple, list]:
        for i in obj:
            if group.ismember(i) == False:
                return False
        return True
    else:
        return group.ismember(obj)
    

# does timings, group membership check, verification
def individualVerification(group, cdhObj,  pk, msgs, sigs, N):
    failed = []
#    trials = 10
#   
    if groupMembershipCheck(group, pk) == False:
        return False 

    for i in range(N):
        if groupMembershipCheck(group, sigs[i]) == False:
            failed.append(i)
            break
        if cdhObj.verify(pk, msgs[i], sigs[i]):
            print("Verified sig ", i)
            continue
#    EndBenchmark(bID)
    return failed
        

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
    
    #printAll(mList, sigList, N)
    
    arrs = individualVerification(groupObj, cdh, pk, mList, sigList, N)

    print("Failed len is zero? ", len(arrs))
    