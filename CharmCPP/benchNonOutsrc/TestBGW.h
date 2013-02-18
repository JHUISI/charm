#ifndef BGW05_H
#define BGW05_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Bgw05
{
public:
	PairingGroup group;
	Bgw05() { group.setCurve(AES_SECURITY); };
	~Bgw05() {};
	void setup(int n, CharmList & pk, CharmList & msk);
	void keygen(CharmList & pk, CharmList & msk, int n, CharmMetaListG1 & skComplete);
	void encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct);
	void decrypt(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmMetaListG1 & skComplete, GT & KDecrypt);

private:
	};


#endif
