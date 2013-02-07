#include "DFA.h"

DFA::DFA()
{

}

DFA::~DFA()
{
}

void DFA::constructDFA(string rexpr)
{
	return;
}
//Q = [0, 1, 2]
//T = [ (0, 1, 'a'), (1, 1, 'b'), (1, 2, 'a') ]
//q0 = 0
//F = [2]

bool DFA::accept(CharmListStr & w)
{
	return true;
}
CharmListInt DFA::getStates()
{
	CharmListInt q;
	q[0] = 0;
	q[1] = 1;
	q[2] = 2;
	q[3] = 3;
	return q;
}

CharmListStr DFA::getAlphabet()
{
	CharmListStr a;
	a[0] = "a";
	a[1] = "b";
	return a;
}

int DFA::getAcceptState(CharmMetaListInt & T)
{
	return 2;
}

CharmListInt DFA::getAcceptStates()
{
	CharmListInt f;
	f[0] = 2;
	return f;
}

CharmMetaListInt DFA::getTransitions()
{
//	 [(0, 1, 'a'), (1, 2, 'a'), (1, 3, 'b'), (3, 2, 'a'), (3, 3, 'b')]
//	char s0 = 'a', 97 s1 = 'b'; 98
	CharmMetaListInt t;
	CharmListInt t0, t1, t2, t3, t4;
	t0[0] = 0; t0[1] = 1; t0[2] = 97; // atoi(&s0);
	t1[0] = 1; t1[1] = 2; t1[2] = 97; // atoi(&s1);
	t2[0] = 1; t2[1] = 3; t2[2] = 98; // atoi(&s0);
	t3[0] = 3; t3[1] = 2; t3[2] = 97; // atoi(&s0);
	t4[0] = 3; t4[1] = 3; t4[2] = 98; // atoi(&s0);

	t[0] = t0;
	t[1] = t1;
	t[2] = t2;
	t[3] = t3;
	t[4] = t4;
	return t;
}

CharmMetaListInt DFA::getTransitions(CharmListStr & w)
{   // 1-indexed
	// {1: (0, 1, 'a'), 2: (1, 3, 'b'), 3: (3, 2, 'a')}
//	char s0 = 'a', s1 = 'b';
	CharmMetaListInt t;
	CharmListInt t0, t1, t2, t3;
	t0[0] = 0; t0[1] = 1; t0[2] = 97;
	t1[0] = 1; t1[1] = 3; t1[2] = 98;
	t2[0] = 3; t2[1] = 2; t2[2] = 97;

	t.insert(1, t0);
	t.insert(2, t1);
	t.insert(3, t2);

	return t;
}

string DFA::hashToKey(CharmListInt t)
{
	stringstream ss;
	string res;
	if (t[2] == 97) {
		res = 'a';
	}
	else if(t[2] == 98) {
		res = 'b';
	}
	ss << "(" << t[0] << "," << t[1] << "," << res << ")";
	return ss.str();
}

string DFA::getString(string w)
{
	return w;
}

string DFA::getString(int w)
{
	if (w == 97) {
		return "a";
	}
	else if(w == 98) {
		return "b";
	}
}

CharmListStr DFA::getSymbols(string s) // convert "abc" to {1:"a", 2:"b", etc}
{
	CharmListStr s2;
	int index = 1;
	const char *tmp = s.c_str();
	for(int i = 0; i < (int) s.length(); i++) {
		s2.insert(index, string(&tmp[i], 1));
		index++;
	}
	return s2;
}
