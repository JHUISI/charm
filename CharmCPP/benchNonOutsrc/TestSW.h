#ifndef SW05_H
#define SW05_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Sw05
{
public:
	PairingGroup group;
	Sw05() { group.setCurve(AES_SECURITY); };
	~Sw05() {};
	void setup(int n, CharmList & pk, ZR & mk);
	G2 evalT(CharmList & pk, int n, ZR & x);
	void extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, CharmList & sk);
	void encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT);
	void decrypt(CharmList & pk, CharmList & sk, CharmList & CT, int dParam, GT & M);

private:
	SecretUtil util;
};


#endif
