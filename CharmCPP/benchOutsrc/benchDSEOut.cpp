#include "TestDSEOut.h"
#include <fstream>

void benchmarkDSE(ofstream & outfile1, ofstream & outfile2, int iterationCount, string & transformResults, string & decoutResults)
{
	Dsewaters09 dse;
	Benchmark benchT, benchD;
    CharmList msk, mpk, pk, skBlinded, ct, transformOutputList;
//    CharmListStr S;
    GT M, newM;
    ZR bf0;
    string id = "somebody@example.com and other people!!!!!";
    double tf_in_ms, de_in_ms;

	dse.setup(mpk, msk);
	dse.keygen(mpk, msk, id, bf0, skBlinded);

    M = dse.group.random(GT_t);
    cout << "M: " << convert_str(M) << endl;
    dse.encrypt(mpk, M, id, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
//	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchT.start();
		dse.transform(ct, skBlinded, transformOutputList);
		benchT.stop();
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		dse.decout(transformOutputList, bf0, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
//	}

	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << iterationCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults = benchD.getRawResultString();

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
	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 1;
	string transformResults, decoutResults;

	cout << "Benchmark iterations: " << iterationCount << endl;
	benchmarkDSE(outfile1, outfile2, iterationCount, transformResults, decoutResults);

	outfile1.close();
	outfile2.close();
//	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;
//	cout << transformResults << endl;
//	cout << "<=== Transform benchmarkBSW breakdown ===>" << endl;
//
//	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;
//	cout << decoutResults << endl;
//	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;

	return 0;
}

