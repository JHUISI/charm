#include "TestHIBE.h"

int l = 5;

void Hibe::setup(int l, int z, CharmList & mpk, CharmList & mk)
{
    ZR alpha;
    ZR beta;
    G1 g;
    G2 gb;
    G1 g1;
    G2 g1b;
    CharmListZR delta;
    CharmListG1 h;
    CharmListG2 hb;
    G2 g0b;
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

void Hibe::keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pk, CharmList & sk)
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
    G2 resVarName0;
    G2 resVarName1;
    G2 d0DotProdCalc;
    G2 d0;
    
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
    //;
    for (int y = 0; y < 5; y++)
    {
        resVarName1 = group.exp(group.mul(group.exp(g1b, Id[y]), hb[y]), r[y]);
        resVarName0 = group.mul(resVarName0, resVarName1);
    }
    d0DotProdCalc = resVarName0;
    d0 = group.mul(g0b, d0DotProdCalc);
    pk.insert(0, id);
    sk.insert(0, d0);
    sk.insert(1, d);
    return;
}

void Hibe::encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    string id;
    ZR s;
    GT A = group.init(GT_t);
    G1 B;
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

void Hibe::decrypt(CharmList & pk, CharmList & sk, CharmList & ct, GT & M)
{
    G2 d0;
    CharmListG2 d;
    GT A;
    G1 B;
    CharmListG1 C;
    GT resVarName2 = group.init(GT_t);
    GT resVarName3 = group.init(GT_t);
    GT D = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    
    d0 = sk[0].getG2();
    d = sk[1].getListG2();
    
    A = ct[0].getGT();
    B = ct[1].getG1();
    C = ct[2].getListG1();
    //;
    for (int y = 0; y < 5; y++)
    {
        resVarName3 = group.pair(C[y], d[y]);
        resVarName2 = group.mul(resVarName2, resVarName3);
    }
    D = resVarName2;
    denominator = group.pair(B, d0);
    fraction = group.div(D, denominator);
    M = group.mul(A, fraction);
    return;
}

