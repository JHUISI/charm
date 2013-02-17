#include "TestLWOut.h"

void Lw10::setup(CharmList & gpk)
{
    G1 gG1 = group.init(G1_t);
    G2 gG2 = group.init(G2_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    gpk.insert(0, gG1);
    gpk.insert(1, gG2);
    return;
}

void Lw10::authsetup(CharmList & gpk, CharmListStr & authS, CharmMetaList & msk, CharmMetaList & pk)
{
    G1 gG1 = group.init(G1_t);
    G2 gG2 = group.init(G2_t);
//    G1 gG1;
//    G2 gG2;
    int Y = 0;
    ZR alpha = group.init(ZR_t);
    ZR y = group.init(ZR_t);
    string z;
    GT eggalph = group.init(GT_t);
    G2 gy = group.init(G2_t);
    CharmList tmpList0;
    CharmList tmpList1;
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    
    gG1 = gpk[0].getG1();
    gG2 = gpk[1].getG2();
    Y = authS.length();
    for (int i = 0; i < Y; i++)
    {
        alpha = group.random(ZR_t);
        y = group.random(ZR_t);
        z = authS[i];
        eggalph = group.exp(group.pair(gG1, gG2), alpha);
        gy = group.exp(gG2, y);
        tmpList0.insert(0, alpha);
        tmpList0.insert(1, y);
        msk.insert(z, tmpList0);
        tmpList1.insert(0, eggalph);
        tmpList1.insert(1, gy);
        pk.insert(z, tmpList1);
    }
    return;
}

void Lw10::keygen(CharmList & gpk, CharmMetaList & msk, string & gid, CharmListStr & userS, CharmListZR & blindingFactorKBlinded, CharmList & skBlinded)
{
    string gidBlinded;
    G1 gG1;
    G2 gG2;
    G1 h = group.init(G1_t);
    int Y = 0;
    string z;
    CharmListG1 K;
    CharmListG1 KBlinded;
    gidBlinded = gid;
    
    gG1 = gpk[0].getG1();
    gG2 = gpk[1].getG2();
    h = group.hashListToG1(gidBlinded);
    Y = userS.length();
    for (int i = 0; i < Y; i++)
    {
        z = userS[i];
        K.insert(z, group.mul(group.exp(gG1, msk[z][0].getZR()), group.exp(h, msk[z][1].getZR())));
    }
    CharmListStr K_keys = K.strkeys();
    int K_len = K.length();
    for (int y_var = 0; y_var < K_len; y_var++)
    {
        string y = K_keys[y_var];
        blindingFactorKBlinded.insert(y, group.random(ZR_t));
        KBlinded.insert(y, group.exp(K[y], group.div(1, blindingFactorKBlinded[y])));
    }
    skBlinded.insert(0, gidBlinded);
    skBlinded.insert(1, KBlinded);
    return;
}

void Lw10::encrypt(CharmMetaList & pk, CharmList & gpk, GT & M, string & policy_str, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    Policy policy;
    CharmListStr attrs;
    ZR s = group.init(ZR_t);
    int w = 0;
    CharmDictZR s_sh;
    CharmDictZR w_sh;
    int Y = 0;
    GT egg = group.init(GT_t);
    GT C0 = group.init(GT_t);
    ZR r = group.init(ZR_t);
    string k;
    CharmListGT C1;
    CharmListG2 C2;
    CharmListG2 C3;
    
    gG1 = gpk[0].getG1();
    gG2 = gpk[1].getG2();
    policy = util.createPolicy(policy_str);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    w = 0;
    s_sh = util.calculateSharesDict(group, s, policy);
    w_sh = util.calculateSharesDict(group, w, policy);
    Y = s_sh.length();
    egg = group.pair(gG1, gG2);
    C0 = group.mul(M, group.exp(egg, s));
    for (int y = 0; y < Y; y++)
    {
        r = group.random(ZR_t);
        k = attrs[y];
        C1.insert(k, group.mul(group.exp(egg, s_sh[k]), group.exp(pk[k][0].getGT(), r)));
        C2.insert(k, group.exp(gG2, r));
        C3.insert(k, group.mul(group.exp(pk[k][1].getG2(), r), group.exp(gG2, w_sh[k])));
    }
    ct.insert(0, policy_str);
    ct.insert(1, C0);
    ct.insert(2, C1);
    ct.insert(3, C2);
    ct.insert(4, C3);
    return;
}

void Lw10::transform(CharmList & skBlinded, CharmListStr & userS, CharmList & ct, CharmList & transformOutputList, CharmListStr & attrs, int & Y, CharmList & transformOutputListForLoop)
{
    string policy_str;
    GT C0;
    CharmListGT C1;
    CharmListG2 C2;
    CharmListG2 C3;
    string gidBlinded;
    CharmListG1 KBlinded;
    Policy policy;
    CharmDictZR coeff;
    G1 h_gid = group.init(G1_t);
    string kDecrypt;
    GT result0 = group.init(GT_t);
    GT numerator = group.init(GT_t);
    GT denominator = group.init(GT_t);
    
    policy_str = ct[0].strPtr;
    C0 = ct[1].getGT();
    C1 = ct[2].getListGT();
    C2 = ct[3].getListG2();
    C3 = ct[4].getListG2();
    
    gidBlinded = skBlinded[0].strPtr;
    KBlinded = skBlinded[1].getListG1();
    transformOutputList.insert(1, C0);
    policy = util.createPolicy(policy_str);
    attrs = util.prune(policy, userS);
    coeff = util.getCoefficients(group, policy);
    transformOutputList.insert(0, group.hashListToG1(gidBlinded));
    h_gid = transformOutputList[0].getG1();
    Y = attrs.length();
    for (int y = 0; y < Y; y++)
    {
		//NOP;
        kDecrypt = GetString(attrs[y]);
        transformOutputListForLoop.insert(10+8*y, group.pair(h_gid, C3[kDecrypt]));
        result0 = transformOutputListForLoop[10+8*y].getGT();
        transformOutputListForLoop.insert(11+8*y, group.mul(group.exp(result0, coeff[kDecrypt]), group.exp(C1[kDecrypt], coeff[kDecrypt])));
        numerator = transformOutputListForLoop[11+8*y].getGT();
        transformOutputListForLoop.insert(12+8*y, group.pair(group.exp(KBlinded[kDecrypt], coeff[kDecrypt]), C2[kDecrypt]));
        denominator = transformOutputListForLoop[12+8*y].getGT();
    }
    return;
}

void Lw10::decout(CharmListStr & userS, CharmList & transformOutputList, CharmListZR & blindingFactorKBlinded, CharmListStr & attrs, int Y, CharmList & transformOutputListForLoop, GT & M)
{
    GT C0 = group.init(GT_t);
    G1 h_gid = group.init(G1_t);
    GT dotProd = group.init(GT_t, 1);
    string kDecrypt;
    GT result0 = group.init(GT_t);
    GT numerator = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    C0 = transformOutputList[1].getGT();
    h_gid = transformOutputList[0].getG1();
    group.init(dotProd, 1);
    for (int y = 0; y < Y; y++)
    {
		//NOP;
        kDecrypt = GetString(attrs[y]);
        result0 = transformOutputListForLoop[10+8*y].getGT();
        numerator = transformOutputListForLoop[11+8*y].getGT();
        denominator = group.exp(transformOutputListForLoop[12+8*y].getGT(), blindingFactorKBlinded[kDecrypt]);
        fraction = group.mul(numerator, group.exp(denominator, -1));
        dotProd = group.mul(dotProd, fraction);
    }
    M = group.mul(C0, group.exp(dotProd, -1));
    return;
}

