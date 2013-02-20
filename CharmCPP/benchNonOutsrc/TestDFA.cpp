#include "TestDFA.h"

void Dfa12::setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk)
{
    G1 g;
    G1 z;
    G1 hstart;
    G1 hend;
    int A = 0;
    string a;
    CharmListG1 h; // fix
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

void Dfa12::keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, CharmList & sk)
{
    GT egg;
    G1 g;
    G1 z;
    CharmListG1 h; // fix
    G1 hstart;
    G1 hend;
    int qlen = 0;
    CharmListG1 D;
    ZR rstart;
    G1 Kstart1;
    G1 Kstart2;
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
    int Flen = 0;
    int x = 0;
    ZR rx;
    CharmListG1 KendList1;
    CharmListG1 KendList2;
    
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
    Kstart2 = group.exp(g, rstart);
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
        K3.insert(key, group.mul(D[t1], group.exp(h[t2], r)));
    }
    Flen = F.length();
    for (int i = 0; i < Flen; i++)
    {
        x = F[i];
        rx = group.random(ZR_t);
        KendList1.insert(x, group.mul(msk, group.mul(D[x], group.exp(hend, rx))));
        KendList2.insert(x, group.exp(g, rx));
    }
    sk.insert(0, Kstart1);
    sk.insert(1, Kstart2);
    sk.insert(2, KendList1);
    sk.insert(3, KendList2);
    sk.insert(4, K1);
    sk.insert(5, K2);
    sk.insert(6, K3);
    return;
}

void Dfa12::encrypt(CharmList & mpk, CharmListStr & w, GT & M, CharmList & ct)
{
    GT egg;
    G1 g;
    G1 z;
    CharmListG1 h; // fix
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
        C2.insert(i, group.mul(group.exp(h[a], s[i]), group.exp(z, s[i-1])));
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

void Dfa12::decrypt(CharmList & sk, CharmList & ct, GT & M, CharmMetaListInt & Ti, int & x) // NO_TYPE & dfaM,
{
    G1 Kstart1;
    G1 Kstart2;
    CharmListG1 KendList1;
    CharmListG1 KendList2;
    CharmListG1 K1;
    CharmListG1 K2;
    CharmListG1 K3;
    G1 Cend1;
    G1 Cend2;
    CharmListStr w;
    CharmListG1 C1;
    CharmListG1 C2;
    GT Cm;
    int l = 0;
//    CharmMetaListInt Ti;
    CharmListGT B;
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
//    int x = 0;
    GT result1 = group.init(GT_t);
    GT Bend = group.init(GT_t);
    
    Kstart1 = sk[0].getG1();
    Kstart2 = sk[1].getG1();
    KendList1 = sk[2].getListG1();
    KendList2 = sk[3].getListG1();
    K1 = sk[4].getListG1();
    K2 = sk[5].getListG1();
    K3 = sk[6].getListG1();
    
    Cend1 = ct[0].getG1();
    Cend2 = ct[1].getG1();
    w = ct[2].getListStr();
    C1 = ct[3].getListG1();
    C2 = ct[4].getListG1();
    Cm = ct[5].getGT();
    l = w.length();
//    if ( ( (dfaUtil.accept(w)) == (false) ) ) // dfaM,
//    {
//        return;
//    }
//    Ti = dfaUtil.getTransitions(w); // dfaM,
    B.insert(0, group.mul(group.pair(C1[0], Kstart1), group.exp(group.pair(C2[0], Kstart2), -1)));
    for (int i = 1; i < l+1; i++)
    {
        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        result0 = group.mul(group.pair(C1[j], K1[key]), group.mul(group.exp(group.pair(C2[i], K2[key]), -1), group.pair(C1[i], K3[key])));
        B.insert(i, group.mul(B[i-1], result0));
    }
//    x = dfaUtil.getAcceptState(Ti);
    result1 = group.mul(group.exp(group.pair(Cend1, KendList1[x]), -1), group.pair(Cend2, KendList2[x]));
    Bend = group.mul(B[l], result1);
    M = group.div(Cm, Bend);
    return;
}

