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
	void keygen(CharmList & pk, CharmList & msk, int n, ZR & bf0, CharmList & skCompleteBlinded);
	void encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct);
	void transform(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & skCompleteBlinded, CharmList & transformOutputList);
	void decout(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & skCompleteBlinded, CharmList & transformOutputList, ZR & bf0, GT & KDecrypt);

private:
	};


#endif