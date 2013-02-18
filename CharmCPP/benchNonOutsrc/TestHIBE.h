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
	void keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pk, CharmList & sk);
	void encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct);
	void decrypt(CharmList & pk, CharmList & sk, CharmList & ct, GT & M);

private:
	};


#endif