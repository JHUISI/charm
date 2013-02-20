import builtinFuncs_dfa
from builtinFuncs_dfa import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.DFA import DFA

group = None

secparam = 80


def setup(alphabet):
    hG1 = {}
    hG2 = {}

    gG1 = group.random(G1)
    gG2 = group.random(G2)
    z = group.random(ZR)
    zG1 = (gG1 ** z)
    zG2 = (gG2 ** z)
    hstart = group.random(ZR)
    hstartG1 = (gG1 ** hstart)
    hstartG2 = (gG2 ** hstart)
    hend = group.random(ZR)
    hendG1 = (gG1 ** hend)
    hendG2 = (gG2 ** hend)
    A = len(alphabet)
    for i in range(0, A):
        a = getString(alphabet[i])
        ha = group.random(ZR)
        hG1[a] = (gG1 ** ha)
        hG2[a] = (gG2 ** ha)
    alpha = group.random(ZR)
    egg = (pair(gG1, gG2) ** alpha)
    msk = (gG1 ** -alpha)
    mpk = [egg, gG1, gG2, zG1, zG2, hG1, hG2, hstartG1, hstartG2, hendG1, hendG2]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, Q, T, F):
    K3 = {}
    K2 = {}
    K1 = {}
    KendList2 = {}
    KendList1 = {}
    K3Blinded = {}
    KendList1Blinded = {}
    DG1 = {}
    K1Blinded = {}
    K2Blinded = {}
    KendList2Blinded = {}

    bf0 = group.random(ZR)
    egg, gG1, gG2, zG1, zG2, hG1, hG2, hstartG1, hstartG2, hendG1, hendG2 = mpk
    qlen = len(Q)
    for i in range(0, qlen+1):
        DG1[i] = group.random(G1)
    rstart = group.random(ZR)
    Kstart1 = (DG1[0] * (hstartG1 ** rstart))
    Kstart1Blinded = (Kstart1 ** (1 / bf0))
    Kstart2 = (gG1 ** rstart)
    Kstart2Blinded = (Kstart2 ** (1 / bf0))
    Tlen = len(T)
    for i in range(0, Tlen):
        r = group.random(ZR)
        t = T[i]
        t0 = t[0]
        t1 = t[1]
        t2 = getString(t[2])
        key = hashToKey(t)
        K1[key] = ((DG1[t0] ** -1) * (zG1 ** r))
        K2[key] = (gG1 ** r)
        K3[key] = (DG1[t1] * (hG1[t2] ** r))
    for y in K1:
        K1Blinded[y] = (K1[y] ** (1 / bf0))
    for y in K2:
        K2Blinded[y] = (K2[y] ** (1 / bf0))
    for y in K3:
        K3Blinded[y] = (K3[y] ** (1 / bf0))
    Flen = len(F)
    for i in range(0, Flen):
        x = F[i]
        rx = group.random(ZR)
        KendList1[x] = (msk * (DG1[x] * (hendG1 ** rx)))
        KendList2[x] = (gG1 ** rx)
    for y in KendList1:
        KendList1Blinded[y] = (KendList1[y] ** (1 / bf0))
    for y in KendList2:
        KendList2Blinded[y] = (KendList2[y] ** (1 / bf0))
    skBlinded = [Kstart1Blinded, Kstart2Blinded, KendList1Blinded, KendList2Blinded, K1Blinded, K2Blinded, K3Blinded]
    output = (bf0, skBlinded)
    return output

def encrypt(mpk, w, M):
    C2 = {}
    s = {}
    C1 = {}

    egg, gG1, gG2, zG1, zG2, h, hstartG1, hstartG2, hendG1, hendG2 = mpk
    l = len(w)
    for i in range(0, l+1):
        s[i] = group.random(ZR)
    Cm = (M * (egg ** s[l]))
    C1[0] = (gG2 ** s[0])
    C2[0] = (hstartG2 ** s[0])
    for i in range(1, l+1):
        a = getString(w[i])
        C1[i] = (gG2 ** s[i])
        C2[i] = ((hG2[a] ** s[i]) * (zG2 ** s[i-1]))
    Cend1 = (gG2 ** s[l])
    Cend2 = (hendG2 ** s[l])
    ct = [Cend1, Cend2, w, C1, C2, Cm]
    output = ct
    return output

def transform(skBlinded, ct, dfaM):
    transformOutputListForLoop = {}
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
        transformOutputListForLoop[1000+7*i] = ((pair(C1[j], K1Blinded[key]) * pair((C2[i] ** -1), K2Blinded[key])) * pair(C1[i], K3Blinded[key]))
        result0 = transformOutputListForLoop[1000+7*i]
    x = getAcceptState(Ti)
    transformOutputList[1] = (pair((Cend1 ** -1), KendList1Blinded[x]) * pair(Cend2, KendList2Blinded[x]))
    result1 = transformOutputList[1]
    output = (transformOutputList, l, Ti, transformOutputListForLoop)
    return output

def decout(dfaM, transformOutputList, bf0, l, Ti, transformOutputListForLoop):
    B = {}

    Cm = transformOutputList[3]
    w = transformOutputList[2]
    if ( ( (accept(dfaM, w)) == (False) ) ):
        pass
    B[0] = (transformOutputList[0] ** bf0)
    for i in range(1, l+1):
        pass
        key = hashToKey(Ti[i])
        j = (i - 1)
        result0 = (transformOutputListForLoop[1000+7*i] ** bf0)
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
    #group = PairingGroup(secparam)

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

