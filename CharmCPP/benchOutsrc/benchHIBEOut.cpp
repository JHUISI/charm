#include "TestHIBEOut.h"
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

void benchmarkHIBE(Hibe & hibe, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, int ID_string_len, int iterationCount, CharmListStr & keygenResults, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	int l = 5;
	int z = 32;
	Benchmark benchT, benchD, benchK;
    CharmList mk, mpk, pk, skBlinded, skBlinded2, ct, transformOutputList;
//    CharmListStr S;
    GT M, newM;
    ZR uf0;
    string id = getID(ID_string_len); // "somebody@example.com";
    double tf_in_ms, de_in_ms, kg_in_ms;
    stringstream s0;

	hibe.setup(l, z, mpk, mk);
	// BENCHMARK KEYGEN SETUP
	for(int i = 0; i < iterationCount; i++) {
		benchK.start();
		hibe.keygen(mpk, mk, id, pk, uf0, skBlinded2);
		benchK.stop();
		kg_in_ms = benchK.computeTimeInMilliseconds();
	}
	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
	s0 << ID_string_len << " " << benchK.getAverage() << endl;
	outfile0 << s0.str();
    keygenResults[ID_string_len] = benchK.getRawResultString();
	// BENCHMARK KEYGEN SETUP
	hibe.keygen(mpk, mk, id, pk, uf0, skBlinded);

    M = hibe.group.random(GT_t);
    hibe.encrypt(mpk, pk, M, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchT.start();
		hibe.transform(pk, skBlinded, ct, transformOutputList);
		benchT.stop();
		//cout << "transformCT =\n" << transformOutputList << endl;
		tf_in_ms = benchT.computeTimeInMilliseconds();

		benchD.start();
		hibe.decout(pk, transformOutputList, uf0, newM);
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
	string FIXED = "fixed", RANGE = "range";
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ ID-string => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int ID_string_len = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "ID-string: " << ID_string_len << endl;
	cout << "measurement: " << fixOrRange << endl;

	srand(time(NULL));
	Hibe hibe;
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
			benchmarkHIBE(hibe, outfile0, outfile1, outfile2, i, iterationCount, keygenResults, transformResults, decoutResults);
		}
		s3 << transformResults << endl;
		s4 << decoutResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkHIBE(hibe, outfile0, outfile1, outfile2, ID_string_len, iterationCount, keygenResults, transformResults, decoutResults);
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
	outfile1.close();
	outfile2.close();
	outfile3.close();
	outfile4.close();
	outfile5.close();
	return 0;
}

