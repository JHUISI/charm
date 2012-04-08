

#include "group.h"

PairingGroup::PairingGroup(int sec_level)
{
	cout << "Initializing underlying curve." << endl;
	pfcObject = new PFC(sec_level);
}

PairingGroup::~PairingGroup()
{
	delete pfcObject;
}

void PairingGroup::random(Big & b)
{
	pfcObject.random(b);
}

