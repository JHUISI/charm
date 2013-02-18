#include "TestSW.h"
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

void benchmarkSW(Sw05 & sw, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
    CharmList pk, sk, CT;
    CharmListStr w, wPrime;
    GT M, newM;
    ZR bf0, uf0, mk;
    int n = attributeCount, dParam = attributeCount;

    double de_in_ms;

    sw.setup(n, pk, mk);
    getAttributes(w, attributeCount);
    //cout << "w :\n" << w << endl;
    getAttributes(wPrime, attributeCount);
    //cout << "wPrime :\n" << wPrime << endl;
    sw.extract(mk, w, pk, dParam, n, sk);

    M = sw.group.random(GT_t);

    sw.encrypt(pk, wPrime, M, n, CT);

    stringstream s1, s2;

    //cout << "ct =\n" << CT << endl;
	for(int i = 0; i < iterationCount; i++) {
		benchD.start();
		sw.decrypt(pk, sk, CT, dParam, newM);
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
	Sw05 sw;
	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 1;
	int attributeCount = 100;
	int i = attributeCount;
	CharmListStr decryptResults;
//	for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << " attributes." << endl;
		benchmarkSW(sw, outfile1, outfile2, i, iterationCount, decryptResults);
//	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;

	return 0;
}

