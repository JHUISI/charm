#include "TestBSWOut.h"

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

void Bsw07::keygen(CharmList & pk, CharmList & mk, CharmListStr & S, ZR & bf0, CharmList & skBlinded)
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
    G1 DBlinded = group.init(G1_t);
    int Y = 0;
    ZR sUSy = group.init(ZR_t);
    string y0;
    CharmListG1 Dj;
    CharmListG2 Djp;
    CharmListG1 DjBlinded;
    CharmListG2 DjpBlinded;
    bf0 = group.random(ZR_t);
    
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
    DBlinded = group.exp(D, group.div(1, bf0));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        sUSy = group.random(ZR_t);
        y0 = S[y];
        Dj.insert(y0, group.mul(p0, group.exp(group.hashListToG1(y0), sUSy)));
        Djp.insert(y0, group.exp(gG2, sUSy));
    }
    CharmListStr Dj_keys = Dj.strkeys();
    int Dj_len = Dj_keys.length();
    for (int y_var = 0; y_var < Dj_len; y_var++)
    {
        string y = Dj_keys[y_var];
        DjBlinded.insert(y, group.exp(Dj[y], group.div(1, bf0)));
    }
    CharmListStr Djp_keys = Djp.strkeys();
    int Djp_len = Djp_keys.length();
    for (int y_var = 0; y_var < Djp_len; y_var++)
    {
        string y = Djp_keys[y_var];
        DjpBlinded.insert(y, group.exp(Djp[y], group.div(1, bf0)));
    }
    skBlinded.insert(0, DBlinded);
    skBlinded.insert(1, DjBlinded);
    skBlinded.insert(2, DjpBlinded);
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

void Bsw07::transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList)
{
    string policyUSstr;
    GT Ctl;
    G2 C;
    CharmListG2 Cr;
    CharmListG1 Cpr;
    G1 DBlinded;
    CharmListG1 DjBlinded;
    CharmListG2 DjpBlinded;
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
    
    policyUSstr = ct[0].strPtr;
    Ctl = ct[1].getGT();
    C = ct[2].getG2();
    Cr = ct[3].getListG2();
    Cpr = ct[4].getListG1();
    
    DBlinded = skBlinded[0].getG1();
    DjBlinded = skBlinded[1].getListG1();
    DjpBlinded = skBlinded[2].getListG2();
    transformOutputList.insert(3, Ctl);
    policy = util.createPolicy(policyUSstr);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    transformOutputList.insert(0, group.init(GT_t));
    reservedVarName0 = transformOutputList[0].getGT();
    for (int y = 0; y < Y; y++)
    {
		//NOP;
        yGetStringSuffix = GetString(attrs[y]);
        transformOutputListForLoop.insert(10+5*y, group.mul(group.pair(group.exp(Cr[yGetStringSuffix], coeff[yGetStringSuffix]), DjBlinded[yGetStringSuffix]), group.pair(group.exp(DjpBlinded[yGetStringSuffix], group.neg(coeff[yGetStringSuffix])), Cpr[yGetStringSuffix])));
        reservedVarName1 = transformOutputListForLoop[10+5*y].getGT();
        transformOutputListForLoop.insert(11+5*y, group.mul(reservedVarName0, reservedVarName1));
        reservedVarName0 = transformOutputListForLoop[11+5*y].getGT();
    }
    transformOutputList.insert(1, reservedVarName0);
    A = transformOutputList[1].getGT();
    transformOutputList.insert(2, group.pair(C, DBlinded));
    result0 = transformOutputList[2].getGT();
    return;
}

void Bsw07::decout(CharmList & pk, CharmListStr & S, CharmList & transformOutputList, ZR & bf0, GT & M)
{
    GT Ctl = group.init(GT_t);
    GT reservedVarName0 = group.init(GT_t);
    GT A = group.init(GT_t);
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    Ctl = transformOutputList[3].getGT();
    reservedVarName0 = transformOutputList[0].getGT();
    A = group.exp(transformOutputList[1].getGT(), bf0);
    result0 = group.exp(transformOutputList[2].getGT(), bf0);
    result1 = group.mul(result0, group.exp(A, -1));
    M = group.mul(Ctl, group.exp(result1, -1));
    return;
}

