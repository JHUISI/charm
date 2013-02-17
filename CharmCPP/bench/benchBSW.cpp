#include "TestBSW.h"
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

void start(timeval_t startTime)
{
    // Get the starting time.
    gettimeofday(&startTime, NULL);
}

void stop(timeval_t endTime)
{
    gettimeofday(&endTime, NULL);
}

void benchmarkWATERS(ofstream & outfile1, ofstream & outfile2, int attributeCount, int iterationCount, CharmListStr & transformResults, CharmListStr & decoutResults)
{
	timeval_t startTime, endTime;
	Bsw07 bsw;
    CharmList mk, pk, skBlinded, ct, transformOutputList;
    CharmListStr S;
    GT M, newM;
    ZR bf0;
    double micro_in_ms = 1000;

    double sum_in_ms = 0.0, tf_in_ms, decout_in_ms;

    bsw.setup(mk, pk);
    getAttributes(S, attributeCount);
    bsw.keygen(pk, mk, S, bf0, skBlinded);

    M = bsw.group.random(GT_t);
    string policy_str =  getPolicy(attributeCount); // get a policy string
    bsw.encrypt(pk, M, policy_str, ct);

    stringstream s1, s2, ss1, ss2;

    //cout << "ct =\n" << ct << endl;
    sum_in_ms = 0.0;
	for(int i = 0; i < iterationCount; i++) {
		gettimeofday(&startTime, NULL);
		// run TRANSFORM
		bsw.transform(pk, skBlinded, S, ct, transformOutputList);
		gettimeofday(&endTime, NULL);
		//cout << "transformCT =\n" << transformOutputList << endl;

		tf_in_ms = (endTime.tv_sec - startTime.tv_sec) * 1000000 + (endTime.tv_usec - startTime.tv_usec);
		double tmp = (tf_in_ms / micro_in_ms);
		ss1 << tmp << ", ";
		sum_in_ms += tmp;
	}
    double avg_tf = sum_in_ms / iterationCount;
    s1 << attributeCount << " " << avg_tf;
    outfile1 << s1.str() << endl;
    cout << "transform benchmark: " << avg_tf << " ms" << endl;
    //cout << "raw benchmarks: " << ss1.str() << endl;
    transformResults[attributeCount] = ss1.str();

    sum_in_ms = 0.0;
	for(int i = 0; i < iterationCount; i++)
	{
		gettimeofday(&startTime, NULL);
		// run DECOUT
		bsw.decout(pk, S, transformOutputList, bf0, newM);
		gettimeofday(&endTime, NULL);
		decout_in_ms = (endTime.tv_sec - startTime.tv_sec) * 1000000 + (endTime.tv_usec - startTime.tv_usec);
		double tmp = (decout_in_ms / micro_in_ms);
		ss2 << tmp << ", ";
		sum_in_ms += tmp;
	}

    double avg_decout = sum_in_ms / iterationCount;
    s2 << attributeCount << " " << avg_decout;
    outfile2 << s2.str() << endl;
    cout << "decout benchmark: " << avg_decout << " ms" << endl;
	//cout << "raw benchmarks: " << ss2.str() << endl;
    decoutResults[attributeCount] = ss2.str();

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
	string filename = "test";
	ofstream outfile1, outfile2;
	string f1 = filename + "_tra.dat";
	string f2 = filename + "_dec.dat";
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	int iterationCount = 10;
	int attributeCount = 10;
	CharmListStr transformResults, decoutResults;
	for(int i = 2; i <= attributeCount; i++) {
		cout << "Benchmark with " << i << " attributes." << endl;
		benchmarkWATERS(outfile1, outfile2, i, iterationCount, transformResults, decoutResults);
	}

	outfile1.close();
	outfile2.close();
	cout << "<=== Transform Result breakdown ===>" << endl;
	cout << transformResults << endl;
	cout << "<=== Transform Result breakdown ===>" << endl;

	cout << "<=== Decout Result breakdown ===>" << endl;
	cout << decoutResults << endl;
	cout << "<=== Decout Result breakdown ===>" << endl;

	return 0;
}

