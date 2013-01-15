#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(int n, CharmList & pk, CharmList & msk)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    GT egg = group.init(GT_t);
    ZR y = group.init(ZR_t);
    GT Y = group.init(GT_t);
    CharmListZR t;
    CharmListZR v;
    CharmListZR r;
    CharmListZR m;
    CharmListG1 T;
    CharmListG1 V;
    CharmListG1 R;
    CharmListG1 M;
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    egg = group.pair(g1, g2);
    y = group.random(ZR_t);
    Y = group.exp(egg, y);
    for (int i = 0; i < n; i++)
    {
        t.insert(i, group.random(ZR_t));
        v.insert(i, group.random(ZR_t));
        r.insert(i, group.random(ZR_t));
        m.insert(i, group.random(ZR_t));
        T.insert(i, group.exp(g1, t[i]));
        V.insert(i, group.exp(g1, v[i]));
        R.insert(i, group.exp(g1, r[i]));
        M.insert(i, group.exp(g1, m[i]));
    }
    pk.insert(0, g1);
    pk.insert(1, g2);
    pk.insert(2, n);
    pk.insert(3, Y);
    pk.insert(4, T);
    pk.insert(5, V);
    pk.insert(6, R);
    pk.insert(7, M);
    msk.insert(0, y);
    msk.insert(1, t);
    msk.insert(2, v);
    msk.insert(3, r);
    msk.insert(4, m);
    return;
}

void keygen(CharmList & pk, CharmList & msk, NO_TYPE & yVector, CharmListZR & blindingFactorLVectorBlinded, CharmListZR & blindingFactorYVectorBlinded, CharmList & sk2Blinded)
{
