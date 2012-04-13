#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

string decout(PairingGroup & group, CharmDict & partCT, ZR & zz, GT & egg)
{
	GT R;
	GT T0 = partCT["T0"].getGT();
	string T1 = partCT["T1"].strPtr;
	GT T2 = partCT["T2"].getGT();

	CharmList sList;

	R = group.div(T0, group.exp(T2, zz));
	string s_sesskey = DeriveKey(R);
	// string M = SymDec(s_sesskey, T1); // need to implement this as well ==> TRICKY!!!
	string M = "original message here.";

	sList.append(R);
	sList.append(M);
	ZR s = group.hashListToZR(sList);

	if( (T0 == group.mul(R, group.exp(egg, s))) && (T2 == group.exp(egg, s / zz)) ) {
		cout << "Successful Decryption!!!" << endl;
		return M; // should be a string at this point
	}
	else {
		cout << "FAILED DECRYPTION!!!" << endl;
		return string("Failed!!");
	}
}

int main()
{
	PairingGroup group(AES_SECURITY);

	// get filename with ciphertext, secret key and public key ==> deserialize into object
	// follow 'key' : 'value' format and parsing will be easier using standard string handling functions

	// verify objects well-formed

	// call decout(group, ciphertext, zz, pk) ==> M or error!

    cout << "Hello World!!!" << endl;
	return 0;
}
