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
	void keygen(CharmList & pk, CharmList & msk, CharmListInt & yVector, CharmList & sk);
	void encrypt(GT & Message, CharmListInt & xVector, CharmList & pk, CharmList & CT);
	void decrypt(CharmList & CT, CharmList & sk, GT & Message2);

private:
	};


#endif