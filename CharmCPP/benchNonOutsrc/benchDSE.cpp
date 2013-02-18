#include "TestDSE.h"
#include <fstream>

void benchmarkDSE(Dsewaters09 & dse, ofstream & outfile1, ofstream & outfile2, int iterationCount, string & decryptResults)
{
	Benchmark benchT, benchD;
    CharmList msk, mpk, pk, sk, ct;
//    CharmListStr S;
    GT M, newM;
    ZR bf0;
    string id = "somebody@example.com and other people!!!!!";
    double de_in_ms;

	dse.setup(mpk, msk);
	dse.keygen(mpk, msk, id, sk);

    M = dse.group.random(GT_t);
    cout << "M: " << convert_str(M) << endl;
    dse.encrypt(mpk, M, id, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
//	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchD.start();
		dse.decrypt(ct, sk, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
//	}

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults = benchD.getRawResultString();

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
	Dsewaters09 dse;
	string filename = "dse";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 1;
	string decryptResults;

	cout << "Benchmark iterations: " << iterationCount << endl;
	benchmarkDSE(dse, outfile1, outfile2, iterationCount, decryptResults);

	outfile1.close();
	outfile2.close();
	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;

	return 0;
}

