
#include "TestBGW.h"
#include <fstream>
#include <time.h>

void getRandomReceivers(CharmListInt & recs, int numRecs)
{
	int val;
	for(int i = 0; i < numRecs; i++) {
		val = (int) (rand() % numRecs) + 1;
		if(recs.contains(val) == false) {
			recs[i] = val;
		}
		else {
			i--;
			continue;
		}
	}
	//cout << "Recs:\n" << recs << endl;
	return;
}

void benchmarkBGW(Bgw05 & bgw, ofstream & outfile1, ofstream & outfile2, int numOfRecs, int iterationCount, CharmListStr & keygenResults, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD, benchK;
	CharmList pk, msk, Hdr, ct;
	CharmMetaListG1 skComplete, skComplete2;
	CharmListInt S;
//	int receivers[] = {1, 3, 5, 12, 14};
// 	S.init(receivers, 5);
//	int n = 15, i = 1;
	GT K, KDecrypt;
	ZR bf0;
	getRandomReceivers(S, numOfRecs);
	int n = numOfRecs, i = S[(rand() % numOfRecs)];
	double kg_in_ms;
	bgw.setup(n, pk, msk);
//	cout << "pk: " << pk << endl;
//	cout << "msk: " << msk << endl;
	// BENCHMARK KEYGEN SETUP
	for(int i = 0; i < iterationCount; i++) {
		benchK.start();
		bgw.keygen(pk, msk, n, skComplete2);
		benchK.stop();
		kg_in_ms = benchK.computeTimeInMilliseconds();
	}
	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
    stringstream s1;
	s1 << numOfRecs << " " << benchK.getAverage() << endl;
	outfile1 << s1.str();
    keygenResults[numOfRecs] = benchK.getRawResultString();
	// BENCHMARK KEYGEN SETUP

	bgw.keygen(pk, msk, n, skComplete);
//	cout << "tk: " <<  skCompleteBlinded << endl;
//	cout << "bf: " << bf0 << endl;
	cout << "receiver: " << i << endl;
	bgw.encrypt(S, pk, n, ct);

	Hdr = ct[0].getList();
	K = ct[1].getGT();

	double de_in_ms;
	stringstream s2;
	for(int j = 0; j < iterationCount; j++) {
		benchD.start();
		bgw.decrypt(S, i, n, Hdr, pk, skComplete, KDecrypt);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}
	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
	s2 << numOfRecs << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[numOfRecs] = benchD.getRawResultString();
//    cout << convert_str(K) << endl;
//    cout << convert_str(KDecrypt) << endl;
    if(K == KDecrypt) {
      cout << "Successful Decryption!" << endl;
    }
    else {
      cout << "FAILED Decryption." << endl;
    }
}

int main(int argc, const char *argv[])
{
	string FIXED = "fixed", RANGE = "range";
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ numReceivers => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int numRecs = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "numReceivers: " << numRecs << endl;
	cout << "measurement: " << fixOrRange << endl;

	Bgw05 bgw;
	srand(time(NULL));
	string filename = string(argv[0]);
	stringstream s4, s5;
	ofstream outfile1, outfile2, outfile3, outfile4;
	string f1 = filename + "_keygen.dat";
	string f2 = filename + "_decrypt.dat";
	string f3 = filename + "_keygen_raw.txt";
	string f4 = filename + "_decrypt_raw.txt";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
	outfile3.open(f3.c_str());
	outfile4.open(f4.c_str());

	CharmListStr keygenResults, decryptResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= numRecs; i++) {
			cout << "Benchmark with group of " << i << " recipients." << endl;
			benchmarkBGW(bgw, outfile1, outfile2, i, iterationCount, keygenResults, decryptResults);
		}
		s4 << decryptResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkBGW(bgw, outfile1, outfile2, numRecs, iterationCount, keygenResults, decryptResults);
		s4 << numRecs << " " << decryptResults[numRecs] << endl;
		s5 << numRecs << " " << keygenResults[numRecs] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile4 << s4.str();
	outfile1 << s5.str();
	outfile1.close();
	outfile2.close();
	outfile4.close();
	return 0;
}
