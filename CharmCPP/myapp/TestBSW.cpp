#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(SS512);

SecretUtil util;

void setup(CharmList & mk, CharmList & pk)
{
    G1 g = group.init(G1_t);
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 h = group.init(G1_t);
    G1 f = group.init(G1_t);
    G1 i = group.init(G1_t);
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    h = group.exp(g, beta);
    f = group.exp(g, group.div(1, beta));
    i = group.exp(g, alpha);
    egg = group.exp(group.pair(g, g), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, g);
    pk.insert(1, h);
    pk.insert(2, f);
    pk.insert(3, egg);
    return;
}

void keygen(CharmList & pk, CharmList & mk, CharmListStr & S, CharmList & sk)
{
    G1 g;
    G1 h;
    G1 f;
    GT egg;
    ZR beta;
    G1 i;
    ZR r = group.init(ZR_t);
    G1 p0 = group.init(G1_t);
    G1 D = group.init(G1_t);
    int Y = 0;
    ZR s_y = group.init(ZR_t);
    string y0;
    CharmListG1 Dj;
    CharmListG1 Djp;
    
    g = pk[0].getG1();
    h = pk[1].getG1();
    f = pk[2].getG1();
    egg = pk[3].getGT();
    
    beta = mk[0].getZR();
    i = mk[1].getG1();
    r = group.random(ZR_t);
    p0 = group.exp(h, r);
    D = group.exp(group.mul(i, p0), group.div(1, beta));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        s_y = group.random(ZR_t);
        y0 = S[y];
        Dj.insert(y0, group.mul(p0, group.exp(group.hashListToG1(y0), s_y)));
        Djp.insert(y0, group.exp(g, s_y));
    }
    sk.insert(0, D);
    sk.insert(1, Dj);
    sk.insert(2, Djp);
    return;
}

void encrypt(CharmList & pk, GT & M, string & policy_str, CharmList & ct)
{
    G1 g;
    G1 h;
    G1 f;
    GT egg;
    Policy policy;
    CharmListStr attrs;
    ZR s = group.init(ZR_t);
    CharmDictZR sh;
    int Y = 0;
    GT Ctl = group.init(GT_t);
    G1 C = group.init(G1_t);
    string y1;
    CharmListG1 Cr;
    CharmListG1 Cpr;
    
    g = pk[0].getG1();
    h = pk[1].getG1();
    f = pk[2].getG1();
    egg = pk[3].getGT();
    policy = util.createPolicy(policy_str);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    sh = util.calculateSharesDict(group, s, policy);
    Y = sh.length();
    Ctl = group.mul(M, group.exp(egg, s));
    C = group.exp(h, s);
    for (int y = 0; y < Y; y++)
    {
        y1 = attrs[y];
        Cr.insert(y1, group.exp(g, sh[y1]));
        Cpr.insert(y1, group.exp(group.hashListToG1(y1), sh[y1]));
    }
    ct.insert(0, policy_str);
    ct.insert(1, Ctl);
    ct.insert(2, C);
    ct.insert(3, Cr);
    ct.insert(4, Cpr);
    return;
}

void decrypt(CharmList & pk, CharmList & sk, CharmListStr & S, CharmList & ct, GT & M)
{
    string policy_str;
    GT Ctl;
    G1 C;
    CharmListG1 Cr;
    CharmListG1 Cpr;
    G1 D;
    CharmListG1 Dj;
    CharmListG1 Djp;
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
    
    policy_str = ct[0].strPtr;
    Ctl = ct[1].getGT();
    C = ct[2].getG1();
    Cr = ct[3].getListG1();
    Cpr = ct[4].getListG1();
    
    D = sk[0].getG1();
    Dj = sk[1].getListG1();
    Djp = sk[2].getListG1();
    policy = util.createPolicy(policy_str);
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

int main()
{
    CharmList mk, pk, sk, ct;
    CharmListStr S;
    GT M, newM;

    setup(mk, pk);
    S.append("ONE");
    S.append("TWO");

    keygen(pk, mk, S, sk);

    M = group.random(GT_t);
    string policy_str = "(ONE and TWO)";
    encrypt(pk, M, policy_str, ct);

    decrypt(pk, sk, S, ct, newM);
    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return 0;
}
