#include "TestDFAOut.h"

void Dfa12::setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk)
{
    G1 gG1;
    G2 gG2;
    ZR z;
    G1 zG1;
    G2 zG2;
    ZR hstart;
    G1 hstartG1;
    G2 hstartG2;
    ZR hend;
    G1 hendG1;
    G2 hendG2;
    int A = 0;
    string a;
    ZR ha;
    CharmListG1 hG1;
    CharmListG2 hG2;
    ZR alpha;
    GT egg = group.init(GT_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    z = group.random(ZR_t);
    zG1 = group.exp(gG1, z);
    zG2 = group.exp(gG2, z);
    hstart = group.random(ZR_t);
    hstartG1 = group.exp(gG1, hstart);
    hstartG2 = group.exp(gG2, hstart);
    hend = group.random(ZR_t);
    hendG1 = group.exp(gG1, hend);
    hendG2 = group.exp(gG2, hend);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = dfaUtil.getString(alphabet[i]);
        ha = group.random(ZR_t);
        hG1.insert(a, group.exp(gG1, ha));
        hG2.insert(a, group.exp(gG2, ha));
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    msk = group.exp(gG1, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, gG1);
    mpk.insert(2, gG2);
    mpk.insert(3, zG1);
    mpk.insert(4, zG2);
    mpk.insert(5, hG1);
    mpk.insert(6, hG2);
    mpk.insert(7, hstartG1);
    mpk.insert(8, hstartG2);
    mpk.insert(9, hendG1);
    mpk.insert(10, hendG2);
    return;
}

void Dfa12::keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, ZR & bf0, CharmList & skBlinded)
{
    GT egg;
    G1 gG1;
    G2 gG2;
    G1 zG1;
    G2 zG2;
    CharmListG1 hG1;
    CharmListG2 hG2;
    G1 hstartG1;
    G2 hstartG2;
    G1 hendG1;
    G2 hendG2;
    int qlen = 0;
    CharmListG1 DG1;
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
    gG1 = mpk[1].getG1();
    gG2 = mpk[2].getG2();
    zG1 = mpk[3].getG1();
    zG2 = mpk[4].getG2();
    hG1 = mpk[5].getListG1();
    hG2 = mpk[6].getListG2();
    hstartG1 = mpk[7].getG1();
    hstartG2 = mpk[8].getG2();
    hendG1 = mpk[9].getG1();
    hendG2 = mpk[10].getG2();
    qlen = Q.length();
    for (int i = 0; i < qlen+1; i++)
    {
        DG1.insert(i, group.random(G1_t));
    }
    rstart = group.random(ZR_t);
    Kstart1 = group.mul(DG1[0], group.exp(hstartG1, rstart));
    Kstart1Blinded = group.exp(Kstart1, group.div(1, bf0));
    Kstart2 = group.exp(gG1, rstart);
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
        K1.insert(key, group.mul(group.exp(DG1[t0], -1), group.exp(zG1, r)));
        K2.insert(key, group.exp(gG1, r));
        K3.insert(key, group.mul(DG1[t1], group.exp(hG1[t2], r)));
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
        KendList1.insert(x, group.mul(msk, group.mul(DG1[x], group.exp(hendG1, rx))));
        KendList2.insert(x, group.exp(gG1, rx));
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

void Dfa12::encrypt(CharmList & mpk, CharmListStr & w, GT & M, CharmList & ct)
{
    GT egg;
    G1 gG1;
    G2 gG2;
    G1 zG1;
    G2 zG2;
    CharmListG1 hG1;
    CharmListG2 hG2;
    G1 hstartG1;
    G2 hstartG2;
    G1 hendG1;
    G2 hendG2;
    int l = 0;
    CharmListZR s;
    GT Cm = group.init(GT_t);
    CharmListG2 C1;
    CharmListG2 C2;
    string a;
    G2 Cend1;
    G2 Cend2;
    
    egg = mpk[0].getGT();
    gG1 = mpk[1].getG1();
    gG2 = mpk[2].getG2();
    zG1 = mpk[3].getG1();
    zG2 = mpk[4].getG2();
    hG1 = mpk[5].getListG1();
    hG2 = mpk[6].getListG2();
    hstartG1 = mpk[7].getG1();
    hstartG2 = mpk[8].getG2();
    hendG1 = mpk[9].getG1();
    hendG2 = mpk[10].getG2();
    l = w.length();
    for (int i = 0; i < l+1; i++)
    {
        s.insert(i, group.random(ZR_t));
    }
    Cm = group.mul(M, group.exp(egg, s[l]));
    C1.insert(0, group.exp(gG2, s[0]));
    C2.insert(0, group.exp(hstartG2, s[0]));
    for (int i = 1; i < l+1; i++)
    {
        a = dfaUtil.getString(w[i]);
        C1.insert(i, group.exp(gG2, s[i]));
        C2.insert(i, group.mul(group.exp(hG2[a], s[i]), group.exp(zG2, s[i-1])));
    }
    Cend1 = group.exp(gG2, s[l]);
    Cend2 = group.exp(hendG2, s[l]);
    ct.insert(0, Cend1);
    ct.insert(1, Cend2);
    ct.insert(2, w);
    ct.insert(3, C1);
    ct.insert(4, C2);
    ct.insert(5, Cm);
    return;
}

void Dfa12::transform(CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList, int & l, CharmMetaListInt & Ti, int & x, CharmList & transformOutputListForLoop)
{
    G1 Kstart1Blinded;
    G1 Kstart2Blinded;
    CharmListG1 KendList1Blinded;
    CharmListG1 KendList2Blinded;
    CharmListG1 K1Blinded;
    CharmListG1 K2Blinded;
    CharmListG1 K3Blinded;
    G2 Cend1;
    G2 Cend2;
    CharmListStr w;
    CharmListG2 C1;
    CharmListG2 C2;
    GT Cm;
    CharmListGT B;
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
//    int x = 0;
    GT result1 = group.init(GT_t);
    
    Kstart1Blinded = skBlinded[0].getG1();
    Kstart2Blinded = skBlinded[1].getG1();
    KendList1Blinded = skBlinded[2].getListG1();
    KendList2Blinded = skBlinded[3].getListG1();
    K1Blinded = skBlinded[4].getListG1();
    K2Blinded = skBlinded[5].getListG1();
    K3Blinded = skBlinded[6].getListG1();
    
    Cend1 = ct[0].getG2();
    Cend2 = ct[1].getG2();
    w = ct[2].getListStr();
    C1 = ct[3].getListG2();
    C2 = ct[4].getListG2();
    Cm = ct[5].getGT();
    transformOutputList.insert(3, Cm);
    transformOutputList.insert(2, w);
    l = w.length();
//    if ( ( (dfaUtil.accept(dfaM, w)) == (false) ) )
//    {
//
//        return false;
//    }
//    Ti = dfaUtil.getTransitions(dfaM, w);
    transformOutputList.insert(0, group.mul(group.pair(C1[0], Kstart1Blinded), group.pair(group.exp(C2[0], -1), Kstart2Blinded)));
    B.insert(0, transformOutputList[0].getGT());
    for (int i = 1; i < l+1; i++)
    {

        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        transformOutputListForLoop.insert(10+7*i, group.mul(group.mul(group.pair(C1[j], K1Blinded[key]), group.pair(group.exp(C2[i], -1), K2Blinded[key])), group.pair(C1[i], K3Blinded[key])));
        result0 = transformOutputListForLoop[10+7*i].getGT();
    }
//    x = dfaUtil.getAcceptState(Ti);
    transformOutputList.insert(1, group.mul(group.pair(group.exp(Cend1, -1), KendList1Blinded[x]), group.pair(Cend2, KendList2Blinded[x])));
    result1 = transformOutputList[1].getGT();
    return;
}

void Dfa12::decout(CharmList & transformOutputList, ZR & bf0, int l, CharmMetaListInt & Ti, CharmList & transformOutputListForLoop, GT & M)
{
    GT Cm = group.init(GT_t);
    CharmListStr w;
    CharmListGT B;
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    GT Bend = group.init(GT_t);
    Cm = transformOutputList[3].getGT();
    w = transformOutputList[2].getListStr();
//    if ( ( (dfaUtil.accept(dfaM, w)) == (false) ) )
//    {
//    	return;
//    }
    B.insert(0, group.exp(transformOutputList[0].getGT(), bf0));
    for (int i = 1; i < l+1; i++)
    {

        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        result0 = group.exp(transformOutputListForLoop[10+7*i].getGT(), bf0);
        B.insert(i, group.mul(B[i-1], result0));
    }
    result1 = group.exp(transformOutputList[1].getGT(), bf0);
    Bend = group.mul(B[l], result1);
    M = group.mul(Cm, group.exp(Bend, -1));
    return;
}

