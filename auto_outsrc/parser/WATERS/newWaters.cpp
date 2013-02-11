#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(AES_SECURITY);

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

void keygen(CharmList & pk, CharmList & msk, CharmListStr & S, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
    ZR zz = group.init(ZR_t);
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
    G1 KlBlinded = group.init(G1_t);
    blindingFactor0Blinded = group.random(ZR_t);
    zz = group.random(ZR_t);
    
    g1 = pk[0].getG1();
    g2 = pk[1].getG2();
    egg = pk[2].getGT();
    g1a = pk[3].getG1();
    g2a = pk[4].getG2();
    
    g1alph = msk[0].getG1();
    g2alph = msk[1].getG2();
    t = group.random(ZR_t);
    K = group.mul(g2alph, group.exp(g2a, t));
    KBlinded = group.exp(K, group.div(1, blindingFactor0Blinded));
    L = group.exp(g2, t);
    LBlinded = L;
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        z = S[y];
        Kl.insert(z, group.exp(group.hashListToG1(z), t));
    }
    KlBlinded = Kl;
    skBlinded.insert(0, KBlinded);
    skBlinded.insert(1, LBlinded);
    skBlinded.insert(2, KlBlinded);
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

void transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList, Policy & policy, CharmDictZR & coeff)
{
