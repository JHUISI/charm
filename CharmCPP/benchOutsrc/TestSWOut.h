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
	void extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, ZR & uf0, ZR & bf0, CharmList & skBlinded);
	void encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT);
	void transform(CharmList & pk, CharmList & skBlinded, CharmList & CT, int dParam, CharmList & transformOutputList, CharmListStr & SKeys, int & SLen, CharmList & transformOutputListForLoop);
	void decout(CharmList & pk, int dParam, CharmList & transformOutputList, ZR & bf0, ZR & uf0, CharmListStr & SKeys, int SLen, CharmList & transformOutputListForLoop, GT & M);

private:
	SecretUtil util;
};


#endif
