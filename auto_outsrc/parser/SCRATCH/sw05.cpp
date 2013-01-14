#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(NO_TYPE & n, CharmListG1 & d, CharmList & pk, CharmList & mk)
{
    G1 g = group.init(G1_t);
    ZR y = group.init(ZR_t);
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    CharmListG2 t;
    ZR dummyVar = group.init(ZR_t);
    g = group.random(G1_t);
    y = group.random(ZR_t);
    g1 = group.exp(g, y);
    g2 = group.random(G2_t);
    for (int i = 0; i < n+1; i++)
    {
        t.insert(i, group.random(G2_t));
    }
    dummyVar = group.random(ZR_t);
    pk.insert(0, g);
    pk.insert(1, g1);
    pk.insert(2, g2);
    pk.insert(3, t);
    mk.insert(0, y);
    mk.insert(1, dummyVar);
    return;
}

void evalT(CharmList & pk, NO_TYPE & n, NO_TYPE & x, G2 & T)
{
