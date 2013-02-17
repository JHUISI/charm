#ifndef BSW07_H
#define BSW07_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Bsw07
{
public:
	PairingGroup group;
	Bsw07() { group.setCurve(MNT160); };
	~Bsw07() {};
	void setup(CharmList & mk, CharmList & pk);
	void keygen(CharmList & pk, CharmList & mk, CharmListStr & S, ZR & bf0, CharmList & skBlinded);
	void encrypt(CharmList & pk, GT & M, string & policyUSstr, CharmList & ct);
	void transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList);
	void decout(CharmList & pk, CharmListStr & S, CharmList & transformOutputList, ZR & bf0, GT & M);

private:
	SecretUtil util;
};


#endif
