#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int l = 5;

PairingGroup group(AES_SECURITY);

void setup(int l, int z, CharmList & mpk, CharmList & mk)
{
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 g = group.init(G1_t);
    G2 gb = group.init(G2_t);
    G1 g1 = group.init(G1_t);
    G2 g1b = group.init(G2_t);
    CharmListZR delta;
    CharmListG1 h;
    CharmListG2 hb;
    G2 g0b = group.init(G2_t);
    GT v = group.init(GT_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    g = group.random(G1_t);
    gb = group.random(G2_t);
    g1 = group.exp(g, alpha);
    g1b = group.exp(gb, alpha);
    for (int y = 0; y < l; y++)
    {
        delta.insert(y, group.random(ZR_t));
        h.insert(y, group.exp(g, delta[y]));
        hb.insert(y, group.exp(gb, delta[y]));
    }
    g0b = group.exp(gb, group.mul(alpha, beta));
    v = group.pair(g, g0b);
    mpk.insert(0, g);
    mpk.insert(1, g1);
    mpk.insert(2, h);
    mpk.insert(3, gb);
    mpk.insert(4, g1b);
    mpk.insert(5, hb);
    mpk.insert(6, v);
    mk.insert(0, g0b);
    return;
}

void keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pk, ZR & bf0, CharmList & skBlinded)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    G2 g0b;
    CharmListZR Id;
    CharmListZR r;
    CharmListG2 d;
    CharmListZR blindingFactordBlinded;
    CharmListG2 dBlinded;
    G2 resVarName0 = group.init(G2_t);
    G2 resVarName1 = group.init(G2_t);
    G2 d0DotProdCalc = group.init(G2_t);
    G2 d0 = group.init(G2_t);
    G2 d0Blinded = group.init(G2_t);
    bf0 = group.random(ZR_t);
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    g0b = mk[0].getG2();
    Id = stringToInt(group, id, 5, 32);
    for (int y = 0; y < 5; y++)
    {
        r.insert(y, group.random(ZR_t));
        d.insert(y, group.exp(gb, r[y]));
    }
    CharmList d_keys = d.keys();
    int d_len = d.length();
    for (int y_var = 0; y_var < d_len; y_var++)
    {
        y = d_keys[y_var];
        blindingFactordBlinded.insert(y, bf0);
        dBlinded.insert(y, group.exp(d[y], group.div(1, blindingFactordBlinded[y].getZR())));
    }
    //;
    for (int y = 0; y < 5; y++)
    {
        resVarName1 = group.exp(group.mul(group.exp(g1b, Id[y]), hb[y]), r[y]);
        resVarName0 = group.mul(resVarName0, resVarName1);
    }
    d0DotProdCalc = resVarName0;
    d0 = group.mul(g0b, d0DotProdCalc);
    d0Blinded = group.exp(d0, group.div(1, bf0));
    pk.insert(0, id);
    skBlinded.insert(0, d0Blinded);
    skBlinded.insert(1, dBlinded);
    return;
}

void encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    string id;
    ZR s = group.init(ZR_t);
    GT A = group.init(GT_t);
    G1 B = group.init(G1_t);
    CharmListZR Id;
    CharmListG1 C;
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    id = pk[0].strPtr;
    s = group.random(ZR_t);
    A = group.mul(M, group.exp(v, s));
    B = group.exp(g, s);
    Id = stringToInt(group, id, 5, 32);
    for (int y = 0; y < 5; y++)
    {
        C.insert(y, group.exp(group.mul(group.exp(g1, Id[y]), h[y]), s));
    }
    ct.insert(0, A);
    ct.insert(1, B);
    ct.insert(2, C);
    return;
}

void transform(CharmList & pk, CharmList & skBlinded, CharmList & ct, GT & transformOutputList)
{
    G2 d0Blinded;
    CharmListG2 dBlinded;
    GT A;
    G1 B;
    CharmListG1 C;
    GT resVarName3 = group.init(GT_t);
    GT denominator = group.init(GT_t);
    
    d0Blinded = skBlinded[0].getG2();
    dBlinded = skBlinded[1].getListG2();
    
    A = ct[0].getGT();
    B = ct[1].getG1();
    C = ct[2].getListG1();
    transformOutputList.insert(1, A);
    for (int y = 0; y < 5; y++)
    {
		//NOP;
        transformOutputList.insert(1000+3*y, group.pair(C[y], dBlinded[y]));
        resVarName3 = transformOutputList[1000+3*y].getGT();
    }
    transformOutputList.insert(0, group.pair(B, d0Blinded));
    denominator = transformOutputList[0].getGT();
    return;
}

void decout(CharmList & pk, GT & transformOutputList, ZR & bf0, GT & M)
{
    GT A = group.init(GT_t);
    GT resVarName2 = group.init(GT_t);
    GT resVarName3 = group.init(GT_t);
    GT D = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    A = transformOutputList[1].getGT();
    //;
    for (int y = 0; y < 5; y++)
    {
		//NOP;
        resVarName3 = group.exp(transformOutputList[1000+3*y].getGT(), bf0);
        resVarName2 = group.mul(resVarName2, resVarName3);
    }
    D = resVarName2;
    denominator = group.exp(transformOutputList[0].getGT(), bf0);
    fraction = group.mul(D, group.exp(denominator, -1));
    M = group.mul(A, fraction);
    return;
}

int main()
{
    return 0;
}
