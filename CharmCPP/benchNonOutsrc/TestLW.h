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
	void keygen(CharmList & gpk, CharmMetaList & msk, string & gid, CharmListStr & userS, CharmList & sk);
	void encrypt(CharmMetaList & pk, CharmList & gpk, GT & M, string & policy_str, CharmList & ct);
	void decrypt(CharmList & sk, CharmListStr & userS, CharmList & ct, GT & M);

private:
	SecretUtil util;
};


#endif