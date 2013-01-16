#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(list<int> & alphabet, CharmList & mpk, G1 & msk)
{
    G1 g = group.init(G1_t);
    G1 z = group.init(G1_t);
    G1 hstart = group.init(G1_t);
    G1 hend = group.init(G1_t);
    int A = 0;
    NO_TYPE a = group.init(NO_TYPE_t);
    NO TYPE FOUND FOR h
    ZR alpha = group.init(ZR_t);
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    z = group.random(G1_t);
    hstart = group.random(G1_t);
    hend = group.random(G1_t);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = string(alphabet[i]);
        h.insert(a, group.random(G1_t));
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(g, g), alpha);
    msk = group.exp(g, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, g);
    mpk.insert(2, z);
    mpk.insert(3, h);
    mpk.insert(4, hstart);
    mpk.insert(5, hend);
    return;
}

void keygen(CharmList & mpk, G1 & msk, NO_TYPE & dfaM, ZR & blindingFactor0Blinded, CharmList & skBlinded)
{
