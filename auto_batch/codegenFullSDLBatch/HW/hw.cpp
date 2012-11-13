#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
#include <math.h>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(G1 & g1, G2 & g2)
{
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    return;
}

void keygen(G1 & g1, G2 & g2, int *i, CharmList & pk, ZR & sk)
{
    ZR a = group.init(ZR_t);
    G2 A = group.init(G2_t);
    G1 u = group.init(G1_t);
    G1 v = group.init(G1_t);
    G1 d = group.init(G1_t);
    GT U = group.init(GT_t);
    GT V = group.init(GT_t);
    GT D = group.init(GT_t);
    ZR w = group.init(ZR_t);
    ZR z = group.init(ZR_t);
    ZR h = group.init(ZR_t);
    G1 w1 = group.init(G1_t);
    G2 w2 = group.init(G2_t);
    G1 z1 = group.init(G1_t);
    G2 z2 = group.init(G2_t);
    G1 h1 = group.init(G1_t);
    G2 h2 = group.init(G2_t);
    a = group.random(ZR_t);
    A = group.exp(g2, a);
    u = group.random(G1_t);
    v = group.random(G1_t);
    d = group.random(G1_t);
    U = group.pair(u, A);
    V = group.pair(v, A);
    D = group.pair(d, A);
    w = group.random(ZR_t);
    z = group.random(ZR_t);
    h = group.random(ZR_t);
    w1 = group.exp(g1, w);
    w2 = group.exp(g2, w);
    z1 = group.exp(g1, z);
    z2 = group.exp(g2, z);
    h1 = group.exp(g1, h);
    h2 = group.exp(g2, h);
    *i = 1;
    pk.append(U);
    pk.append(V);
    pk.append(D);
    pk.append(g1);
    pk.append(g2);
    pk.append(w1);
    pk.append(w2);
    pk.append(z1);
    pk.append(z2);
    pk.append(h1);
    pk.append(h2);
    pk.append(u);
    pk.append(v);
    pk.append(d);
    sk = a;
    return;
}

void sign(CharmList & pk, ZR & sk, int *i, string m, G1 & sig1, G1 & sig2, ZR & r)
{
    GT U;
    GT V;
    GT D;
    G1 g1;
    G2 g2;
    G1 w1;
    G2 w2;
    G1 z1;
    G2 z2;
    G1 h1;
    G2 h2;
    G1 u;
    G1 v;
    G1 d;
    ZR M = group.init(ZR_t);
    ZR t = group.init(ZR_t);
    ZR n = group.init(ZR_t);
    
    U = pk[0].getGT();
    V = pk[1].getGT();
    D = pk[2].getGT();
    g1 = pk[3].getG1();
    g2 = pk[4].getG2();
    w1 = pk[5].getG1();
    w2 = pk[6].getG2();
    z1 = pk[7].getG1();
    z2 = pk[8].getG2();
    h1 = pk[9].getG1();
    h2 = pk[10].getG2();
    u = pk[11].getG1();
    v = pk[12].getG1();
    d = pk[13].getG1();
    *i = group.add(*i, 1);
    M = group.hashListToZR(m);
    r = group.random(ZR_t);
    t = group.random(ZR_t);
    n = ceillog(2, *i);
    sig1 = group.mul(group.exp(group.mul(group.exp(u, M), group.mul(group.exp(v, r), d)), sk), group.exp(group.mul(group.exp(w1, n), group.mul(group.exp(z1, ZR(*i)), h1)), t));
    sig2 = group.exp(g1, t);
    return;
}

bool verify(GT & U, GT & V, GT & D, G2 & g2, G2 & w2, G2 & z2, G2 & h2, string m, G1 & sig1, G1 & sig2, ZR & r, int i)
{
    ZR M = group.init(ZR_t);
    ZR n = group.init(ZR_t);
    M = group.hashListToZR(m);
    n = ceillog(2, i);
    if ( ( (group.pair(sig1, g2)) == (group.mul(group.exp(U, M), group.mul(group.exp(V, r), group.mul(D, group.pair(sig2, group.mul(group.exp(w2, n), group.mul(group.exp(z2, i), h2))))))) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(GT & D, GT & U, GT & V, G2 & g2, G2 & h2, CharmListZR & rlist, CharmListG1 & sig1list, CharmListG1 & sig2list, G2 & w2, G2 & z2)
{
    if ( ( (group.ismember(D)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(U)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(V)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(h2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(rlist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(sig1list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(sig2list)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(w2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(z2)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotACache, CharmListG1 & dotECache, CharmListG1 & dotFCache, CharmListG1 & dotGCache, CharmListZR & sumBCache, CharmListZR & sumCCache, CharmListZR & sumDCache, G2 & g2, GT & U, GT & V, GT & D, G2 & w2, G2 & z2, G2 & h2)
{
    G1 dotALoopVal = group.init(G1_t, 1);
    G1 dotELoopVal = group.init(G1_t, 1);
    G1 dotFLoopVal = group.init(G1_t, 1);
    G1 dotGLoopVal = group.init(G1_t, 1);
    ZR sumBLoopVal = group.init(ZR_t, 0);
    ZR sumCLoopVal = group.init(ZR_t, 0);
    ZR sumDLoopVal = group.init(ZR_t, 0);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(dotALoopVal, 1);
    group.init(dotELoopVal, 1);
    group.init(dotFLoopVal, 1);
    group.init(dotGLoopVal, 1);
    group.init(sumBLoopVal, 0);
    group.init(sumCLoopVal, 0);
    group.init(sumDLoopVal, 0);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        dotALoopVal = group.mul(dotALoopVal, dotACache[z]);
        dotELoopVal = group.mul(dotELoopVal, dotECache[z]);
        dotFLoopVal = group.mul(dotFLoopVal, dotFCache[z]);
        dotGLoopVal = group.mul(dotGLoopVal, dotGCache[z]);
        sumBLoopVal = group.add(sumBLoopVal, sumBCache[z]);
        sumCLoopVal = group.add(sumCLoopVal, sumCCache[z]);
        sumDLoopVal = group.add(sumDLoopVal, sumDCache[z]);
    }
    if ( ( (group.pair(dotALoopVal, g2)) == (group.mul(group.exp(U, sumBLoopVal), group.mul(group.exp(V, sumCLoopVal), group.mul(group.exp(D, sumDLoopVal), group.mul(group.pair(dotELoopVal, w2), group.mul(group.pair(dotFLoopVal, z2), group.pair(dotGLoopVal, h2))))))) ) )
    {
        return;
    }
    else
    {
        midwayFloat = group.div(group.sub(endSigNum, startSigNum), 2);
        midway = int(midwayFloat);
    }
    if ( ( (midway) == (0) ) )
    {
        incorrectIndices.push_back(startSigNum);
    }
    else
    {
        midSigNum = group.add(startSigNum, midway);
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2);
    }
    return;
}

bool batchverify(GT & D, GT & U, GT & V, G2 & g2, G2 & h2, int ilist[], CharmListStr & mlist, CharmListZR & rlist, CharmListG1 & sig1list, CharmListG1 & sig2list, G2 & w2, G2 & z2, list<int> & incorrectIndices)
{
    CharmListZR delta;
    ZR M = group.init(ZR_t);
    ZR n = group.init(ZR_t);
    CharmListG1 dotACache;
    CharmListG1 dotECache;
    CharmListG1 dotFCache;
    CharmListG1 dotGCache;
    CharmListZR sumBCache;
    CharmListZR sumCCache;
    CharmListZR sumDCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(D, U, V, g2, h2, rlist, sig1list, sig2list, w2, z2)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        M = group.hashListToZR(mlist[z]);
        n = ceillog(2, ilist[z]);
        dotACache[z] = group.exp(sig1list[z], delta[z]);
        dotECache[z] = group.exp(sig2list[z], group.mul(delta[z], n));
        dotFCache[z] = group.exp(sig2list[z], group.mul(delta[z], ilist[z]));
        dotGCache[z] = group.exp(sig2list[z], delta[z]);
        sumBCache[z] = group.mul(M, delta[z]);
        sumCCache[z] = group.mul(rlist[z], delta[z]);
        sumDCache[z] = delta[z];
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2);
    return true;
}

int main()
{
    ZR sk, r;
    G1 sig1, sig2;
    CharmList pk;
    int i;
    GT U;
    GT V;
    GT D;
    G1 g1;
    G2 g2;
    G1 w1;
    G2 w2;
    G1 z1;
    G2 z2;
    G1 h1;
    G2 h2;
    G1 u;
    G1 v;
    G1 d;
    string m0 = "message0";
    string m1 = "message1";

    CharmListZR rlist;
    CharmListG1 sig1list, sig2list;
    int ilist[2];
    int i0, i1;

    setup(g1, g2);

    keygen(g1, g2, &i, pk, sk);

    U = pk[0].getGT();
    V = pk[1].getGT();
    D = pk[2].getGT();
    g1 = pk[3].getG1();
    g2 = pk[4].getG2();
    w1 = pk[5].getG1();
    w2 = pk[6].getG2();
    z1 = pk[7].getG1();
    z2 = pk[8].getG2();
    h1 = pk[9].getG1();
    h2 = pk[10].getG2();
    u = pk[11].getG1();
    v = pk[12].getG1();
    d = pk[13].getG1();
 

    sign(pk, sk, &i0, m0, sig1list[0], sig2list[0], rlist[0]);
    sign(pk, sk, &i1, m1, sig1list[1], sig2list[1], rlist[1]);
   
    bool status = verify(U, V, D, g2, w2, z2, h2, m0, sig1list[0], sig2list[0], rlist[0], i0);
    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;

    status = verify(U, V, D, g2, w2, z2, h2, m1, sig1list[1], sig2list[1], rlist[1], i1);
    if(status == true)
       cout << "True!" << endl;
    else
       cout << "False!" << endl;

    list<int> incorrectIndices;
    ilist[0] = i0;
    ilist[1] = i1;
    CharmListStr mlist;
    mlist[0] = m0;
    mlist[1] = m1;
    batchverify(D, U, V, g2, h2, ilist, mlist, rlist, sig1list, sig2list, w2, z2, incorrectIndices);
    cout << "Incorrect indices: ";
    for (list<int>::iterator it = incorrectIndices.begin(); it != incorrectIndices.end(); it++)
         cout << *it << " ";
    cout << endl;

    return 0;
}

