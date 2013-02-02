#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

PairingGroup group(MNT160);

SecretUtil util;

void setup(int n, CharmList & pk, ZR & mk) // good to go
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

G2 evalT(CharmList & pk, int n, ZR x)
{
	G2 T;
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    CharmListZR N;
    CharmListInt Nint; // NO TYPE FOUND FOR Nint
    CharmListZR coeffs;
    G2 prodResult = group.init(G2_t);
    int lenNint = 0;
    int loopVarEvalT = 0;
    ZR j = group.init(ZR_t);
    int loopVarMinusOne = 0;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    for (int i = 0; i < n+1; i++)
    {
    	// N.insert(i, group.init(ZR_t)); // fix
    	N[i] = group.init(ZR_t, i+1); // fix this
        Nint[i] = i+1; // Nint.insert(i, group.add(i, 1));
    }

    coeffs = util.recoverCoefficientsDict(group, N);
    //;
    lenNint = Nint.length();
    for (int i = 0; i < lenNint; i++)
    {
        loopVarEvalT = Nint[i];
        //;
        loopVarMinusOne = loopVarEvalT - 1; // group.sub(loopVarEvalT, 1);
        prodResult = group.mul(prodResult, group.exp(t[loopVarMinusOne], coeffs[loopVarEvalT]));
    }
    T = group.mul(group.exp(g2, group.mul(x, n)), prodResult);
    return T;
}

void extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, CharmList & sk)
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
    ZR loopVar2 = group.init(ZR_t);
    G2 evalTVar = group.init(G2_t);
    CharmListG2 D;
    CharmListG1 d;
	string loopVar2Str;
    
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

    shares = util.genSharesForX(group, mk, q, wHash); // fix this
    for (int i = 0; i < lenw; i++)
    {
        loopVar2 = wHash[i]; // add to SDL
    	loopVar2Str = w[i]; // fix in SDL
        evalTVar = evalT(pk, n, loopVar2);
        D.insert(loopVar2Str, group.mul(group.exp(g2, shares[i]), group.exp(evalTVar, r)));
        d.insert(loopVar2Str, group.exp(g, r));
    }
    sk.insert(0, w);
    sk.insert(1, D);
    sk.insert(2, d);
    return;
}

void encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    int wPrimeLen = 0;
    string loopVarStr; // fix
    ZR loopVar = group.init(ZR_t);
//    CharmListZR wPrimeHash;
//    int wPrimeHashLen = 0;
    ZR s = group.init(ZR_t);
    GT Eprime = group.init(GT_t);
    G1 Eprimeprime = group.init(G1_t);
    G2 evalTVar = group.init(G2_t);
    CharmListG2 E;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
//    wPrimeLen = wPrime.length();
//    for (int i = 0; i < wPrimeLen; i++)
//    {
//        loopVarStr = wPrime[i]; // fix
//        wPrimeHash.insert(i, group.hashListToZR(loopVarStr), loopVarStr);
//    }
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

void decrypt(CharmList & pk, CharmList & sk, CharmList & CT, int dParam, GT & M)
{
//    CharmListStr wPrimeHash;
    GT Eprime;
    G1 Eprimeprime;
    CharmListG2 E;
//    CharmListStr wHash;
    CharmListG2 D;
    CharmListG1 d;
    CharmListZR S; // = group.init(ZR_t); // has incorrect type CharmListZR instead of ZR
    CharmListStr Skeys, w, wPrime;
    CharmListZR coeffs;
    GT prod = group.init(GT_t);
    int SLen = 0;
    string loopVar; // = group.init(ZR_t);
    GT loopProd = group.init(GT_t);
    
    wPrime = CT[0].getListStr();
    Eprime = CT[1].getGT();
    Eprimeprime = CT[2].getG1();
    E = CT[3].getListG2();
    
    w = sk[0].getListStr();
    D = sk[1].getListG2();
    d = sk[2].getListG1();
    S = util.intersectionSubset(group, w, wPrime, dParam); // fix: now builtin
    coeffs = util.recoverCoefficientsDict(group, S); // fix in SDL
    //;
    Skeys = S.strkeys(); // fix add keys function
    SLen = S.length();
    for (int i = 0; i < SLen; i++)
    {
        loopVar = Skeys[i]; // fix
//        cout << "i=" << i << ", loopVar=" << loopVar << endl;
        loopProd = group.exp(group.div(group.pair(d[loopVar], E[loopVar]), group.pair(Eprimeprime, D[loopVar])), coeffs[loopVar]);
        prod = group.mul(prod, loopProd);
    }
    M = group.mul(Eprime, prod);
    return;
}

int main()
{
	ZR mk;
	CharmList pk, sk, CT;
	CharmListStr ID, wPrime;
	GT M, newM;
	int n = 6, d = 4; // n = max, d = required

	// private identity
	ID.append("insurance");
	ID.append("oncology");
	ID.append("doctor");
	ID.append("nurse");
	ID.append("JHU");

	// public identity
	wPrime.append("insurance");
	wPrime.append("oncology");
	wPrime.append("doctor");
	wPrime.append("JHU");
	wPrime.append("billing");
	wPrime.append("misc");

	setup(n, pk, mk);

	extract(mk, ID, pk, d, n, sk);

	M = group.random(GT_t);
	encrypt(pk, wPrime, M, n, CT);

	decrypt(pk, sk, CT, d, newM);
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
