#include "TestCKRSOut.h"
#include <fstream>
#include <time.h>

string getID(int len)
{
	string alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
	string id = "";
	int val, alpha_len = alphabet.size();
	for(int i = 0; i < len; i++)
	{
		val = (int) (rand() % alpha_len);
		id +=  alphabet[val];
	}
	cout << "Rand selected ID: '" << id << "'" << endl;
	return id;
}

void benchmarkCKRS(Ibeckrs09 & ckrs, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, int ID_string_len, int iterationCount, CharmListStr & keygenResults, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	int n = 5;
	int l = 32;
	Benchmark benchT, benchD, benchK;
	CharmList mpk, msk, ct, skBlinded, skBlinded2, transformOutputList;
    GT M, newM;
    ZR uf1;
    string id = getID(ID_string_len); // "somebody@example.com";
    double tf_in_ms, de_in_ms, kg_in_ms;

    ckrs.setup(n, l, mpk, msk);
	// BENCHMARK KEYGEN SETUP
	for(int i = 0; i < iterationCount; i++) {
		benchK.start();
		ckrs.extract(mpk, msk, id, uf1, skBlinded2);
		benchK.stop();
		kg_in_ms = benchK.computeTimeInMilliseconds();
	}
	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
    stringstream s0;
	s0 << ID_string_len << " " << benchK.getAverage() << endl;
	outfile0 << s0.str();
    keygenResults[ID_string_len] = benchK.getRawResultString();
	// BENCHMARK KEYGEN SETUP
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
		tf_in_ms = benchT.computeTimeInMilliseconds();
		//cout << "transformCT =\n" << transformOutputList << endl;

		benchD.start();
		ckrs.decout(transformOutputList, uf1, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Transform avg: " << benchT.getAverage() << endl;
	s1 << iterationCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
    transformResults[ID_string_len] = benchT.getRawResultString();

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decoutResults[ID_string_len] = benchD.getRawResultString();
	// measure ciphertext size
	cout << "CT size: " << measureSize(ct) << " bytes" << endl;
	cout << "CTOut size: " << measureSize(transformOutputList) << " bytes" << endl;

    //cout << convert_str(M) << endl;
    //cout << convert_str(newM) << endl;
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
	string FIXED = "fixed", RANGE = "range";
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ ID-string => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int ID_string_len = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "ID-string: " << ID_string_len << endl;
	cout << "measurement: " << fixOrRange << endl;

	srand(time(NULL));
	Ibeckrs09 ckrs;
	string filename = string(argv[0]);
	stringstream s3, s4, s5;
	ofstream outfile0, outfile1, outfile2, outfile3, outfile4, outfile5;
	string f0 = filename + "_keygenout.dat";
	string f1 = filename + "_transform.dat";
	string f2 = filename + "_decout.dat";
	string f3 = filename + "_transform_raw.txt";
	string f4 = filename + "_decout_raw.txt";
	string f5 = filename + "_keygenout_raw.txt";
	outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
	outfile3.open(f3.c_str());
	outfile4.open(f4.c_str());
	outfile5.open(f5.c_str());

	CharmListStr keygenResults, transformResults, decoutResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= ID_string_len; i++) {
			benchmarkCKRS(ckrs, outfile0, outfile1, outfile2, i, iterationCount, keygenResults, transformResults, decoutResults);
		}
		s3 << transformResults << endl;
		s4 << decoutResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkCKRS(ckrs, outfile0, outfile1, outfile2, ID_string_len, iterationCount, keygenResults, transformResults, decoutResults);
		s3 << ID_string_len << " " << transformResults[ID_string_len] << endl;
		s4 << ID_string_len << " " << decoutResults[ID_string_len] << endl;
		s5 << ID_string_len << " " << keygenResults[ID_string_len] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile3 << s3.str();
	outfile4 << s4.str();
	outfile5 << s5.str();
	outfile0.close();
	outfile1.close();
	outfile2.close();
	outfile3.close();
	outfile4.close();
	outfile5.close();
	return 0;
}

