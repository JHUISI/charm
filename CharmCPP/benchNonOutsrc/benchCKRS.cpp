#include "TestCKRS.h"
#include <fstream>

void benchmarkCKRS(Ibeckrs09 & ckrs, ofstream & outfile1, ofstream & outfile2, int iterationCount, string & decryptResults)
{
	int n = 5;
	int l = 32;
	Benchmark benchT, benchD;
	CharmList mpk, msk, ct, sk;
    GT M, newM;
    string id = "somebody@example.com"; // make this longer?
    double de_in_ms;

	ckrs.setup(n, l, mpk, msk);
	ckrs.extract(mpk, msk, id, sk);

    M = ckrs.group.random(GT_t);
    ckrs.encrypt(mpk, M, id, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchD.start();
		ckrs.decrypt(sk, ct, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults = benchD.getRawResultString();

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
	string filename = "ckrs";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 100;
	string decryptResults;

	cout << "Benchmark iterations: " << iterationCount << endl;
	benchmarkCKRS(ckrs, outfile1, outfile2, iterationCount, decryptResults);

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt benchmarkBSW breakdown ===>" << endl;

	return 0;
}

