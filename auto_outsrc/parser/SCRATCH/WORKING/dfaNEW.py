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
    blindingFactorKendList1Blinded = {}
    Klist = {}
    KendList2 = {}
    KendList1 = {}
    blindingFactorKendList2Blinded = {}
    D = {}
    K = {}
    KendList1Blinded = {}
    KendList2Blinded = {}

    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    egg, g, z, h, hstart, hend = mpk
    Q, S, T, q0, F = dfaM
    dfaMBlinded = dfaM
    qlen = len(Q)
    for i in range(0, qlen+1):
        D[i] = group.random(G1)
    rstart = group.random(ZR)
    Kstart1 = (D[0] * (hstart ** rstart))
    Kstart1Blinded = (Kstart1 ** (1 / blindingFactor0Blinded))
    Kstart2 = (g ** rstart)
    Kstart2Blinded = (Kstart2 ** (1 / blindingFactor0Blinded))
    Tlen = len(T)
    for i in range(0, Tlen):
        r = group.random(ZR)
        t = T[i]
        x = t[0]
        y = t[1]
        tt = string(t[2])
        key = hashToInt(t)
        K[key] = {}
        Klist = {}
        Klist[1] = ((D[x] ** -1) * (z ** r))
        Klist[2] = (g ** r)
        Klist[3] = (D[y] * (h[tt] ** r))
        K[key] = (Klist)
    KBlinded = K
    Flen = len(F)
    for i in range(0, Flen):
        x = F[i]
        rx = group.random(ZR)
        KendList1[x] = (msk * (D[x] * (hend ** rx)))
        KendList2[x] = (g ** rx)
    for y in KendList2:
        blindingFactorKendList2Blinded[y] = blindingFactor0Blinded
        KendList2Blinded[y] = (KendList2[y] ** (1 / blindingFactorKendList2Blinded[y]))
    for y in KendList1:
        blindingFactorKendList1Blinded[y] = blindingFactor0Blinded
        KendList1Blinded[y] = (KendList1[y] ** (1 / blindingFactorKendList1Blinded[y]))
    sk = [Kstart1Blinded, Kstart2Blinded, KBlinded, KendList1Blinded, KendList2Blinded, dfaMBlinded]
    skBlinded = [Kstart1Blinded, Kstart2Blinded, KBlinded, KendList1Blinded, KendList2Blinded, dfaMBlinded]
    output = (blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, w, M):
    C = {}
    s = {}

    egg, g, z, h, hstart, hend = mpk
    l = len(w)
    for i in range(0, l+1):
        s[i] = group.random(ZR)
    Cm = (M * (egg ** s[l]))
    C[0] = {}
    C[0][1] = (g ** s[0])
    C[0][2] = (hstart ** s[0])
    for i in range(1, l+1):
        a = string(w[i])
        C[i] = {}
        C[i][1] = (g ** s[i])
        C[i][2] = ((h[a] ** s[i]) * (z ** s[i-1]))
    Cend1 = (g ** s[l])
    Cend2 = (hend ** s[l])
    ct = [Cm, C, Cend1, Cend2, w]
    output = ct
    return output

def transform(sk, ct):
    transformOutputList = {}
    B = {}

    Kstart1, Kstart2, K, KendList1, KendList2, dfaM = sk
    Cm, C, Cend1, Cend2, w = ct
    transformOutputList[0] = len(w)
    l = transformOutputList[0]
    if ( ( (accept(dfaM, w)) == (False) ) ):
        pass
        transformOutputList[1] = False
        output = transformOutputList[1]
        return output
    transformOutputList[2] = getTransitions(dfaM, w)
    Ti = transformOutputList[2]
    transformOutputList[3] = (pair(C[0][1], Kstart1) * pair((C[0][2] ** -1), Kstart2))
    B[0] = transformOutputList[3]
    for i in range(1, l+1):
        pass
        transformOutputList[1000+8*i] = hashToInt(Ti[i])
        st = transformOutputList[1000+8*i]
        transformOutputList[1001+8*i] = K[st]
        Klist = transformOutputList[1001+8*i]
        transformOutputList[1002+8*i] = (i - 1)
        j = transformOutputList[1002+8*i]
        transformOutputList[1003+8*i] = (pair(C[j][1], Klist[1]) * (pair((C[i][2] ** -1), Klist[2]) * pair(C[i][1], Klist[3])))
        result0 = transformOutputList[1003+8*i]
    transformOutputList[4] = getAcceptState(Ti)
    x = transformOutputList[4]
    transformOutputList[5] = (pair((Cend1 ** -1), KendList1[x]) * pair(Cend2, KendList2[x]))
    result1 = transformOutputList[5]
    output = transformOutputList
    return output

def decout(sk, ct, transformOutputList, blindingFactor0Blinded):
    B = {}

    Kstart1, Kstart2, K, KendList1, KendList2, dfaM = sk
    Cm, C, Cend1, Cend2, w = ct
    l = transformOutputList[0]
    if ( ( (accept(dfaM, w)) == (False) ) ):
        pass
        output = transformOutputList[1]
        return output
    Ti = transformOutputList[2]
    B[0] = (transformOutputList[3] ** blindingFactor0Blinded)
    for i in range(1, l+1):
        pass
        st = transformOutputList[1000+8*i]
        Klist = transformOutputList[1001+8*i]
        j = transformOutputList[1002+8*i]
        result0 = transformOutputList[1003+8*i]
        B[i] = (B[i-1] * result0)
    x = transformOutputList[4]
    result1 = (transformOutputList[5] ** blindingFactor0Blinded)
    Bend = (B[l] * result1)
    M = (Cm * (Bend ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    alphabet = ['a', 'b']
    dfa = DFA("ab*a", alphabet)
    builtinFuncs_dfa.DFAObj = dfa
    dfaM = dfa.constructDFA()

    (mpk, msk) = setup(alphabet)

    (blindingFactor0Blinded, skBlinded) = keygen(mpk, msk, dfaM)
    w = dfa.getSymbols("abba")
    M = group.random(GT)
    print("M :", M)
    ct = encrypt(mpk, w, M)

    transformOutputList = transform(skBlinded, ct)
    origM = decout(skBlinded, ct, transformOutputList, blindingFactor0Blinded)



    print("rec M :", origM)
    assert M == origM, "failed decryption"
    print("SUCCESSFUL DECRYPTION!!!") 


if __name__ == '__main__':
    main()

