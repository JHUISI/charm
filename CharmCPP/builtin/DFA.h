#ifndef DFA_H
#define DFA_H

#include <iostream>
#include <string>
#include <sstream>
#include "CharmListStr.h"
#include "Charm.h"
using namespace std;

//#include "regex.h"

class DFA
{
public:
	DFA();
	~DFA();
	void constructDFA(string rexpr);
	void setDFAMachine(CharmListInt & Q, CharmListStr & S, CharmMetaListInt & T, int q0, CharmListInt & F);

	bool accept(CharmListStr & w);
	CharmListInt getStates();
	CharmListStr getAlphabet();
	int getAcceptState(CharmMetaListInt & T);
	CharmListInt getAcceptStates();
	CharmMetaListInt getTransitions(); // get all the possible transitions
	CharmMetaListInt getTransitions(CharmListStr & w); // what's the argument here?
	string hashToKey(CharmListInt t);
	string getString(string w);
	string getString(int w);
	CharmListStr getSymbols(string s); // convert "abc" to {1:"a", 2:"b", etc}
private:
//	RegEx re;
	CharmListStr alphabet;
	int q0; // initial state
	CharmListInt Q, F; // list of states, accepting states
	CharmMetaListInt T; // list of transitions
	CharmListStr S; // list of
};

#endif
