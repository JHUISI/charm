
#include "TestBGWOut.h"
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

void benchmarkBGW(Bgw05 & bgw, ofstream & outfile1, ofstream & outfile2, int numOfRecs, int iterationCount, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	Benchmark benchT, benchD;
	CharmList pk, msk, Hdr, ct, skCompleteBlinded, transformOutputList;
	CharmListInt S;
//	int receivers[] = {1, 3, 5, 12, 14};
// 	S.init(receivers, 5);
//	int n = 15, i = 1;
	GT K, KDecrypt;
	ZR bf0;
	getRandomReceivers(S, numOfRecs);
	int n = numOfRecs, i = S[(rand() % numOfRecs)];

	bgw.setup(n, pk, msk);
//	cout << "pk: " << pk << endl;
//	cout << "msk: " << msk << endl;

	bgw.keygen(pk, msk, n, bf0, skCompleteBlinded);
//	cout << "tk: " <<  skCompleteBlinded << endl;
//	cout << "bf: " << bf0 << endl;
	cout << "receiver: " << i << endl;
	bgw.encrypt(S, pk, n, ct);

	Hdr = ct[0].getList();
	K = ct[1].getGT();

	double tf_in_ms, de_in_ms;
	stringstream s1, s2;
	for(int j = 0; j < iterationCount; j++) {
		benchT.start();
		bgw.transform(S, i, n, Hdr, pk, skCompleteBlinded, transformOutputList);
		benchT.stop();
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		bgw.decout(S, i, n, Hdr, pk, skCompleteBlinded, transformOutputList, bf0, KDecrypt);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}
	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << numOfRecs << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults[numOfRecs] = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << numOfRecs << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults[numOfRecs] = benchD.getRawResultString();
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
	stringstream s3, s4;
	ofstream outfile1, outfile2, outfile3, outfile4;
	string f1 = filename + "_transform.dat";
	string f2 = filename + "_decout.dat";
	string f3 = filename + "_transform_raw.txt";
	string f4 = filename + "_decout_raw.txt";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
	outfile3.open(f3.c_str());
	outfile4.open(f4.c_str());

	CharmListStr transformResults, decoutResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= numRecs; i++) {
			cout << "Benchmark with group of " << i << " recipients." << endl;
			benchmarkBGW(bgw, outfile1, outfile2, i, iterationCount, transformResults, decoutResults);
		}
		s3 << transformResults << endl;
		s4 << decoutResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkBGW(bgw, outfile1, outfile2, numRecs, iterationCount, transformResults, decoutResults);
		s3 << numRecs << " " << transformResults[numRecs] << endl;
		s4 << numRecs << " " << decoutResults[numRecs] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile3 << s3.str();
	outfile4 << s4.str();
	outfile1.close();
	outfile2.close();
	outfile3.close();
	outfile4.close();
//	cout << "<=== Transform benchmarkBGW breakdown ===>" << endl;
//	cout << transformResults << endl;
//	cout << "<=== Transform benchmarkBGW breakdown ===>" << endl;
//
//	cout << "<=== Decout benchmarkBGW breakdown ===>" << endl;
//	cout << decoutResults << endl;
//	cout << "<=== Decout benchmarkBGW breakdown ===>" << endl;
	return 0;
}

