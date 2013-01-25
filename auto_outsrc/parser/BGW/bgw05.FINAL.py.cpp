#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(NO_TYPE & nParam, CharmList & pk, CharmList & msk)
{
    int n = 0;
    G1 g = group.init(G1_t);
    ZR alpha = group.init(ZR_t);
    int endIndexOfList = 0;
    CharmListG1 giValues;
    ZR gamma = group.init(ZR_t);
    G1 v = group.init(G1_t);
    ZR dummyVar = group.init(ZR_t);
    n = nParam;
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    endIndexOfList = group.add(group.mul(2, n), 1);
    for (int i = 1; i < endIndexOfList; i++)
    {
        giValues.insert(i, group.exp(g, group.exp(alpha, i)));
    }
    gamma = group.random(ZR_t);
    v = group.exp(g, gamma);
    pk.insert(0, g);
    pk.insert(1, n);
    pk.insert(2, giValues);
    pk.insert(3, v);
    dummyVar = group.random(ZR_t);
    msk.insert(0, gamma);
    msk.insert(1, dummyVar);
    return;
}

void keygen(CharmList & pk, CharmList & msk, ZR & blindingFactor0Blinded, CharmList & skCompleteBlinded)
{
