
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
	cout << "Recs:\n" << recs << endl;
	return;
}

void benchmarkBGW(Bgw05 & bgw, ofstream & outfile1, ofstream & outfile2, int numOfRecs, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
	CharmList pk, msk, Hdr, ct;
	CharmMetaListG1 skComplete;
	CharmListInt S;
//	int receivers[] = {1, 3, 5, 12, 14};
// 	S.init(receivers, 5);
//	int n = 15, i = 1;
	GT K, KDecrypt;
	ZR bf0;
	getRandomReceivers(S, numOfRecs);
	int n = numOfRecs, i = S[2];

	bgw.setup(n, pk, msk);
//	cout << "pk: " << pk << endl;
//	cout << "msk: " << msk << endl;

	bgw.keygen(pk, msk, n, skComplete);
//	cout << "tk: " <<  skCompleteBlinded << endl;
//	cout << "bf: " << bf0 << endl;
	cout << "receiver: " << i << endl;
	bgw.encrypt(S, pk, n, ct);

	Hdr = ct[0].getList();
	K = ct[1].getGT();

	double de_in_ms;
	stringstream s1, s2;
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
	Bgw05 bgw;
	srand(time(NULL));

	string filename = "bgw"; // fill in
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 10; // fill in
	int numberOfReceivers = 15; // fill in
	int i = numberOfReceivers;
	CharmListStr decryptResults;
	//for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with group of " << i << " recipients." << endl;
		benchmarkBGW(bgw, outfile1, outfile2, i, iterationCount, decryptResults);
	//}

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt benchmarkBGW breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt benchmarkBGW breakdown ===>" << endl;
    return 0;
}
