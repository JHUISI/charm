#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 100;

int l = 3;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(G2 & P, G2 & g, ZR & alpha)
{
    g = group.random(G2_t);
    alpha = group.random(ZR_t);
    P = group.exp(g, alpha);
    return;
}

void concat(NO_TYPE & ID_List, string L)
{
    int l = 0;
    group.init(L);
    l = len(ID_List);
    for (int y = 0; y < l; y++)
    {
        L = (L + ID_List[y]);
    }
    return;
}

void keygen(ZR & alpha, string ID, G1 & pk, G1 & sk)
{
    sk = group.exp(group.hashListToG1(ID), alpha);
    pk = group.hashListToG1(ID);
    return;
}

void sign(string ID, CharmListStr & ID_list, G1 & pk, G1 & sk, string M, CharmListStr & Lt, CharmListG1 & pklist, CharmListG1 & u, G1 & S)
{
    CharmListZR h;
    int s = 0;
    ZR *r = group.init(ZR_t);
    G1 *dotProd = group.init(G1_t, 1);
    Lt = concat(ID_list);
    for (int i = 0; i < l; i++)
    {
        if ( ( (ID) != (ID_list[i]) ) )
        {
            u[i] = group.random(G1_t);
            h[i] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[i])));
        }
        else
        {
            s = i;
        }
    }
    *r = group.random(ZR_t);
    for (int y = 0; y < l; y++)
    {
        pklist[y] = group.hashListToG1(ID_list[y]);
    }
    group.init(*dotProd, 1);
    for (int i = 0; i < l; i++)
    {
        if ( ( (ID) != (ID_list[i]) ) )
        {
            *dotProd = group.mul(*dotProd, group.mul(u[i], group.exp(pklist[i], h[i])));
        }
    }
    u[s] = group.mul(group.exp(pk, *r), group.exp(*dotProd, -1));
    h[s] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[s])));
    S = group.exp(sk, group.add(h[s], *r));
    return;
}

bool verify(CharmListStr & Lt, CharmListG1 & pklist, G2 & P, G2 & g, string M, CharmListG1 & u, G1 & S)
{
    CharmListZR h;
    G1 *dotProd = group.init(G1_t, 1);
    for (int y = 0; y < l; y++)
    {
        h[y] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[y])));
    }
    group.init(*dotProd, 1);
    for (int y = 0; y < l; y++)
    {
        *dotProd = group.mul(*dotProd, group.mul(u[y], group.exp(pklist[y], h[y])));
    }
    if ( ( (group.pair(*dotProd, P)) == (group.pair(S, g)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & P, CharmListG1 & Slist, G2 & g, CharmListG1 & pklist, CharmList & ulist)
{
    if ( ( (group.ismember(P)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Slist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(pklist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(ulist)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListG1 & dotBCache, CharmListG1 & dotCCache, G2 & P, G2 & g)
{
    G1 *dotBLoopVal = group.init(G1_t, 1);
    G1 *dotCLoopVal = group.init(G1_t, 1);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    group.init(*dotBLoopVal, 1);
    group.init(*dotCLoopVal, 1);
    for (int z = startSigNum; z < endSigNum; z++)
    {
        *dotBLoopVal = group.mul(*dotBLoopVal, dotBCache[z]);
        *dotCLoopVal = group.mul(*dotCLoopVal, dotCCache[z]);
    }
    if ( ( (group.pair(*dotBLoopVal, P)) == (group.pair(*dotCLoopVal, g)) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotBCache, dotCCache, P, g);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g);
    }
    return;
}

bool batchverify(CharmListStr & Lt, CharmListStr & Mlist, G2 & P, CharmListG1 & Slist, G2 & g, CharmListG1 & pklist, CharmList & ulist, list<int> & incorrectIndices)
{
    CharmListZR delta;
    G1 *dotALoopVal = group.init(G1_t, 1);
    ZR *h = group.init(ZR_t);
    CharmListG1 dotBCache;
    CharmListG1 dotCCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(P, Slist, g, pklist, ulist)) == (false) ) )
    {
        return false;
    }
    for (int z = 0; z < N; z++)
    {
        group.init(*dotALoopVal, 1);
        for (int y = 0; y < l; y++)
        {
            *h = group.hashListToZR((Element(Mlist[z][y]) + Element(Lt) + Element(ulist[z][y])));
            *dotALoopVal = group.mul(*dotALoopVal, group.mul(group.exp(ulist[z][y], delta[z]), group.exp(pklist[y], group.mul(*h, delta[z]))));
        }
        dotBCache[z] = *dotALoopVal;
        dotCCache[z] = group.exp(Slist[z], delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotBCache, dotCCache, P, g);
    return true;
}

int main()
{
    return 0;
}
