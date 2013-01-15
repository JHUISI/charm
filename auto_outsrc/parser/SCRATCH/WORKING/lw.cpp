#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

int N = 2;

int secparam = 80;

PairingGroup group(AES_SECURITY);

void setup(CharmList & gpk)
{
    G1 g = group.init(G1_t);
    G1 dummyVar = group.init(G1_t);
    g = group.random(G1_t);
    dummyVar = group.random(G1_t);
    gpk.insert(0, g);
    gpk.insert(1, dummyVar);
    return;
}

void authsetup(CharmList & gpk, CharmList & authS, CharmList & msk, CharmList & pk)
{
