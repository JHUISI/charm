#include "userFuncs_BSW.h"

string decout(PairingGroup & group, CharmDict & partCT, ZR & zz, GT & omega)
{
	GT T0;
	string T1;
	GT T2;
	GT R;
	string s_sesskey;
	string M;
	CharmList hashRandM;
	ZR s;
	string output;
	
	T0 = partCT["T0"].getGT();
	T1 = partCT["T1"].strPtr;
	T2 = partCT["T2"].getGT();
	R = group.mul(T0, group.exp(T2, zz));
	s_sesskey = DeriveKey(R);
	M = SymDec(s_sesskey, T1);
	hashRandM.append(R);
	hashRandM.append(M);
	s = group.hashListToZR(hashRandM);
	if ( ( (( (T0) == (group.mul(R, group.exp(omega, s))) )) && (( (T2) == (group.exp(omega, group.div(s, zz))) )) ) )
	{
		output = M;
	}
	else
	{
		userErrorFunction("invalid ciphertext");
		return "";
	}
	return output;
}

int main(int argc, char* argv[])
{
	PairingGroup group(MNT160);

	CharmDict dict;
	ZR zz;
	GT pk;

	Element T0, T1, T2;
	dict.set("T0", T0);
	dict.set("T1", T1);
	dict.set("T2", T2);

	parsePartCT("partCT_BSW_.txt", dict);
	parseKeys("keys_BSW_.txt", zz, pk);

	string M = decout(group, dict, zz, pk);

	cout << M << endl;

	return 0;
}
