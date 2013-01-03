#include "CharmCAPI.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(80);
int n = 8;
int l = 32;

void setup(int n, int l, CharmList & mpk, CharmList & msk)
{
    ZR alpha = group.init(ZR_t);
    ZR t1 = group.init(ZR_t);
    ZR t2 = group.init(ZR_t);
    ZR t3 = group.init(ZR_t);
    ZR t4 = group.init(ZR_t);
    G1 g = group.init(G1_t);
    G2 h = group.init(G2_t);
    GT omega = group.init(GT_t);
    CharmListZR z;
    CharmListG1 gl;
    CharmListG2 hl;
    G1 v1 = group.init(G1_t);
    G1 v2 = group.init(G1_t);
    G1 v3 = group.init(G1_t);
    G1 v4 = group.init(G1_t);
    alpha = group.random(ZR_t);
    t1 = group.random(ZR_t);
    t2 = group.random(ZR_t);
    t3 = group.random(ZR_t);
    t4 = group.random(ZR_t);
    g = group.random(G1_t);
    h = group.random(G2_t);
    omega = group.exp(group.pair(g, h), group.mul(t1, group.mul(t2, alpha)));
    for (int y = 0; y < n; y++)
    {
        z.insert(y, group.random(ZR_t));
        gl.insert(y, group.exp(g, z[y]));
        hl.insert(y, group.exp(h, z[y]));
    }
    v1 = group.exp(g, t1);
    v2 = group.exp(g, t2);
    v3 = group.exp(g, t3);
    v4 = group.exp(g, t4);
    mpk.insert(0, omega);
    mpk.insert(1, g);
    mpk.insert(2, h);
    mpk.insert(3, gl);
    mpk.insert(4, hl);
    mpk.insert(5, v1);
    mpk.insert(6, v2);
    mpk.insert(7, v3);
    mpk.insert(8, v4);
    mpk.insert(9, n);
    mpk.insert(10, l);
    msk.insert(0, alpha);
    msk.insert(1, t1);
    msk.insert(2, t2);
    msk.insert(3, t3);
    msk.insert(4, t4);
    return;
}

void extract(CharmList & mpk, CharmList & msk, string & id, ZR & blindingFactord0Blinded, ZR & blindingFactord1Blinded, ZR & blindingFactord2Blinded, ZR & blindingFactor0Blinded, ZR & blindingFactor1Blinded, CharmList & skBlinded)
{
    string idBlinded; //= group.init(string_t); fix in CG
    ZR zz = group.init(ZR_t);
    GT omega;
    G1 g;
    G2 h;
    CharmListG1 gl; // incorrect type -- fix in CG
    CharmListG2 hl; // incorrect type -- fix in CG
    G1 v1;
    G1 v2;
    G1 v3;
    G1 v4;
    ZR alpha;
    ZR t1;
    ZR t2;
    ZR t3;
    ZR t4;
    ZR r1 = group.init(ZR_t);
    ZR r2 = group.init(ZR_t);
    CharmListZR hID;
    G2 reservedVarName0 = group.init(G2_t);
    G2 reservedVarName1 = group.init(G2_t);
    G2 hashIDDotProd = group.init(G2_t);
    G2 hashID = group.init(G2_t);
    G2 d0 = group.init(G2_t);
    G2 d0Blinded = group.init(G2_t);
    G2 halpha = group.init(G2_t);
    G2 hashID2r1 = group.init(G2_t);
    G2 d1 = group.init(G2_t);
    G2 d1Blinded = group.init(G2_t);
    G2 d2 = group.init(G2_t);
    G2 d2Blinded = group.init(G2_t);
    G2 hashID2r2 = group.init(G2_t);
    G2 d3 = group.init(G2_t);
    G2 d3Blinded = group.init(G2_t);
    G2 d4 = group.init(G2_t);
    G2 d4Blinded = group.init(G2_t);
    CharmList sk;
    blindingFactord0Blinded = group.random(ZR_t);
    blindingFactord1Blinded = group.random(ZR_t);
    blindingFactord2Blinded = group.random(ZR_t);
    blindingFactor0Blinded = group.random(ZR_t);
    blindingFactor1Blinded = group.random(ZR_t);
    idBlinded = id;
    zz = group.random(ZR_t);
    
    omega = mpk[0].getGT();
    g = mpk[1].getG1();
    h = mpk[2].getG2();
    gl = mpk[3].getListG1();
    hl = mpk[4].getListG2();
    v1 = mpk[5].getG1();
    v2 = mpk[6].getG1();
    v3 = mpk[7].getG1();
    v4 = mpk[8].getG1();
    //n = mpk[9].getZR();
    //l = mpk[10].getZR();
    
    alpha = msk[0].getZR();
    t1 = msk[1].getZR();
    t2 = msk[2].getZR();
    t3 = msk[3].getZR();
    t4 = msk[4].getZR();
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    hID = stringToInt(group, id, n, l);
    cout << "hID: " << endl;
    cout << hID << endl;
    //group.init(reservedVarName0);
    for (int y = 0; y < n; y++)
    {
        reservedVarName1 = group.exp(hl[y], hID[y]);
        reservedVarName0 = group.mul(reservedVarName0, reservedVarName1);
    }
    hashIDDotProd = reservedVarName0;
    hashID = group.mul(hl[0], hashIDDotProd);
    d0 = group.exp(h, group.add(group.mul(r1, group.mul(t1, t2)), group.mul(r2, group.mul(t3, t4))));
    d0Blinded = group.exp(d0, group.div(1, blindingFactord0Blinded));
    halpha = group.exp(h, group.neg(alpha));
    hashID2r1 = group.exp(hashID, group.neg(r1));
    d1 = group.mul(group.exp(halpha, t2), group.exp(hashID2r1, t2));
    d1Blinded = group.exp(d1, group.div(1, blindingFactord1Blinded));
    d2 = group.mul(group.exp(halpha, t1), group.exp(hashID2r1, t1));
    d2Blinded = group.exp(d2, group.div(1, blindingFactord2Blinded));
    hashID2r2 = group.exp(hashID, group.neg(r2));
    d3 = group.exp(hashID2r2, t4);
    d3Blinded = group.exp(d3, group.div(1, blindingFactor0Blinded));
    d4 = group.exp(hashID2r2, t3);
    d4Blinded = group.exp(d4, group.div(1, blindingFactor1Blinded));
    sk.insert(0, idBlinded);
    sk.insert(1, d0Blinded);
    sk.insert(2, d1Blinded);
    sk.insert(3, d2Blinded);
    sk.insert(4, d3Blinded);
    sk.insert(5, d4Blinded);
    skBlinded.insert(0, idBlinded);
    skBlinded.insert(1, d0Blinded);
    skBlinded.insert(2, d1Blinded);
    skBlinded.insert(3, d2Blinded);
    skBlinded.insert(4, d3Blinded);
    skBlinded.insert(5, d4Blinded);
    return;
}

void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct)
{
    GT omega;
    G1 g;
    G2 h;
    CharmListG1 gl; // fix in CG ==> G1 gl;
    CharmListG2 hl; // fix in CG ==> G2 hl;
    G1 v1;
    G1 v2;
    G1 v3;
    G1 v4;
    ZR s = group.init(ZR_t);
    ZR s1 = group.init(ZR_t);
    ZR s2 = group.init(ZR_t);
    CharmListZR hID1;
    G1 reservedVarName2 = group.init(G1_t);
    G1 reservedVarName3 = group.init(G1_t);
    G1 hashID1DotProd = group.init(G1_t);
    G1 hashID1 = group.init(G1_t);
    GT cpr = group.init(GT_t);
    G1 c0 = group.init(G1_t);
    G1 c1 = group.init(G1_t);
    G1 c2 = group.init(G1_t);
    G1 c3 = group.init(G1_t);
    G1 c4 = group.init(G1_t);
    
    omega = mpk[0].getGT();
    g = mpk[1].getG1();
    h = mpk[2].getG2();
    gl = mpk[3].getListG1();
    hl = mpk[4].getListG2();
    v1 = mpk[5].getG1();
    v2 = mpk[6].getG1();
    v3 = mpk[7].getG1();
    v4 = mpk[8].getG1();
    s = group.random(ZR_t);
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    hID1 = stringToInt(group, id, n, l);
    cout << "hID1: " << endl;
    cout << hID1 << endl;
    //group.init(reservedVarName2); // fix in CG
    for (int y = 0; y < n; y++)
    {
        reservedVarName3 = group.exp(gl[y], hID1[y]);
        reservedVarName2 = group.mul(reservedVarName2, reservedVarName3);
    }
    hashID1DotProd = reservedVarName2;
    hashID1 = group.mul(gl[0], hashID1DotProd);
    cpr = group.mul(group.exp(omega, s), M);
    c0 = group.exp(hashID1, s);
    c1 = group.exp(v1, group.sub(s, s1));
    c2 = group.exp(v2, s1);
    c3 = group.exp(v3, group.sub(s, s2));
    c4 = group.exp(v4, s2);
    ct.insert(0, c0);
    ct.insert(1, c1);
    ct.insert(2, c2);
    ct.insert(3, c3);
    ct.insert(4, c4);
    ct.insert(5, cpr);
    return;
}

void transform(CharmList & sk, CharmList & ct, CharmList & transformOutputList)
{
    string id;
    G2 d0;
    G2 d1;
    G2 d2;
    G2 d3;
    G2 d4;
    G1 c0;
    G1 c1;
    G1 c2;
    G1 c3;
    G1 c4;
    GT cpr;
    
    id = sk[0].strPtr;
    d0 = sk[1].getG2();
    d1 = sk[2].getG2();
    d2 = sk[3].getG2();
    d3 = sk[4].getG2();
    d4 = sk[5].getG2();
    
    c0 = ct[0].getG1();
    c1 = ct[1].getG1();
    c2 = ct[2].getG1();
    c3 = ct[3].getG1();
    c4 = ct[4].getG1();
    cpr = ct[5].getGT();
    transformOutputList.insert(0, group.pair(c0, d0));
    transformOutputList.insert(1, group.pair(c1, d1));
    transformOutputList.insert(2, group.pair(c2, d2));
    transformOutputList.insert(3, group.pair(c3, d3));
    transformOutputList.insert(4, group.pair(c4, d4));
    return;
}

void decout(CharmList & sk, CharmList & ct, CharmList & transformOutputList, ZR & blindingFactord0Blinded, ZR & blindingFactord1Blinded, ZR & blindingFactord2Blinded, ZR & blindingFactor0Blinded, ZR & blindingFactor1Blinded, GT & M)
{
    string id;
    G2 d0;
    G2 d1;
    G2 d2;
    G2 d3;
    G2 d4;
    G1 c0;
    G1 c1;
    G1 c2;
    G1 c3;
    G1 c4;
    GT cpr;
    GT result = group.init(GT_t);
    
    id = sk[0].strPtr;
    d0 = sk[1].getG2();
    d1 = sk[2].getG2();
    d2 = sk[3].getG2();
    d3 = sk[4].getG2();
    d4 = sk[5].getG2();
    
    c0 = ct[0].getG1();
    c1 = ct[1].getG1();
    c2 = ct[2].getG1();
    c3 = ct[3].getG1();
    c4 = ct[4].getG1();
    cpr = ct[5].getGT();
    result = group.mul(group.exp(transformOutputList[0].getGT(), blindingFactord0Blinded), group.mul(group.exp(transformOutputList[1].getGT(), blindingFactord1Blinded), group.mul(group.exp(transformOutputList[2].getGT(), blindingFactord2Blinded), group.mul(group.exp(transformOutputList[3].getGT(), blindingFactor0Blinded), group.exp(transformOutputList[4].getGT(), blindingFactor1Blinded)))));
    M = group.mul(cpr, result);
    return;
}

int main()
{
    CharmList mpk, msk, skBlinded, ct, transformOutputList;
    ZR blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded;

    GT M = group.random(GT_t);
    cout << "M1 :=> " << M << endl;
    GT MII = group.init(GT_t);

    string idArg = "john@example.com";

    setup(n, l, mpk, msk);
    extract(mpk, msk, idArg, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded, skBlinded);
    encrypt(mpk, M, idArg, ct);
    transform(skBlinded, ct, transformOutputList);
    decout(skBlinded, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded, MII);

    cout << "M2 :=> " << MII << endl;
    if(M == MII)
       cout << "SUCCESSFUL DECRYPTION!!!" << endl;
    else
       cout << "FAILED DECRYPTION... :-(" << endl;
    return 0;
}
