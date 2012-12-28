import builtinFuncs_dfa 
from builtinFuncs_dfa import * 
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.DFA import DFA

group = None

secparam = "SS512"


def setup(alphabet):
    h = {}
    g = group.random(G1)
    z = group.random(G1)
    hstart = group.random(G1)
    hend = group.random(G1)
    A = len(alphabet)
    for i in range(0, A):
        a = string(alphabet[i])
        h[a] = group.random(G1)
    alpha = group.random(ZR)
    egg = (pair(g, g) ** alpha)
    msk = (g ** -alpha)
    mpk = [egg, g, z, h, hstart, hend]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, dfaM):
    D = {}
    K = {}
    Klist = {}
    Kend = {}
    KendList = {}

    egg, g, z, h, hstart, hend = mpk
    Q, S, T, q0, F = dfaM
    qlen = len(Q)
    for i in range(0, qlen+1):
        D[i] = group.random(G1)
    rstart = group.random(ZR)
    Kstart1 = (D[0] * (hstart ** rstart))
    Kstart2 = (g ** rstart)
    Tlen = len(T)
    for i in range(0, Tlen):
        r = group.random(ZR)
        x = T[i][0]
        y = T[i][1]
        tt = string(T[i][2])
        key = hashToInt(T[i])
        Klist[1] = ((D[x] ** -1) * (z ** r))
        Klist[2] = (g ** r)
        Klist[3] = (D[y] * (h[tt] ** r))
        K[key] = dict(Klist)
    Flen = len(F)
    for i in range(0, Flen):
        x = F[i]
        rx = group.random(ZR)
        KendList[1] = (msk * (D[x] * (hend ** rx)))
        KendList[2] = (g ** rx)
        Kend[x] = dict(KendList)
    sk = [Kstart1, Kstart2, K, Kend, dfaM]
    output = sk
    return output

def encrypt(mpk, w, M):
    C = {}
    Ct = {}
    s = {}

    egg, g, z, h, hstart, hend = mpk
    l = len(w)
    for i in range(0, l+1):
        s[i] = group.random(ZR)
    Cm = (M * (egg ** s[l]))
    Ct[1] = (g ** s[0])
    Ct[2] = (hstart ** s[0])
    C[0] = dict(Ct)
    for i in range(1, l+1):
        a = string(w[i])
        Ct[1] = (g ** s[i])
        Ct[2] = ((h[a] ** s[i]) * (z ** s[i-1]))
        C[i] = dict(Ct)
    Cend1 = (g ** s[l])
    Cend2 = (hend ** s[l])
    ct = [Cm, C, Cend1, Cend2, w]
    output = ct
    return output

def decrypt(sk, ct):
    B = {}

    Kstart1, Kstart2, K, Kend, dfaM = sk
    Cm, C, Cend1, Cend2, w = ct
    l = len(w)
    if ( ( (accept(dfaM, w)) == (False) ) ):
        output = False
        return output
    Ti = getTransitions(dfaM, w)
    B[0] = (pair(C[0][1], Kstart1) * (pair(C[0][2], Kstart2) ** -1))
    for i in range(1, l+1):
        st = hashToInt(Ti[i])
        Klist = K[st]
        B[i] = (B[i-1] * (pair(C[i-1][1], Klist[1]) * ((pair(C[i][2], Klist[2]) ** -1) * pair(C[i][1], Klist[3]))))
    x = getAcceptState(Ti)
    Bend = (B[l] * ((pair(Cend1, Kend[x][1]) ** -1) * pair(Cend2, Kend[x][2])))
    M = (Cm / Bend)
    output = M
    return output

def main():
    global group
    group = PairingGroup(secparam)

    alphabet = ['a', 'b']
    dfa = DFA("ab*a", alphabet)
    builtinFuncs_dfa.DFAObj = dfa
    dfaM = dfa.constructDFA()

    (mpk, msk) = setup(alphabet)

    sk = keygen(mpk, msk, dfaM)
    w = dfa.getSymbols("abba")
    M = group.random(GT)
    print("M :", M)
    ct = encrypt(mpk, w, M)

    origM = decrypt(sk, ct)
    print("rec M :", origM)
    assert M == origM, "failed decryption"
    print("SUCCESSFUL DECRYPTION!!!") 
     
if __name__ == '__main__':
    main()

