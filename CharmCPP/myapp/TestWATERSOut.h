#ifndef WATERS09_H
#define WATERS09_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;

class Waters09
{
public:
   PairingGroup group;
   Waters09() { group.setCurve(AES_SECURITY); };
   ~Waters09() { };
   void setup(CharmList & msk, CharmList & pk);
   void keygen(CharmList & pk, CharmList & msk, CharmListStr & S, ZR & bf0, CharmList & skBlinded);
   void encrypt(CharmList & pk, GT & M, string & policy_str, CharmList & ct);
   void transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList, int & Y);
   void decout(CharmList & pk, CharmListStr & S, CharmList & transformOutputList, ZR & bf0, int Y, GT & M);

private:
   SecretUtil util; 
};

#endif
