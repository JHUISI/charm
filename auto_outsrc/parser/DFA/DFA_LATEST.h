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
	void keygen(CharmList & mpk, G1 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, ZR & bf0, CharmList & skBlinded);
	void encrypt(CharmList & mpk, string & w, GT & M, CharmList & ct);
	void transform(CharmList & skBlinded, CharmList & ct, NO_TYPE & dfaM, CharmList & transformOutputList, int & l, CharmMetaListInt & Ti, CharmList & transformOutputListForLoop);
	void decout(NO_TYPE & dfaM, CharmList & transformOutputList, ZR & bf0, int l, CharmMetaListInt & Ti, CharmList & transformOutputListForLoop, GT & M);

private:
	DFA dfaUtil;
};


#endif