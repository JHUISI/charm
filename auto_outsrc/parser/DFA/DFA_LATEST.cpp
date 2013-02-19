#include "DFA/DFA_LATEST.h"

void Dfa12::setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk)
{
    G1 g;
    G1 z;
    G1 hstart;
    G1 hend;
    int A = 0;
    string a;
    NO TYPE FOUND FOR h
    ZR alpha;
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    z = group.random(G1_t);
    hstart = group.random(G1_t);
    hend = group.random(G1_t);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = dfaUtil.getString(alphabet[i]);
        h.insert(a, group.random(G1_t));
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(g, g), alpha);
    msk = group.exp(g, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, g);
    mpk.insert(2, z);
    mpk.insert(3, h);
    mpk.insert(4, hstart);
    mpk.insert(5, hend);
    return;
}

void Dfa12::keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, ZR & bf0, CharmList & skBlinded)
{
    GT egg;
    G1 g;
    G1 z;
    NO TYPE FOUND FOR h
    G1 hstart;
    G1 hend;
    int qlen = 0;
    CharmListG1 D;
    ZR rstart;
    G1 Kstart1;
    G1 Kstart1Blinded;
    G1 Kstart2;
    G1 Kstart2Blinded;
    int Tlen = 0;
    ZR r;
    CharmListInt t;
    int t0 = 0;
    int t1 = 0;
    string t2;
    string key;
    CharmListG1 K1;
    CharmListG1 K2;
    CharmListG1 K3;
    CharmListG1 K1Blinded;
    CharmListG1 K2Blinded;
    CharmListG1 K3Blinded;
    int Flen = 0;
    int x = 0;
    ZR rx;
    CharmListG1 KendList1;
    CharmListG1 KendList2;
    CharmListG1 KendList1Blinded;
    CharmListG1 KendList2Blinded;
    bf0 = group.random(ZR_t);
    
    egg = mpk[0].getGT();
    g = mpk[1].getG1();
    z = mpk[2].getG1();
    h = mpk[3].getListG1();
    hstart = mpk[4].getG1();
    hend = mpk[5].getG1();
    qlen = Q.length();
    for (int i = 0; i < qlen+1; i++)
    {
        D.insert(i, group.random(G1_t));
    }
    rstart = group.random(ZR_t);
    Kstart1 = group.mul(D[0], group.exp(hstart, rstart));
    Kstart1Blinded = group.exp(Kstart1, group.div(1, bf0));
    Kstart2 = group.exp(g, rstart);
    Kstart2Blinded = group.exp(Kstart2, group.div(1, bf0));
    Tlen = T.length();
    for (int i = 0; i < Tlen; i++)
    {
        r = group.random(ZR_t);
        t = T[i];
        t0 = t[0];
        t1 = t[1];
        t2 = dfaUtil.getString(t[2]);
        key = dfaUtil.hashToKey(t);
        K1.insert(key, group.mul(group.exp(D[t0], -1), group.exp(z, r)));
        K2.insert(key, group.exp(g, r));
        K3.insert(key, group.mul(D[t1], group.exp(h[t2].getG1(), r)));
    }
    CharmListStr K1_keys = K1.strkeys();
    int K1_len = K1_keys.length();
    for (int y_var = 0; y_var < K1_len; y_var++)
    {
        string y = K1_keys[y_var];
        K1Blinded.insert(y, group.exp(K1[y], group.div(1, bf0)));
    }
    CharmListStr K2_keys = K2.strkeys();
    int K2_len = K2_keys.length();
    for (int y_var = 0; y_var < K2_len; y_var++)
    {
        string y = K2_keys[y_var];
        K2Blinded.insert(y, group.exp(K2[y], group.div(1, bf0)));
    }
    CharmListStr K3_keys = K3.strkeys();
    int K3_len = K3_keys.length();
    for (int y_var = 0; y_var < K3_len; y_var++)
    {
        string y = K3_keys[y_var];
        K3Blinded.insert(y, group.exp(K3[y], group.div(1, bf0)));
    }
    Flen = F.length();
    for (int i = 0; i < Flen; i++)
    {
        x = F[i];
        rx = group.random(ZR_t);
        KendList1.insert(x, group.mul(msk, group.mul(D[x], group.exp(hend, rx))));
        KendList2.insert(x, group.exp(g, rx));
    }
    CharmListInt KendList1_keys = KendList1.keys();
    int KendList1_len = KendList1_keys.length();
    for (int y_var = 0; y_var < KendList1_len; y_var++)
    {
        int y = KendList1_keys[y_var];
        KendList1Blinded.insert(y, group.exp(KendList1[y], group.div(1, bf0)));
    }
    CharmListInt KendList2_keys = KendList2.keys();
    int KendList2_len = KendList2_keys.length();
    for (int y_var = 0; y_var < KendList2_len; y_var++)
    {
        int y = KendList2_keys[y_var];
        KendList2Blinded.insert(y, group.exp(KendList2[y], group.div(1, bf0)));
    }
    skBlinded.insert(0, Kstart1Blinded);
    skBlinded.insert(1, Kstart2Blinded);
    skBlinded.insert(2, KendList1Blinded);
    skBlinded.insert(3, KendList2Blinded);
    skBlinded.insert(4, K1Blinded);
    skBlinded.insert(5, K2Blinded);
    skBlinded.insert(6, K3Blinded);
    return;
}

void Dfa12::encrypt(CharmList & mpk, string & w, GT & M, CharmList & ct)
{
    GT egg;
    G1 g;
    G1 z;
    NO TYPE FOUND FOR h
    G1 hstart;
    G1 hend;
    int l = 0;
    CharmListZR s;
    GT Cm = group.init(GT_t);
    CharmListG1 C1;
    CharmListG1 C2;
    string a;
    G1 Cend1;
    G1 Cend2;
    
    egg = mpk[0].getGT();
    g = mpk[1].getG1();
    z = mpk[2].getG1();
    h = mpk[3].getListG1();
    hstart = mpk[4].getG1();
    hend = mpk[5].getG1();
    l = w.length();
    for (int i = 0; i < l+1; i++)
    {
        s.insert(i, group.random(ZR_t));
    }
    Cm = group.mul(M, group.exp(egg, s[l]));
    C1.insert(0, group.exp(g, s[0]));
    C2.insert(0, group.exp(hstart, s[0]));
    for (int i = 1; i < l+1; i++)
    {
        a = dfaUtil.getString(w[i]);
        C1.insert(i, group.exp(g, s[i]));
        C2.insert(i, group.mul(group.exp(h[a].getG1(), s[i]), group.exp(z, s[i-1])));
    }
    Cend1 = group.exp(g, s[l]);
    Cend2 = group.exp(hend, s[l]);
    ct.insert(0, Cend1);
    ct.insert(1, Cend2);
    ct.insert(2, w);
    ct.insert(3, C1);
    ct.insert(4, C2);
    ct.insert(5, Cm);
    return;
}

void Dfa12::transform(CharmList & skBlinded, CharmList & ct, NO_TYPE & dfaM, CharmList & transformOutputList, int & l, CharmMetaListInt & Ti, CharmList & transformOutputListForLoop)
{
    G1 Kstart1Blinded;
    G1 Kstart2Blinded;
    CharmListG1 KendList1Blinded;
    CharmListG1 KendList2Blinded;
    CharmListG1 K1Blinded;
    CharmListG1 K2Blinded;
    CharmListG1 K3Blinded;
    G1 Cend1;
    G1 Cend2;
    string w;
    CharmListG1 C1;
    CharmListG1 C2;
    GT Cm;
    NO TYPE FOUND FOR B
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
    int x = 0;
    GT result1 = group.init(GT_t);
    
    Kstart1Blinded = skBlinded[0].getG1();
    Kstart2Blinded = skBlinded[1].getG1();
    KendList1Blinded = skBlinded[2].getListG1();
    KendList2Blinded = skBlinded[3].getListG1();
    K1Blinded = skBlinded[4].getListG1();
    K2Blinded = skBlinded[5].getListG1();
    K3Blinded = skBlinded[6].getListG1();
    
    Cend1 = ct[0].getG1();
    Cend2 = ct[1].getG1();
    w = ct[2].strPtr;
    C1 = ct[3].getListG1();
    C2 = ct[4].getListG1();
    Cm = ct[5].getGT();
    transformOutputList.insert(3, Cm);
    transformOutputList.insert(2, w);
    l = w.length();
    if ( ( (dfaUtil.accept(dfaM, w)) == (false) ) )
    {

        return false;
    }
    Ti = dfaUtil.getTransitions(dfaM, w);
    transformOutputList.insert(0, group.mul(group.pair(C1[0].getG1(), Kstart1Blinded), group.pair(group.exp(C2[0].getG1(), -1), Kstart2Blinded)));
    B.insert(0, transformOutputList[0]);
    for (int i = 1; i < l+1; i++)
    {

        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        transformOutputListForLoop.insert(1000+7*i, group.mul(group.mul(group.pair(C1[j].getG1(), K1Blinded[key]), group.pair(group.exp(C2[i].getG1(), -1), K2Blinded[key])), group.pair(C1[i].getG1(), K3Blinded[key])));
        result0 = transformOutputListForLoop[1000+7*i].getGT();
    }
    x = dfaUtil.getAcceptState(Ti);
    transformOutputList.insert(1, group.mul(group.pair(group.exp(Cend1, -1), KendList1Blinded[x]), group.pair(Cend2, KendList2Blinded[x])));
    result1 = transformOutputList[1].getGT();
    return;
}

void Dfa12::decout(NO_TYPE & dfaM, CharmList & transformOutputList, ZR & bf0, int l, CharmMetaListInt & Ti, CharmList & transformOutputListForLoop, GT & M)
{
    GT Cm = group.init(GT_t);
    string w;
    NO TYPE FOUND FOR B
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    GT Bend = group.init(GT_t);
    Cm = transformOutputList[3].getGT();
    w = transformOutputList[2];
    if ( ( (dfaUtil.accept(dfaM, w)) == (false) ) )
    {

    }
    B.insert(0, group.exp(transformOutputList[0], bf0));
    for (int i = 1; i < l+1; i++)
    {

        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        result0 = group.exp(transformOutputListForLoop[1000+7*i].getGT(), bf0);
        B.insert(i, group.mul(B[i-1], result0));
    }
    result1 = group.exp(transformOutputList[1].getGT(), bf0);
    Bend = group.mul(B[l], result1);
    M = group.mul(Cm, group.exp(Bend, -1));
    return;
}

