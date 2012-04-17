#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;
#define DEBUG  true

string decout(PairingGroup & group, CharmDict & partCT, ZR & zz, GT & egg)
{
	GT R;
	GT T0 = partCT["T0"].getGT();
	string T1 = partCT["T1"].strPtr;
	GT T2 = partCT["T2"].getGT();

	CharmList sList;

	R = group.div(T0, group.exp(T2, zz));
	string s_sesskey = DeriveKey(R);
	string M = SymDec(s_sesskey, T1);
	if(DEBUG) {
		cout << "R := " << convert_str(R) << endl;
		cout << "Session key := " << s_sesskey << endl;
		cout << "M := " << M << endl;
	}

	sList.append(R);
	sList.append(M);
	ZR s = group.hashListToZR(sList);

	if( (T0 == group.mul(R, group.exp(egg, s))) && (T2 == group.exp(egg, group.div(s, zz))) ) {
		cout << "Successful Decryption!!!" << endl;
		return M; // should be a string at this point
	}
	else {
		cout << "FAILED DECRYPTION!!!" << endl;
		return string("Failed!!");
	}
}

int main(int argc, char* argv[])
{
	if(argc < 3) {
		cout << "Usage: " << argv[0] << " [ partCT.txt ] [ keys.txt ]" << endl;
		return -1;
	}
	cout << "argc = " << argc << endl;
	for(int i = 0; i < argc; i++)
		cout << "argv[" << i << "] = " << argv[i] << endl;

   PairingGroup group(AES_SECURITY);

	// get filename with ciphertext, secret key and public key ==> deserialize into object
	// follow 'key' : 'value' format and parsing will be easier using standard string handling functions
	CharmDict dict;
	ZR sk;
	GT pk;

	Element T0,T1,T2;
	dict.set("T0", T0);
	dict.set("T1", T1);
	dict.set("T2", T2);
	// verify objects well-formed
	parsePartCT(argv[1], dict);
	parseKeys(argv[2], sk, pk);
	cout << "sk => " << sk << endl;
	cout << "pk => " << convert_str(pk) << endl;

	// call decout(group, ciphertext, zz, pk) ==> M or error!
	string M = decout(group, dict, sk, pk);
	cout << "Recovered message :=> " << M << endl;
	return 0;
}
