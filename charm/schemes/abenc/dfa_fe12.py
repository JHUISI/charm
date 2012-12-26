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
from charm.toolbox.DFA import DFA

debug = False
class FE_DFA:
    def __init__(self, _groupObj, _dfaObj):
        global group, dfaObj
        group = _groupObj
        dfaObj = _dfaObj
        
    def setup(self, alphabet):
        g, z, h_start, h_end = group.random(G1, 4)
        h = {'start':h_start, 'end':h_end }
        for sigma in alphabet:
            h[str(sigma)] = group.random(G1)
        alpha = group.random(ZR)
        
        msk = g ** -alpha
        mpk = {'egg':pair(g, g) ** alpha, 'g':g, 'z':z, 'h':h }
        return (mpk, msk)
    
    def keygen(self, mpk, msk, dfaM):
        Q, S, T, q0, F = dfaM
        q = len(Q)
        # associate D_i with each state q_i in Q
        D = group.random(G1, q+1) # [0, q] including q-th index
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
        
        C[0] = {}
        C[0][1] = mpk['g'] ** s[0]
        C[0][2] = mpk['h']['start'] ** s[0]
        
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
        l = len(w)
        B = {}
        # if DFA does not accept string, return immediately
        if not dfaObj.accept(dfaM, w):
            print("DFA rejects: ", w)
            return False
        
        Ti = dfaObj.getTransitions(dfaM, w) # returns a tuple of transitions 
        B[0] = pair(C[0][1],  K['start1']) * (pair(C[0][2], K['start2']) ** -1)
        for i in range(1, l+1):
            ti = Ti[i]
            if debug: print("transition: ", ti)
            B[i] = B[i-1] * pair(C[i-1][1], K[str(ti)][1]) * (pair(C[i][2], K[str(ti)][2]) ** -1) * pair(C[i][1], K[str(ti)][3])
        
        x = dfaObj.getAcceptState(Ti) # retrieve accept state
        Bend = B[l] * (pair(C['end1'], K['end'][str(x)][1]) ** -1) * pair(C['end2'], K['end'][str(x)][2]) 
        M = C['m'] / Bend  
        return M
    
def main():
    global group
    group = PairingGroup("SS512")
    
    alphabet = {'a', 'b'}
    dfa = DFA("ab*a", alphabet)
    dfaM = dfa.constructDFA()
    
    fe = FE_DFA(group, dfa)
    
    (mpk, msk) = fe.setup(alphabet)
    if debug: print("mpk :=>", mpk, "\n\n")
    
    sk = fe.keygen(mpk, msk, dfaM)
    if debug: print("sk :=>", sk)
    
    w = dfa.getSymbols("abba")
    M = group.random(GT)
    ct = fe.encrypt(mpk, w, M)
    
    origM = fe.decrypt(sk, ct)
    assert M == origM, "failed decryption!"
    if debug: print("Successful Decryption!!!!!")
    
if __name__ == "__main__":
    debug = True
    main()
    
    
    
            