#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(NO_TYPE & l, NO_TYPE & z, CharmList & mpk, CharmList & mk)
{
    ZR alpha = group.init(ZR_t);
    ZR beta = group.init(ZR_t);
    G1 g = group.init(G1_t);
    G2 gb = group.init(G2_t);
    G1 g1 = group.init(G1_t);
    G2 g1b = group.init(G2_t);
    CharmListZR delta;
    CharmListG1 h;
    CharmListG2 hb;
    G2 g0b = group.init(G2_t);
    GT v = group.init(GT_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    g = group.random(G1_t);
    gb = group.random(G2_t);
    g1 = group.exp(g, alpha);
    g1b = group.exp(gb, alpha);
    for (int y = 0; y < l; y++)
    {
        delta.insert(y, group.random(ZR_t));
        h.insert(y, group.exp(g, delta[y]));
        hb.insert(y, group.exp(gb, delta[y]));
    }
    g0b = group.exp(gb, group.mul(alpha, beta));
    v = group.pair(g, g0b);
    mpk.insert(0, g);
    mpk.insert(1, g1);
    mpk.insert(2, h);
    mpk.insert(3, gb);
    mpk.insert(4, g1b);
    mpk.insert(5, hb);
    mpk.insert(6, v);
    mpk.insert(7, l);
    mpk.insert(8, z);
    mk.insert(0, g0b);
    mk.insert(1, None);
    return;
}

void keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pkBlinded, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
