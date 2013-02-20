#ifndef DFA12_H
#define DFA12_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Dfa12
{
public:
	PairingGroup group;
	Dfa12() { group.setCurve(AES_SECURITY); };
	~Dfa12() {};
	void setup(CharmListStr & alphabet, CharmList & mpk, G1 & msk);
	void keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, CharmList & sk);
	void encrypt(CharmList & mpk, CharmListStr & w, GT & M, CharmList & ct);
	void decrypt(CharmList & sk, CharmList & ct, GT & M); // figure out what a dfaM type should be: NO_TYPE & dfaM
	DFA dfaUtil;

private:
};


#endif
