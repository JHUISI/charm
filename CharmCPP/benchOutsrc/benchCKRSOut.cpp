#include "TestCKRSOut.h"
#include <fstream>

void benchmarkCKRS(Ibeckrs09 & ckrs, ofstream & outfile1, ofstream & outfile2, int iterationCount, string & transformResults, string & decoutResults)
{
	int n = 5;
	int l = 32;
	Benchmark benchT, benchD;
	CharmList mpk, msk, ct, skBlinded, transformOutputList;
    GT M, newM;
    ZR uf1;
    string id = "somebody@example.com"; // make this longer?
    double tf_in_ms, de_in_ms;

	ckrs.setup(n, l, mpk, msk);
	ckrs.extract(mpk, msk, id, uf1, skBlinded);

    M = ckrs.group.random(GT_t);
    ckrs.encrypt(mpk, M, id, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchT.start();
		ckrs.transform(skBlinded, ct, transformOutputList);
		benchT.stop();
		//cout << "transformCT =\n" << transformOutputList << endl;
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		ckrs.decout(transformOutputList, uf1, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << iterationCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults = benchD.getRawResultString();

    cout << convert_str(M) << endl;
    cout << convert_str(newM) << endl;
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
	Ibeckrs09 ckrs;
	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 100;
	string transformResults, decoutResults;

	cout << "Benchmark iterations: " << iterationCount << endl;
	benchmarkCKRS(ckrs, outfile1, outfile2, iterationCount, transformResults, decoutResults);

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

