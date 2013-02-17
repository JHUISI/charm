#include "TestSW.h"

void Sw05::setup(int n, CharmList & pk, ZR & mk)
{
    G1 g = group.init(G1_t);
    ZR y = group.init(ZR_t);
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    CharmListG2 t;
    g = group.random(G1_t);
    y = group.random(ZR_t);
    g1 = group.exp(g, y);
    g2 = group.random(G2_t);
    for (int i = 0; i < n+1; i++)
    {
        t.insert(i, group.random(G2_t));
    }
    pk.insert(0, g);
    pk.insert(1, g1);
    pk.insert(2, g2);
    pk.insert(3, t);
    mk = y;
    return;
}

G2 evalT(CharmList & pk, int n, ZR & x)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    CharmListZR N;
    CharmListInt Nint;
    CharmDictZR coeffs;
    G2 prodResult = group.init(G2_t);
    int lenNint = 0;
    int loopVarEvalT = 0;
    int loopVarM1 = 0;
    G2 T = group.init(G2_t);
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    for (int i = 0; i < n+1; i++)
    {
        N.insert(i, group.init(ZR_t));
        Nint.insert(i, (i + 1));
    }
    coeffs = util.recoverCoefficientsDict(group, N);
    //;
    lenNint = Nint.length();
    for (int i = 0; i < lenNint; i++)
    {
        loopVarEvalT = Nint[i];
        loopVarM1 = (loopVarEvalT - 1);
        prodResult = group.mul(prodResult, group.exp(t[loopVarM1], coeffs[loopVarEvalT]));
    }
    T = group.mul(group.exp(g2, (x * n)), prodResult);
    return T;
}

void Sw05::extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, CharmList & sk)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    int lenw = 0;
    string loopVar1;
    CharmListZR wHash;
    ZR r = group.init(ZR_t);
    CharmListZR q;
    CharmListZR shares;
    int wHashLen = 0;
    ZR loopVar2 = group.init(ZR_t);
    string loopVar2Str;
    G2 evalTVar = group.init(G2_t);
    CharmListG2 D;
    CharmListG1 d;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    lenw = w.length();
    for (int i = 0; i < lenw; i++)
    {
        loopVar1 = w[i];
        wHash.insert(i, group.hashListToZR(loopVar1));
    }
    r = group.random(ZR_t);
    q.insert(0, mk);
    for (int i = 1; i < dParam; i++)
    {
        q.insert(i, group.random(ZR_t));
    }
    shares = genSharesForX(mk, q, wHash);
    wHashLen = wHash.length();
    for (int i = 0; i < wHashLen; i++)
    {
        loopVar2 = wHash[i];
        loopVar2Str = w[i];
        evalTVar = evalT(pk, n, loopVar2);
        D.insert(loopVar2Str, group.mul(group.exp(g2, shares[i]), group.exp(evalTVar, r)));
        d.insert(loopVar2Str, group.exp(g, r));
    }
    sk.insert(0, w);
    sk.insert(1, D);
    sk.insert(2, d);
    return;
}

void Sw05::encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    ZR s = group.init(ZR_t);
    GT Eprime = group.init(GT_t);
    G1 Eprimeprime = group.init(G1_t);
    int wPrimeLen = 0;
    ZR loopVar = group.init(ZR_t);
    string loopVarStr;
    G2 evalTVar = group.init(G2_t);
    CharmListG2 E;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    s = group.random(ZR_t);
    Eprime = group.mul(M, group.exp(group.pair(g1, g2), s));
    Eprimeprime = group.exp(g, s);
    wPrimeLen = wPrime.length();
    for (int i = 0; i < wPrimeLen; i++)
    {
        loopVar = group.hashListToZR(wPrime[i]);
        loopVarStr = wPrime[i];
        evalTVar = evalT(pk, n, loopVar);
        E.insert(loopVarStr, group.exp(evalTVar, s));
    }
    CT.insert(0, wPrime);
    CT.insert(1, Eprime);
    CT.insert(2, Eprimeprime);
    CT.insert(3, E);
    return;
}

void Sw05::decrypt(CharmList & pk, CharmList & sk, CharmList & CT, int dParam, GT & M)
{
    CharmListStr wPrime;
    GT Eprime;
    G1 Eprimeprime;
    CharmListG2 E;
    CharmListStr w;
    CharmListG2 D;
    CharmListG1 d;
    CharmListZR S;
    CharmDictZR coeffs;
    GT prod = group.init(GT_t);
    CharmListStr SKeys;
    int SLen = 0;
    string loopVar3;
    GT loopProd = group.init(GT_t);
    
    wPrime = CT[0].getListStr();
    Eprime = CT[1].getGT();
    Eprimeprime = CT[2].getG1();
    E = CT[3].getListG2();
    
    w = sk[0].getListStr();
    D = sk[1].getListG2();
    d = sk[2].getListG1();
    S = util.intersectionSubset(group, wHash, wPrimeHash, dParam);
    coeffs = util.recoverCoefficientsDict(group, S);
    //;
    SKeys = S.strkeys();
    SLen = S.length();
    for (int i = 0; i < SLen; i++)
    {
        loopVar3 = SKeys[i];
        loopProd = group.exp(group.div(group.pair(d[loopVar3], E[loopVar3]), group.pair(Eprimeprime, D[loopVar3])), coeffs[loopVar3]);
        prod = group.mul(prod, loopProd);
    }
    M = group.mul(Eprime, prod);
    return;
}

