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

void benchmarkWATERS(Lw10 & lw, ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD;
	CharmMetaList msk, pk;
	CharmList gpk, sk, ct;
	CharmListStr authS, userS; // set this
	GT M, newM;

	string gid = "jhu@authority.com", policy_str = "((ATTR4 or ATTR3) and (ATTR2 or ATTR1))"; // set this

    double tf_in_ms, de_in_ms;

    getAttributes(authS, 4);
    getAttributes(userS, 3);
    // getAttributes(authS, attributeCount);
    //string policy_str =  getPolicy(attributeCount); // get a policy string

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

int main()
{
	Lw10 lw;
	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 10;
	int attributeCount = 10;
	CharmListStr decryptResults;
	for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << " attributes." << endl;
		benchmarkWATERS(lw, outfile1, outfile2, i, iterationCount, decryptResults);
	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Decrypt Result breakdown ===>" << endl;
	cout << decryptResults << endl;
	cout << "<=== Decrypt Result breakdown ===>" << endl;

	return 0;
}

