#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(CharmList & mk, CharmList & pk)
{
    G1 g = group.init(G1_t);
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 h = group.init(G1_t);
    G1 f = group.init(G1_t);
    G1 i = group.init(G1_t);
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    h = group.exp(g, beta);
    f = group.exp(g, group.div(1, beta));
    i = group.exp(g, alpha);
    egg = group.exp(group.pair(g, g), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, g);
    pk.insert(1, h);
    pk.insert(2, f);
    pk.insert(3, egg);
    return;
}

void keygen(CharmList & pk, CharmList & mk, CharmList & S, ZR & blindingFactorDBlinded, CharmList & skBlinded)
{
