#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(CharmList & mpk, CharmList & msk)
{
    G1 g = group.init(G1_t);
    G1 w = group.init(G1_t);
    G1 u = group.init(G1_t);
    G1 h = group.init(G1_t);
    G1 v = group.init(G1_t);
    G1 v1 = group.init(G1_t);
    G1 v2 = group.init(G1_t);
    ZR a1 = group.init(ZR_t);
    ZR a2 = group.init(ZR_t);
    ZR b = group.init(ZR_t);
    ZR alpha = group.init(ZR_t);
    G1 gb = group.init(G1_t);
    G1 ga1 = group.init(G1_t);
    G1 ga2 = group.init(G1_t);
    G1 gba1 = group.init(G1_t);
    G1 gba2 = group.init(G1_t);
    G1 tau1 = group.init(G1_t);
    G1 tau2 = group.init(G1_t);
    G1 tau1b = group.init(G1_t);
    G1 tau2b = group.init(G1_t);
    GT egga = group.init(GT_t);
    G1 galpha = group.init(G1_t);
    G1 galphaUSa1 = group.init(G1_t);
    g = group.random(G1_t);
    w = group.random(G1_t);
    u = group.random(G1_t);
    h = group.random(G1_t);
    v = group.random(G1_t);
    v1 = group.random(G1_t);
    v2 = group.random(G1_t);
    a1 = group.random(ZR_t);
    a2 = group.random(ZR_t);
    b = group.random(ZR_t);
    alpha = group.random(ZR_t);
    gb = group.exp(g, b);
    ga1 = group.exp(g, a1);
    ga2 = group.exp(g, a2);
    gba1 = group.exp(gb, a1);
    gba2 = group.exp(gb, a2);
    tau1 = group.mul(v, group.exp(v1, a1));
    tau2 = group.mul(v, group.exp(v2, a2));
    tau1b = group.exp(tau1, b);
    tau2b = group.exp(tau2, b);
    egga = group.exp(group.pair(g, g), group.mul(alpha, group.mul(a1, b)));
    galpha = group.exp(g, alpha);
    galphaUSa1 = group.exp(galpha, a1);
    mpk.insert(0, g);
    mpk.insert(1, gb);
    mpk.insert(2, ga1);
    mpk.insert(3, ga2);
    mpk.insert(4, gba1);
    mpk.insert(5, gba2);
    mpk.insert(6, tau1);
    mpk.insert(7, tau2);
    mpk.insert(8, tau1b);
    mpk.insert(9, tau2b);
    mpk.insert(10, w);
    mpk.insert(11, u);
    mpk.insert(12, h);
    mpk.insert(13, egga);
    msk.insert(0, galpha);
    msk.insert(1, galphaUSa1);
    msk.insert(2, v);
    msk.insert(3, v1);
    msk.insert(4, v2);
    msk.insert(5, alpha);
    return;
}

void keygen(CharmList & mpk, CharmList & msk, string & id, ZR & bf0, ZR & bf8, CharmList & skBlinded)
{
    string idBlinded;
    G1 g;
    G1 gb;
    G1 ga1;
    G1 ga2;
    G1 gba1;
    G1 gba2;
    G1 tau1;
    G1 tau2;
    G1 tau1b;
    G1 tau2b;
    G1 w;
    G1 u;
    G1 h;
    GT egga;
    G1 galpha;
    G1 galphaUSa1;
    G1 v;
    G1 v1;
    G1 v2;
    ZR alpha;
    ZR r1 = group.init(ZR_t);
    ZR r2 = group.init(ZR_t);
    ZR z1 = group.init(ZR_t);
    ZR z2 = group.init(ZR_t);
    ZR tagUSk = group.init(ZR_t);
    ZR tagUSkBlinded = group.init(ZR_t);
    ZR r = group.init(ZR_t);
    ZR idUShash = group.init(ZR_t);
    G1 D1 = group.init(G1_t);
    G1 D1Blinded = group.init(G1_t);
    G1 D2 = group.init(G1_t);
    G1 D2Blinded = group.init(G1_t);
    G1 D3 = group.init(G1_t);
    G1 D3Blinded = group.init(G1_t);
    G1 D4 = group.init(G1_t);
    G1 D4Blinded = group.init(G1_t);
    G1 D5 = group.init(G1_t);
    G1 D5Blinded = group.init(G1_t);
    G1 D6 = group.init(G1_t);
    G1 D6Blinded = group.init(G1_t);
    G1 D7 = group.init(G1_t);
    G1 D7Blinded = group.init(G1_t);
    G1 K = group.init(G1_t);
    G1 KBlinded = group.init(G1_t);
    bf0 = group.random(ZR_t);
    bf8 = group.random(ZR_t);
    idBlinded = id;
    
    g = mpk[0].getG1();
    gb = mpk[1].getG1();
    ga1 = mpk[2].getG1();
    ga2 = mpk[3].getG1();
    gba1 = mpk[4].getG1();
    gba2 = mpk[5].getG1();
    tau1 = mpk[6].getG1();
    tau2 = mpk[7].getG1();
    tau1b = mpk[8].getG1();
    tau2b = mpk[9].getG1();
    w = mpk[10].getG1();
    u = mpk[11].getG1();
    h = mpk[12].getG1();
    egga = mpk[13].getGT();
    
    galpha = msk[0].getG1();
    galphaUSa1 = msk[1].getG1();
    v = msk[2].getG1();
    v1 = msk[3].getG1();
    v2 = msk[4].getG1();
    alpha = msk[5].getZR();
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    z1 = group.random(ZR_t);
    z2 = group.random(ZR_t);
    tagUSk = group.random(ZR_t);
    tagUSkBlinded = group.exp(tagUSk, group.div(1, bf8));
    r = group.add(r1, r2);
    idUShash = group.hashListToZR(idBlinded);
    D1 = group.mul(galphaUSa1, group.exp(v, r));
    D1Blinded = group.exp(D1, group.div(1, bf0));
    D2 = group.mul(group.mul(group.exp(g, group.neg(alpha)), group.exp(v1, r)), group.exp(g, z1));
    D2Blinded = group.exp(D2, group.div(1, bf0));
    D3 = group.exp(gb, group.neg(z1));
    D3Blinded = group.exp(D3, group.div(1, bf0));
    D4 = group.mul(group.exp(v2, r), group.exp(g, z2));
    D4Blinded = group.exp(D4, group.div(1, bf0));
    D5 = group.exp(gb, group.neg(z2));
    D5Blinded = group.exp(D5, group.div(1, bf0));
    D6 = group.exp(gb, r2);
    D6Blinded = group.exp(D6, group.div(1, bf0));
    D7 = group.exp(g, r1);
    D7Blinded = group.exp(D7, group.div(1, bf0));
    K = group.exp(group.mul(group.mul(group.exp(u, idUShash), group.exp(w, tagUSkBlinded)), h), r1);
    KBlinded = group.exp(K, group.div(1, bf0));
    skBlinded.insert(0, idBlinded);
    skBlinded.insert(1, D1Blinded);
    skBlinded.insert(2, D2Blinded);
    skBlinded.insert(3, D3Blinded);
    skBlinded.insert(4, D4Blinded);
    skBlinded.insert(5, D5Blinded);
    skBlinded.insert(6, D6Blinded);
    skBlinded.insert(7, D7Blinded);
    skBlinded.insert(8, KBlinded);
    skBlinded.insert(9, tagUSkBlinded);
    return;
}

void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct)
{
    G1 g;
    G1 gb;
    G1 ga1;
    G1 ga2;
    G1 gba1;
    G1 gba2;
    G1 tau1;
    G1 tau2;
    G1 tau1b;
    G1 tau2b;
    G1 w;
    G1 u;
    G1 h;
    GT egga;
    ZR s1 = group.init(ZR_t);
    ZR s2 = group.init(ZR_t);
    ZR t = group.init(ZR_t);
    ZR tagUSc = group.init(ZR_t);
    ZR s = group.init(ZR_t);
    ZR idUShash2 = group.init(ZR_t);
    GT C0 = group.init(GT_t);
    G1 C1 = group.init(G1_t);
    G1 C2 = group.init(G1_t);
    G1 C3 = group.init(G1_t);
    G1 C4 = group.init(G1_t);
    G1 C5 = group.init(G1_t);
    G1 C6 = group.init(G1_t);
    G1 C7 = group.init(G1_t);
    G1 E1 = group.init(G1_t);
    G1 E2 = group.init(G1_t);
    
    g = mpk[0].getG1();
    gb = mpk[1].getG1();
    ga1 = mpk[2].getG1();
    ga2 = mpk[3].getG1();
    gba1 = mpk[4].getG1();
    gba2 = mpk[5].getG1();
    tau1 = mpk[6].getG1();
    tau2 = mpk[7].getG1();
    tau1b = mpk[8].getG1();
    tau2b = mpk[9].getG1();
    w = mpk[10].getG1();
    u = mpk[11].getG1();
    h = mpk[12].getG1();
    egga = mpk[13].getGT();
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    t = group.random(ZR_t);
    tagUSc = group.random(ZR_t);
    s = group.add(s1, s2);
    idUShash2 = group.hashListToZR(id);
    C0 = group.mul(M, group.exp(egga, s2));
    C1 = group.exp(gb, s);
    C2 = group.exp(gba1, s1);
    C3 = group.exp(ga1, s1);
    C4 = group.exp(gba2, s2);
    C5 = group.exp(ga2, s2);
    C6 = group.mul(group.exp(tau1, s1), group.exp(tau2, s2));
    C7 = group.mul(group.mul(group.exp(tau1b, s1), group.exp(tau2b, s2)), group.exp(w, group.neg(t)));
    E1 = group.exp(group.mul(group.mul(group.exp(u, idUShash2), group.exp(w, tagUSc)), h), t);
    E2 = group.exp(g, t);
    ct.insert(0, C0);
    ct.insert(1, C1);
    ct.insert(2, C2);
    ct.insert(3, C3);
    ct.insert(4, C4);
    ct.insert(5, C5);
    ct.insert(6, C6);
    ct.insert(7, C7);
    ct.insert(8, E1);
    ct.insert(9, E2);
    ct.insert(10, tagUSc);
    return;
}

void transform(CharmList & ct, CharmList & skBlinded, CharmList & transformOutputList)
{
    string idBlinded;
    G1 D1Blinded;
    G1 D2Blinded;
    G1 D3Blinded;
    G1 D4Blinded;
    G1 D5Blinded;
    G1 D6Blinded;
    G1 D7Blinded;
    G1 KBlinded;
    ZR tagUSkBlinded;
    GT C0;
    G1 C1;
    G1 C2;
    G1 C3;
    G1 C4;
    G1 C5;
    G1 C6;
    G1 C7;
    G1 E1;
    G1 E2;
    ZR tagUSc;
    ZR tag = group.init(ZR_t);
    GT A1 = group.init(GT_t);
    GT A2 = group.init(GT_t);
    GT A4 = group.init(GT_t);
    
    idBlinded = skBlinded[0].strPtr;
    D1Blinded = skBlinded[1].getG1();
    D2Blinded = skBlinded[2].getG1();
    D3Blinded = skBlinded[3].getG1();
    D4Blinded = skBlinded[4].getG1();
    D5Blinded = skBlinded[5].getG1();
    D6Blinded = skBlinded[6].getG1();
    D7Blinded = skBlinded[7].getG1();
    KBlinded = skBlinded[8].getG1();
    tagUSkBlinded = skBlinded[9].getZR();
    
    C0 = ct[0].getGT();
    C1 = ct[1].getG1();
    C2 = ct[2].getG1();
    C3 = ct[3].getG1();
    C4 = ct[4].getG1();
    C5 = ct[5].getG1();
    C6 = ct[6].getG1();
    C7 = ct[7].getG1();
    E1 = ct[8].getG1();
    E2 = ct[9].getG1();
    tagUSc = ct[10].getZR();
    transformOutputList.insert(4, C0);
    transformOutputList.insert(0, group.exp(group.sub(tagUSc, tagUSkBlinded), -1));
    tag = transformOutputList[0].getZR();
    transformOutputList.insert(1, group.mul(group.mul(group.mul(group.mul(group.pair(C1, D1Blinded), group.pair(C2, D2Blinded)), group.pair(C3, D3Blinded)), group.pair(C4, D4Blinded)), group.pair(C5, D5Blinded)));
    A1 = transformOutputList[1].getGT();
    transformOutputList.insert(2, group.mul(group.pair(C6, D6Blinded), group.pair(C7, D7Blinded)));
    A2 = transformOutputList[2].getGT();
    transformOutputList.insert(3, group.mul(group.pair(E1, D7Blinded), group.pair(group.exp(E2, -1), KBlinded)));
    A4 = transformOutputList[3].getGT();
    return;
}

void decout(CharmList & transformOutputList, ZR & bf0, ZR & bf8, GT & M)
{
    GT C0 = group.init(GT_t);
    ZR tag = group.init(ZR_t);
    GT A1 = group.init(GT_t);
    GT A2 = group.init(GT_t);
    GT A3 = group.init(GT_t);
    GT A4 = group.init(GT_t);
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    C0 = transformOutputList[4].getGT();
    tag = transformOutputList[0].getZR();
    A1 = group.exp(transformOutputList[1].getGT(), bf0);
    A2 = group.exp(transformOutputList[2].getGT(), bf0);
    A3 = group.mul(A1, group.exp(A2, -1));
    A4 = group.exp(transformOutputList[3].getGT(), bf0);
    result0 = group.exp(A4, tag);
    result1 = group.mul(A3, group.exp(result0, -1));
    M = group.mul(C0, group.exp(result1, -1));
    return;
}

int main()
{
    return 0;
}
