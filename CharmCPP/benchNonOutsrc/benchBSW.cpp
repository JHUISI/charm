#include "TestBSW.h"
#include <fstream>

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

void benchmarkBSW(Bsw07 & bsw, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
    CharmList mk, pk, sk, ct;
    CharmListStr S;
    GT M, newM;
    double de_in_ms;

    bsw.setup(mk, pk);
    getAttributes(S, attributeCount);
    bsw.keygen(pk, mk, S, sk);

    M = bsw.group.random(GT_t);
    string policy_str =  getPolicy(attributeCount); // get a policy string
    bsw.encrypt(pk, M, policy_str, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		benchD.start();
		bsw.decrypt(pk, sk, S, ct, newM);
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

int main(int argc, const char *argv[])
{
	Bsw07 bsw;
	string filename = "bsw";
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
		benchmarkBSW(bsw, outfile1, outfile2, i, iterationCount, decryptResults);
	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;

	return 0;
}

