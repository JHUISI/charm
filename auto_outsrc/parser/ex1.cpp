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

void keygen(G2 & g2, GT & egga, CharmList & msk, GT & pk, GT & pkBlinded, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
    ZR zz = group.init(ZR_t);
    ZR a;
    ZR dummyVar;
    ZR t = group.init(ZR_t);
    G2 d = group.init(G2_t);
    G2 dBlinded = group.init(G2_t);
    GT eggat = group.init(GT_t);
    pk = group.init(GT_t);
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

void transform(GT & pk, CharmList & skBlinded, GT & c0, G1 & c1, G1 & c2, G1 & c3, CharmList & transformOutputList)
{
    G2 d;
    ZR dummyVar2;
    GT result = group.init(GT_t);
    
    d = skBlinded[0].getG2();
    //dummyVar2 = skBlinded[1].getZR();
    transformOutputList.insert(0, group.pair(group.mul(c1, group.mul(c2, c3)), d));
    result = transformOutputList[0].getGT();
    cout << "transformList : " << transformOutputList << endl;
    return;
}

void decout(GT & pk, GT & c0, G1 & c1, G1 & c2, G1 & c3, CharmList & transformOutputList, ZR & blindingFactor0Blinded, GT & M)
{
    G2 d;
    ZR dummyVar2;
    GT result = group.init(GT_t);
    
   // d = sk[0].getG2();
   // dummyVar2 = sk[1].getZR();
    result = group.exp(transformOutputList[0].getGT(), blindingFactor0Blinded);
    M = group.mul(c0, group.exp(result, -1));
    return;
}

int main()
{
    ZR blindingFactor0Blinded;
    G1 g1;
    G2 g2; 
    GT egga, pk, pkBlinded;
    CharmList sk, msk, skBlinded, transformOutputList;

    setup(g1, g2, egga, msk);

    keygen(g2, egga, msk, pk, pkBlinded, blindingFactor0Blinded, skBlinded);

    GT M = group.random(GT_t);
    cout << "M1 :=> " << M.g << endl;
    GT MII = group.init(GT_t);
    G1 c1, c2, c3;
    GT c0 = group.init(GT_t);
    encrypt(g1, pk, M, c0, c1, c2, c3);

    cout << "c0 : " << c0.g << endl;
    cout << "c1 : " << c1.g << endl;
    cout << "c2 : " << c2.g << endl;
    cout << "c3 : " << c3.g << endl;
    transform(pk, skBlinded, c0, c1, c2, c3, transformOutputList);

    decout(pk, c0, c1, c2, c3, transformOutputList, blindingFactor0Blinded, MII);

    cout << "M2 :=> " << MII.g << endl;

    return 0;
}
