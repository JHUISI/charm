#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(CharmList & msk, CharmList & pk)
{
    G1 g1 = group.init(G1_t);
    G2 g2 = group.init(G2_t);
    ZR alpha = group.init(ZR_t);
    ZR a = group.init(ZR_t);
    GT egg = group.init(GT_t);
    G1 g1alph = group.init(G1_t);
    G2 g2alph = group.init(G2_t);
    G1 g1a = group.init(G1_t);
    G2 g2a = group.init(G2_t);
    g1 = group.random(G1_t);
    g2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    a = group.random(ZR_t);
    egg = group.exp(group.pair(g1, g2), alpha);
    g1alph = group.exp(g1, alpha);
    g2alph = group.exp(g2, alpha);
    g1a = group.exp(g1, a);
    g2a = group.exp(g2, a);
    msk.insert(0, g1alph);
    msk.insert(1, g2alph);
    pk.insert(0, g1);
    pk.insert(1, g2);
    pk.insert(2, egg);
    pk.insert(3, g1a);
    pk.insert(4, g2a);
    return;
}

void keygen(CharmList & pk, CharmList & msk, CharmList & S, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
