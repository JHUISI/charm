#include "TestSWOut.h"
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

void benchmarkSW(Sw05 & sw, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	Benchmark benchT, benchD;
    CharmList pk, skBlinded, CT, transformOutputList, transformOutputListForLoop;
    CharmListStr w, wPrime;
    GT M, newM;
    ZR bf0, uf0, mk;
    int n = attributeCount, dParam = 1;

    double tf_in_ms, de_in_ms;

    sw.setup(n, pk, mk);
    getAttributes(w, attributeCount);
    //cout << "w :\n" << w << endl;
    getAttributes(wPrime, attributeCount);
    //cout << "wPrime :\n" << wPrime << endl;
    sw.extract(mk, w, pk, dParam, n, uf0, bf0, skBlinded);

    M = sw.group.random(GT_t);

    sw.encrypt(pk, wPrime, M, n, CT);

    stringstream s1, s2;

    //cout << "ct =\n" << CT << endl;
	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		CharmListStr SKeys;
		int SLen;
		benchT.start();
		sw.transform(pk, skBlinded, CT, dParam, transformOutputList, SKeys, SLen, transformOutputListForLoop);
		benchT.stop();
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		sw.decout(pk, dParam, transformOutputList, bf0, uf0, SKeys, SLen, transformOutputListForLoop, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << attributeCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults[attributeCount] = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << attributeCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults[attributeCount] = benchD.getRawResultString();

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

	int iterationCount = 10;
	int attributeCount = 100;
	int i = attributeCount;
	CharmListStr transformResults, decoutResults;
//	for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << " attributes." << endl;
		benchmarkSW(sw, outfile1, outfile2, i, iterationCount, transformResults, decoutResults);
//	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;
	cout << transformResults << endl;
	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;

	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;
	cout << decoutResults << endl;
	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;

	return 0;
}

