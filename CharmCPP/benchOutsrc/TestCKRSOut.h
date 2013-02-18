#ifndef IBECKRS09_H
#define IBECKRS09_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Ibeckrs09
{
public:
	PairingGroup group;
	Ibeckrs09() { group.setCurve(AES_SECURITY); };
	~Ibeckrs09() {};
	void setup(int n, int l, CharmList & mpk, CharmList & msk);
	void extract(CharmList & mpk, CharmList & msk, string & id, ZR & uf1, CharmList & skBlinded);
	void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct);
	void transform(CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList);
	void decout(CharmList & transformOutputList, ZR & uf1, GT & M);

private:
	};


#endif