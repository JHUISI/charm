#include "TestLW.h"
#include <sys/time.h>
#include <fstream>

typedef struct timeval timeval_t;
string createString(int i)
{
	stringstream ss;
	ss << "ATTR" << i;
	return ss.str();
}

void getAttributes(CharmListStr & attrList, int max)
{
	for(int i = 1; i <= max; i++) {
		attrList.append(createString(i));
	}
}

string getPolicy(int max)
{
	string policystr;
	if(max >= 2) {
		policystr = "(" + createString(1) + " and " + createString(2) + ")";
	}
	else if(max == 1) {
		policystr = createString(1);
	}

	for(int i = 3; i <= max; i++)
	{
		policystr = "(" + policystr + " and " + createString(i) + ")";
	}

	return policystr;
}

void benchmarkLW(Lw10 & lw, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
	CharmMetaList msk, pk;
	CharmList gpk, sk, ct;
	CharmListStr authS, userS; // set this
	GT M, newM;

	string gid = "jhu@authority.com"; // , policy_str = "((ATTR4 or ATTR3) and (ATTR2 or ATTR1))"; // set this

    double de_in_ms;

    getAttributes(authS, attributeCount);
    getAttributes(userS, attributeCount);
    // getAttributes(authS, attributeCount);
    string policy_str =  getPolicy(attributeCount); // get a policy string

    lw.setup(gpk);
    lw.authsetup(gpk, authS, msk, pk);

    lw.keygen(gpk, msk, gid, userS, sk);
    M = lw.group.random(GT_t);
    lw.encrypt(pk, gpk, M, policy_str, ct);

    stringstream s1, s2;

	for(int i = 0; i < iterationCount; i++) {
		// run Decrypt
		benchD.start();
		lw.decrypt(sk, userS, ct, newM);
		benchD.stop();

		de_in_ms = benchD.computeTimeInMilliseconds();
		//cout << i << ": Raw DE: " << de_in_ms << endl;
	}

	cout << "Decout avg: " << benchD.getAverage() << endl;
	s2 << attributeCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[attributeCount] = benchD.getRawResultString();

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
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ attributeCount => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int attributeCount = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "attributeCount: " << attributeCount << endl;
	cout << "measurement: " << fixOrRange << endl;

	Lw10 lw;
	string filename = string(argv[0]);
	stringstream s3, s4;
	ofstream outfile2, outfile4;
	string f2 = filename + "_decrypt.dat";
	string f4 = filename + "_decrypt_raw.txt";
	outfile2.open(f2.c_str());
	outfile4.open(f4.c_str());

	CharmListStr decryptResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= attributeCount; i++) {
			cout << "Benchmark with " << i << " attributes." << endl;
			benchmarkLW(lw, outfile2, i, iterationCount, decryptResults);
		}
		s4 << decryptResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		cout << "Benchmark with " << attributeCount << " attributes." << endl;
		benchmarkLW(lw, outfile2, attributeCount, iterationCount, decryptResults);
		s4 << attributeCount << " " << decryptResults[attributeCount] << endl;
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

