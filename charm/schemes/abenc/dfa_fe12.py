'''
Brent Waters (Pairing-based)
 
| From: "Functional Encryption for Regular Languages".
| Published in: 2012
| Available from: http://eprint.iacr.org/2012/384
| Notes: 
| Security Assumption: 
|
| type:           functional encryption ("public index")
| setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       12/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

def accept(dfaM, w):
    # TODO: add code to check that the dfa accepts the string w
    return True

def getTransitions(dfaM, w):
    # TODO: extract transitions from dfaM applied to w. 
#    ti = [(0, 1, 'a'), (1, 1, 'b'), (1, 1, 'b'), (1, 2, a)]
#    ti = {1:(0, 1, 'a'), 2:(1, 1, 'b'), 3:(1, 1, 'b'), 4:(1, 2, 'a')}
    ti = {1:(0, 1, 'a'), 2:(1, 1, 'b'), 3:(1, 1, 'b'), 4:(1, 2, 'a')}
    return ti

def getAcceptState(transitions):
    assert type(transitions) == dict, "'transitions' not the right type"
    t_len = len(transitions.keys())
    return int(transitions[t_len][1])

class FE_DFA:
    def __init__(self, groupObj):
        global group
        group = groupObj
        
    def setup(self, Sigma):
        g, z, h_start, h_end = group.random(G1, 4)
        h = {'start':h_start, 'end':h_end }
        for sigma in Sigma:
            h[str(sigma)] = group.random(G1)
        alpha = group.random(ZR)
        
        msk = g ** -alpha
        mpk = {'egg':pair(g, g) ** alpha, 'g':g, 'z':z, 'h':h }
        return (mpk, msk)
    
    def keygen(self, mpk, msk, dfaM):
        Q, T, q0, F = dfaM
        q = len(Q)+1
        # associate D_i with each state q_i in Q
        D = group.random(G1, q) # [0, q] including q-th index
        r_start = group.random(ZR)
        K = {}
        K['start1'] = D[0] * (mpk['h']['start'] ** r_start)
        K['start2'] = mpk['g'] ** r_start
        
        for t in T: # for each tuple, t in transition list
            r = group.random(ZR)
            (x, y, sigma) = t
            K[str(t)] = {}
            K[str(t)][1] = (D[x] ** -1) * (mpk['z'] ** r)
            K[str(t)][2] = mpk['g'] ** r
            K[str(t)][3] = D[y] * ((mpk['h'][str(sigma)]) ** r)
        
        # for each accept state in the set of all accept states
        K['end'] = {}
        for x in F:
            rx = group.random(ZR)
            K['end'][str(x)] = {}
            K['end'][str(x)][1] = msk * D[x] * (mpk['h']['end'] ** rx)
            K['end'][str(x)][2] = mpk['g'] ** rx
            
        sk = {'K':K, 'dfaM':dfaM }
        return sk
    
    def encrypt(self, mpk, w, M):
        l = len(w) # symbols of string        
        s = group.random(ZR, l+1) # l+1 b/c it includes 'l'-th index
        C = {}
        C['m'] = M * (mpk['egg'] ** s[l])
        
        C['start1'] = mpk['g'] ** s[0]
        C['start2'] = mpk['h']['start'] ** s[0]
        
        C[0] = {}
        C[0][1] = C['start1']
        
        for i in range(1, l+1):
            C[i] = {}
            C[i][1] = mpk['g'] ** s[i]
            C[i][2] = (mpk['h'][ str(w[i]) ] ** s[i]) * (mpk['z'] ** s[i-1])
        
        C['end1'] = mpk['g'] ** s[l]
        C['end2'] = mpk['h']['end'] ** s[l]        
        ct = {'C':C, 'w':w}
        return ct
    
    def decrypt(self, sk, ct):
        K, dfaM = sk['K'], sk['dfaM']
        C, w = ct['C'], ct['w']
        Q, T, q0, F = dfaM
        l = len(w)
        B = {}
        # if DFA does not accept string, return immediately
        if not accept(dfaM, w):
            return False
        
        Ti = getTransitions(dfaM, w) # returns a tuple of transitions 
        B[0] = pair(C['start1'],  K['start1']) * (pair(C['start2'], K['start2']) ** -1)
        for i in range(1, l+1):
            ti = Ti[i]
            print("transition : ", ti)
            B[i] = B[i-1] * pair(C[i-1][1], K[str(ti)][1]) * (pair(C[i][2], K[str(ti)][2]) ** -1) * pair(C[i][1], K[str(ti)][3])
        
        x = getAcceptState(Ti) # retrieve accept state
        print("x :=", x)
        Bend = B[l] * (pair(C['end1'], K['end'][str(x)][1]) ** -1) * pair(C['end2'], K['end'][str(x)][2]) 
        M = C['m'] / Bend  
        return M
    
def main():
    global group
    group = PairingGroup("SS512")
    
    # describe sample DFA...provide methods to convert regex to DFA
    Sigma = {'a', 'b'}
    Q = {0, 1, 2}
    T = [ (0, 1, 'a'), (1, 1, 'b'), (1, 2, 'a') ]
    q0 = 0
    F = {2}
    dfaM = [Q, T, q0, F]
    
    fe = FE_DFA(group)
    
    (mpk, msk) = fe.setup(Sigma)
    #print("mpk :=>", mpk, "\n\n")
    
    sk = fe.keygen(mpk, msk, dfaM)
    print("sk :=>", sk)
    
    w = {1:'a', 2:'b', 3:'b', 4:'a'} # string has to be 1-indexed
    M = group.random(GT)
    ct = fe.encrypt(mpk, w, M)
    
    origM = fe.decrypt(sk, ct)
    assert M == origM, "failed decryption!"
    print("Successful Decryption!!!!!")
    
if __name__ == "__main__":
    main()
    
    
    
            