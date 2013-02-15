#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(AES_SECURITY);

SecretUtil util;

void setup(int n, CharmList & pk, ZR & mk)
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

void evalT(CharmList & pk, int n, ZR & x, G2 & T)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    CharmListInt N;
    CharmDictZR coeffs;
    G2 prodResult = group.init(G2_t);
    int lenN = 0;
    int loopVarEvalT = 0;
    int loopVarM1 = 0;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    for (int i = 0; i < n+1; i++)
    {
        N.insert(i, group.add(i, 1));
    }
    coeffs = util.recoverCoefficientsDict(group, N);
    //;
    lenN = N.length();
    for (int i = 0; i < lenN; i++)
    {
        loopVarEvalT = N[i];
        loopVarM1 = group.sub(loopVarEvalT, 1);
        prodResult = group.mul(prodResult, group.exp(t[loopVarM1], coeffs[loopVarEvalT]));
    }
    T = group.mul(group.exp(g2, group.mul(x, n)), prodResult);
    return;
}

void extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, ZR & bf0, CharmList & skBlinded)
{
    string wBlinded;
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
    CharmListZR blindingFactordBlinded;
    CharmListG1 dBlinded;
    CharmListZR blindingFactorDBlinded;
    CharmListG2 DBlinded;
    bf0 = group.random(ZR_t);
    wBlinded = w;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    lenw = wBlinded.length();
    for (int i = 0; i < lenw; i++)
    {
        loopVar1 = wBlinded[i];
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
        loopVar2Str = wBlinded[i];
        evalTVar = evalT(pk, n, loopVar2);
        D.insert(loopVar2Str, group.mul(group.exp(g2, shares[i]), group.exp(evalTVar, r)));
        d.insert(loopVar2Str, group.exp(g, r));
    }
    CharmList d_keys = d.keys();
    int d_len = d.length();
    for (int y_var = 0; y_var < d_len; y_var++)
    {
        y = d_keys[y_var];
        blindingFactordBlinded.insert(y, bf0);
        dBlinded.insert(y, group.exp(d[y], group.div(1, blindingFactordBlinded[y].getZR())));
    }
    CharmList D_keys = D.keys();
    int D_len = D.length();
    for (int y_var = 0; y_var < D_len; y_var++)
    {
        y = D_keys[y_var];
        blindingFactorDBlinded.insert(y, bf0);
        DBlinded.insert(y, group.exp(D[y], group.div(1, blindingFactorDBlinded[y].getZR())));
    }
    skBlinded.insert(0, wBlinded);
    skBlinded.insert(1, DBlinded);
    skBlinded.insert(2, dBlinded);
    return;
}

void encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT)
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

void transform(CharmList & pk, CharmList & skBlinded, CharmList & CT, int dParam, CharmList & transformOutputList, CharmListStr & SKeys, int SLen)
{
