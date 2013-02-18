#include "TestWATERS.h"

string createString(int i)
{
	stringstream ss;
	ss << "ATTR" << i;
	return ss.str();
}

void getAttributes(CharmListStr & attrList, int max)
{
	for(int i = 1; i <= max; i++) {
		attrList.append(createString(i));
	}
}

string getPolicy(int max)
{
	string policystr;
	if(max >= 2) {
		policystr = "(" + createString(1) + " and " + createString(2) + ")";
	}
	else if(max == 1) {
		policystr = createString(1);
	}

	for(int i = 3; i <= max; i++)
	{
		policystr = "(" + policystr + " and " + createString(i) + ")";
	}

	return policystr;
}

void benchmarkWATERS(Waters09 & waters, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
    CharmList msk, pk, sk, ct;
    CharmListStr S;
    GT M, newM;
    double de_in_ms;

    waters.setup(msk, pk);
    getAttributes(S, attributeCount);
    waters.keygen(pk, msk, S, sk);

    M = waters.group.random(GT_t);
    string policy_str =  getPolicy(attributeCount); // get a policy string
    waters.encrypt(pk, M, policy_str, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		benchD.start();
		waters.decrypt(pk, sk, S, ct, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
	s2 << attributeCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[attributeCount] = benchD.getRawResultString();
//    cout << convert_str(M) << endl;
//    cout << convert_str(newM) << endl;
    if(M == newM) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
    return;
}

int main()
{
	Waters09 waters;
	string filename = "waters";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 10;
	int attributeCount = 10;
	CharmListStr decryptResults;
	for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << " attributes." << endl;
		benchmarkWATERS(waters, outfile1, outfile2, i, iterationCount, decryptResults);
	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt benchmarkWATERS breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt benchmarkWATERS breakdown ===>" << endl;

	return 0;
}

