#ifndef LW10_H
#define LW10_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Lw10
{
public:
	PairingGroup group;
	Lw10() { group.setCurve(AES_SECURITY); };
	~Lw10() {};
	void setup(CharmList & gpk);
	void authsetup(CharmList & gpk, CharmListStr & authS, CharmMetaList & msk, CharmMetaList & pk);
	void keygen(CharmList & gpk, CharmMetaList & msk, string & gid, CharmListStr & userS, CharmListZR & blindingFactorKBlinded, CharmList & skBlinded);
	void encrypt(CharmMetaList & pk, CharmList & gpk, GT & M, string & policy_str, CharmList & ct);
	void transform(CharmList & skBlinded, CharmListStr & userS, CharmList & ct, CharmList & transformOutputList, CharmListStr & attrs, int & Y, CharmList & transformOutputListForLoop);
	void decout(CharmListStr & userS, CharmList & transformOutputList, CharmListZR & blindingFactorKBlinded, CharmListStr & attrs, int Y, CharmList & transformOutputListForLoop, GT & M);

private:
	SecretUtil util;
};


#endif