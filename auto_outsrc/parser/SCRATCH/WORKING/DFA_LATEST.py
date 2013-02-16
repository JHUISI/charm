import builtinFuncs_dfa
from builtinFuncs_dfa import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.DFA import DFA
group = None

secparam = 80


def setup(alphabet):
    h = {}

    g = group.random(G1)
    z = group.random(G1)
    hstart = group.random(G1)
    hend = group.random(G1)
    A = len(alphabet)
    for i in range(0, A):
        a = getString(alphabet[i])
        h[a] = group.random(G1)
    alpha = group.random(ZR)
    egg = (pair(g, g) ** alpha)
    msk = (g ** -alpha)
    mpk = [egg, g, z, h, hstart, hend]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, Q, T, F):
    blindingFactorKendList1Blinded = {}
    K3 = {}
    K2 = {}
    K1 = {}
    KendList2 = {}
    KendList1 = {}
    blindingFactorK3Blinded = {}
    blindingFactorKendList2Blinded = {}
    blindingFactorK2Blinded = {}
    K3Blinded = {}
    D = {}
    blindingFactorK1Blinded = {}
    KendList1Blinded = {}
    K1Blinded = {}
    K2Blinded = {}
    KendList2Blinded = {}

    bf0 = group.random(ZR)
    egg, g, z, h, hstart, hend = mpk
    qlen = len(Q)
    for i in range(0, qlen+1):
        D[i] = group.random(G1)
    rstart = group.random(ZR)
    Kstart1 = (D[0] * (hstart ** rstart))
    Kstart1Blinded = (Kstart1 ** (1 / bf0))
    Kstart2 = (g ** rstart)
    Kstart2Blinded = (Kstart2 ** (1 / bf0))
    Tlen = len(T)
    for i in range(0, Tlen):
        r = group.random(ZR)
        t = T[i]
        t0 = t[0]
        t1 = t[1]
        t2 = getString(t[2])
        key = hashToKey(t)
        K1[key] = ((D[t0] ** -1) * (z ** r))
        K2[key] = (g ** r)
        K3[key] = (D[t1] * (h[t2] ** r))
    for y in K1:
        blindingFactorK1Blinded[y] = bf0
        K1Blinded[y] = (K1[y] ** (1 / blindingFactorK1Blinded[y]))
    for y in K2:
        blindingFactorK2Blinded[y] = bf0
        K2Blinded[y] = (K2[y] ** (1 / blindingFactorK2Blinded[y]))
    for y in K3:
        blindingFactorK3Blinded[y] = bf0
        K3Blinded[y] = (K3[y] ** (1 / blindingFactorK3Blinded[y]))
    Flen = len(F)
    for i in range(0, Flen):
        x = F[i]
        rx = group.random(ZR)
        KendList1[x] = (msk * (D[x] * (hend ** rx)))
        KendList2[x] = (g ** rx)
    for y in KendList1:
        blindingFactorKendList1Blinded[y] = bf0
        KendList1Blinded[y] = (KendList1[y] ** (1 / blindingFactorKendList1Blinded[y]))
    for y in KendList2:
        blindingFactorKendList2Blinded[y] = bf0
        KendList2Blinded[y] = (KendList2[y] ** (1 / blindingFactorKendList2Blinded[y]))
    skBlinded = [Kstart1Blinded, Kstart2Blinded, KendList1Blinded, KendList2Blinded, K1Blinded, K2Blinded, K3Blinded]
    output = (bf0, skBlinded)
    return output

def encrypt(mpk, w, M):
    C2 = {}
    s = {}
    C1 = {}

    egg, g, z, h, hstart, hend = mpk
    l = len(w)
    for i in range(0, l+1):
        s[i] = group.random(ZR)
    Cm = (M * (egg ** s[l]))
    C1[0] = (g ** s[0])
    C2[0] = (hstart ** s[0])
    for i in range(1, l+1):
        a = getString(w[i])
        C1[i] = (g ** s[i])
        C2[i] = ((h[a] ** s[i]) * (z ** s[i-1]))
    Cend1 = (g ** s[l])
    Cend2 = (hend ** s[l])
    ct = [Cend1, Cend2, w, C1, C2, Cm]
    output = ct
    return output

def transform(skBlinded, ct, dfaM):
    transformOutputList = {}
    B = {}

    Kstart1Blinded, Kstart2Blinded, KendList1Blinded, KendList2Blinded, K1Blinded, K2Blinded, K3Blinded = skBlinded
    Cend1, Cend2, w, C1, C2, Cm = ct
    transformOutputList[3] = Cm
    transformOutputList[2] = w
    l = len(w)
    if ( ( (accept(dfaM, w)) == (False) ) ):
        pass
        output = False
        return output
    Ti = getTransitions(dfaM, w)
    transformOutputList[0] = (pair(C1[0], Kstart1Blinded) * pair((C2[0] ** -1), Kstart2Blinded))
    B[0] = transformOutputList[0]
    for i in range(1, l+1):
        pass
        key = hashToKey(Ti[i])
        j = (i - 1)
        transformOutputList[1000+7*i] = ((pair(C1[j], K1Blinded[key]) * pair((C2[i] ** -1), K2Blinded[key])) * pair(C1[i], K3Blinded[key]))
        result0 = transformOutputList[1000+7*i]
    x = getAcceptState(Ti)
    transformOutputList[1] = (pair((Cend1 ** -1), KendList1Blinded[x]) * pair(Cend2, KendList2Blinded[x]))
    result1 = transformOutputList[1]
    output = (transformOutputList, Ti)
    return output

def decout(transformOutputList, bf0, Ti, dfaM):
    B = {}

    Cm = transformOutputList[3]
    w = transformOutputList[2]

    #MUST FIX
    l = len(w)

    if ( ( (accept(dfaM, w)) == (False) ) ):
        pass
    B[0] = (transformOutputList[0] ** bf0)
    for i in range(1, l+1):
        pass
        key = hashToKey(Ti[i])
        j = (i - 1)
        result0 = (transformOutputList[1000+7*i] ** bf0)
        B[i] = (B[i-1] * result0)
    result1 = (transformOutputList[1] ** bf0)
    Bend = (B[l] * result1)
    M = (Cm * (Bend ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    alphabet = ['a', 'b']
    dfa = DFA("ab*a", alphabet)
    builtinFuncs_dfa.DFAObj = dfa
    dfaM = dfa.constructDFA()

    (mpk, msk) = setup(alphabet)

    Q, S, T, q0, F = dfaM

    (blindingFactor0Blinded, skBlinded) = keygen(mpk, msk, Q, T, F)
    w = dfa.getSymbols("abbba")
    M = group.random(GT)
    print("M :", M)
    ct = encrypt(mpk, w, M)

    (transformOutputList, Ti) = transform(skBlinded, ct, dfaM)
    origM = decout(transformOutputList, blindingFactor0Blinded, Ti, dfaM)


    print("rec M :", origM)
    assert M == origM, "failed decryption"
    print("SUCCESSFUL DECRYPTION!!!") 


if __name__ == '__main__':
    main()

