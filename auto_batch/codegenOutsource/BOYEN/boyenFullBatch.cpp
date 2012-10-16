#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 100;

int l = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

ZR & SmallExp(int bits) {
    big t = mirvar(0);
    bigbits(bits, t);

    ZR *z = new ZR(t);
    mr_free(t);
    return *z;
}

void setup(CharmList & mpk, G1 & g1, G2 & g2)
{
    ZR *a0 = group.init(ZR_t);
    ZR *b0 = group.init(ZR_t);
    ZR *c0 = group.init(ZR_t);
    G1 *A0 = group.init(G1_t);
    G1 *B0 = group.init(G1_t);
    G1 *C0 = group.init(G1_t);
    G2 *At0 = group.init(G2_t);
    G2 *Bt0 = group.init(G2_t);
    G2 *Ct0 = group.init(G2_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    *a0 = group.random(ZR_t);
    *b0 = group.random(ZR_t);
    *c0 = group.random(ZR_t);
    *A0 = group.exp(g1, *a0);
    *B0 = group.exp(g1, *b0);
    *C0 = group.exp(g1, *c0);
    *At0 = group.exp(g2, *a0);
    *Bt0 = group.exp(g2, *b0);
    *Ct0 = group.exp(g2, *c0);
    mpk.append(*A0);
    mpk.append(*B0);
    mpk.append(*C0);
    mpk.append(*At0);
    mpk.append(*Bt0);
    mpk.append(*Ct0);
    return;
}

void keygen(G1 & g1, G2 & g2, CharmList & pk, CharmList & sk)
{
    ZR *a = group.init(ZR_t);
    ZR *b = group.init(ZR_t);
    ZR *c = group.init(ZR_t);
    G1 *A = group.init(G1_t);
    G2 *At = group.init(G2_t);
    G1 *B = group.init(G1_t);
    G2 *Bt = group.init(G2_t);
    G1 *C = group.init(G1_t);
    G2 *Ct = group.init(G2_t);
    *a = group.random(ZR_t);
    *b = group.random(ZR_t);
    *c = group.random(ZR_t);
    *A = group.exp(g1, *a);
    *At = group.exp(g2, *a);
    *B = group.exp(g1, *b);
    *Bt = group.exp(g2, *b);
    *C = group.exp(g1, *c);
    *Ct = group.exp(g2, *c);
    sk.append(*a);
    sk.append(*b);
    sk.append(*c);
    pk.append(*A);
    pk.append(*B);
    pk.append(*C);
    pk.append(*At);
    pk.append(*Bt);
    pk.append(*Ct);
    return;
}

void sign(G1 & g1, CharmListG1 & Alist, CharmListG1 & Blist, CharmListG1 & Clist, CharmList & sk, CharmListStr & Mlist, NO_TYPE & index, CharmListG1 & S, CharmListZR & t)
{
    ZR *m = group.init(ZR_t);
    CharmListZR s;
    G1 *prod0 = group.init(G1_t);
    G1 *prod1 = group.init(G1_t);
    G1 *resultSign = group.init(G1_t);
    ZR *d = group.init(ZR_t);
    *m = group.hashListToZR(M);
    for (int y = 0; y < l; y++)
    {
        if ( ( (y) != (index) ) )
        {
            s[y] = group.random(ZR_t);
            S[y] = group.exp(g1, s[y]);
        }
    }
    for (int y = 0; y < l; y++)
    {
        t[y] = group.random(ZR_t);
    }
    *prod0 = group.exp(group.mul(group.mul(Alist[0], group.exp(Blist[0], *m)), group.exp(Clist[0], t[0])), -s[0]);
    for (int y = 1; y < l; y++)
    {
        if ( ( (y) != (index) ) )
        {
            *prod1 = group.mul(*prod1, group.exp(group.mul(Alist[y], group.mul(group.exp(Blist[y], m[y]), group.exp(Clist[y], t[y]))), -s[y]));
        }
    }
    *resultSign = group.mul(*prod0, *prod1);
    *d = group.add(group.add(a, group.mul(b, *m)), group.mul(c, t[index]));
    S[index] = group.exp(group.mul(g1, *resultSign), group.div(1, *d));
    return;
}

bool verify(G1 & g1, G2 & g2, G2 & Atlist, G2 & Btlist, G2 & Ctlist, string M, CharmListG1 & S, CharmListZR & t)
{
    GT *D = group.init(GT_t);
    ZR *m = group.init(ZR_t);
    GT *resultVerify = group.init(GT_t);
    *D = group.pair(g1, g2);
    *m = group.hashListToZR(M);
    for (int y = 0; y < l; y++)
    {
        *resultVerify = group.mul(*resultVerify, group.pair(S[y], group.mul(Atlist[y], group.mul(group.exp(Btlist[y], *m), group.exp(Ctlist[y], t[y])))));
    }
    if ( ( (*resultVerify) == (*D) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

bool membership(G2 & Atlist, G2 & Btlist, G2 & Ctlist, CharmListG1 & Slist, G1 & g1, G2 & g2, CharmListZR & tlist)
{
    if ( ( (group.ismember(Atlist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Btlist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Ctlist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(Slist)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g1)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(g2)) == (false) ) )
    {
        return false;
    }
    if ( ( (group.ismember(tlist)) == (false) ) )
    {
        return false;
    }
    return true;
}

void dividenconquer(CharmListZR & delta, int startSigNum, int endSigNum, list<int> & incorrectIndices, CharmListGT & dotDCache, G2 & Atlist, G2 & Btlist, G2 & Ctlist, CharmListStr & Mlist, CharmListG1 & Slist, G1 & g1, G2 & g2, CharmListZR & tlist)
{
    GT *dotDLoopVal = group.init(GT_t);
    G1 *dotALoopVal = group.init(G1_t);
    G1 *dotBLoopVal = group.init(G1_t);
    G1 *dotCLoopVal = group.init(G1_t);
    GT *dotELoopVal = group.init(GT_t);
    int midwayFloat = 0;
    int midway = 0;
    int midSigNum = 0;
    for (int z = startSigNum; z < endSigNum; z++)
    {
        *dotDLoopVal = group.mul(*dotDLoopVal, dotDCache[z]);
    }
    for (int y = 0; y < l; y++)
    {
        for (int z = startSigNum; z < endSigNum; z++)
        {
            *dotALoopVal = group.mul(*dotALoopVal, group.exp(Slist[z][y], delta[z]));
            *dotBLoopVal = group.mul(*dotBLoopVal, group.exp(Slist[z][y], group.mul(m[z], delta[z])));
            *dotCLoopVal = group.mul(*dotCLoopVal, group.exp(Slist[z][y], group.mul(tlist[z][y], delta[z])));
        }
        *dotELoopVal = group.mul(*dotELoopVal, group.mul(group.pair(*dotALoopVal, Atlist[y]), group.mul(group.pair(*dotBLoopVal, Btlist[y]), group.pair(*dotCLoopVal, Ctlist[y]))));
    }
    if ( ( (*dotELoopVal) == (*dotDLoopVal) ) )
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist);
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist);
    }
    return;
}

bool batchverify(G2 & Atlist, G2 & Btlist, G2 & Ctlist, CharmListStr & Mlist, CharmListG1 & Slist, G1 & g1, G2 & g2, CharmListZR & tlist, list<int> & incorrectIndices)
{
    CharmListZR delta;
    GT *D = group.init(GT_t);
    CharmListGT dotDCache;
    for (int z = 0; z < N; z++)
    {
        delta[z] = SmallExp(secparam);
    }
    if ( ( (membership(Atlist, Btlist, Ctlist, Slist, g1, g2, tlist)) == (false) ) )
    {
        return false;
    }
    *D = group.pair(g1, g2);
    for (int z = 0; z < N; z++)
    {
        dotDCache[z] = group.exp(*D, delta[z]);
    }
    dividenconquer(delta, 0, N, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist);
    return true;
}

int main()
{
    return 0;
}
