#ifndef HIBE_H
#define HIBE_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Hibe
{
public:
	PairingGroup group;
	Hibe() { group.setCurve(AES_SECURITY); };
	~Hibe() {};
	void setup(int l, int z, CharmList & mpk, CharmList & mk);
	void keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pk, ZR & uf0, CharmList & skBlinded);
	void encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct);
	void transform(CharmList & pk, CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList);
	void decout(CharmList & pk, CharmList & transformOutputList, ZR & uf0, GT & M);

private:
	};


#endif