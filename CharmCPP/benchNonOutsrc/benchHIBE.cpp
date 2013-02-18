#include "TestHIBE.h"
#include <fstream>

void benchmarkHIBE(Hibe & hibe, ofstream & outfile1, ofstream & outfile2, int iterationCount, string & decryptResults)
{
	int l = 5;
	int z = 32;
	Benchmark benchT, benchD;
    CharmList mk, mpk, pk, sk, ct;
    GT M, newM;
    ZR uf0;
    string id = "somebody@example.com"; // make this longer?
    double de_in_ms;

	hibe.setup(l, z, mpk, mk);
	hibe.keygen(mpk, mk, id, pk, sk);

    M = hibe.group.random(GT_t);
    hibe.encrypt(mpk, pk, M, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		benchD.start();
		hibe.decrypt(pk, sk, ct, newM);
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
	Hibe hibe;
	string filename = "hibe";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 1;
	string decryptResults;

	cout << "Benchmark iterations: " << iterationCount << endl;
	benchmarkHIBE(hibe, outfile1, outfile2, iterationCount, decryptResults);

	outfile1.close();
	outfile2.close();

	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decout benchmarkBSW breakdown ===>" << endl;

	return 0;
}

