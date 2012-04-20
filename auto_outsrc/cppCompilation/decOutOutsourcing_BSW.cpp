#include "userFuncs_BSW.h"

string decout(PairingGroup & group, CharmDict & partCT, ZR & zz, GT & egg)
{
	
	GT T0 = partCT["T0"].getGT();
	string T1 = partCT["T1"].strPtr;
	GT T2 = partCT["T2"].getGT();
	GT R = group.div(T0, group.exp(T2, zz));
	string s_sesskey = DeriveKey(R);
	string M = SymDec(s_sesskey, T1);
	CharmList hashRandM;
	hashRandM.append(R);
	hashRandM.append(M);
	ZR s = group.hashListToZR(hashRandM);
	if ( ( (( (T0) == (group.mul(R, group.exp(egg, s))) )) && (( (T2) == (group.exp(egg, group.div(s, zz))) )) ) )
	{
		string output = M;
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

	return 0;
}
