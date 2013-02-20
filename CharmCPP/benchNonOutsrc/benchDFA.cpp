
#include "TestDFA.h"

int main(int argc, const char *argv[])
{
	Dfa12 dfa12;

	dfa12.dfaUtil.constructDFA("ab*a");
	CharmList mpk, sk, ct;
	CharmListStr alphabet = dfa12.dfaUtil.getAlphabet();
	CharmListStr w;
	CharmListInt Q = dfa12.dfaUtil.getStates(), F = dfa12.dfaUtil.getAcceptStates(); // get all states, and all accept states
	CharmMetaListInt T = dfa12.dfaUtil.getTransitions(); // get all transitions in DFA
	G1 msk;
	GT M, newM, Cm;

	cout << "Q:\n" << Q << endl;
	cout << "F:\n" << F << endl;
	cout << "T:\n" << T << endl;

	dfa12.setup(alphabet, mpk, msk);

	cout << "MPK:\n" << mpk << endl;
	cout << "MSK:\n" << convert_str(msk) << endl;
	dfa12.keygen(mpk, msk, Q, T, F, sk);

	cout << "SK:\n" << sk << endl;

	// build w
	w = dfa12.dfaUtil.getSymbols("aba");
	M = dfa12.group.random(GT_t);
	dfa12.encrypt(mpk, w, M, ct);

	dfa12.decrypt(sk, ct, newM);
    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return 0;
}

