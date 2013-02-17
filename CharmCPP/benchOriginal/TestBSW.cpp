#include "TestBSW.h"

void Bsw07::setup(CharmList & mk, CharmList & pk)
{
    G1 gG1 = group.init(G1_t);
    G2 gG2 = group.init(G2_t);
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 hG1 = group.init(G1_t);
    G2 hG2 = group.init(G2_t);
    G1 i = group.init(G1_t);
    GT egg = group.init(GT_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    hG1 = group.exp(gG1, beta);
    hG2 = group.exp(gG2, beta);
    i = group.exp(gG1, alpha);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, hG1);
    pk.insert(3, hG2);
    pk.insert(4, egg);
    return;
}

void Bsw07::keygen(CharmList & pk, CharmList & mk, CharmListStr & S, CharmList & sk)
{
    G1 gG1;
    G2 gG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    ZR beta;
    G1 i;
    ZR r = group.init(ZR_t);
    G1 p0 = group.init(G1_t);
    G1 D = group.init(G1_t);
    int Y = 0;
    ZR sUSy = group.init(ZR_t);
    string y0;
    CharmListG1 Dj;
    CharmListG2 Djp;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    hG1 = pk[2].getG1();
    hG2 = pk[3].getG2();
    egg = pk[4].getGT();
    
    beta = mk[0].getZR();
    i = mk[1].getG1();
    r = group.random(ZR_t);
    p0 = group.exp(hG1, r);
    D = group.exp(group.mul(i, p0), group.div(1, beta));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        sUSy = group.random(ZR_t);
        y0 = S[y];
        Dj.insert(y0, group.mul(p0, group.exp(group.hashListToG1(y0), sUSy)));
        Djp.insert(y0, group.exp(gG2, sUSy));
    }
    sk.insert(0, D);
    sk.insert(1, Dj);
    sk.insert(2, Djp);
    return;
}

void Bsw07::encrypt(CharmList & pk, GT & M, string & policyUSstr, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    Policy policy;
    CharmListStr attrs;
    ZR s = group.init(ZR_t);
    CharmDictZR sh;
    int Y = 0;
    GT Ctl = group.init(GT_t);
    G2 C = group.init(G2_t);
    string y1;
    CharmListG2 Cr;
    CharmListG1 Cpr;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    hG1 = pk[2].getG1();
    hG2 = pk[3].getG2();
    egg = pk[4].getGT();
    policy = util.createPolicy(policyUSstr);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    sh = util.calculateSharesDict(group, s, policy);
    Y = sh.length();
    Ctl = group.mul(M, group.exp(egg, s));
    C = group.exp(hG2, s);
    for (int y = 0; y < Y; y++)
    {
        y1 = attrs[y];
        Cr.insert(y1, group.exp(gG2, sh[y1]));
        Cpr.insert(y1, group.exp(group.hashListToG1(y1), sh[y1]));
    }
    ct.insert(0, policyUSstr);
    ct.insert(1, Ctl);
    ct.insert(2, C);
    ct.insert(3, Cr);
    ct.insert(4, Cpr);
    return;
}

void Bsw07::decrypt(CharmList & pk, CharmList & sk, CharmListStr & S, CharmList & ct, GT & M)
{
    string policyUSstr;
    GT Ctl;
    G2 C;
    CharmListG2 Cr;
    CharmListG1 Cpr;
    G1 D;
    CharmListG1 Dj;
    CharmListG2 Djp;
    Policy policy;
    CharmListStr attrs;
    CharmDictZR coeff;
    int Y = 0;
    GT reservedVarName0 = group.init(GT_t);
    string yGetStringSuffix;
    GT reservedVarName1 = group.init(GT_t);
    GT A = group.init(GT_t);
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    
    policyUSstr = ct[0].strPtr;
    Ctl = ct[1].getGT();
    C = ct[2].getG2();
    Cr = ct[3].getListG2();
    Cpr = ct[4].getListG1();
    
    D = sk[0].getG1();
    Dj = sk[1].getListG1();
    Djp = sk[2].getListG2();
    policy = util.createPolicy(policyUSstr);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    //;
    for (int y = 0; y < Y; y++)
    {
        yGetStringSuffix = GetString(attrs[y]);
        reservedVarName1 = group.exp(group.div(group.pair(Cr[yGetStringSuffix], Dj[yGetStringSuffix]), group.pair(Djp[yGetStringSuffix], Cpr[yGetStringSuffix])), coeff[yGetStringSuffix]);
        reservedVarName0 = group.mul(reservedVarName0, reservedVarName1);
    }
    A = reservedVarName0;
    result0 = group.pair(C, D);
    result1 = group.div(result0, A);
    M = group.div(Ctl, result1);
    return;
}

