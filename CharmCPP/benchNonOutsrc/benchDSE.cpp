#include "TestDSE.h"
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

void benchmarkDSE(Dsewaters09 & dse, ofstream & outfile2, int ID_string_len, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
    CharmList msk, mpk, pk, sk, ct;
    GT M, newM;
    ZR bf0;
    string id = getID(ID_string_len); // "somebody@example.com and other people!!!!!";
    double de_in_ms;

	dse.setup(mpk, msk);
	dse.keygen(mpk, msk, id, sk);

    M = dse.group.random(GT_t);
    //cout << "M: " << convert_str(M) << endl;
    dse.encrypt(mpk, M, id, ct);

    stringstream s1, s2;

    //cout << "ct =\n" << ct << endl;
	for(int i = 0; i < iterationCount; i++) {
		// run TRANSFORM
		benchD.start();
		dse.decrypt(ct, sk, newM);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();
	}

	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[ID_string_len] = benchD.getRawResultString();

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
	Dsewaters09 dse;
	string filename = string(argv[0]);
	stringstream s4;
	ofstream outfile1, outfile2, outfile3, outfile4;
	string f2 = filename + "_decrypt.dat";
	string f4 = filename + "_decrypt_raw.txt";
	outfile2.open(f2.c_str());
	outfile4.open(f4.c_str());

	CharmListStr decryptResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= ID_string_len; i++) {
			benchmarkDSE(dse, outfile2, i, iterationCount, decryptResults);
		}
		s4 << decryptResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkDSE(dse, outfile2, ID_string_len, iterationCount, decryptResults);
		s4 << ID_string_len << " " << decryptResults[ID_string_len] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile4 << s4.str();
	outfile2.close();
	outfile4.close();
	return 0;
}

