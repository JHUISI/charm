#ifndef HVE08_H
#define HVE08_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Hve08
{
public:
	PairingGroup group;
	Hve08() { group.setCurve(AES_SECURITY); };
	~Hve08() {};
	void setup(int n, CharmList & pk, CharmList & msk);
	void keygen(CharmList & pk, CharmList & msk, CharmListInt & yVector, ZR & uf1, CharmList & skBlinded);
	void encrypt(GT & Message, CharmListInt & xVector, CharmList & pk, CharmList & CT);
	void transform(CharmList & CT, CharmList & skBlinded, CharmList & transformOutputList);
	void decout(CharmList & transformOutputList, ZR & uf1, GT & Message2);

private:
	};


#endif