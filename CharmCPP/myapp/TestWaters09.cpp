#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(MNT160);

SecretUtil util;

void setup(CharmList & msk, CharmList & pk)
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

void keygen(CharmList & pk, CharmList & msk, CharmListStr & S, CharmList & sk)
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
    G2 L = group.init(G2_t);
    int Y = 0;
    string z;
    CharmListG1 Kl;
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    egg = pk[2].getGT();
    g1a = pk[3].getG1();
    g2a = pk[4].getG2();
    
    g1alph = msk[0].getG1();
    g2alph = msk[1].getG2();
    t = group.random(ZR_t);
    K = group.mul(g2alph, group.exp(g2a, t));
    L = group.exp(g2, t);
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        z = S[y];
        Kl.insert(z, group.exp(group.hashListToG1(z), t));
    }
    sk.insert(0, K);
    sk.insert(1, L);
    sk.insert(2, Kl);
    return;
}

void encrypt(CharmList & pk, GT & M, string & policy_str, CharmList & ct)
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

void decrypt(CharmList & pk, CharmList & sk, CharmListStr & S, CharmList & ct, GT & M)
{
    string policy_str;
    GT C;
    G1 Cpr;
    CharmListG1 Cn;
    CharmListG2 Dn;
    G2 K;
    G2 L;
    CharmListG1 Kl;
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
    C = ct[1].getGT();
    Cpr = ct[2].getG1();
    Cn = ct[3].getListG1();
    Dn = ct[4].getListG2();
    
    K = sk[0].getG2();
    L = sk[1].getG2();
    Kl = sk[2].getListG1();
    policy = util.createPolicy(policy_str);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    //;
    for (int y = 0; y < Y; y++)
    {
        yGetStringSuffix = GetString(attrs[y]);
        reservedVarName1 = group.exp(group.mul(group.pair(Cn[yGetStringSuffix], L), group.pair(Kl[yGetStringSuffix], Dn[yGetStringSuffix])), coeff[yGetStringSuffix]);
        reservedVarName0 = group.mul(reservedVarName0, reservedVarName1);
    }
    A = reservedVarName0;
    result0 = group.pair(Cpr, K);
    result1 = group.div(result0, A);
    M = group.div(C, result1);
    return;
}

int main()
{
    CharmList msk, pk, sk, ct;
    CharmListStr S;
    GT M, newM;

    setup(msk, pk);
    S.append("ONE");
    S.append("TWO");

    keygen(pk, msk, S, sk);

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
