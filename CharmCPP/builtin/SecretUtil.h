#ifndef SECRETUTIL_H
#define SECRETUTIL_H

#include <string>
#include <iostream>
using namespace std;

extern "C" {
#include "util.h"
#include "policy.h"
}
#include "CharmDict.h"
#include "CharmListStr.h"

class Policy
{
public:
	charm_attribute_policy *p;
	bool isInit;
	Policy();
	~Policy();
	Policy(const Policy&);
	Policy& operator=(const Policy&);
    friend ostream& operator<<(ostream&, const Policy&);
};


/* implements secret sharing */
class SecretUtil
{
public: 
	SecretUtil(); // PairingGroup&);
	~SecretUtil();
	Policy createPolicy(string s);
	CharmListStr prune(Policy& pol, CharmListStr attrs);
	CharmListStr getAttributeList(Policy& pol);
	// CharmDict getCoefficients(Policy& pol); // TODO: implement
	// CharmDict calculateSharesDict(ZR, Policy&); // TODO: implement
	// CharmList? calculateSharesList(ZR, Policy&); // TODO: implement


private:
//	PairingGroup group;
};







#endif
