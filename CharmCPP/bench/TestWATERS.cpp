#include "TestWATERS.h"

void Waters09::setup(CharmList & msk, CharmList & pk)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    ZR alpha = group.init(ZR_t);
    ZR a = group.init(ZR_t);
    GT egg = group.init(GT_t);
    G1 g1alph = group.init(G1_t);
    G2 g2alph = group.init(G2_t);
    G1 g1a = group.init(G1_t);
    G2 g2a = group.init(G2_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    a = group.random(ZR_t);
    egg = group.exp(group.pair(g1, g2), alpha);
    g1alph = group.exp(g1, alpha);
    g2alph = group.exp(g2, alpha);
    g1a = group.exp(g1, a);
    g2a = group.exp(g2, a);
    msk.insert(0, g1alph);
    msk.insert(1, g2alph);
    pk.insert(0, g1);
    pk.insert(1, g2);
    pk.insert(2, egg);
    pk.insert(3, g1a);
    pk.insert(4, g2a);
    return;
}

void Waters09::keygen(CharmList & pk, CharmList & msk, CharmListStr & S, ZR & bf0, CharmList & skBlinded)
{
    G1 g1;
    G2 g2;
    GT egg;
    G1 g1a;
    G2 g2a;
    G1 g1alph;
    G2 g2alph;
    ZR t = group.init(ZR_t);
    G2 K = group.init(G2_t);
    G2 KBlinded = group.init(G2_t);
    G2 L = group.init(G2_t);
    G2 LBlinded = group.init(G2_t);
    int Y = 0;
    string z;
    CharmListG1 Kl;
    CharmListG1 KlBlinded;
    bf0 = group.random(ZR_t);
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    egg = pk[2].getGT();
    g1a = pk[3].getG1();
    g2a = pk[4].getG2();
    
    g1alph = msk[0].getG1();
    g2alph = msk[1].getG2();
    t = group.random(ZR_t);
    K = group.mul(g2alph, group.exp(g2a, t));
    KBlinded = group.exp(K, group.div(1, bf0));
    L = group.exp(g2, t);
    LBlinded = group.exp(L, group.div(1, bf0));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        z = S[y];
        Kl.insert(z, group.exp(group.hashListToG1(z), t));
    }
    CharmListStr Kl_keys = Kl.strkeys();
    int Kl_len = Kl.length();
    for (int y_var = 0; y_var < Kl_len; y_var++)
    {
        string y = Kl_keys[y_var];
        KlBlinded.insert(y, group.exp(Kl[y], group.div(1, bf0)));
    }
    skBlinded.insert(0, KBlinded);
    skBlinded.insert(1, LBlinded);
    skBlinded.insert(2, KlBlinded);
    return;
}

void Waters09::encrypt(CharmList & pk, GT & M, string & policy_str, CharmList & ct)
{
    G1 g1;
    G2 g2;
    GT egg;
    G1 g1a;
    G2 g2a;
    Policy policy;
    CharmListStr attrs;
    ZR s = group.init(ZR_t);
    CharmListZR sh;
    int Y = 0;
    GT C = group.init(GT_t);
    G1 Cpr = group.init(G1_t);
    ZR r = group.init(ZR_t);
    string k;
    ZR x = group.init(ZR_t);
    CharmListG1 Cn;
    CharmListG2 Dn;
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    egg = pk[2].getGT();
    g1a = pk[3].getG1();
    g2a = pk[4].getG2();
    policy = util.createPolicy(policy_str);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    sh = util.calculateSharesList(group, s, policy);
    Y = sh.length();
    C = group.mul(M, group.exp(egg, s));
    Cpr = group.exp(g1, s);
    for (int y = 0; y < Y; y++)
    {
        r = group.random(ZR_t);
        k = attrs[y];
        x = sh[y];
        Cn.insert(k, group.mul(group.exp(g1a, x), group.exp(group.hashListToG1(k), group.neg(r))));
        Dn.insert(k, group.exp(g2, r));
    }
    ct.insert(0, policy_str);
    ct.insert(1, C);
    ct.insert(2, Cpr);
    ct.insert(3, Cn);
    ct.insert(4, Dn);
    return;
}

void Waters09::transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList)
{
    string policy_str;
    GT C;
    G1 Cpr;
    CharmListG1 Cn;
    CharmListG2 Dn;
    G2 KBlinded;
    G2 LBlinded;
    CharmListG1 KlBlinded;
    Policy policy;
    CharmListStr attrs;
    CharmDictZR coeff;
    int Y = 0;
    GT reservedVarName0 = group.init(GT_t);
    string yGetStringSuffix;
    CharmList transformOutputListForLoop;
    GT reservedVarName1 = group.init(GT_t);
    GT A = group.init(GT_t);
    GT result0 = group.init(GT_t);
    
    policy_str = ct[0].strPtr;
    C = ct[1].getGT();
    Cpr = ct[2].getG1();
    Cn = ct[3].getListG1();
    Dn = ct[4].getListG2();
    
    KBlinded = skBlinded[0].getG2();
    LBlinded = skBlinded[1].getG2();
    KlBlinded = skBlinded[2].getListG1();
    transformOutputList.insert(3, C);
    policy = util.createPolicy(policy_str);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    transformOutputList.insert(0, group.init(GT_t));
    reservedVarName0 = transformOutputList[0].getGT();
    for (int y = 0; y < Y; y++)
    {
		//NOP;
        yGetStringSuffix = GetString(attrs[y]);
        transformOutputListForLoop.insert(10+5*y, group.mul(group.pair(group.exp(Cn[yGetStringSuffix], coeff[yGetStringSuffix]), LBlinded), group.pair(group.exp(KlBlinded[yGetStringSuffix], coeff[yGetStringSuffix]), Dn[yGetStringSuffix])));
        reservedVarName1 = transformOutputListForLoop[10+5*y].getGT();
        transformOutputListForLoop.insert(11+5*y, group.mul(reservedVarName0, reservedVarName1));
        reservedVarName0 = transformOutputListForLoop[11+5*y].getGT();
    }
    transformOutputList.insert(1, reservedVarName0);
    A = transformOutputList[1].getGT();
    transformOutputList.insert(2, group.pair(Cpr, KBlinded));
    result0 = transformOutputList[2].getGT();
    return;
}

void Waters09::decout(CharmList & pk, CharmListStr & S, CharmList & transformOutputList, ZR & bf0, GT & M)
{
    GT C = group.init(GT_t);
    GT reservedVarName0 = group.init(GT_t);
    GT A = group.init(GT_t);
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    C = transformOutputList[3].getGT();
    reservedVarName0 = transformOutputList[0].getGT();
    A = group.exp(transformOutputList[1].getGT(), bf0);
    result0 = group.exp(transformOutputList[2].getGT(), bf0);
    result1 = group.mul(result0, group.exp(A, -1));
    M = group.mul(C, group.exp(result1, -1));
    return;
}

