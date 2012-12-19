#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(G1 & g1, G2 & g2, GT & egga, CharmList & msk)
{
    ZR a = group.init(ZR_t);
    ZR dummyVar = group.init(ZR_t);
    a = group.random(ZR_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    egga = group.exp(group.pair(g1, g2), a);
    dummyVar = group.random(ZR_t);
    msk.append(a);
    msk.append(dummyVar);
    return;
}

void keygen(G2 & g2, GT & egga, CharmList & msk, GT & pkBlinded, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
    ZR zz = group.init(ZR_t);
    ZR a;
    ZR dummyVar;
    ZR t = group.init(ZR_t);
    G2 d = group.init(G2_t);
    G2 dBlinded = group.init(G2_t);
    GT eggat = group.init(GT_t);
    GT pk = group.init(GT_t);
    ZR dummyVar2 = group.init(ZR_t);
    ZR dummyVar2Blinded = group.init(ZR_t);
    CharmList sk;
    blindingFactor0Blinded = group.random(ZR_t);
    zz = group.random(ZR_t);
    
    a = msk[0].getZR();
    dummyVar = msk[1].getZR();
    t = group.random(ZR_t);
    d = group.exp(g2, group.mul(a, t));
    dBlinded = group.exp(d, group.div(1, blindingFactor0Blinded));
    eggat = group.exp(egga, t);
    pk = eggat;
    pkBlinded = pk;
    dummyVar2 = group.random(ZR_t);
    dummyVar2Blinded = dummyVar2;
    sk.append(dBlinded);
    sk.append(dummyVar2Blinded);
    skBlinded.append(dBlinded);
    skBlinded.append(dummyVar2Blinded);
    return;
}

void encrypt(G1 & g1, GT & pk, GT & M, GT & c0, G1 & c1, G1 & c2, G1 & c3)
{
    ZR s1 = group.init(ZR_t);
    ZR s2 = group.init(ZR_t);
    ZR s3 = group.init(ZR_t);
    ZR s = group.init(ZR_t);
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    s3 = group.random(ZR_t);
    s = group.add(s1, group.add(s2, s3));
    c0 = group.mul(M, group.exp(pk, s));
    c1 = group.exp(g1, s1);
    c2 = group.exp(g1, s2);
    c3 = group.exp(g1, s3);
    return;
}

void transform(GT & pk, CharmList & sk, GT & c0, G1 & c1, G1 & c2, G1 & c3, CharmList & transformOutputList)
{
    G2 d;
    ZR dummyVar2;
    GT result = group.init(GT_t);
    
    d = sk[0].getG2();
    dummyVar2 = sk[1].getZR();
    transformOutputList[0] = group.pair(group.mul(c1, group.mul(c2, c3)), d);
    result = transformOutputList[0];
    return;
}

void decout(GT & pk, CharmList & sk, GT & c0, G1 & c1, G1 & c2, G1 & c3, CharmList & transformOutputList, ZR & blindingFactor0Blinded, GT & M)
{
    G2 d;
    ZR dummyVar2;
    GT result = group.init(GT_t);
    
    d = sk[0].getG2();
    dummyVar2 = sk[1].getZR();
    result = group.exp(transformOutputList[0], blindingFactor0Blinded);
    M = group.mul(c0, group.exp(result, -1));
    return;
}

int main()
{
    return 0;
}
