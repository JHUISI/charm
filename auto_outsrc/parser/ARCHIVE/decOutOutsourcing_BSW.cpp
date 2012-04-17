#include "sdlconfig.h"
#include <iostream>
#include <sstream>
#include <string>
using namespace std;
#define DEBUG  true

string decout(PairingGroup & groupObj, CharmDict & partCT, ZR & zz, GT & egg)
{
	CharmDict input;
	input.append(partCT);
	input.append(zz);
	input.append(egg);
	CharmDict partCT;
	partCT.append(T0);
	partCT.append(T1);
	partCT.append(T2);
	GT R = groupObj.div(T0, groupObj.exp(T2, zz));
	string s_sesskey = DeriveKey(R);
	string M = SymDec(s_sesskey, T1);
	CharmDict hashRandM;
	hashRandM.append(R);
	hashRandM.append(M);
	ZR s = groupObj.hashListToZR(hashRandM);
	if ( ( (( (T0) == (groupObj.mul(R, groupObj.exp(egg, s))) )) && (( (T2) == (groupObj.exp(egg, groupObj.div(s, zz))) )) ) )
	{
		CharmDict output = M;
	}
	else
	{
		userErrorFunction('invalid ciphertext');
		return NULL;
	}
	return M;
}

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	M = decout(sys.argv[1], sys.argv[2], sys.argv[3])
